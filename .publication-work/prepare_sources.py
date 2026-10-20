"""One-time, local-only release preparation. Original sources remain untouched."""
import ast
import io
import re
import tokenize
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / 'publication_release'
CJK = re.compile(r'[\u3400-\u9fff]')
DOCS = {
    'Motion': 'Control the serial stepper drives and parallel gripper.',
    'send_msg': 'Send a hexadecimal command and return the serial response bytes.',
    'send_instr': 'Send a CRC-protected command to a supported axis; return its hexadecimal reply.',
    'initial_setup': 'Configure pulses, current, direction, positioning mode, and speed.',
    'get_running_status': 'Return eight status bits, least significant first.\n\nBits 0 through 6: fault, enabled, running, reserved, command complete,\npath complete, homing complete.',
    'get_axis_status': 'Check every axis and stop execution if a drive reports a fault.',
    'get_position': 'Return the motor position as high and low hexadecimal words.',
    '_to_hex_8_bytes': 'Split a non-negative position into two 16-bit hexadecimal words.',
    'check_move_status': 'Wait until the drive no longer reports motion.\n\nThis checks the running bit, not measured endpoint accuracy.',
    'single_move': 'Move one axis to the requested absolute position in drive units.',
    'move_xyz': 'Move x and y, then the optional z axes. A z position of -1 leaves it unchanged.',
    'Weighing': 'Read and tare the serial balance; reported weights use milligrams.',
    'tare': 'Tare the balance and wait for its settling delay.',
    'record_weigh': 'Request a displayed weight in milligrams, or return None on a read failure.',
    'calc_crc': 'Append a little-endian Modbus CRC16.\n\nAccept hexadecimal text or bytes and preserve the input representation.',
    'handle_weighing_head': 'Pick up (flag=1) or return (flag=2) the head for a chemical.\n\nReturn the initial, alignment, and dispensing positions from the head table.',
    'align_weighing_head': 'Align the weighing head with the ZR actuator.',
    'move_to_xyz': 'Move axes in the sequence selected by flag.\n\n1: x,y,z1; 2: z1,x,y; 3: x,y,z2; 4: z2,x,y; 5: z1,z2,x,y.',
    'handle_sample_bottle': 'Transfer a bottle to the balance (flag=1) or return it to the rack (flag=2).',
    'weighing_params': 'Calculate dispensing settings from the chemical database and target mass in mg.',
    'weighing_action': 'Run the specified number of actuator cycles at the alignment and dispensing positions.',
    'monitor_weight': 'Set the stop event when the measured mass reaches the coarse threshold in mg.',
    'start_weighing': 'Run coarse and fine dispensing and return the measured mass in mg.',
    'extract_and_save_columns': 'Validate and export selected columns from an Excel workbook.',
    'config_logger': 'Return a console and UTF-8 file logger for the requested log path.',
    'split_task': 'Split the supplied workbook into solid and liquid task tables.',
}
STRINGS = {
    '夹爪初始化完成 Gripper initialization completed': 'Gripper initialization completed',
    '电机驱动器初始设置已完成 Motor driver initial setup completed': 'Motor driver initial setup completed',
    '天平去皮完成 Balance shelling completed': 'Balance tare completed',
    '设备初始化完成 Device Initialized': 'Device initialized',
    '配置文件读取成功, 内容为: ': 'Configuration loaded: ',
    '测试平均掉落量为0，重新测试': 'Mean dispensed mass is zero; retrying',
    '回零进行中 Axis': ' homing in progress; axis ',
    '回零完成 Axis': ' homing completed; axis ',
    '轴)未接收到数据': ' axis): no data received',
    '轴)通信时出错: ': ' axis): communication error: ',
    '经过3次尝试，从串口 ': 'No response after three retries on serial port ',
    'Z轴回到安全高度': 'Z axes returned to the configured clearance height',
    '缺少必要的配置信息': 'Required configuration is missing',
    '夹持物品掉落': 'Gripped object was dropped',
    '夹爪夹持完成': 'Gripper closed',
    '夹爪张开完成': 'Gripper opened',
    '打开串口失败: ': 'Failed to open serial port: ',
    '发送消息时发生错误: ': 'Failed to send message: ',
    '无效的轴: ': 'Invalid axis: ',
    '. 有效值为: ': '. Supported axes: ',
    '与设备(': 'Device (',
    ' 的地址为 ': ', device address ',
    ' 的设备(': ', device (',
    '轴故障': ' axis fault',
    '读取配置文件 ': 'Failed to read configuration ',
    '配置文件中缺少 ': 'Configuration is missing ',
    ' 配置.': ' settings.',
    '配置文件 ': 'Configuration file ',
    ' 读取成功.': ' loaded successfully.',
    ' 未找到.': ' was not found.',
    ' 时出错: ': ': ',
    '称重完成: ': 'Measured weight: ',
    '开始动作': 'Starting dispensing cycles: ',
    '次，执行器深度': '; actuator depth: ',
    '开始称重，目标重量': 'Starting weighing; target mass (mg): ',
    '当前重量': 'Current mass (mg): ',
    '测试平均掉落量：': 'Mean dispensed mass (mg): ',
    '目标重量：': 'Target mass (mg): ',
    '，实际重量: ': '; measured mass (mg): ',
    '，当前重量：': '; current mass (mg): ',
    '，执行器深度': '; actuator depth: ',
    '，掉落量：': '; dispensed mass (mg): ',
    '，目标掉落量：': '; target dispensed mass (mg): ',
    '，误差百分比：': '; relative error (%): ',
    '，误差': '; error (mg): ',
    '，超过粗称阈值': '; reached coarse threshold (mg): ',
    '，重新测试': '; retrying',
    'liquid_task_columns中以下列不存在于Excel文件中：': 'Missing liquid-task columns: ',
    'solid_task_columns中以下列不存在于Excel文件中：': 'Missing solid-task columns: ',
    '以下列不存在于Excel文件中：': 'Missing workbook columns: ',
    '数据已保存到 ': 'Saved data to ',
    '轴': 'Axis ',
}

for p in (ROOT / 'solid_handling_station').rglob('*.py'):
    # Replaced separately by validated English implementations below.
    if p.name == 'station_server.py':
        continue
    source = p.read_text(encoding='utf-8-sig')
    tree = ast.parse(source)
    lines = source.splitlines(keepends=True)
    changes = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef)):
            doc = ast.get_docstring(node)
            if doc and CJK.search(doc):
                expr = node.body[0]
                doc = DOCS[node.name]
                indent = ' ' * expr.col_offset
                replacement = indent + '"""' + doc.replace('\n', '\n' + indent) + '"""\n'
                changes.append((expr.lineno-1, expr.end_lineno, replacement))
    for start, end, replacement in sorted(changes, reverse=True):
        lines[start:end] = [replacement]
    source = ''.join(lines)
    # Drop redundant non-English comments, retaining existing English translations.
    tokens = []
    for tok in tokenize.generate_tokens(io.StringIO(source).readline):
        if tok.type == tokenize.COMMENT and CJK.search(tok.string):
            last = max(m.end() for m in CJK.finditer(tok.string))
            tail = tok.string[last:].strip(' ,.:;，。：；')
            english = tail if re.match(r'[A-Za-z][A-Za-z ]{8,}', tail) else ''
            tok = tok._replace(string=('# ' + english) if english else '')
        tokens.append(tok)
    source = tokenize.untokenize(tokens)
    for old, new in STRINGS.items():
        source = source.replace(old, new)
    p.write_text(source, encoding='utf-8', newline='\n')

# Identical station communication classes already exist in English.
solid = ROOT / 'solid_handling_station'
for name in ['client/station_info.py', 'server/station_server.py']:
    (solid / name).write_text((ROOT / 'liquid-handling-workstation' / name).read_text(encoding='utf-8'), encoding='utf-8')

for p in solid.rglob('*.yaml'):
    source = p.read_text(encoding='utf-8')
    source = '\n'.join(line.split('#')[0].rstrip() if CJK.search(line) else line for line in source.splitlines()) + '\n'
    source = re.sub(r'10\.26\.50\.234', '192.0.2.11', source)
    p.write_text('# Example configuration; validate all ports and positions for your installation.\n' + source, encoding='utf-8')

# XLSX numerical values, cells, styles, formulas, and relationships are unchanged.
# Only Office document properties (author/title metadata) are anonymized in English.
for p in ROOT.rglob('*.xlsx'):
    with zipfile.ZipFile(p) as z:
        members = [(info, z.read(info.filename)) for info in z.infolist()]
    with zipfile.ZipFile(p, 'w', zipfile.ZIP_DEFLATED) as z:
        for info, data in members:
            if info.filename.startswith('docProps/') and info.filename.endswith('.xml'):
                source = data.decode('utf-8')
                source = re.sub(r'>([^<]*)<', lambda m: '><' if CJK.search(m[1]) else m[0], source)
                data = source.encode('utf-8')
            z.writestr(info, data)

print('Translated retained Python docstrings and messages; sanitized workbook document properties.')
