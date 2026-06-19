import ctypes
import platform

systype = platform.system()
if systype == 'Windows':
    if platform.architecture()[0] == '64bit':
        zauxdll = ctypes.WinDLL('E:\\Users\\1250\\Desktop\\photocatalytic-automation\\devices\\zmotion\\zauxdll.dll')
        print('Windows x64')
    else:
        zauxdll = ctypes.WinDLL('E:\\Users\\1250\\Desktop\\photocatalytic-automation\\devices\\zmotion\\zauxdll.dll')
        print('Windows x86')
elif systype == 'Darwin':
    zmcdll = ctypes.CDLL('.\\zmotion.dylib')
    print("macOS")
elif systype == 'Linux':
    zmcdll = ctypes.CDLL('.\\zmotion.so')
    print("Linux")
else:
    print("OS Not Supported!!")


class ZAUXDLL:
    def __init__(self):
        self.handle = ctypes.c_void_p()

    def ZAux_Execute(self, pszCommand):
        '''
        Description: Excute , .

        param pszCommand: . type: sting

        param uiResponseLength: . type: uint32

        Return: , . type: int32,sting

       '''
        _str = pszCommand.encode('utf-8')
        psResponse = ctypes.c_char_p()
        psResponse.value = b''
        uiResponseLength = 2048
        ret = zauxdll.ZAux_Execute(
            self.handle, _str, psResponse, uiResponseLength)
        rev = psResponse.value.decode('utf-8')
        return ret, rev

    def ZAux_DirectCommand(self, pszCommand):
        '''
        Description: DirectCommand , .

        param pszCommand: . type: sting

        param uiResponseLength: . type: uint32

        Return: , . type: int32,sting

       '''
        _str = pszCommand.encode('utf-8')
        psResponse = ctypes.c_char_p()
        psResponse.value = b''
        uiResponseLength = 2048
        ret = zauxdll.ZAux_DirectCommand(
            self.handle, _str, psResponse, uiResponseLength)
        rev = psResponse.value.decode('utf-8')
        return ret, rev

    def ZAux_OpenEth(self, ipaddr):
        '''
        Description: .

        param ipaddress:IP , . type: sting

        Return: . type: int32

       '''
        ip_bytes = ipaddr.encode('utf-8')
        p_ip = ctypes.c_char_p(ip_bytes)
        ret = zauxdll.ZAux_OpenEth(p_ip, ctypes.pointer(self.handle))
        return ret

    def ZAux_SearchEthlist(self, address_buff_length, ms):
        #  '''
        # Description: IP ..
        #
        # param addrbufflength: IP type: uint32
        #
        # param ms: . type: uint32
        #
        # Return,Ipaddrlist: , IP type: sting
        #
        # '''

        # ip_address_list = ctypes.c_char_p(ip_address_list.encode('utf-8'))
        address_buff_length = ctypes.c_uint32(address_buff_length)
        ms = ctypes.c_uint32(ms)
        ip = ctypes.c_char_p("".encode('utf-8'))
        ret = zauxdll.ZAux_SearchEthlist(ip, address_buff_length, ms)
        return ret, ip

    def ZAux_SearchEth(self, ipaddress, uims):
        #  '''
        # Description: .
        #
        # param ipaddress: IP . type: sting
        #
        # param uims: . type: uint32
        #
        # Return: , ERR_OK . type: int32
        #
        # '''
        ip_bytes = ipaddress.encode('utf-8')
        p_ip = ctypes.c_char_p(ip_bytes)
        ret = zauxdll.ZAux_SearchEth(
            p_ip, ctypes.c_int(uims), ctypes.pointer(self.handle))
        return ret

    def ZAux_OpenCom(self, comid):
        '''
        Description: , .

        param comid: type: uint32

        Return: . type: int32

       '''
        ret = zauxdll.ZAux_OpenCom(ctypes.c_uint32(
            comid), ctypes.pointer(self.handle))
        return ret

    def ZAux_Close(self):
        '''
        Description: .

        Return: . type: int32

       '''
        ret = zauxdll.ZAux_Close(self.handle)
        return ret

    def ZAux_Direct_GetAD(self, ionum):
        '''
        Description: .

        param ionum:AIN . type: int

        Return: , 4 0-4095. type: int32,folat

       '''
        value = ctypes.c_float()
        ret = zauxdll.ZAux_Direct_GetAD(
            self.handle, ctypes.c_int(ionum), ctypes.byref(value))
        return ret, value

    def ZAux_Direct_SetDA(self, ionum, fValue):
        '''
        Description: .

        param ionum:DA . type: int

        param fValue: 4 0-4095. type: float

        Return: . type: int32

       '''
        ret = zauxdll.ZAux_Direct_SetDA(
            self.handle, ctypes.c_int(ionum), ctypes.c_float(fValue))
        return ret

    def ZAux_Direct_GetDA(self, ionum):
        '''
        Description: .

        param ionum: . type: int

        Return: , 4 0-4095. type: int32, float

       '''
        value = ctypes.c_float()
        ret = zauxdll.ZAux_Direct_GetDA(
            self.handle, ctypes.c_int(ionum), ctypes.byref(value))
        return ret, value

    def ZAux_SearchAndOpenCom(self, uimincomidfind, uimaxcomidfind, uims):
        '''
        Description: .

        param uimincomidfind: . type: uint32

        param uimincomidfind: . type: uint32

        param uims: . type: uint32

        Return: , COM, handle . type: int32,uint

       '''
        value = ctypes.c_int()
        ret = zauxdll.ZAux_SearchAndOpenCom(ctypes.c_uint32(uimincomidfind), ctypes.c_uint32(uimaxcomidfind),
                                            ctypes.byref(value), uims, ctypes.pointer(self.handle))
        return ret, value

    def ZAux_OpenEth(self, ipaddr):
        '''
        Description: .

        param ipaddr:IP , . type: sting

        Return: . type: int32

       '''
        ip_bytes = ipaddr.encode('utf-8')
        p_ip = ctypes.c_char_p(ip_bytes)
        ret = zauxdll.ZAux_OpenEth(p_ip, ctypes.pointer(self.handle))
        return ret

    def ZAux_SetComDefaultBaud(self, dwBaudRate, dwByteSize, dwParity, dwStopBits):
        '''
        Description: .

        param dwBaudRate: . type: uint32

        param dwParity:NOPARITY, . type: uint32

        param dwStopBits:ONESTOPBIT . type: uint32

        Return: . type: int32

       '''
        ret = zauxdll.ZAux_SetComDefaultBaud(ctypes.c_uint32(dwBaudRate), ctypes.c_uint32(dwByteSize),
                                             ctypes.c_uint32(dwParity), ctypes.c_uint32(dwStopBits))
        return ret

    def ZAux_SetIp(self, ipaddress):
        '''
        Description: IP .

        param ipaddress:IP . type: sting

        Return: . type: int32

       '''
        ip_bytes = ipaddress.encode('utf-8')
        p_ip = ctypes.c_char_p(ip_bytes)
        ret = zauxdll.ZAux_SetIp(self.handle, p_ip)
        return ret

    def ZAux_Resume(self):
        '''
        Description: BAS .

        Return: . type: int32

       '''
        ret = zauxdll.ZAux_Resume(self.handle)
        return ret

    def ZAux_Pause(self):
        '''
        Description: BAS

        Return: . type: int32

       '''
        ret = zauxdll.ZAux_Pause(self.handle)
        return ret

    def ZAux_BasDown(self, Filename, run_mode):
        '''
        Description: BAS ZAR .

        param Filename:BAS . type: sting

        :param run_mode:0-RAM  1-ROM。   type: uint32

        Return: . type: int32

       '''
        _str = Filename.encode('utf-8')
        ret = zauxdll.ZAux_BasDown(
            self.handle, _str, run_mode, ctypes.pointer(self.handle))
        return ret

    def ZAux_Direct_GetIn(self, ionum):
        '''
        Description: .

        param ionum:IN . type: int

        Return: , . type: int32, uint32

       '''
        value = ctypes.c_int32()
        ret = zauxdll.ZAux_Direct_GetIn(
            self.handle, ctypes.c_int(ionum), ctypes.byref(value))
        return ret, value

    def ZAux_Direct_SetOp(self, ionum, iValue):
        '''
        Description: .

        param ionum: . type: int

        param iValue: . type: uint32

        Return: . type: int32

       '''

        ret = zauxdll.ZAux_Direct_SetOp(self.handle, ionum, iValue)
        return ret

    def ZAux_Direct_GetOp(self, ionum):
        '''
        Description: .

        param ionum: . type: int

        Return: , . type: int32,uint32

       '''
        value = ctypes.c_int32()
        ret = zauxdll.ZAux_Direct_GetOp(
            self.handle, ctypes.c_int(ionum), ctypes.byref(value))
        return ret, value

    def ZAux_Direct_SetInvertIn(self, ionum, bifInvert):
        '''
        Description: .

        param ionum: . type: int

        param bifInvert: 0\\1. type: int


        Return: . type: int32

       '''
        ret = zauxdll.ZAux_Direct_SetInvertIn(self.handle, ionum, bifInvert)
        return ret

    def ZAux_Direct_GetInvertIn(self, ionum):
        '''
        Description: .

        param ionum: . type: int

        Return: , . type: int32 ,int

       '''
        value = ctypes.c_int32()
        ret = zauxdll.ZAux_Direct_GetInvertIn(
            self.handle, ctypes.c_int(ionum), ctypes.byref(value))
        return ret, value

    def ZAux_Direct_SetPwmFreq(self, ionum, fValue):
        '''
        Description: pwm .

        param ionum:PWM . type: int

        param fValue: PWM1M PWM 2K. type: float

        Return: . type: int32

       '''
        ret = zauxdll.ZAux_Direct_SetPwmFreq(
            self.handle, ctypes.c_int(ionum), ctypes.c_float(fValue))
        return ret

    def ZAux_Direct_SetPwmDuty(self, ionum, fValue):
        '''
        Description: pwm .

        param ionum:PWM . type: int

        param fValue: 0-1 0 PWM . type: float

        Return: . type: int32

       '''

        ret = zauxdll.ZAux_Direct_SetPwmDuty(
            self.handle, ctypes.c_int(ionum), ctypes.c_float(fValue))
        return ret

    def ZAux_Direct_GetPwmDuty(self, ionum):
        '''
        Description: pwm .

        param ionum:PWM . type: int

        Return: , . type: int32,float

       '''

        ret = zauxdll.ZAux_Direct_SetPwmDuty(self.handle, ctypes.c_int(ionum))
        return ret

    def ZAux_Direct_GetPwmFreq(self, ionum):
        '''
        Description: pwm .

        param ionum:PWM . type: int

        Return: , . type: int32,float

       '''
        value = ctypes.c_float()
        ret = zauxdll.ZAux_Direct_GetPwmFreq(
            self.handle, ctypes.c_int(ionum), ctypes.byref(value))
        return ret, value

    def ZAux_GetModbusIn(self, ionumfirst, ionumend):
        '''
        Description: .

        param ionumfirst:IN . type: int

        param ionumend:IN . type: int

        Return: , . type: int32,uint8

       '''
        value = ctypes.c_int8()
        ret = zauxdll.ZAux_GetModbusIn(self.handle, ctypes.c_int(ionumfirst), ctypes.c_int(ionumend),
                                       ctypes.byref(value))
        return ret, value

    def ZAux_GetModbusOut(self, ionumfirst, ionumend):
        '''
        Description: .

        param ionumfirst:IN . type: int

        param ionumend:IN . type: int

        Return: , . type: int32,uint8

        '''
        value = ctypes.c_int8()
        ret = zauxdll.ZAux_GetModbusOut(self.handle, ctypes.c_int(ionumfirst), ctypes.c_int(ionumend),
                                        ctypes.byref(value))
        return ret, value

    def ZAux_GetModbusDpos(self, imaxaxises):
        '''
        Description: DPOS.

        param imaxaxises: type: int

        Return: , 0 . type: int32,float

        '''
        value = (ctypes.c_float * imaxaxises)()
        ret = zauxdll.ZAux_GetModbusDpos(self.handle, imaxaxises, value)
        return ret, value

    def ZAux_GetModbusMpos(self, imaxaxises):
        '''
        Description: MPOS.

        param imaxaxises: type: int

        Return: , 0 . type: int32,float

        '''
        value = (ctypes.c_float * imaxaxises)()
        ret = zauxdll.ZAux_GetModbusMpos(self.handle, imaxaxises, value)
        return ret, value

    def ZAux_GetModbusCurSpeed(self, imaxaxises):
        '''
        Description: .

        param imaxaxises: type: int

        Return: , 0 . type: int32,float

        '''
        value = (ctypes.c_float * imaxaxises)()
        ret = zauxdll.ZAux_GetModbusCurSpeed(self.handle, imaxaxises, value)
        return ret, value

    def ZAux_Direct_SetAccel(self, iaxis, fValue):
        '''
        Description: .

        param iaxis: type: int

        param fValue: type: float

        Return: . type: int32

        '''
        ret = zauxdll.ZAux_Direct_SetAccel(
            self.handle, ctypes.c_int(iaxis), ctypes.c_float(fValue))
        return ret

    def ZAux_Direct_SetParam(self, sParam, iaxis, fset):
        '''
        Description: sParam: .

        param sParam: "DPOS" ... type: sting

        param iaxis: type: int

        param fset: type: float

        Return: . type: int32

        '''
        _str = sParam.encode('utf-8')
        ret = zauxdll.ZAux_Direct_SetParam(
            self.handle, _str, ctypes.c_int(iaxis), ctypes.c_float(fset))
        return ret

    def ZAux_Direct_GetParam(self, sParam, iaxis):
        '''
        Description: , sParam: .

        param sParam: "DPOS" ... type: sting

        param iaxis: type: int

        Return: , . type: int32,float

        '''
        value = ctypes.c_float()
        _str = sParam.encode('utf-8')
        ret = zauxdll.ZAux_Direct_GetParam(
            self.handle, _str, ctypes.c_int(iaxis), ctypes.byref(value))
        return ret, value

    def ZAux_Direct_GetAccel(self, iaxis):
        '''
        Description: .

        param sParam: . type: int

        Return: , . type: int32,float

        '''
        value = ctypes.c_float()
        ret = zauxdll.ZAux_Direct_GetAccel(
            self.handle, iaxis, ctypes.byref(value))
        return ret, value

    def ZAux_Direct_GetAddax(self, iaxis):
        '''
        Description: .

        param iaxis: . type:int

        Return: , . type: int32,float

        '''
        value = ctypes.c_int()
        ret = zauxdll.ZAux_Direct_GetAddax(
            self.handle, ctypes.c_int(iaxis), ctypes.byref(value))
        return ret, value

    def ZAux_Direct_SetAlmIn(self, iaxis, iValue):
        '''
        Description: .

        param iaxis: . type: int

        param iValue: , -1 type: int

        Return: . type: int32
        '''

        ret = zauxdll.ZAux_Direct_SetAlmIn(
            self.handle, ctypes.c_int(iaxis), ctypes.c_int(iValue))
        return ret

    def ZAux_Direct_GetAlmIn(self, iaxis):
        '''
        Description: .

        param iaxis: . type:int

        Return: , . type: int32,int

        '''
        value = ctypes.c_int()
        ret = zauxdll.ZAux_Direct_GetAlmIn(
            self.handle, ctypes.c_int(iaxis), ctypes.byref(value))
        return ret, value

    def ZAux_Direct_SetAtype(self, iaxis, iValue):
        '''
        Description: .

        param iaxis: . type: int

        param iValue: . type: int

        Return: . type: int32
        '''

        ret = zauxdll.ZAux_Direct_SetAtype(
            self.handle, ctypes.c_int(iaxis), ctypes.c_int(iValue))
        return ret

    def ZAux_Direct_GetAtype(self, iaxis):
        '''
        Description: .

        param iaxis: . type:int

        Return: , . type: int32,int

        '''
        value = ctypes.c_int()
        ret = zauxdll.ZAux_Direct_GetAtype(
            self.handle, ctypes.c_int(iaxis), ctypes.byref(value))
        return ret, value

    def ZAux_Direct_GetAxisStatus(self, iaxis):
        '''
        Description: .

        param iaxis: . type:int

        Return: , . type: int32,int

        '''
        value = ctypes.c_int()
        ret = zauxdll.ZAux_Direct_GetAxisStatus(
            self.handle, ctypes.c_int(iaxis), ctypes.byref(value))
        return ret, value

    def ZAux_Direct_SetAxisAddress(self, iaxis, piValue):
        '''
        Description: .

        param iaxis: . type: int

        param piValue: . type: int

        Return: . type: int32
        '''

        ret = zauxdll.ZAux_Direct_SetAxisAddress(
            self.handle, ctypes.c_int(iaxis), ctypes.c_int(piValue))
        return ret

    def ZAux_Direct_GetAxisAddress(self, iaxis):
        '''
        Description: .

        param iaxis: . type:int

        Return: , . type: int32,int

        '''
        value = ctypes.c_int()
        ret = zauxdll.ZAux_Direct_GetAxisAddress(
            self.handle, ctypes.c_int(iaxis), ctypes.byref(value))
        return ret, value

    def ZAux_Direct_SetAxisEnable(self, iaxis, iValue):
        '''
        Description: ( ).

        param iaxis: . type: int

        param iValue: 0- 1- . type: int

        Return: . type: int32

        '''
        ret = zauxdll.ZAux_Direct_SetAxisEnable(
            self.handle, ctypes.c_int(iaxis), ctypes.c_int(iValue))
        return ret

    def ZAux_Direct_GetAxisEnable(self, iaxis):
        '''
        Description: .

        param iaxis: . type:int

        Return: , . type: int32,int

        '''
        value = ctypes.c_int()
        ret = zauxdll.ZAux_Direct_GetAxisEnable(
            self.handle, ctypes.c_int(iaxis), ctypes.byref(value))
        return ret, value

    def ZAux_Direct_SetClutchRate(self, iaxis, fValue):
        '''
        Description: .

        param iaxis: . type: int

        param fValue: . type: float

        Return: . type: int32

        '''
        ret = zauxdll.ZAux_Direct_SetClutchRate(
            self.handle, ctypes.c_int(iaxis), ctypes.c_float(fValue))
        return ret

    def ZAux_Direct_GetClutchRate(self, iaxis):
        '''
        Description: .

        param iaxis: . type:int

        Return: , . type: int32,float

        '''
        value = ctypes.c_float()
        ret = zauxdll.ZAux_Direct_GetClutchRate(
            self.handle, ctypes.c_int(iaxis), ctypes.byref(value))
        return ret, value

    def ZAux_Direct_SetCloseWin(self, iaxis, fValue):
        '''
        Description: .

        param iaxis: . type: int

        param fValue: . type: float

        Return: . type: int32

        '''

        ret = zauxdll.ZAux_Direct_SetCloseWin(
            self.handle, ctypes.c_int(iaxis), ctypes.c_float(fValue))
        return ret

    def ZAux_Direct_GetCloseWin(self, iaxis):
        '''
        Description: .

        param iaxis: . type:int

        Return: , . type: int32,float

        '''
        value = ctypes.c_float()
        ret = zauxdll.ZAux_Direct_GetCloseWin(
            self.handle, ctypes.c_int(iaxis), ctypes.byref(value))
        return ret, value

    def ZAux_Direct_SetCornerMode(self, iaxis, iValue):
        '''
        Description: .

        param iaxis: . type:int

        param iValue: . type:int

        Return: . type: int32

        '''
        ret = zauxdll.ZAux_Direct_SetCornerMode(
            self.handle, ctypes.c_int(iaxis), ctypes.c_int(iValue))
        return ret

    def ZAux_Direct_GetCornerMode(self, iaxis):
        '''
        Description: .

        param iaxis: . type:int

        Return: , . type: int32,int

        '''
        value = ctypes.c_int()
        ret = zauxdll.ZAux_Direct_GetCornerMode(
            self.handle, ctypes.c_int(iaxis), ctypes.byref(value))
        return ret, value

    def ZAux_Direct_SetCreep(self, iaxis, fValue):
        '''
        Description: .

        param iaxis: . type:int

        param fValue: . type:float

        Return: . type: int32

        '''
        value = ctypes.c_float()
        ret = zauxdll.ZAux_Direct_SetCreep(self.handle, ctypes.c_int(iaxis), ctypes.c_float(fValue),
                                           ctypes.byref(value))
        return ret

    def ZAux_Direct_GetCreep(self, iaxis):
        '''
        Description: .

        param iaxis: . type:int

        Return: , . type: int32,float

        '''
        value = ctypes.c_float()
        ret = zauxdll.ZAux_Direct_GetCreep(
            self.handle, ctypes.c_int(iaxis), ctypes.byref(value))
        return ret, value

    def ZAux_Direct_SetDatumIn(self, iaxis, iValue):
        '''
        Description: -1 .

        param iaxis: . type:int

        param iValue: . type:int

        Return: . type: int32

        '''

        ret = zauxdll.ZAux_Direct_SetDatumIn(
            self.handle, ctypes.c_int(iaxis), ctypes.c_int(iValue))
        return ret

    def ZAux_Direct_GetDatumIn(self, iaxis):
        '''
        Description: .

        param iaxis: . type:int

        Return: , . type: int32,int

        '''
        value = ctypes.c_int()
        ret = zauxdll.ZAux_Direct_GetDatumIn(
            self.handle, ctypes.c_int(iaxis), ctypes.byref(value))
        return ret, value

    def ZAux_Direct_SetDecel(self, iaxis, fValue):
        '''
        Description: .

        param iaxis: . type:int

        param fValue: . type:float

        Return: . type: int32

        '''

        ret = zauxdll.ZAux_Direct_SetDecel(
            self.handle, ctypes.c_int(iaxis), ctypes.c_float(fValue))
        return ret

    def ZAux_Direct_GetDecel(self, iaxis):
        '''
        Description

        param iaxis: . type:int

        Return: , . type: int32,float

        '''
        value = ctypes.c_float()
        ret = zauxdll.ZAux_Direct_GetDecel(
            self.handle, ctypes.c_int(iaxis), ctypes.byref(value))
        return ret, value

    def ZAux_Direct_SetDecelAngle(self, iaxis, fValue):
        '''
        Description: , , .

        param iaxis: . type:int

        param fValue: . type:float

        Return: . type: int32

        '''

        ret = zauxdll.ZAux_Direct_SetDecelAngle(
            self.handle, ctypes.c_int(iaxis), ctypes.c_float(fValue))
        return ret

    def ZAux_Direct_GetDecelAngle(self, iaxis):
        '''
        Description: , .

        param iaxis: . type:int

        Return: , . type: int32,float

        '''
        value = ctypes.c_float()
        ret = zauxdll.ZAux_Direct_GetDecelAngle(
            self.handle, ctypes.c_int(iaxis), ctypes.byref(value))
        return ret, value

    def ZAux_Direct_SetDpos(self, iaxis, fValue):
        '''
        Description: .

        param iaxis: . type:int

        param fValue: . type:float

        Return: . type: int32

        '''

        ret = zauxdll.ZAux_Direct_SetDpos(
            self.handle, ctypes.c_int(iaxis), ctypes.c_float(fValue))
        return ret

    def ZAux_Direct_GetDpos(self, iaxis):
        '''
        Description: .

        param iaxis: . type:int

        Return: , . type: int32,float

        '''
        value = ctypes.c_float()
        ret = zauxdll.ZAux_Direct_GetDpos(
            self.handle, ctypes.c_int(iaxis), ctypes.byref(value))
        return ret, value

    def ZAux_Direct_GetEncoder(self, iaxis):
        '''
        Description: ( ).

        param iaxis: . type:int

        Return: , . type: int32,float

        '''
        value = ctypes.c_float()
        ret = zauxdll.ZAux_Direct_GetEncoder(
            self.handle, ctypes.c_int(iaxis), ctypes.byref(value))
        return ret, value

    def ZAux_Direct_GetEndMove(self, iaxis):
        '''
        Description: .

        param iaxis: . type:int

        Return: , . type: int32,float

        '''
        value = ctypes.c_float()
        ret = zauxdll.ZAux_Direct_GetEndMove(
            self.handle, ctypes.c_int(iaxis), ctypes.byref(value))
        return ret, value

    def ZAux_Direct_GetEndMoveBuffer(self, iaxis):
        '''
        Description: , .

        param iaxis: . type:int

        Return: , . type: int32,float

        '''
        value = ctypes.c_float()
        ret = zauxdll.ZAux_Direct_GetEndMoveBuffer(
            self.handle, ctypes.c_int(iaxis), ctypes.byref(value))
        return ret, value

    def ZAux_Direct_SetEndMoveSpeed(self, iaxis, fValue):
        '''
        Description: SP .

        param iaxis: . type:int

        param fValue: . type:float

        Return: . type: int32

        '''

        ret = zauxdll.ZAux_Direct_SetEndMoveSpeed(
            self.handle, ctypes.c_int(iaxis), ctypes.c_float(fValue))
        return ret

    def ZAux_Direct_GetEndMoveSpeed(self, iaxis):
        '''
        Description: SP .

        param iaxis: . type:int

        Return: , . type: int32,float

        '''
        value = ctypes.c_float()
        ret = zauxdll.ZAux_Direct_GetEndMoveSpeed(
            self.handle, ctypes.c_int(iaxis), ctypes.byref(value))
        return ret, value

    def ZAux_Direct_SetErrormask(self, iaxis, iValue):
        '''
        Description: , AXISSTATUS WDOG.

        param iaxis: . type:int

        param iValue: . type:int

        Return: . type: int32

        '''

        ret = zauxdll.ZAux_Direct_SetErrormask(
            self.handle, ctypes.c_int(iaxis), ctypes.c_int(iValue))
        return ret

    def ZAux_Direct_GetErrormask(self, iaxis):
        '''
        Description: , AXISSTATUS WDOG.

        param iaxis: . type:int

        Return: , . type: int32,int

        '''
        value = ctypes.c_int()
        ret = zauxdll.ZAux_Direct_GetErrormask(
            self.handle, ctypes.c_int(iaxis), ctypes.byref(value))
        return ret, value

    def ZAux_Direct_SetFastJog(self, iaxis, iValue):
        '''
        Description: JOG .

        param iaxis: . type:int

        param iValue: JOG . type:int

        Return: . type: int32

        '''

        ret = zauxdll.ZAux_Direct_SetFastJog(
            self.handle, ctypes.c_int(iaxis), ctypes.c_int(iValue))
        return ret

    def ZAux_Direct_GetFastJog(self, iaxis):
        '''
        Description: JOG .

        param iaxis: . type:int

        Return: , JOG . type: int32,int

        '''
        value = ctypes.c_int()
        ret = zauxdll.ZAux_Direct_GetFastJog(
            self.handle, ctypes.c_int(iaxis), ctypes.byref(value))
        return ret, value

    def ZAux_Direct_SetFastDec(self, iaxis, fValue):
        '''
        Description: .

        param iaxis: . type:int

        param fValue: . type:float

        Return: . type: int32

        '''

        ret = zauxdll.ZAux_Direct_SetFastDec(
            self.handle, ctypes.c_int(iaxis), ctypes.c_float(fValue))
        return ret

    def ZAux_Direct_GetFastDec(self, iaxis):
        '''
        Description: .

        param iaxis: . type:int

        Return: , . type: int32,float

        '''
        value = ctypes.c_float()
        ret = zauxdll.ZAux_Direct_GetFastDec(
            self.handle, ctypes.c_int(iaxis), ctypes.byref(value))
        return ret, value

    def ZAux_Direct_GetFe(self, iaxis):
        '''
        Description: .

        param iaxis: . type:int

        Return: , . type: int32,float

        '''
        value = ctypes.c_float()
        ret = zauxdll.ZAux_Direct_GetFe(
            self.handle, ctypes.c_int(iaxis), ctypes.byref(value))
        return ret, value

    def ZAux_Direct_SetFeLimit(self, iaxis, fValue):
        '''
        Description: .

        param iaxis: . type:int

        param fValue: . type:float

        Return: . type: int32

        '''

        ret = zauxdll.ZAux_Direct_SetFeLimit(
            self.handle, ctypes.c_int(iaxis), ctypes.c_float(fValue))
        return ret

    def ZAux_Direct_GetFeLimit(self, iaxis):
        '''
        Description: .

        param iaxis: . type:int

        Return: , . type: int32,float

        '''
        value = ctypes.c_float()
        ret = zauxdll.ZAux_Direct_GetFeLimit(
            self.handle, ctypes.c_int(iaxis), ctypes.byref(value))
        return ret, value

    def ZAux_Direct_SetFRange(self, iaxis, fValue):
        '''
        Description: .

        param iaxis: . type:int

        param fValue: . type:float

        Return: . type: int32

        '''

        ret = zauxdll.ZAux_Direct_SetFRange(
            self.handle, ctypes.c_int(iaxis), ctypes.c_float(fValue))
        return ret

    def ZAux_Direct_GetFeRange(self, iaxis):
        '''
        Description: .

        param iaxis: . type:int

        Return: , . type: int32,float

        '''
        value = ctypes.c_float()
        ret = zauxdll.ZAux_Direct_GetFeRange(
            self.handle, ctypes.c_int(iaxis), ctypes.byref(value))
        return ret, value

    def ZAux_Direct_SetFholdIn(self, iaxis, iValue):
        '''
        Description: .

        param iaxis: . type:int

        param fValue: . type:int

        Return: . type: int32

        '''

        ret = zauxdll.ZAux_Direct_SetFholdIn(
            self.handle, ctypes.c_int(iaxis), ctypes.c_int(iValue))
        return ret

    def ZAux_Direct_GetFholdIn(self, iaxis):
        '''
        Description: .

        param iaxis: . type:int

        Return: , HOLDIN . type: int32,int

        '''
        value = ctypes.c_int()
        ret = zauxdll.ZAux_Direct_GetFholdIn(
            self.handle, ctypes.c_int(iaxis), ctypes.byref(value))
        return ret, value

    def ZAux_Direct_SetFhspeed(self, iaxis, pfValue):
        '''
        Description: .

        param iaxis: . type:int

        param fValue: . type:float

        Return: . type: int32

        '''

        ret = zauxdll.ZAux_Direct_SetFhspeed(
            self.handle, ctypes.c_int(iaxis), ctypes.c_float(pfValue))
        return ret

    def ZAux_Direct_GetFhspeed(self, iaxis):
        '''
        Description: .

        param iaxis: . type:int

        Return: , . type: int32,int

        '''
        value = ctypes.c_float()
        ret = zauxdll.ZAux_Direct_GetFhspeed(
            self.handle, ctypes.c_int(iaxis), ctypes.byref(value))
        return ret, value

    def ZAux_Direct_SetForceSpeed(self, iaxis, fValue):
        '''
        Description: SP .

        param iaxis: . type:int

        param fValue: . type:float

        Return: . type: int32

        '''

        ret = zauxdll.ZAux_Direct_SetForceSpeed(
            self.handle, ctypes.c_int(iaxis), ctypes.c_float(fValue))
        return ret

    def ZAux_Direct_GetForceSpeed(self, iaxis):
        '''
        Description: SP .

        param iaxis: . type:int

        Return: , SP . type: int32,int

        '''
        value = ctypes.c_float()
        ret = zauxdll.ZAux_Direct_GetForceSpeed(
            self.handle, ctypes.c_int(iaxis), ctypes.byref(value))
        return ret, value

    def ZAux_Direct_SetFsLimit(self, iaxis, fValue):
        '''
        Description: , .

        param iaxis: . type:int

        param fValue: . type:float

        Return: . type: int32

        '''

        ret = zauxdll.ZAux_Direct_SetFsLimit(
            self.handle, ctypes.c_int(iaxis), ctypes.c_float(fValue))
        return ret

    def ZAux_Direct_GetFsLimit(self, iaxis):
        '''
        Description: .

        param iaxis: . type:int

        Return: , . type: int32,float

        '''
        value = ctypes.c_float()
        ret = zauxdll.ZAux_Direct_GetFsLimit(
            self.handle, ctypes.c_int(iaxis), ctypes.byref(value))
        return ret, value

    def ZAux_Direct_SetFullSpRadius(self, iaxis, fValue):
        '''
        Description: .

        param iaxis: . type:int

        param fValue: . type:float

        Return: . type: int32

        '''

        ret = zauxdll.ZAux_Direct_SetFullSpRadius(
            self.handle, ctypes.c_int(iaxis), ctypes.c_float(fValue))
        return ret

    def ZAux_Direct_GetFullSpRadius(self, iaxis):
        '''
        Description: .

        param iaxis: . type:int

        Return: , . type: int32,float

        '''
        value = ctypes.c_float()
        ret = zauxdll.ZAux_Direct_GetFullSpRadius(
            self.handle, ctypes.c_int(iaxis), ctypes.byref(value))
        return ret, value

    def ZAux_Direct_SetFwdIn(self, iaxis, iValue):
        '''
        Description: -1 .

        param iaxis: . type:int

        param iValue: . type:int

        Return: . type: int32

        '''

        ret = zauxdll.ZAux_Direct_SetFwdIn(
            self.handle, ctypes.c_int(iaxis), ctypes.c_int(iValue))
        return ret

    def ZAux_Direct_GetFwdIn(self, iaxis):
        '''
        Description: .

        param iaxis: . type:int

        Return: , . type: int32,float

        '''
        value = ctypes.c_int()
        ret = zauxdll.ZAux_Direct_GetFwdIn(
            self.handle, ctypes.c_int(iaxis), ctypes.byref(value))
        return ret, value

    def ZAux_Direct_SetFwdJog(self, iaxis, iValue):
        '''
        Description: JOG .

        param iaxis: . type:int

        param iValue: JOG . type:int

        Return: . type: int32

        '''
        ret = zauxdll.ZAux_Direct_SetFwdJog(
            self.handle, ctypes.c_int(iaxis), ctypes.c_int(iValue))
        return ret

    def ZAux_Direct_GetFwdJog(self, iaxis):
        '''
        Description: JOG .

        param iaxis: . type:int

        Return: , JOG . type: int32,int

        '''
        value = ctypes.c_int()
        ret = zauxdll.ZAux_Direct_GetFwdJog(
            self.handle, ctypes.c_int(iaxis), ctypes.byref(value))
        return ret, value

    def ZAux_Direct_GetIfIdle(self, iaxis):
        '''
        Description: .

        param iaxis: . type:int

        Return: , 0- -1 . type: int32,int

        '''
        value = ctypes.c_int()
        ret = zauxdll.ZAux_Direct_GetIfIdle(
            self.handle, ctypes.c_int(iaxis), ctypes.byref(value))
        return ret, value

    def ZAux_Direct_SetInvertStep(self, iaxis, iValue):
        '''
        Description: .

        param iaxis: . type:int

        param iValue: + \\ . type:int

        Return: . type: int32
        '''

        ret = zauxdll.ZAux_Direct_SetInvertStep(
            self.handle, ctypes.c_int(iaxis), ctypes.c_int(iValue))
        return ret

    def ZAux_Direct_GetInvertStep(self, iaxis):
        '''
        Description: .

        param iaxis: . type:int

        Return: , . type: int32,int

        '''
        value = ctypes.c_int()
        ret = zauxdll.ZAux_Direct_GetInvertStep(
            self.handle, ctypes.c_int(iaxis), ctypes.byref(value))
        return ret, value

    def ZAux_Direct_SetInterpFactor(self, iaxis, iValue):
        '''
        Description: , (1). .

        param iaxis: . type:int

        param iValue: 0- 1- . type:int

        Return: . type: int32
        '''

        ret = zauxdll.ZAux_Direct_SetInterpFactor(
            self.handle, ctypes.c_int(iaxis), ctypes.c_int(iValue))
        return ret

    def ZAux_Direct_GetInterpFactor(self, iaxis):
        '''
        Description: , (1). .

        param iaxis: . type:int

        Return: , . type: int32,int

        '''
        value = ctypes.c_int()
        ret = zauxdll.ZAux_Direct_GetInterpFactor(
            self.handle, ctypes.c_int(iaxis), ctypes.byref(value))
        return ret, value

    def ZAux_Direct_SetJogSpeed(self, iaxis, fValue):
        '''
        Description: JOG .

        param iaxis: . type:int

        param fValue: . type:float

        Return: . type: int32
        '''

        ret = zauxdll.ZAux_Direct_SetJogSpeed(
            self.handle, ctypes.c_int(iaxis), ctypes.c_float(fValue))
        return ret

    def ZAux_Direct_GetJogSpeed(self, iaxis):
        '''
        Description: , (1). .

        param iaxis: . type:int

        Return: , . type: int32,int

        '''
        value = ctypes.c_float()
        ret = zauxdll.ZAux_Direct_GetJogSpeed(
            self.handle, ctypes.c_int(iaxis), ctypes.byref(value))
        return ret, value

    def ZAux_Direct_GetLoaded(self, iaxis):
        '''
        Description: .

        param iaxis: . type:int

        Return: , -1 0- . type: int32,int

        '''
        value = ctypes.c_int()
        ret = zauxdll.ZAux_Direct_GetLoaded(
            self.handle, ctypes.c_int(iaxis), ctypes.byref(value))
        return ret, value

    def ZAux_Direct_GetLinkax(self, iaxis):
        '''
        Description: .

        param iaxis: . type:int

        Return: , . type: int32,int

        '''
        value = ctypes.c_int()
        ret = zauxdll.ZAux_Direct_GetLinkax(
            self.handle, ctypes.c_int(iaxis), ctypes.byref(value))
        return ret, value

    def ZAux_Direct_SetLspeed(self, iaxis, fValue):
        '''
        Description: .

        param iaxis: . type:int

        param fValue: . type:float

        Return: . type: int32
        '''

        ret = zauxdll.ZAux_Direct_SetLspeed(
            self.handle, ctypes.c_int(iaxis), ctypes.c_float(fValue))
        return ret

    def ZAux_Direct_GetLspeed(self, iaxis):
        '''
        Description: .

        param iaxis: . type:int

        Return: , . type: int32,float

        '''
        value = ctypes.c_float()
        ret = zauxdll.ZAux_Direct_GetLspeed(
            self.handle, ctypes.c_int(iaxis), ctypes.byref(value))
        return ret, value

    def ZAux_Direct_SetHomeWait(self, iaxis, fValue):
        '''
        Description: .

        param iaxis: . type:int

        param fValue: MS. type:int

        Return: . type: int32

        '''

        ret = zauxdll.ZAux_Direct_SetHomeWait(
            self.handle, ctypes.c_int(iaxis), ctypes.c_int(fValue))
        return ret

    def ZAux_Direct_GetHomeWait(self, iaxis):
        '''
        Description: .

        param iaxis: . type:int

        Return: , . type: int32,int

        '''
        value = ctypes.c_int()
        ret = zauxdll.ZAux_Direct_GetHomeWait(
            self.handle, ctypes.c_int(iaxis), ctypes.byref(value))
        return ret, value

    def ZAux_Direct_GetMark(self, iaxis):
        '''
        Description: .

        param iaxis: . type:int

        Return: , -1- 0- . type: int32,int

        '''
        value = ctypes.c_int()
        ret = zauxdll.ZAux_Direct_GetMark(
            self.handle, ctypes.c_int(iaxis), ctypes.byref(value))
        return ret, value

    def ZAux_Direct_GetMarkB(self, iaxis):
        '''
        Description: b .

        param iaxis: . type:int

        Return: , -1- 0- . type: int32,int

        '''
        value = ctypes.c_int()
        ret = zauxdll.ZAux_Direct_GetMarkB(
            self.handle, ctypes.c_int(iaxis), ctypes.byref(value))
        return ret, value

    def ZAux_Direct_SetMaxSpeed(self, iaxis, iValue):
        '''
        Description: .

        param iaxis: . type:int

        param iValue: type:int

        Return: . type: int32,int

        '''

        ret = zauxdll.ZAux_Direct_SetMaxSpeed(
            self.handle, ctypes.c_int(iaxis), ctypes.c_int(iValue))
        return ret

    def ZAux_Direct_GetMaxSpeed(self, iaxis):
        '''
        Description: .

        param iaxis: . type:int

        Return: , . type:int32,int

        '''
        value = ctypes.c_int()
        ret = zauxdll.ZAux_Direct_GetMaxSpeed(
            self.handle, ctypes.c_int(iaxis), ctypes.byref(value))
        return ret, value

    def ZAux_Direct_SetMerge(self, iaxis, iValue):
        '''
        Description: .

        param iaxis: . type:int

        param iValue: 0- 1- . type:int

        Return: , . type: int32,int

        '''
        ret = zauxdll.ZAux_Direct_SetMerge(
            self.handle, ctypes.c_int(iaxis), ctypes.c_int(iValue))
        return ret

    def ZAux_Direct_GetMerge(self, iaxis):
        '''
        Description: .

        param iaxis: . type:int

        Return: , . type: int32,int

        '''
        value = ctypes.c_int()
        ret = zauxdll.ZAux_Direct_GetMerge(
            self.handle, ctypes.c_int(iaxis), ctypes.byref(value))
        return ret, value

    def ZAux_Direct_GetMovesBuffered(self, iaxis):
        '''
        Description: .

        param iaxis: . type:int

        Return: , . type: int32,int

        '''
        value = ctypes.c_int()
        ret = zauxdll.ZAux_Direct_GetMovesBuffered(
            self.handle, ctypes.c_int(iaxis), ctypes.byref(value))
        return ret, value

    def ZAux_Direct_GetMoveCurmark(self, iaxis):
        '''
        Description: MOVE_MARK .

        param iaxis: . type:int

        Return: , MARK . type: int32,int

        '''
        value = ctypes.c_int()
        ret = zauxdll.ZAux_Direct_GetMoveCurmark(
            self.handle, ctypes.c_int(iaxis), ctypes.byref(value))
        return ret, value

    def ZAux_Direct_SetMovemark(self, iaxis, iValue):
        '''
        Description: MOVE_MARK MARK +1.

        param iaxis: . type:int

        param iValue: MARK . type:int

        Return: . type: int32

        '''

        ret = zauxdll.ZAux_Direct_SetMovemark(
            self.handle, ctypes.c_int(iaxis), ctypes.c_int(iValue))
        return ret

    def ZAux_Direct_SetMpos(self, iaxis, fValue):
        '''
        Description: .

        param iaxis: . type:int

        param fValue: . type:float

        Return: . type: int32

        '''
        ret = zauxdll.ZAux_Direct_SetMpos(
            self.handle, ctypes.c_int(iaxis), ctypes.c_float(fValue))
        return ret

    def ZAux_Direct_GetMpos(self, iaxis):
        '''
        Description: .

        param iaxis: . type:int

        Return: , . type: int32,float

        '''
        value = ctypes.c_float()
        ret = zauxdll.ZAux_Direct_GetMpos(
            self.handle, ctypes.c_int(iaxis), ctypes.byref(value))
        return ret, value

    def ZAux_Direct_GetMspeed(self, iaxis):
        '''
        Description: .

        param iaxis: . type:int

        Return: , . type: int32,float

        '''
        value = ctypes.c_float()
        ret = zauxdll.ZAux_Direct_GetMspeed(
            self.handle, ctypes.c_int(iaxis), ctypes.byref(value))
        return ret, value

    def ZAux_Direct_GetMtype(self, iaxis):
        '''
        Description: .

        param iaxis: . type:int

        Return: , . type: int32,int

        '''
        value = ctypes.c_int()
        ret = zauxdll.ZAux_Direct_GetMtype(
            self.handle, ctypes.c_int(iaxis), ctypes.byref(value))
        return ret, value

    def ZAux_Direct_SetOffpos(self, iaxis, fValue):
        '''
        Description: .

        param iaxis: . type:int

        param fValue: . type:float

        Return: . type: int32

        '''

        ret = zauxdll.ZAux_Direct_SetOffpos(
            self.handle, ctypes.c_int(iaxis), ctypes.c_float(fValue))
        return ret

    def ZAux_Direct_GetOffpos(self, iaxis):
        '''
        Description: .
        param iaxis: . type:int

        Return: , type: int32,float

        '''
        value = ctypes.c_float()
        ret = zauxdll.ZAux_Direct_GetOffpos(
            self.handle, ctypes.c_int(iaxis), ctypes.byref(value))
        return ret, value

    def ZAux_Direct_SetOpenWin(self, iaxis, fValue):
        '''
        Description: .

        param iaxis: . type:int

        param fValue: . type:float

        Return: . type: int32

        '''

        ret = zauxdll.ZAux_Direct_SetOpenWin(
            self.handle, ctypes.c_int(iaxis), ctypes.c_float(fValue))
        return ret

    def ZAux_Direct_GetOpenWin(self, iaxis):
        '''
        Description: .

        param iaxis: . type:int

        Return: , . type: int32,float

        '''
        value = ctypes.c_float()
        ret = zauxdll.ZAux_Direct_GetOpenWin(
            self.handle, ctypes.c_int(iaxis), ctypes.byref(value))
        return ret, value

    def ZAux_Direct_GetRegPos(self, iaxis):
        '''
        Description: (MPOS).

        param iaxis: . type:int

        Return: , . type: int32,float

        '''
        value = ctypes.c_float()
        ret = zauxdll.ZAux_Direct_GetRegPos(
            self.handle, ctypes.c_int(iaxis), ctypes.byref(value))
        return ret, value

    def ZAux_Direct_GetRegPosB(self, iaxis):
        '''
        Description: (MPOS).

        param iaxis: . type:int

        Return: , . type: int32,float

        '''
        value = ctypes.c_float()
        ret = zauxdll.ZAux_Direct_GetRegPosB(
            self.handle, ctypes.c_int(iaxis), ctypes.byref(value))
        return ret, value

    def ZAux_Direct_GetRemain(self, iaxis):
        '''
        Description: .

        param iaxis: . type:int

        Return: , . type: int32,float

        '''
        value = ctypes.c_float()
        ret = zauxdll.ZAux_Direct_GetRemain(
            self.handle, ctypes.c_int(iaxis), ctypes.byref(value))
        return ret, value

    def ZAux_Direct_GetRemain_LineBuffer(self, iaxis):
        '''
        Description: , .

        param iaxis: . type:int

        Return: , . type: int32,int

        '''
        value = ctypes.c_int()
        ret = zauxdll.ZAux_Direct_GetRemain_LineBuffer(
            self.handle, ctypes.c_int(iaxis), ctypes.byref(value))
        return ret, value

    def ZAux_Direct_GetRemain_Buffer(self, iaxis):
        '''
        Description: , .

        param iaxis: . type:int

        Return: , . type: int32,int

        '''
        value = ctypes.c_int()
        ret = zauxdll.ZAux_Direct_GetRemain_Buffer(
            self.handle, ctypes.c_int(iaxis), ctypes.byref(value))
        return ret, value

    def ZAux_Direct_SetRepDist(self, iaxis, fValue):
        '''
        Description: .

        param iaxis: . type:int

        param fValue: . type:float

        Return: . type: int32

        '''

        ret = zauxdll.ZAux_Direct_SetRepDist(
            self.handle, ctypes.c_int(iaxis), ctypes.c_float(fValue))
        return ret

    def ZAux_Direct_GetRepDist(self, iaxis):
        '''
        Description: REP_OPTION DPOS MPOS .

        param iaxis: . type:int

        Return: , . type: int32,float

        '''
        value = ctypes.c_float()
        ret = zauxdll.ZAux_Direct_GetRepDist(
            self.handle, ctypes.c_int(iaxis), ctypes.byref(value))
        return ret, value

    def ZAux_Direct_SetRepOption(self, iaxis, iValue):
        '''
        Description: .

        param iaxis: . type:int

        param iValue: . type:int

        Return: . type: int32

        '''
        ret = zauxdll.ZAux_Direct_SetRepOption(
            self.handle, ctypes.c_int(iaxis), ctypes.c_int(iValue))
        return ret

    def ZAux_Direct_GetRepOption(self, iaxis):
        '''
        Description: .

        param iaxis: . type:int

        Return: , . type: int32,int

        '''
        value = ctypes.c_int()
        ret = zauxdll.ZAux_Direct_GetRepOption(
            self.handle, ctypes.c_int(iaxis), ctypes.byref(value))
        return ret, value

    def ZAux_Direct_SetRevIn(self, iaxis, iValue):
        '''
        Description: ,-1 .

        param iaxis: . type:int

        param iValue: . type:int

        Return: . type: int32

        '''
        ret = zauxdll.ZAux_Direct_SetRevIn(
            self.handle, ctypes.c_int(iaxis), ctypes.c_int(iValue))
        return ret

    def ZAux_Direct_GetRevIn(self, iaxis):
        '''
        Description: ,-1 .

        param iaxis: . type:int

        Return: , . type: int32,int

        '''
        value = ctypes.c_int()
        ret = zauxdll.ZAux_Direct_GetRevIn(
            self.handle, ctypes.c_int(iaxis), ctypes.byref(value))
        return ret, value

    def ZAux_Direct_SetRevJog(self, iaxis, iValue):
        '''
        Description: JOG ,-1 .

        param iaxis: . type:int

        param iValue: . type:int

        Return: . type: int32

        '''

        ret = zauxdll.ZAux_Direct_SetRevJog(
            self.handle, ctypes.c_int(iaxis), ctypes.c_int(iValue))
        return ret

    def ZAux_Direct_GetRevJog(self, iaxis):
        '''
        Description: JOG ,-1 .

        param iaxis: . type:int

        Return: , . type: int32,int

        '''
        value = ctypes.c_int()
        ret = zauxdll.ZAux_Direct_GetRevJog(
            self.handle, ctypes.c_int(iaxis), ctypes.byref(value))
        return ret, value

    def ZAux_Direct_SetRsLimit(self, iaxis, fValue):
        '''
        Description: . .

        param iaxis: . type:int

        param fValue: . type:float

        Return: . type: int32

        '''
        ret = zauxdll.ZAux_Direct_SetRsLimit(
            self.handle, ctypes.c_int(iaxis), ctypes.c_float(fValue))
        return ret

    def ZAux_Direct_GetRsLimit(self, iaxis):
        '''
        Description: .

        param iaxis: . type:int

        Return: , . type: int32,float

        '''
        value = ctypes.c_float()
        ret = zauxdll.ZAux_Direct_GetRsLimit(
            self.handle, ctypes.c_int(iaxis), ctypes.byref(value))
        return ret, value

    def ZAux_Direct_SetSpeed(self, iaxis, fValue):
        '''
        Description: , units\\s, , .

        param iaxis: . type:int

        param fValue: . type:float

        Return: . type: int32

        '''

        ret = zauxdll.ZAux_Direct_SetSpeed(
            self.handle, ctypes.c_int(iaxis), ctypes.c_float(fValue))
        return ret

    def ZAux_Direct_GetSpeed(self, iaxis):
        '''
        Description: , units\\s, , .

        param iaxis: . type:int

        Return: , . type: int32,float

        '''
        value = ctypes.c_float()
        ret = zauxdll.ZAux_Direct_GetSpeed(
            self.handle, ctypes.c_int(iaxis), ctypes.byref(value))
        return ret, value

    def ZAux_Direct_SetSramp(self, iaxis, fValue):
        '''
        Description: S . 0- .

        param iaxis: . type:int

        param fValue:S MS. type:float

        Return: . type: int32

        '''
        ret = zauxdll.ZAux_Direct_SetSramp(
            self.handle, ctypes.c_int(iaxis), ctypes.c_float(fValue))
        return ret

    def ZAux_Direct_GetSramp(self, iaxis):
        '''
        Description: S .

        param iaxis: . type:int

        Return: , . type: int32,float

        '''
        value = ctypes.c_float()
        ret = zauxdll.ZAux_Direct_GetSramp(
            self.handle, ctypes.c_int(iaxis), ctypes.byref(value))
        return ret, value

    def ZAux_Direct_SetStartMoveSpeed(self, iaxis, fValue):
        '''
        Description: SP .

        param iaxis: . type:int

        param fValue: . type:float

        Return: . type: int32

        '''

        ret = zauxdll.ZAux_Direct_SetStartMoveSpeed(
            self.handle, ctypes.c_int(iaxis), ctypes.c_float(fValue))
        return ret

    def ZAux_Direct_GetStartMoveSpeed(self, iaxis):
        '''
        Description: SP .

        param iaxis: . type:int

        Return: , SP . type: int32,float

        '''
        value = ctypes.c_float()
        ret = zauxdll.ZAux_Direct_GetStartMoveSpeed(
            self.handle, ctypes.c_int(iaxis), ctypes.byref(value))
        return ret, value

    def ZAux_Direct_SetStopAngle(self, iaxis, fValue):
        '''
        Description: .

        param iaxis: . type:int

        param fValue: . type:float

        Return: . type: int32

        '''

        ret = zauxdll.ZAux_Direct_SetStopAngle(
            self.handle, ctypes.c_int(iaxis), ctypes.c_float(fValue))
        return ret

    def ZAux_Direct_GetStopAngle(self, iaxis):
        '''
        Description: .

        param iaxis: . type:int

        Return: , . type: int32,float

        '''
        value = ctypes.c_float()
        ret = zauxdll.ZAux_Direct_GetStopAngle(
            self.handle, ctypes.c_int(iaxis), ctypes.byref(value))
        return ret, value

    def ZAux_Direct_SetZsmooth(self, iaxis, fValue):
        '''
        Description: .

        param iaxis: . type:int

        param fValue: . type:float

        Return: . type: int32

        '''

        ret = zauxdll.ZAux_Direct_SetZsmooth(
            self.handle, ctypes.c_int(iaxis), ctypes.c_float(fValue))
        return ret

    def ZAux_Direct_GetZsmooth(self, iaxis):
        '''
        Description: .

        param iaxis: . type:int

        Return: , . type: int32,float

        '''
        value = ctypes.c_float()
        ret = zauxdll.ZAux_Direct_GetZsmooth(
            self.handle, ctypes.c_int(iaxis), ctypes.byref(value))
        return ret, value

    def ZAux_Direct_SetUnits(self, iaxis, fValue):
        '''
        Description: .

        param iaxis: . type:int

        param fValue: . type:float

        Return: . type: int32

        '''

        ret = zauxdll.ZAux_Direct_SetUnits(
            self.handle, ctypes.c_int(iaxis), ctypes.c_float(fValue))
        return ret

    def ZAux_Direct_GetUnits(self, iaxis):
        '''
        Description: .

        param iaxis: . type:int

        Return: , . type: int32,float

        '''
        value = ctypes.c_float()
        ret = zauxdll.ZAux_Direct_GetUnits(
            self.handle, ctypes.c_int(iaxis), ctypes.byref(value))
        return ret, value

    def ZAux_Direct_GetVectorBuffered(self, iaxis):
        '''
        Description: .

        param iaxis: . type:int

        Return: , . type: int32,float

        '''
        value = ctypes.c_float()
        ret = zauxdll.ZAux_Direct_GetVectorBuffered(
            self.handle, ctypes.c_int(iaxis), ctypes.byref(value))
        return ret, value

    def ZAux_Direct_GetVpSpeed(self, iaxis):
        '''
        Description: .

        param iaxis: . type:int

        Return: , . type: int32,float

        '''
        value = ctypes.c_float()
        ret = zauxdll.ZAux_Direct_GetVpSpeed(
            self.handle, ctypes.c_int(iaxis), ctypes.byref(value))
        return ret, value

    def ZAux_Direct_GetVariablef(self, pname):
        '''
        Description: , .

        param iaxis: . type:int

        param pname: \\ DPOS(0). type:string

        Return: , . type: int32,float

        '''
        _str = pname.encode('utf-8')
        value = (ctypes.c_float)()
        ret = zauxdll.ZAux_Direct_GetVariablef(
            self.handle, _str, ctypes.byref(value))
        return ret, value

    def ZAux_Direct_GetVariableInt(self, pname):
        '''
        Description: , .

        param iaxis: . type:int

        param pname: \\ DPOS(0). type:string

        Return: , . type: int32,int

        '''
        _str = pname.encode('utf-8')
        value = ctypes.c_int()
        ret = zauxdll.ZAux_Direct_GetVariableInt(
            self.handle, _str, ctypes.byref(value))
        return ret, value

    # ############# , , 20130901 ###############

    def ZAux_Direct_Base(self, imaxaxises, piAxislist):
        '''
        Description:BASE
         BASE , BASE .
         MOVE BASE .

        param imaxaxises: . type:int

        param piAxislist: . type:int

        Return: . type: int32

        '''
        Axislistarray = (ctypes.c_int * len(piAxislist))(*piAxislist)
        ret = zauxdll.ZAux_Direct_Base(
            self.handle, ctypes.c_int(imaxaxises), Axislistarray)
        return ret

    def ZAux_Direct_Defpos(self, iaxis, pfDpos):
        '''
        Description: DPOS, , SETDPOS .

        param iaxis: . type:int

        param pfDpos: . type:float

        Return: . type: int32

        '''

        ret = zauxdll.ZAux_Direct_Defpos(
            self.handle, ctypes.c_int(iaxis), ctypes.c_float(pfDpos))
        return ret

    def ZAux_Direct_Move(self, imaxaxises, piAxislist, pfDisancelist):
        '''
        Description: 20130901 .

        param imaxaxises: . type:int

        param piAxislist: . type:int

        param pfDisancelist: . type:float

        Return: . type: int32

        '''
        Axislistarray = (ctypes.c_int * len(piAxislist))(*piAxislist)
        pfDisancelisttarray = (
            ctypes.c_int * len(pfDisancelist))(*pfDisancelist)
        ret = zauxdll.ZAux_Direct_Move(
            self.handle, imaxaxises, Axislistarray, pfDisancelisttarray)
        return ret

    def ZAux_Direct_MoveSp(self, imaxaxises, piAxislist, pfDisancelist):
        '''
        Description: SP 20130901 .

        param imaxaxises: . type:int

        param piAxislist: . type:int

        param pfDisancelist: . type:float

        Return: . type: int32

        '''
        Axislistarray = (ctypes.c_int * len(piAxislist))(*piAxislist)
        pfDisancelisttarray = (
            ctypes.c_int * len(pfDisancelist))(*pfDisancelist)
        ret = zauxdll.ZAux_Direct_Move(
            self.handle, imaxaxises, Axislistarray, pfDisancelisttarray)
        return ret

    def ZAux_Direct_MoveAbs(self, imaxaxises, piAxislist, pfDisancelist):
        '''
        Description: 20130901 .

        param imaxaxises: . type:int

        param piAxislist: . type:int

        param pfDisancelist: . type:float

        Return: . type: int32

        '''
        Axislistarray = (ctypes.c_int * len(piAxislist))(*piAxislist)
        pfDisancelisttarray = (
            ctypes.c_int * len(pfDisancelist))(*pfDisancelist)
        ret = zauxdll.ZAux_Direct_Move(
            self.handle, imaxaxises, Axislistarray, pfDisancelisttarray)
        return ret

    def ZAux_Direct_MoveAbsSp(self, imaxaxises, piAxislist, pfDisancelist):
        '''
        Description: SP 20130901 .

        param imaxaxises: . type:int

        param piAxislist: . type:int

        param pfDisancelist: . type:float

        Return: . type: int32

        '''
        Axislistarray = (ctypes.c_int * len(piAxislist))(*piAxislist)
        pfDisancelisttarray = (
            ctypes.c_int * len(pfDisancelist))(*pfDisancelist)
        ret = zauxdll.ZAux_Direct_Move(
            self.handle, imaxaxises, Axislistarray, pfDisancelisttarray)
        return ret

    def ZAux_Direct_MoveModify(self, iaxis, pfDisance):
        '''
        Description: 20130901 .

        param iaxis: . type:int

        param pfDisance: . type:float

        Return: . type: int32

        '''

        ret = zauxdll.ZAux_Direct_MoveModify(
            self.handle, ctypes.c_int(iaxis), ctypes.c_float(pfDisance))
        return ret

    def ZAux_Direct_MoveCirc(self, imaxaxises, piAxislist, fend1, fend2, fcenter1, fcenter2, idirection):
        '''
        Description: 20130901 .

        param imaxaxises: . type:int

        param piAxislist: . type:int

        param fend1: . type:float

        param fend2: . type:float

        param fcenter1: , . type:float

        param fcenter2: , . type:float

        param idirection:0- ,1- . type:int

        Return: . type: int32

        '''
        Axislistarray = (ctypes.c_int * len(piAxislist))(*piAxislist)
        ret = zauxdll.ZAux_Direct_MoveCirc(self.handle, ctypes.c_int(imaxaxises), Axislistarray, ctypes.c_float(fend1),
                                           ctypes.c_float(fend2), ctypes.c_float(
                                               fcenter1), ctypes.c_float(fcenter2),
                                           ctypes.c_int(idirection))
        return ret

    def ZAux_Direct_MoveCircSp(self, imaxaxises, piAxislist, fend1, fend2, fcenter1, fcenter2, idirection):
        '''
        Description: SP 20130901 .

        param imaxaxises: . type:int

        param piAxislist: . type:int

        param fend1: . type:float

        param fend2: . type:float

        param fcenter1: , . type:float

        param fcenter2: , . type:float

        param idirection:0- ,1- . type:int

        Return: . type: int32

        '''
        Axislistarray = (ctypes.c_int * len(piAxislist))(*piAxislist)
        ret = zauxdll.ZAux_Direct_MoveCircSp(self.handle, ctypes.c_int(imaxaxises), Axislistarray,
                                             ctypes.c_float(fend1), ctypes.c_float(
                                                 fend2), ctypes.c_float(fcenter1),
                                             ctypes.c_float(fcenter2), ctypes.c_int(idirection))
        return ret

    def ZAux_Direct_MoveCircAbs(self, imaxaxises, piAxislist, fend1, fend2, fcenter1, fcenter2, idirection):
        '''
        Description: 20130901 .

        param imaxaxises: . type:int

        param piAxislist: . type:int

        param fend1: . type:float

        param fend2: . type:float

        param fcenter1: , . type:float

        param fcenter2: , . type:float

        param idirection:0- ,1- . type:int

        Return: . type: int32

        '''
        Axislistarray = (ctypes.c_int * len(piAxislist))(*piAxislist)
        ret = zauxdll.ZAux_Direct_MoveCircAbs(self.handle, ctypes.c_int(imaxaxises), Axislistarray,
                                              ctypes.c_float(fend1), ctypes.c_float(
                                                  fend2), ctypes.c_float(fcenter1),
                                              ctypes.c_float(fcenter2), ctypes.c_int(idirection))
        return ret

    def ZAux_Direct_MoveCircAbsSp(self, imaxaxises, piAxislist, fend1, fend2, fcenter1, fcenter2, idirection):
        '''
        Description: 20130901 .

        param imaxaxises: . type:int

        param piAxislist: . type:int

        param fend1: . type:float

        param fend2: . type:float

        param fcenter1: , . type:float

        param fcenter2: , . type:float

        param idirection:0- ,1- . type:int

        Return: . type: int32

        '''
        Axislistarray = (ctypes.c_int * len(piAxislist))(*piAxislist)
        ret = zauxdll.ZAux_Direct_MoveCircAbsSp(self.handle, ctypes.c_int(imaxaxises), Axislistarray,
                                                ctypes.c_float(fend1), ctypes.c_float(
                                                    fend2), ctypes.c_float(fcenter1),
                                                ctypes.c_float(fcenter2), ctypes.c_int(idirection))
        return ret

    def ZAux_Direct_MoveCirc2(self, imaxaxises, piAxislist, fmid1, fmid2, fend1, fend2):
        '''
        Description: 3 20130901 .

        param imaxaxises: . type:int

        param piAxislist: . type:int

        param fmid1: , . type:float

        param fmid2: , . type:float

        param fend1: , . type:float

        param fend2: , . type:float

        Return: . type: int32

        '''
        Axislistarray = (ctypes.c_int * len(piAxislist))(*piAxislist)
        ret = zauxdll.ZAux_Direct_MoveCirc2(self.handle, ctypes.c_int(imaxaxises), Axislistarray, ctypes.c_float(fmid1),
                                            ctypes.c_float(fmid2), ctypes.c_float(fend1), ctypes.c_float(fend2))
        return ret

    def ZAux_Direct_MoveCirc2Abs(self, imaxaxises, piAxislist, fmid1, fmid2, fend1, fend2):
        '''
        Description: 3 20130901 .

        param imaxaxises: . type:int

        param piAxislist: . type:int

        param fmid1: , . type:float

        param fmid2: , . type:float

        param fend1: , . type:float

        param fend2: , . type:float

        Return: . type: int32

        '''
        Axislistarray = (ctypes.c_int * len(piAxislist))(*piAxislist)
        ret = zauxdll.ZAux_Direct_MoveCirc2Abs(self.handle, ctypes.c_int(imaxaxises), Axislistarray,
                                               ctypes.c_float(fmid1), ctypes.c_float(
                                                   fmid2), ctypes.c_float(fend1),
                                               ctypes.c_float(fend2))
        return ret

    def ZAux_Direct_MoveCirc2Sp(self, imaxaxises, piAxislist, fmid1, fmid2, fend1, fend2):
        '''
        Description: 3 SP 20130901 .

        param imaxaxises: . type:int

        param piAxislist: . type:int

        param fmid1: , . type:float

        param fmid2: , . type:float

        param fend1: , . type:float

        param fend2: , . type:float

        Return: . type: int32

        '''
        Axislistarray = (ctypes.c_int * len(piAxislist))(*piAxislist)
        ret = zauxdll.ZAux_Direct_MoveCirc2Sp(self.handle, ctypes.c_int(imaxaxises), Axislistarray,
                                              ctypes.c_float(fmid1), ctypes.c_float(
                                                  fmid2), ctypes.c_float(fend1),
                                              ctypes.c_float(fend2))
        return ret

    def ZAux_Direct_MoveCirc2AbsSp(self, imaxaxises, piAxislist, fmid1, fmid2, fend1, fend2):
        '''
        Description: 3 SP 20130901 .

        param imaxaxises: . type:int

        param piAxislist: . type:int

        param fmid1: , . type:float

        param fmid2: , . type:float

        param fend1: , . type:float

        param fend2: , . type:float

        Return: . type: int32

        '''
        Axislistarray = (ctypes.c_int * len(piAxislist))(*piAxislist)
        ret = zauxdll.ZAux_Direct_MoveCirc2AbsSp(self.handle, ctypes.c_int(imaxaxises), Axislistarray,
                                                 ctypes.c_float(fmid1), ctypes.c_float(
                                                     fmid2), ctypes.c_float(fend1),
                                                 ctypes.c_float(fend2))
        return ret

    def ZAux_Direct_MHelical(self, imaxaxises, piAxislist, fend1, fend2, fcenter1, fcenter2, idirection, fDistance3,
                             imode):
        '''
        Description: 3 20130901 .

        param imaxaxises: . type:int

        param piAxislist: . type:int

        param fend1: . type:float

        param fend2: . type:float

        param fcenter1: , . type:float

        param fcenter2: , . type:float

        param idirection: 0- ,1- . type:int

        param fDistance3: . type:float

        param imode: :0( ) .1 . type:int

        Return: . type: int32

        '''
        Axislistarray = (ctypes.c_int * len(piAxislist))(*piAxislist)
        ret = zauxdll.ZAux_Direct_MHelical(self.handle, ctypes.c_int(imaxaxises), Axislistarray, ctypes.c_float(fend1),
                                           ctypes.c_float(fend2), ctypes.c_float(
                                               fcenter1), ctypes.c_float(fcenter2),
                                           ctypes.c_float(idirection), ctypes.c_float(fDistance3), ctypes.c_int(imode))
        return ret

    def ZAux_Direct_MHelicalAbs(self, imaxaxises, piAxislist, fend1, fend2, fcenter1, fcenter2, idirection, fDistance3,
                                imode):
        '''
        Description: 3 20130901 .

        param imaxaxises: . type:int

        param piAxislist: . type:int

        param fend1: . type:float

        param fend2: . type:float

        param fcenter1: , . type:float

        param fcenter2: , . type:float

        param idirection: 0- ,1- . type:int

        param fDistance3: . type:float

        param imode: :0( ) .1 . type:int

        Return: . type: int32

        '''
        Axislistarray = (ctypes.c_int * len(piAxislist))(*piAxislist)
        ret = zauxdll.ZAux_Direct_MHelicalAbs(self.handle, ctypes.c_int(imaxaxises), Axislistarray,
                                              ctypes.c_float(fend1), ctypes.c_float(
                                                  fend2), ctypes.c_float(fcenter1),
                                              ctypes.c_float(fcenter2), ctypes.c_float(
                                                  idirection),
                                              ctypes.c_float(fDistance3), ctypes.c_int(imode))
        return ret

    def ZAux_Direct_MHelicalSp(self, imaxaxises, piAxislist, fend1, fend2, fcenter1, fcenter2, idirection, fDistance3,
                               imode):
        '''
        Description: 3 SP 20130901 .

        param imaxaxises: . type:int

        param piAxislist: . type:int

        param fend1: . type:float

        param fend2: . type:float

        param fcenter1: , . type:float

        param fcenter2: , . type:float

        param idirection: 0- ,1- . type:int

        param fDistance3: . type:float

        param imode: :0( ) .1 . type:int

        Return: . type: int32

        '''
        Axislistarray = (ctypes.c_int * len(piAxislist))(*piAxislist)
        ret = zauxdll.ZAux_Direct_MHelicalSp(self.handle, ctypes.c_int(imaxaxises), Axislistarray,
                                             ctypes.c_float(fend1), ctypes.c_float(
                                                 fend2), ctypes.c_float(fcenter1),
                                             ctypes.c_float(fcenter2), ctypes.c_float(
                                                 idirection),
                                             ctypes.c_float(fDistance3), ctypes.c_int(imode))
        return ret

    def ZAux_Direct_MHelicalAbsSp(self, imaxaxises, piAxislist, fend1, fend2, fcenter1, fcenter2, idirection,
                                  fDistance3, imode):
        '''
        Description: 3 20130901 .

        param imaxaxises: . type:int

        param piAxislist: . type:int

        param fend1: . type:float

        param fend2: . type:float

        param fcenter1: , . type:float

        param fcenter2: , . type:float

        param idirection: 0- ,1- . type:int

        param fDistance3: . type:float

        param imode: :0( ) .1 . type:int

        Return: . type: int32

        '''
        Axislistarray = (ctypes.c_int * len(piAxislist))(*piAxislist)
        ret = zauxdll.ZAux_Direct_MHelicalAbsSp(self.handle, ctypes.c_int(imaxaxises), Axislistarray,
                                                ctypes.c_float(fend1), ctypes.c_float(
                                                    fend2), ctypes.c_float(fcenter1),
                                                ctypes.c_float(fcenter2), ctypes.c_float(
                                                    idirection),
                                                ctypes.c_float(fDistance3), ctypes.c_int(imode))
        return ret

    def ZAux_Direct_MHelical2(self, imaxaxises, piAxislist, fmid1, fmid2, fend1, fend2, fDistance3, imode):
        '''
        Description: 3 3 20130901 .

        param imaxaxises: . type:int

        param piAxislist: . type:int

        param fmid1: . type:float

        param fmid2: . type:float

        param fend1: . type:float

        param fend2: . type:float

        param fDistance3: . type:float

        param imode: . type:int

        Return: . type: int32

        '''
        Axislistarray = (ctypes.c_int * len(piAxislist))(*piAxislist)
        ret = zauxdll.ZAux_Direct_MHelical2(self.handle, ctypes.c_int(imaxaxises), Axislistarray, ctypes.c_float(fmid1),
                                            ctypes.c_float(fmid2), ctypes.c_float(
                                                fend1), ctypes.c_float(fend2),
                                            ctypes.c_float(fDistance3), ctypes.c_int(imode))
        return ret

    def ZAux_Direct_MHelical2Abs(self, imaxaxises, piAxislist, fmid1, fmid2, fend1, fend2, fDistance3, imode):
        '''
        Description: 3 3 20130901 .

        param imaxaxises: . type:int

        param piAxislist: . type:int

        param fmid1: . type:float

        param fmid2: . type:float

        param fend1: . type:float

        param fend2: . type:float

        param fDistance3: . type:float

        param imode: . type:int

        Return: . type: int32

        '''
        Axislistarray = (ctypes.c_int * len(piAxislist))(*piAxislist)
        ret = zauxdll.ZAux_Direct_MHelical2Abs(self.handle, ctypes.c_int(imaxaxises), Axislistarray,
                                               ctypes.c_float(fmid1), ctypes.c_float(
                                                   fmid2), ctypes.c_float(fend1),
                                               ctypes.c_float(fend2), ctypes.c_float(fDistance3), ctypes.c_int(imode))
        return ret

    def ZAux_Direct_MHelical2Sp(self, imaxaxises, piAxislist, fmid1, fmid2, fend1, fend2, fDistance3, imode):
        '''
        Description: 3 3 SP 20130901 .

        param imaxaxises: . type:int

        param piAxislist: . type:int

        param fmid1: . type:float

        param fmid2: . type:float

        param fend1: . type:float

        param fend2: . type:float

        param fDistance3: . type:float

        param imode: . type:int

        Return: . type: int32

        '''
        Axislistarray = (ctypes.c_int * len(piAxislist))(*piAxislist)
        ret = zauxdll.ZAux_Direct_MHelical2Sp(self.handle, ctypes.c_int(imaxaxises), Axislistarray,
                                              ctypes.c_float(fmid1), ctypes.c_float(
                                                  fmid2), ctypes.c_float(fend1),
                                              ctypes.c_float(fend2), ctypes.c_float(fDistance3), ctypes.c_int(imode))
        return ret

    def ZAux_Direct_MHelical2AbsSp(self, imaxaxises, piAxislist, fmid1, fmid2, fend1, fend2, fDistance3, imode):
        '''
        Description: 3 3 SP 20130901 .

        param imaxaxises: . type:int

        param piAxislist: . type:int

        param fmid1: . type:float

        param fmid2: . type:float

        param fend1: . type:float

        param fend2: . type:float

        param fDistance3: . type:float

        param imode: . type:int

        Return: . type: int32

        '''
        Axislistarray = (ctypes.c_int * len(piAxislist))(*piAxislist)
        ret = zauxdll.ZAux_Direct_MHelical2AbsSp(self.handle, ctypes.c_int(imaxaxises), Axislistarray,
                                                 ctypes.c_float(fmid1), ctypes.c_float(
                                                     fmid2), ctypes.c_float(fend1),
                                                 ctypes.c_float(fend2), ctypes.c_float(fDistance3), ctypes.c_int(imode))
        return ret

    def ZAux_Direct_MEclipse(self, imaxaxises, piAxislist, fend1, fend2, fcenter1, fcenter2, idirection, fADis, fBDis):
        '''
        Description: 20130901 .

        param imaxaxises: . type:int

        param piAxislist: . type:int

        param fend1: , . type:float

        param fend2: , . type:float

        param fcenter1: , . type:float

        param fcenter2: , . type:float

        param idirection: 0- ,1- . type:int

        param fADis: , . type:float

        param fBDis: , ,AB . type:float

        Return: . type: int32

        '''
        Axislistarray = (ctypes.c_int * len(piAxislist))(*piAxislist)
        ret = zauxdll.ZAux_Direct_MEclipse(self.handle, ctypes.c_int(imaxaxises), Axislistarray, ctypes.c_float(fend1),
                                           ctypes.c_float(fend2), ctypes.c_float(
                                               fcenter1), ctypes.c_float(fcenter2),
                                           ctypes.c_int(idirection), ctypes.c_float(fADis), ctypes.c_float(fBDis))
        return ret

    def ZAux_Direct_MEclipseAbs(self, imaxaxises, piAxislist, fend1, fend2, fcenter1, fcenter2, idirection, fADis,
                                fBDis):
        '''
        Description: 20130901 .

        param imaxaxises: . type:int

        param piAxislist: . type:int

        param fend1: , . type:float

        param fend2: , . type:float

        param fcenter1: , . type:float

        param fcenter2: , . type:float

        param idirection: 0- ,1- . type:int

        param fADis: , . type:float

        param fBDis: , ,AB . type:float

        Return: . type: int32

        '''
        Axislistarray = (ctypes.c_int * len(piAxislist))(*piAxislist)
        ret = zauxdll.ZAux_Direct_MEclipseAbs(self.handle, ctypes.c_int(imaxaxises), Axislistarray,
                                              ctypes.c_float(fend1), ctypes.c_float(
                                                  fend2), ctypes.c_float(fcenter1),
                                              ctypes.c_float(fcenter2), ctypes.c_int(
                                                  idirection), ctypes.c_float(fADis),
                                              ctypes.c_float(fBDis))
        return ret

    def ZAux_Direct_MEclipseSp(self, imaxaxises, piAxislist, fend1, fend2, fcenter1, fcenter2, idirection, fADis,
                               fBDis):
        '''
        Description: SP 20130901 .

        param imaxaxises: . type:int

        param piAxislist: . type:int

        param fend1: , . type:float

        param fend2: , . type:float

        param fcenter1: , . type:float

        param fcenter2: , . type:float

        param idirection: 0- ,1- . type:int

        param fADis: , . type:float

        param fBDis: , ,AB . type:float

        Return: . type: int32

        '''
        Axislistarray = (ctypes.c_int * len(piAxislist))(*piAxislist)
        ret = zauxdll.ZAux_Direct_MEclipseSp(self.handle, ctypes.c_int(imaxaxises), Axislistarray,
                                             ctypes.c_float(fend1), ctypes.c_float(
                                                 fend2), ctypes.c_float(fcenter1),
                                             ctypes.c_float(fcenter2), ctypes.c_int(
                                                 idirection), ctypes.c_float(fADis),
                                             ctypes.c_float(fBDis))
        return ret

    def ZAux_Direct_MEclipseAbsSp(self, imaxaxises, piAxislist, fend1, fend2, fcenter1, fcenter2, idirection, fADis,
                                  fBDis):
        '''
        Description: SP 20130901 .

        param imaxaxises: . type:int

        param piAxislist: . type:int

        param fend1: , . type:float

        param fend2: , . type:float

        param fcenter1: , . type:float

        param fcenter2: , . type:float

        param idirection: 0- ,1- . type:int

        param fADis: , . type:float

        param fBDis: , ,AB . type:float

        Return: . type: int32

        '''
        Axislistarray = (ctypes.c_int * len(piAxislist))(*piAxislist)
        ret = zauxdll.ZAux_Direct_MEclipseAbsSp(self.handle, ctypes.c_int(imaxaxises), Axislistarray,
                                                ctypes.c_float(fend1), ctypes.c_float(
                                                    fend2), ctypes.c_float(fcenter1),
                                                ctypes.c_float(fcenter2), ctypes.c_int(
                                                    idirection),
                                                ctypes.c_float(fADis), ctypes.c_float(fBDis))
        return ret

    def ZAux_Direct_MEclipseHelical(self, imaxaxises, piAxislist, fend1, fend2, fcenter1, fcenter2, idirection, fADis,
                                    fBDis, fDistance3):
        '''
        Description: + 20130901 .

        param imaxaxises: . type:int

        param piAxislist: . type:int

        param fend1: , . type:float

        param fend2: , . type:float

        param fcenter1: , . type:float

        param fcenter2: , . type:float

        param idirection: 0- ,1- . type:int

        param fADis: , . type:float

        param fBDis: , ,AB . type:float

        param fDistance3: . type:float

        Return: . type: int32

        '''
        Axislistarray = (ctypes.c_int * len(piAxislist))(*piAxislist)
        ret = zauxdll.ZAux_Direct_MEclipseHelical(self.handle, ctypes.c_int(imaxaxises), Axislistarray,
                                                  ctypes.c_float(
                                                      fend1), ctypes.c_float(fend2),
                                                  ctypes.c_float(
                                                      fcenter1), ctypes.c_float(fcenter2),
                                                  ctypes.c_int(
                                                      idirection), ctypes.c_float(fADis),
                                                  ctypes.c_float(fBDis), ctypes.c_float(fDistance3))
        return ret

    def ZAux_Direct_MEclipseHelicalAbs(self, imaxaxises, piAxislist, fend1, fend2, fcenter1, fcenter2, idirection,
                                       fADis, fBDis, fDistance3, ):
        '''
        Description: + 20130901 .

        param imaxaxises: . type:int

        param piAxislist: . type:int

        param fend1: , . type:float

        param fend2: , . type:float

        param fcenter1: , . type:float

        param fcenter2: , . type:float

        param idirection: 0- ,1- . type:int

        param fADis: , . type:float

        param fBDis: , ,AB . type:float

        param fDistance3: . type:float

        Return: . type: int32

        '''
        Axislistarray = (ctypes.c_int * len(piAxislist))(*piAxislist)
        ret = zauxdll.ZAux_Direct_MEclipseHelicalAbs(self.handle, ctypes.c_int(imaxaxises), Axislistarray,
                                                     ctypes.c_float(
                                                         fend1), ctypes.c_float(fend2),
                                                     ctypes.c_float(
                                                         fcenter1), ctypes.c_float(fcenter2),
                                                     ctypes.c_int(
                                                         idirection), ctypes.c_float(fADis),
                                                     ctypes.c_float(fBDis), ctypes.c_float(fDistance3))
        return ret

    def ZAux_Direct_MEclipseHelicalSp(self, imaxaxises, piAxislist, fend1, fend2, fcenter1, fcenter2, idirection, fADis,
                                      fBDis, fDistance3):
        '''
        Description: + SP 20130901 .

        param imaxaxises: . type:int

        param piAxislist: . type:int

        param fend1: , . type:float

        param fend2: , . type:float

        param fcenter1: , . type:float

        param fcenter2: , . type:float

        param idirection: 0- ,1- . type:int

        param fADis: , . type:float

        param fBDis: , ,AB . type:float

        param fDistance3: . type:float

        Return: . type: int32

        '''
        Axislistarray = (ctypes.c_int * len(piAxislist))(*piAxislist)
        ret = zauxdll.ZAux_Direct_MEclipseHelicalSp(self.handle, ctypes.c_int(imaxaxises), Axislistarray,
                                                    ctypes.c_float(
                                                        fend1), ctypes.c_float(fend2),
                                                    ctypes.c_float(
                                                        fcenter1), ctypes.c_float(fcenter2),
                                                    ctypes.c_int(
                                                        idirection), ctypes.c_float(fADis),
                                                    ctypes.c_float(fBDis), ctypes.c_float(fDistance3))
        return ret

    def ZAux_Direct_MEclipseHelicalAbsSp(self, imaxaxises, piAxislist, fend1, fend2, fcenter1, fcenter2, idirection,
                                         fADis, fBDis, fDistance3):
        '''
        Description: + SP 20130901 .

        param imaxaxises: . type:int

        param piAxislist: . type:int

        param fend1: , . type:float

        param fend2: , . type:float

        param fcenter1: , . type:float

        param fcenter2: , . type:float

        param idirection: 0- ,1- . type:int

        param fADis: , . type:float

        param fBDis: , ,AB . type:float

        param fDistance3: . type:float

        Return: . type: int32

        '''
        Axislistarray = (ctypes.c_int * len(piAxislist))(*piAxislist)
        ret = zauxdll.ZAux_Direct_MEclipseHelicalAbsSp(self.handle, ctypes.c_int(imaxaxises), Axislistarray,
                                                       ctypes.c_float(
                                                           fend1), ctypes.c_float(fend2),
                                                       ctypes.c_float(
                                                           fcenter1), ctypes.c_float(fcenter2),
                                                       ctypes.c_int(
                                                           idirection), ctypes.c_float(fADis),
                                                       ctypes.c_float(fBDis), ctypes.c_float(fDistance3))
        return ret

    def ZAux_Direct_MSpherical(self, imaxaxises, piAxislist, fend1, fend2, fend3, fcenter1, fcenter2, fcenter3, imode,
                               fcenter4, fcenter5):
        '''
        Description: + 20130901 .

        param imaxaxises: . type:int

        param piAxislist: . type:int

        param fend1: 1 1 . type:float

        param fend2: 2 1 . type:float

        param fend3: 3 1 . type:float

        param fcenter1: 1 2 . type:float

        param fcenter2: 2 2 . type:float

        param fcenter3: 3 2 . type:float

        param imode: . type:int
                      0 , , , 1 , 2 .
                      1 , 1 , 2 .
                      2 , , , 1 , 2 .
                      3 , , 1 , 2 .

        param fcenter4: 4 . type:float

        param fcenter5: 5 . type:float

        Return: . type: int32

        '''
        Axislistarray = (ctypes.c_int * len(piAxislist))(*piAxislist)
        ret = zauxdll.ZAux_Direct_MSpherical(self.handle, ctypes.c_int(imaxaxises), Axislistarray,
                                             ctypes.c_float(fend1), ctypes.c_float(
                                                 fend2), ctypes.c_float(fend3),
                                             ctypes.c_float(
                                                 fcenter1), ctypes.c_float(fcenter2),
                                             ctypes.c_float(fcenter3), ctypes.c_int(
                                                 imode), ctypes.c_float(fcenter4),
                                             ctypes.c_float(fcenter5))
        return ret

    def ZAux_Direct_MSphericalSp(self, imaxaxises, piAxislist, fend1, fend2, fend3, fcenter1, fcenter2, fcenter3, imode,
                                 fcenter4, fcenter5):
        '''
        Description: + SP 20130901 .

        param imaxaxises: . type:int

        param piAxislist: . type:int

        param fend1: 1 1 . type:float

        param fend2: 2 1 . type:float

        param fend3: 3 1 . type:float

        param fcenter1: 1 2 . type:float

        param fcenter2: 2 2 . type:float

        param fcenter3: 3 2 . type:float

        param imode: . type:int
                      0 , , , 1 , 2 .
                      1 , 1 , 2 .
                      2 , , , 1 , 2 .
                      3 , , 1 , 2 .

        param fcenter4: 4 . type:float

        param fcenter5: 5 . type:float

        Return: . type: int32

        '''
        Axislistarray = (ctypes.c_int * len(piAxislist))(*piAxislist)
        ret = zauxdll.ZAux_Direct_MSphericalSp(self.handle, ctypes.c_int(imaxaxises), Axislistarray,
                                               ctypes.c_float(fend1), ctypes.c_float(
                                                   fend2), ctypes.c_float(fend3),
                                               ctypes.c_float(
                                                   fcenter1), ctypes.c_float(fcenter2),
                                               ctypes.c_float(fcenter3), ctypes.c_int(
                                                   imode), ctypes.c_float(fcenter4),
                                               ctypes.c_float(fcenter5))
        return ret

    def ZAux_Direct_MoveSpiral(self, imaxaxises, piAxislist, centre1, centre2, circles, pitch, distance3, distance4):
        '''
        Description: , , 0 0 .

        param imaxaxises: . type:int

        param piAxislist: . type:int

        param centre1: 1 . type:float

        param centre2: 2 . type:float

        param circles: , , . type:float

        param pitch: , . type:float

        param distance3: 3 , 3 , . type:float

        param distance4: 4 , 4 , . type:float

        Return: . type: int32

        '''
        Axislistarray = (ctypes.c_int * len(piAxislist))(*piAxislist)
        ret = zauxdll.ZAux_Direct_MoveSpiral(self.handle, ctypes.c_int(imaxaxises), Axislistarray,
                                             ctypes.c_float(centre1), ctypes.c_float(
                                                 centre2), ctypes.c_float(circles),
                                             ctypes.c_float(
                                                 pitch), ctypes.c_float(distance3),
                                             ctypes.c_float(distance4))
        return ret

    def ZAux_Direct_MoveSpiralSp(self, imaxaxises, piAxislist, centre1, centre2, circles, pitch, distance3, distance4):
        '''
        Description: SP , , 0 0 .

        param imaxaxises: . type:int

        param piAxislist: . type:int

        param centre1: 1 . type:float

        param centre2: 2 . type:float

        param circles: , , . type:float

        param pitch: , . type:float

        param distance3: 3 , 3 , . type:float

        param distance4: 4 , 4 , . type:float

        Return: . type: int32

        '''
        Axislistarray = (ctypes.c_int * len(piAxislist))(*piAxislist)
        ret = zauxdll.ZAux_Direct_MoveSpiralSp(self.handle, ctypes.c_int(imaxaxises), Axislistarray,
                                               ctypes.c_float(
                                                   centre1), ctypes.c_float(centre2),
                                               ctypes.c_float(
                                                   circles), ctypes.c_float(pitch),
                                               ctypes.c_float(distance3), ctypes.c_float(distance4))
        return ret

    def ZAux_Direct_MoveSmooth(self, imaxaxises, piAxislist, end1, end2, end3, next1, next2, next3, radius):
        '''
        Description: , , , , .

        param imaxaxises: . type:int

        param piAxislist: . type:int

        param end1: 1 . type:float

        param end2: 2 . type:float

        param end3: 3 . type:float

        param next1: 1 . type:float

        param next2: 2 . type:float

        param next3: 3 . type:float

        param radius: , . type:float

        Return: . type: int32

        '''
        Axislistarray = (ctypes.c_int * len(piAxislist))(*piAxislist)
        ret = zauxdll.ZAux_Direct_MoveSmooth(self.handle, ctypes.c_int(imaxaxises), Axislistarray, ctypes.c_float(end1),
                                             ctypes.c_float(end2), ctypes.c_float(
                                                 end3), ctypes.c_float(next1),
                                             ctypes.c_float(next2), ctypes.c_float(next3), ctypes.c_float(radius))
        return ret

    def ZAux_Direct_MoveSmoothSp(self, imaxaxises, piAxislist, end1, end2, end3, next1, next2, next3, radius):
        '''
        Description: SP , , , , .

        param imaxaxises: . type:int

        param piAxislist: . type:int

        param end1: 1 . type:float

        param end2: 2 . type:float

        param end3: 3 . type:float

        param next1: 1 . type:float

        param next2: 2 . type:float

        param next3: 3 . type:float

        param radius: , . type:float

        Return: . type: int32

        '''
        Axislistarray = (ctypes.c_int * len(piAxislist))(*piAxislist)
        ret = zauxdll.ZAux_Direct_MoveSmoothSp(self.handle, ctypes.c_int(imaxaxises), Axislistarray,
                                               ctypes.c_float(end1), ctypes.c_float(
                                                   end2), ctypes.c_float(end3),
                                               ctypes.c_float(next1), ctypes.c_float(
                                                   next2), ctypes.c_float(next3),
                                               ctypes.c_float(radius))
        return ret

    def ZAux_Direct_MovePause(self, iaxis, imode):
        '''
        Description: , . .

        param iaxis: . type:int

        param imode: type:int
                     0( ) .
                     1 .
                     2 , MARK . , .

        Return: . type: int32

        '''

        ret = zauxdll.ZAux_Direct_MovePause(
            self.handle, ctypes.c_int(iaxis), ctypes.c_int(imode))
        return ret

    def ZAux_Direct_MoveResume(self, iaxis):
        '''
        Description: .

        param iaxis: . type:int

        Return: . type: int32

        '''

        ret = zauxdll.ZAux_Direct_MoveResume(self.handle, ctypes.c_int(iaxis))
        return ret

    def ZAux_Direct_MoveLimit(self, iaxis, limitspeed):
        '''
        Description: , .

        param iaxis: . type:int

        param limitspeed: type:float

        Return: . type: int32

        '''

        ret = zauxdll.ZAux_Direct_MoveLimit(
            self.handle, ctypes.c_int(iaxis), ctypes.c_float(limitspeed))
        return ret

    def ZAux_Direct_MoveOp(self, iaxis, ioutnum, ivalue):
        '''
        Description: .

        param iaxis: . type:int

        param ioutnum: type:int

        param ivalue: type:int

        Return: . type: int32

        '''

        ret = zauxdll.ZAux_Direct_MoveOp(self.handle, ctypes.c_int(
            iaxis), ctypes.c_int(ioutnum), ctypes.c_int(ivalue))
        return ret

    def ZAux_Direct_MoveOpMulti(self, iaxis, ioutnumfirst, ioutnumend, ivalue):
        '''
        Description: .

        param iaxis: . type:int

        param ioutnumfirst: type:int

        param ioutnumend: type:int

        param ivalue: type:int

        Return: . type: int32

        '''

        ret = zauxdll.ZAux_Direct_MoveOpMulti(self.handle, ctypes.c_int(iaxis), ctypes.c_int(ioutnumfirst),
                                              ctypes.c_int(ioutnumend), ctypes.c_int(ivalue))
        return ret

    def ZAux_Direct_MoveOp2(self, iaxis, ioutnum, ivalue, iofftimems):
        '''
        Description: , .

        param iaxis: . type:int

        param ioutnum: type:int

        param ivalue: type:int

        param iofftimems: type:int

        Return: . type: int32

        '''
        ret = zauxdll.ZAux_Direct_MoveOp2(self.handle, ctypes.c_int(iaxis), ctypes.c_int(ioutnum), ctypes.c_int(ivalue),
                                          ctypes.c_int(iofftimems))
        return ret

    def ZAux_Direct_MoveAout(self, iaxis, ioutnum, fvalue):
        '''
        Description: , .

        param iaxis: . type:int

        param ioutnum: type:int

        param ivalue: type:int

        param iofftimems: type:int

        Return: . type: int32

        '''
        ret = zauxdll.ZAux_Direct_MoveAout(self.handle, ctypes.c_int(iaxis), ctypes.c_int(ioutnum),
                                           ctypes.c_int(fvalue))
        return ret

    def ZAux_Direct_MoveDelay(self, iaxis, itimems):
        '''
        Description: .

        param iaxis: . type:int

        param itimems: itimems . type:int

        Return: . type: int32

        '''

        ret = zauxdll.ZAux_Direct_MoveDelay(
            self.handle, ctypes.c_int(iaxis), ctypes.c_int(itimems))
        return ret

    def ZAux_Direct_MoveTurnabs(self, tablenum, imaxaxises, piAxislist, pfDisancelist):
        '''
        Description: . 20130901 .

        param iaxis: . type:int

        param tablenum: table . type:int

        param imaxaxises: . type:int

        param piAxislist: . type:int

        param pfDisancelist: . type:float

        Return: . type: int32

        '''
        piAxislistarry = (ctypes.c_float * len(piAxislist))(*piAxislist)
        pfDisancelistarry = (
            ctypes.c_float * len(pfDisancelist))(*pfDisancelist)
        ret = zauxdll.ZAux_Direct_MoveTurnabs(self.handle, ctypes.c_int(tablenum), ctypes.c_int(imaxaxises),
                                              piAxislistarry, pfDisancelistarry)
        return ret

    def ZAux_Direct_McircTurnabs(self, tablenum, refpos1, refpos2, mode, end1, end2, imaxaxises, piAxislist,
                                 pfDisancelist):
        '''
        Description: + . 20130901 .

        param iaxis: . type:int

        param tablenum: table . type:int

        param refpos1: , . type:float

        param refpos2: , . type:float

        param mode: 1- ,2- ,3- , . type:int

        param end1: , . type:float

        param end2: , . type:float

        param imaxaxises: . type:int

        param piAxislist: . type:int

        param pfDisancelist: . type:float

        Return: . type: int32

        '''
        piAxislistarry = (ctypes.c_float * len(piAxislist))(*piAxislist)
        pfDisancelistarry = (
            ctypes.c_float * len(pfDisancelist))(*pfDisancelist)
        ret = zauxdll.ZAux_Direct_McircTurnabs(self.handle, tablenum, refpos1, refpos2, mode, end1, end2, imaxaxises,
                                               piAxislistarry, pfDisancelistarry)
        return ret

    def ZAux_Direct_Cam(self, iaxis, istartpoint, iendpoint, ftablemulti, fDistance):
        '''
        Description: .

        param iaxis: . type:int

        param istartpoint: TABLE . type:int

        param iendpoint: TABLE . type:int

        param ftablemulti: , . type:float

        param fDistance: , . type:float

        Return: . type: int32

        '''

        ret = zauxdll.ZAux_Direct_Cam(self.handle, ctypes.c_int(iaxis), ctypes.c_int(istartpoint),
                                      ctypes.c_int(iendpoint), ctypes.c_float(ftablemulti), ctypes.c_float(fDistance))
        return ret

    def ZAux_Direct_Cambox(self, iaxis, istartpoint, iendpoint, ftablemulti, fDistance, ilinkaxis, ioption,
                           flinkstartpos):
        '''
        Description: .

        param iaxis: . type:int

        param istartpoint: TABLE . type:int

        param iendpoint: TABLE . type:int

        param ftablemulti: , . type:float

        param fDistance: , . type:float

        param ilinkaxis: . type:int

        param ioption: . type:int

        param flinkstartpos:ioption . type:float

        Return: . type: int32

        '''

        ret = zauxdll.ZAux_Direct_Cambox(self.handle, ctypes.c_int(iaxis), ctypes.c_int(istartpoint),
                                         ctypes.c_int(iendpoint), ctypes.c_float(
                                             ftablemulti),
                                         ctypes.c_float(fDistance), ctypes.c_int(
                                             ilinkaxis), ctypes.c_int(ioption),
                                         ctypes.c_float(flinkstartpos))
        return ret

    def ZAux_Direct_Movelink(self, iaxis, fDistance, fLinkDis, fLinkAcc, fLinkDec, iLinkaxis, ioption, flinkstartpos):
        '''
        Description: .

        param iaxis: ( ). type:int

        param fDistance: . type:float

        param fLinkDis: ( ) . type:float

        param fLinkAcc: , . type:float

        param fLinkDec: , . type:float

        param iLinkaxis: . type:int

        param ioption: . type:int

        param flinkstartpos: . type:float

        Return: . type: int32

        '''

        ret = zauxdll.ZAux_Direct_Movelink(self.handle, ctypes.c_int(iaxis), ctypes.c_float(fDistance),
                                           ctypes.c_float(fLinkDis), ctypes.c_float(
                                               fLinkAcc), ctypes.c_float(fLinkDec),
                                           ctypes.c_int(
                                               iLinkaxis), ctypes.c_float(ioption),
                                           ctypes.c_float(flinkstartpos))
        return ret

    def ZAux_Direct_Moveslink(self, iaxis, fDistance, fLinkDis, startsp, endsp, iLinkaxis, ioption, flinkstartpos):
        '''
        Description: .

        param iaxis: ( ). type:int

        param fDistance: . type:float

        param fLinkDis: ( ) . type:float

        param fLinkAcc: ,units\\units , . type:float

        param fLinkDec: ,units\\units , . type:float

        param iLinkaxis: . type:int

        param ioption: . type:int

        param flinkstartpos: . type:float

        Return: . type: int32

        '''

        ret = zauxdll.ZAux_Direct_Moveslink(self.handle, ctypes.c_int(iaxis), ctypes.c_float(fDistance),
                                            ctypes.c_float(fLinkDis), ctypes.c_float(
                                                startsp), ctypes.c_float(endsp),
                                            ctypes.c_int(
                                                iLinkaxis), ctypes.c_int(ioption),
                                            ctypes.c_float(flinkstartpos))
        return ret

    def ZAux_Direct_Connect(self, ratio, link_axis, move_axis):
        '''
        Description: .

        param ratio: , , . type:flot

        param link_axis: , . type:int

        param move_axis: . type:int

        Return: . type: int32

        '''

        ret = zauxdll.ZAux_Direct_Connect(self.handle, ctypes.c_float(ratio), ctypes.c_int(link_axis),
                                          ctypes.c_int(move_axis))
        return ret

    def ZAux_Direct_Connpath(self, ratio, link_axis, move_axis):
        '''
        Description: link_axis .

        param ratio: , , . type:int

        param link_axis: , . type:int

        param move_axis: . type:int

        Return: . type: int32

        '''

        ret = zauxdll.ZAux_Direct_Connpath(self.handle, ctypes.c_float(ratio), ctypes.c_int(link_axis),
                                           ctypes.c_int(move_axis))
        return ret

    def ZAux_Direct_Regist(self, iaxis, imode):
        '''
        Description: link_axis .

        param iaxis: . type:int

        param imode: . type:int

        Return: . type: int32

        '''

        ret = zauxdll.ZAux_Direct_Regist(
            self.handle, ctypes.c_int(iaxis), ctypes.c_int(imode))
        return ret

    def ZAux_Direct_EncoderRatio(self, iaxis, output_count, input_count):
        '''
        Description: , (1,1).

        param iaxis: . type:int

        param output_count: , 65535. type:int

        param input_count: , 65535. type:int

        Return: . type: int32

        '''

        ret = zauxdll.ZAux_Direct_EncoderRatio(self.handle, ctypes.c_int(iaxis), ctypes.c_int(output_count),
                                               ctypes.c_int(input_count))
        return ret

    def ZAux_Direct_StepRatio(self, iaxis, output_count, input_count):
        '''
        Description: , (1,1).

        param iaxis: . type:int

        param output_count: ,1-65535. type:int

        param input_count: ,1-65535. type:int

        Return: . type: int32

        '''
        ret = zauxdll.ZAux_Direct_StepRatio(self.handle, ctypes.c_int(iaxis), ctypes.c_int(output_count),
                                            ctypes.c_int(input_count))
        return ret

    def ZAux_Direct_Rapidstop(self, imode):
        '''
        Description: .

        param imode: . type:int
                      0( )
                                      1
                                      2 .
                                      3 .

        Return: . type: int32

        '''

        ret = zauxdll.ZAux_Direct_Rapidstop(self.handle, ctypes.c_int(imode))
        return ret

    def ZAux_Direct_CancelAxisList(self, imaxaxises, piAxislist, imode):
        '''
        Description: .

        param imaxaxises: . type:int

        param piAxislist: . type:int

        param imode: . type:int
                      0( )
                                      1
                                      2 .
                                      3 .

        Return: . type: int32

        '''
        Axisarry = (ctypes.c_int * len(piAxislist))(*piAxislist)
        ret = zauxdll.ZAux_Direct_CancelAxisList(
            self.handle, ctypes.c_int(imaxaxises), Axisarry, ctypes.c_int(imode))
        return ret

    def ZAux_Direct_Connframe(self, Jogmaxaxises, JogAxislist, frame, tablenum, Virmaxaxises, VirAxislist):
        '''
        Description:CONNFRAME 2 .
。
        param Jogmaxaxises: . type:int

        param JogAxislist: . type:int

        param frame: . type:int

        param tablenum: TABLE . type:int

        param Virmaxaxises: . type:int

        param VirAxislist: . type:int

        Return: . type: int32

        '''
        JogAxislistarry = (ctypes.c_int * len(JogAxislist))(*JogAxislist)
        VirAxislistarry = (ctypes.c_int * len(VirAxislist))(*VirAxislist)
        ret = zauxdll.ZAux_Direct_Connframe(self.handle, ctypes.c_int(Jogmaxaxises), JogAxislistarry,
                                            ctypes.c_int(frame), ctypes.c_int(
                                                tablenum), ctypes.c_int(Virmaxaxises),
                                            VirAxislistarry)
        return ret

    def ZAux_Direct_Connreframe(self, Virmaxaxises, VirAxislist, frame, tablenum, Jogmaxaxises, JogAxislist):
        '''
        Description:CONNREFRAME 2 .

        param Virmaxaxises: . type:int

        param VirAxislist: . type:int

        param frame: . type:int

        param tablenum: TABLE . type:int

        param Jogmaxaxises: . type:int

        param JogAxislist: . type:int

        Return: . type: int32

        '''
        JogAxislistarry = (ctypes.c_int * len(JogAxislist))(*JogAxislist)
        VirAxislistarry = (ctypes.c_int * len(VirAxislist))(*VirAxislist)
        ret = zauxdll.ZAux_Direct_Connreframe(self.handle, Virmaxaxises, VirAxislistarry, frame, tablenum, Jogmaxaxises,
                                              JogAxislistarry)
        return ret

    def ZAux_Direct_Single_Addax(self, iaxis, iaddaxis):
        '''
        Description: iaddaxis iaxis ,ADDAX .

        param iaxis: type:int

        param iaddaxis: . type:int

        Return: . type: int32

        '''

        ret = zauxdll.ZAux_Direct_Single_Addax(
            self.handle, ctypes.c_int(iaxis), ctypes.c_int(iaddaxis))
        return ret

    def ZAux_Direct_Single_Cancel(self, iaxis, imode):
        '''
        Description

        param iaxis: . type:int

        param imode: . type:int
                      0( )
                                      1
                                      2 .
                                      3 .

        Return: . type: int32

        '''

        ret = zauxdll.ZAux_Direct_Single_Cancel(
            self.handle, ctypes.c_int(iaxis), ctypes.c_int(imode))
        return ret

    def ZAux_Direct_Single_Vmove(self, iaxis, idir):
        '''
        Description: .

        param iaxis: . type:int

        param idir: 1 -1 . type:int

        Return: . type: int32

        '''

        ret = zauxdll.ZAux_Direct_Single_Vmove(
            self.handle, ctypes.c_int(iaxis), ctypes.c_int(idir))
        return ret

    def ZAux_Direct_Single_Datum(self, iaxis, imode):
        '''
        Description: .

        param iaxis: . type:int

        param imode: . type:int

        Return: . type: int32

        '''

        ret = zauxdll.ZAux_Direct_Single_Datum(
            self.handle, ctypes.c_int(iaxis), ctypes.c_int(imode))
        return ret

    def ZAux_Direct_GetHomeStatus(self, iaxis):
        '''
        Description: .

        param iaxis: . type:int

        Return,: , 0- 1 . type: int32,uint32

        '''
        value = (ctypes.c_int)()
        ret = zauxdll.ZAux_Direct_GetHomeStatus(
            self.handle, ctypes.c_int(iaxis), ctypes.byref(value))
        return ret, value

    def ZAux_Direct_Single_Move(self, iaxis, fdistance):
        '''
        Description: .

        param iaxis: . type:int

        param fdistance: . type:float

        Return: . type: int32

        '''

        ret = zauxdll.ZAux_Direct_Single_Move(
            self.handle, ctypes.c_int(iaxis), ctypes.c_float(fdistance))
        return ret

    def ZAux_Direct_Single_MoveAbs(self, iaxis, fdistance):
        '''
        Description: .

        param iaxis: . type:int

        param fdistance: . type:float

        Return: . type: int32

        '''

        ret = zauxdll.ZAux_Direct_Single_MoveAbs(
            self.handle, ctypes.c_int(iaxis), ctypes.c_float(fdistance))
        return ret

    def ZAux_Direct_SetVrf(self, vrstartnum, numes, pfValue):
        '''
        Description: VR.

        param vrstartnum:VR . type:int

        param numes: . type:int

        param pfValue: . type:float

        Return: . type: int32

        '''
        pfValuearry = (ctypes.c_float * len(pfValue))(*pfValue)
        ret = zauxdll.ZAux_Direct_SetVrf(self.handle, ctypes.c_int(
            vrstartnum), ctypes.c_int(numes), pfValuearry)
        return ret

    def ZAux_Direct_GetVrf(self, vrstartnum, numes):
        '''
        Description:VR , .

        param vrstartnum:VR . type:int

        param numes: . type:int

        Return: , , . type: int32,float

        '''
        value = (ctypes.c_float * numes)()
        ret = zauxdll.ZAux_Direct_GetVrf(self.handle, ctypes.c_int(vrstartnum), ctypes.c_int(numes),
                                         ctypes.byref(value))
        return ret, value

    def ZAux_Direct_GetVrInt(self, vrstartnum, numes):
        '''
        Description:VRINT , 150401 VRINT DIRECTCOMMAND .

        param vrstartnum:VR . type:int

        param numes: . type:int

        Return: , , . type: int32,float

        '''
        value = (ctypes.c_int * numes)()
        ret = zauxdll.ZAux_Direct_GetVrf(self.handle, ctypes.c_int(vrstartnum), ctypes.c_int(numes),
                                         ctypes.byref(value))
        return ret, value

    def ZAux_Direct_SetTable(self, tabstart, numes, pfValue):
        '''
        Description: table .

        param tabstart: TABLE . type:int

        param numes: . type:int

        param pfValue: . type:float

        Return: . type: int32

        '''
        value = (ctypes.c_float * len(pfValue))(*pfValue)
        ret = zauxdll.ZAux_Direct_SetTable(
            self.handle, ctypes.c_int(tabstart), ctypes.c_int(numes), value)
        return ret

    def ZAux_Direct_GetTable(self, tabstart, numes):
        '''
        Description:table , .

        param tabstart: TABLE . type:int

        param numes: . type:int

        Return: , , . type: int32,float

        '''
        value = (ctypes.c_float * numes)()
        ret = zauxdll.ZAux_Direct_GetTable(self.handle, ctypes.c_int(tabstart), ctypes.c_int(numes),
                                           ctypes.byref(value))
        return ret, value

    def ZAux_TransStringtoFloat(self, pstringin, inumes):
        '''
        Description: float.

        param pstringin: . type:sting

        param inumes: . type:int

        Return: , . type: int32,float

        '''
        _str = pstringin.encode('utf-8')
        value = (ctypes.c_float * inumes)()
        ret = zauxdll.ZAux_TransStringtoFloat(
            _str, inumes, ctypes.byref(value))
        return ret, value

    def ZAux_TransStringtoInt(self, pstringin, inumes):
        '''
        Description: int.

        param pstringin: . type:sting

        param inumes: . type:int

        Return: , . type: int32,int

        '''
        _str = pstringin.encode('utf-8')
        value = (ctypes.c_int * inumes)()
        ret = zauxdll.ZAux_TransStringtoInt(_str, inumes, ctypes.byref(value))
        return ret, value

    def ZAux_WriteUFile(self, sFilename, pVarlist, inum):
        '''
        Description: float , U .

        param sFilename: . type:sting

        param pVarlist: . type:float

        Return: . type: int32

        '''
        _str = sFilename.encode('utf-8')
        value = (ctypes.c_float * len(pVarlist))(*pVarlist)
        ret = zauxdll.ZAux_WriteUFile(
            _str, value, len(pVarlist), ctypes.c_int(inum))
        return ret

    def ZAux_ReadUFile(self, sFilename, inum):
        '''
        Description: float , U .

        param sFilename: . type:sting

        Return: , . type: int32,int

        '''
        _str = sFilename.encode('utf-8')
        value = (ctypes.c_float * (inum))()
        ret = zauxdll.ZAux_ReadUFile(_str, ctypes.byref(value))
        return ret, value

    def ZAux_Modbus_Set0x(self, start, inum, pdata):
        '''
        Description:modbus modbus_bit.

        param start: . type:uint16

        param inum: . type:uint16

        param pdata: ( ). type:uint8

        Return: . type: uint16

        '''
        Axislistarray = (ctypes.c_int * len(pdata))(*pdata)
        ret = zauxdll.ZAux_Modbus_Set0x(self.handle, ctypes.c_uint(
            start), ctypes.c_uint(inum), Axislistarray)
        return ret

    def ZAux_Modbus_Get0x(self, start, inum):
        '''
        Description:modbus modbus_bit.

        param start: . type:uint16

        param inum: . type:uint16

        Return: , . type: int32,uint8

        '''
        value = (ctypes.c_uint8 * inum)()
        ret = zauxdll.ZAux_Modbus_Get0x(self.handle, ctypes.c_uint(
            start), ctypes.c_uint(inum), ctypes.byref(value))
        return ret, value

    def ZAux_Modbus_Set4x(self, start, inum, pdata):
        '''
        Description:modbus MODBUS_REG.

        param start: . type:uint16

        param inum: . type:uint16

         param inum: . type:uint16

        Return: . type: int32

        '''
        Axislistarray = (ctypes.c_int * len(pdata))(*pdata)
        ret = zauxdll.ZAux_Modbus_Set4x(self.handle, ctypes.c_uint(
            start), ctypes.c_uint(inum), Axislistarray)
        return ret

    def ZAux_Modbus_Get4x(self, start, inum):
        '''
        Description:modbus MODBUS_REG.

        param start: . type:uint16

        param inum: . type:uint16

        Return: , REG . type: int32,uint16

        '''
        value = (ctypes.c_int16 * inum)()
        ret = zauxdll.ZAux_Modbus_Get4x(self.handle, ctypes.c_uint(
            start), ctypes.c_uint(inum), ctypes.byref(value))
        return ret, value

    def ZAux_Modbus_Get4x_Float(self, start, inum):
        '''
        Description:Modbus MODBUS_IEEE . MODBUS_IEEE.

        param start: . type:uint16

        param inum: . type:uint16

        Return: , REG . type: int32,float

        '''
        value = (ctypes.c_float * inum)()
        ret = zauxdll.ZAux_Modbus_Get4x_Float(self.handle, ctypes.c_uint(start), ctypes.c_uint(inum),
                                              ctypes.byref(value))
        return ret, value

    def ZAux_Modbus_Set4x_Float(self, start, inum, pdata):
        '''
        Description: :modbus . MODBUS_IEEE

        param start: . type:uint16

        param inum: . type:uint16

         param pdata: . type:float

        Return: . type: int32

        '''
        Axislistarray = (ctypes.c_float * len(pdata))(*pdata)
        ret = zauxdll.ZAux_Modbus_Set4x_Float(
            self.handle, ctypes.c_uint(start), ctypes.c_int(inum), Axislistarray)
        return ret

    def ZAux_Modbus_Get4x_Long(self, start, inum):
        '''
        Description: :modbus MODBUS_LONG.

        param start: . type:uint16

        param inum: . type:uint16

        Return: , REG . type: int32,int32

        '''

        value = (ctypes.c_int32 * inum)()
        ret = zauxdll.ZAux_Modbus_Get4x_Long(self.handle, ctypes.c_uint(
            start), ctypes.c_int(inum), ctypes.byref(value))
        return ret, value

    def ZAux_Modbus_Set4x_Long(self, start, inum, pidata):
        '''
        Description: :modbus MODBUS_LONG.

        param start: . type:uint16

        param inum: . type:uint16

        param inum: . type:int32

        Return: . type: int32

        '''
        Axislistarray = (ctypes.c_int32 * len(pidata))(*pidata)
        ret = zauxdll.ZAux_Modbus_Set4x_Long(
            self.handle, ctypes.c_uint(start), ctypes.c_int(inum), Axislistarray)
        return ret

    def ZAux_Modbus_Set4x_String(self, start, inum, pdata):
        '''
        Description: modbus_string.

        param start:modbus . type:uint16

        param inum: . type:uint16

        param pdata: . type:sting

        Return: . type: int32

        '''
        _str = pdata.encode('utf-8')
        ret = zauxdll.ZAux_Modbus_Set4x_String(
            self.handle, ctypes.c_uint(start), ctypes.c_int(inum), _str)
        return ret

    def ZAux_Modbus_Get4x_String(self, start, inum):
        '''
        Description: modbus_string.

        param start:modbus . type:uint16

        param inum: . type:uint16

        Return: , . type: int32,sting

        '''
        value = (ctypes.c_char * inum)()
        ret = zauxdll.ZAux_Modbus_Get4x_String(self.handle, ctypes.c_uint(start), ctypes.c_int(inum),
                                               ctypes.byref(value))
        return ret, value

    def ZAux_FlashWritef(self, uiflashid, uinumes, pfvlue):
        '''
        Description: flash , float .

        param uiflashid:modbus . type:uint16

        param uinumes: . type:int32

        param pfvlue: . type:float

        Return: . type: int32,int32

        '''
        Axislistarray = (ctypes.c_float * len(pfvlue))(*pfvlue)
        ret = zauxdll.ZAux_FlashWritef(self.handle, ctypes.c_uint16(
            uiflashid), ctypes.c_int32(uinumes), Axislistarray)
        return ret

    def ZAux_FlashReadf(self, uiflashid, uinumes):
        '''
        Description: flash , float .

        param uiflashid:flash . type:uint16

        param uinumes: . type:int32

        Return: , . type: int32,int32

        '''
        value = (ctypes.c_float * uinumes)()
        ret = zauxdll.ZAux_FlashReadf(self.handle, ctypes.c_uint16(uiflashid), ctypes.c_int32(uinumes),
                                      ctypes.byref(value))
        return ret, value

    def ZAux_Trigger(self):
        '''
        Description: 150723 .

        '''
        ret = zauxdll.ZAux_Trigger(self.handle)
        return ret

    def ZAux_Direct_MovePara(self, base_axis, paraname, iaxis, fvalue):
        '''
        Description: . 20170503 .

        param base_axis: . type:uint32

        param paraname: . type:sting

        param iaxis: . type: uint32

        param fvalue: . type:float

        Return: . type: int32

        '''
        _str = paraname.encode('utf-8')
        ret = zauxdll.ZAux_Direct_MovePara(self.handle, ctypes.c_uint32(base_axis), _str, ctypes.c_int32(iaxis),
                                           ctypes.c_float(fvalue))
        return ret

    def ZAux_Direct_MovePwm(self, base_axis, pwm_num, pwm_duty, pwm_freq):
        '''
        Description: PWM 20170503 .

        param base_axis: . type:uint32

        param pwm_num:PWM . type:uint32

        param pwm_duty: . type: float

        param pwm_freq: . type:float

        Return: . type: int32

        '''

        ret = zauxdll.ZAux_Direct_MovePwm(self.handle, ctypes.c_uint32(base_axis), ctypes.c_uint32(pwm_num),
                                          ctypes.c_float(pwm_duty), ctypes.c_float(pwm_freq))
        return ret

    def ZAux_Direct_MoveASynmove(self, base_axis, iaxis, fdist, ifsp):
        '''
        Description: . 20170503 .

        param base_axis: . type:uint32

        param iaxis: . type:uint32

        param fdist: . type: float

        param ifsp: SP . type:uint32

        Return: . type: int32

        '''
        ret = zauxdll.ZAux_Direct_MoveASynmove(self.handle, ctypes.c_uint32(base_axis), ctypes.c_uint32(iaxis),
                                               ctypes.c_float(fdist), ctypes.c_int32(ifsp))
        return ret

    def ZAux_Direct_MoveTable(self, base_axis, table_num, fvalue):
        '''
        Description: TABLE.

        param base_axis: . type:uint32

        param table_num:TABLE . type:uint32

        param fvalue: . type: float

        Return: . type: int32

        '''
        ret = zauxdll.ZAux_Direct_MoveTable(self.handle, ctypes.c_uint32(base_axis), ctypes.c_uint32(table_num),
                                            ctypes.c_float(fvalue))
        return ret

    def ZAux_Direct_MoveWait(self, base_axis, paraname, inum, Cmp_mode, fvalue):
        '''
        Description:BASE 150802 , XPLC160405 .

        param base_axis: . type: uint32

        param paraname: DPOS MPOS IN AIN VPSPEED MSPEED MODBUS_REG MODBUS_IEEE MODBUS_BIT NVRAM VECT_BUFFED REMAIN . type: string

        param inum: . type: int

        param Cmp_mode: 1 >= 0= -1<= IN BIT . type: int

        param fvalue: . type: float

        Return: . type: int32

        '''
        _str = paraname.encode('utf-8')
        ret = zauxdll.ZAux_Direct_MoveWait(self.handle, ctypes.c_uint32(base_axis), _str, ctypes.c_int(inum),
                                           ctypes.c_int(Cmp_mode), ctypes.c_float(fvalue))
        return ret

    def ZAux_Direct_MoveTask(self, base_axis, tasknum, labelname):
        '''
        Description:BASE TASK , , .

        param base_axis: . type: uint32

        param tasknum: . type: uint32

        param labelname:BAS . type: sting

        Return: . type: int32

        '''
        _str = labelname.encode('utf-8')
        ret = zauxdll.ZAux_Direct_MoveTask(self.handle, ctypes.c_uint32(
            base_axis), ctypes.c_uint32(tasknum), _str)
        return ret

    def ZAux_Direct_Pswitch(self, num, enable, axisnum, outnum, outstate, setpos, resetpos):
        '''
        Description: PSWITCH.

        param num: 0-15. type: int

        param enable: 0\\1. type: int

        param axisnum: . type: int

        param outnum: . type: int

        param outstate: 0\\1 . type: int

        param setpos: . type: float

        param resetpos: . type: float

        Return: . type: int32

        '''

        ret = zauxdll.ZAux_Direct_Pswitch(self.handle, ctypes.c_int(num), ctypes.c_int(enable), ctypes.c_int(axisnum),
                                          ctypes.c_int(outnum), ctypes.c_int(
                                              outstate), ctypes.c_float(setpos),
                                          ctypes.c_float(resetpos))
        return ret

    def ZAux_Direct_HwPswitch(self, Axisnum, Mode, Direction, Reserve, Tablestart, Tableend):
        '''
        Description: 4 .

        param Axisnum: . type: int

        param Mode: 1- 2- . type: int

        param Direction: 0- 1- . type: int

        param Reserve: . type: int

        param Tablestart:TABLE . type: int

        param Tableend:TABLE . type: int

        Return: . type: int32

        '''

        ret = zauxdll.ZAux_Direct_HwPswitch(self.handle, ctypes.c_int(Axisnum), ctypes.c_int(Mode),
                                            ctypes.c_int(Direction), ctypes.c_int(
                                                Reserve), ctypes.c_int(Tablestart),
                                            ctypes.c_int(Tableend))
        return ret

    def ZAux_Direct_GetHwPswitchBuff(self, axisnum):
        '''
        Description: 4 .

        param axisnum: . type: int

        Return: , . type: int32,int

        '''
        value = (ctypes.c_int)()
        ret = zauxdll.ZAux_Direct_GetHwPswitchBuff(
            self.handle, ctypes.c_int(axisnum), ctypes.byref(value))
        return ret, value

    def ZAux_Direct_HwTimer(self, mode, cyclonetime, optime, reptimes, opstate, opnum):
        '''
        Description: 4 .

        param mode: . type: int

        param cyclonetime: us . type: int

        param optime: us . type: int

        param reptimes: . type: int

        param opstate: . type: int

        param opnum: . type: int

        Return: . type: int32

        '''

        ret = zauxdll.ZAux_Direct_HwTimer(self.handle, ctypes.c_int(mode), ctypes.c_int(cyclonetime),
                                          ctypes.c_int(optime), ctypes.c_int(
                                              reptimes), ctypes.c_int(opstate),
                                          ctypes.c_int(opnum))
        return ret

    def ZAux_Direct_GetAxisStopReason(self, iaxis):
        '''
        Description: .

        param iaxis: . type: int

        Return: , , . type: int32,int

        '''
        value = (ctypes.c_int)()
        ret = zauxdll.ZAux_Direct_GetAxisStopReason(
            self.handle, ctypes.c_int(iaxis), ctypes.byref(value))
        return ret, value

    def ZAux_Direct_GetAllAxisPara(self, sParam, imaxaxis):
        '''
        Description: .

        param sParam:Baisc . type: sting

        param imaxaxis: . type: int

        Return: , . type: int32,float

        '''
        _str = sParam.encode('utf-8')
        value = (ctypes.c_float * imaxaxis)()
        ret = zauxdll.ZAux_Direct_GetAllAxisPara(
            self.handle, _str, ctypes.c_int(imaxaxis), ctypes.byref(value))
        return ret, value

    def ZAux_Direct_GetAllAxisInfo(self, max_axis, idle_status, target_pos_status, feedback_pos_status, axis_status):
        max_axis = ctypes.c_int(max_axis)
        '''
        Description: .
    
        param max_axis: . type: int

        param idle_status: . type: int

        param target_pos_status: .
        
        param feedback_pos_status: .
        
        param axis_status: .

        Return: , . type: int32,float

        '''
        # c
        # idle_status = ctypes.pointer(ctypes.c_int(idle_status))
        # target_pos_status = ctypes.pointer(ctypes.c_float(target_pos_status))
        # feedback_pos_status = ctypes.pointer(ctypes.c_float(feedback_pos_status))
        # axis_status = ctypes.pointer(ctypes.c_int(axis_status))
        ret = zauxdll.ZAux_Direct_GetAllAxisInfo(self.handle, max_axis, idle_status, target_pos_status,
                                                 feedback_pos_status, axis_status)

    def ZAux_Direct_SetUserArray(self, arrayname, arraystart, numes, pfValue):
        '''
        Description: BASIC .

        param arrayname: . type: sting

        param arraystart: us . type: int

        param numes: . type: int

        param pfValue: . type: float

        Return: . type: int32

        '''
        _str = arrayname.encode('utf-8')
        ARRYY = (ctypes.c_float * len(pfValue))(*pfValue)
        ret = zauxdll.ZAux_Direct_SetUserArray(
            self.handle, _str, ctypes.c_int(arraystart), ctypes.c_int(numes), ARRYY)
        return ret

    def ZAux_Direct_GetUserArray(self, arrayname, arraystart, numes):
        '''
        Description: BASIC , .

        param arrayname: . type: sting

        param arraystart: us . type: int

        param numes: . type: int

        Return: , . type: int32,float

        '''
        _str = arrayname.encode('utf-8')
        value = (ctypes.c_float * numes)()
        ret = zauxdll.ZAux_Direct_GetUserArray(self.handle, _str, ctypes.c_int(arraystart), ctypes.c_int(numes),
                                               ctypes.byref(value))
        return ret, value

    def ZAux_Direct_SetUserVar(self, varname, pfValue):
        '''
        Description: .

        param varname: . type: sting

        param pfValue: . type: float

        Return: . type: int32

        '''
        _str = varname.encode('utf-8')
        ret = zauxdll.ZAux_Direct_SetUserVar(
            self.handle, _str, ctypes.c_float(pfValue))
        return ret

    def ZAux_Direct_GetUserVar(self, varname):
        '''
        Description: .

        param varname: . type: sting

        Return: , . type: int32,float

        '''
        _str = varname.encode('utf-8')
        value = (ctypes.c_float)()
        ret = zauxdll.ZAux_Direct_GetUserVar(
            self.handle, _str, ctypes.byref(value))
        return ret, value

    def ZAux_OpenPci(self, cardnum):
        '''
        Description: .

        param cardnum:PCI . type: uint32

        Return: . type: int32

        '''
        ret = zauxdll.ZAux_OpenPci(ctypes.c_int(
            cardnum), ctypes.pointer(self.handle))
        return ret

    def ZAux_BusCmd_GetNodeNum(self, slot):
        '''
        Description: .

        param slot: 0. type: int

        Return: , .type: int32,int

        '''
        value = (ctypes.c_int)()
        ret = zauxdll.ZAux_BusCmd_GetNodeNum(
            self.handle, ctypes.c_int(slot), ctypes.byref(value))
        return ret, value

    def ZAux_BusCmd_GetNodeInfo(self, slot, node, sel):
        '''
        Description: .

        param slot: 0. type: int

        param node: 0. type: int

        param sel: 0- 1- 2- 3- 10-IN 11-OUT . type: int

        Return: , .type: int32,int

        '''
        value = (ctypes.c_int)()
        ret = zauxdll.ZAux_BusCmd_GetNodeInfo(self.handle, ctypes.c_int(slot), ctypes.c_int(node), ctypes.c_int(sel),
                                              ctypes.byref(value))
        return ret, value

    def ZAux_BusCmd_GetNodeStatus(self, slot, node):
        '''
        Description: .

        param slot: 0. type: int

        param node: 0. type: int

        Return: , bit0- bit1- bit2- .type: int32,int

        '''
        value = (ctypes.c_int)()
        ret = zauxdll.ZAux_BusCmd_GetNodeStatus(self.handle, ctypes.c_int(slot), ctypes.c_int(node),
                                                ctypes.byref(value))
        return ret, value

    def ZAux_BusCmd_SDORead(self, slot, node, index, subindex, aype):
        '''
        Description: SDO .

        param slot: 0. type: uint32

        param node: 0. type: uint32

        param index: ( 10 )0. type: uint32

        param subindex: ( 10 ). type: uint32

        param aype: 1-bool 2-int8 3-int16 4-int32 5-uint8 6-uint16 7-uint32. type: uint32

        Return: , : int32,int

        '''
        value = (ctypes.c_int)()
        ret = zauxdll.ZAux_BusCmd_SDORead(self.handle, ctypes.c_int(slot), ctypes.c_int(node), ctypes.c_int(index),
                                          ctypes.c_int(subindex), ctypes.c_int(aype), ctypes.byref(value))
        return ret, value

    def ZAux_BusCmd_SDOWrite(self, slot, node, index, subindex, aype, Vvalue):
        '''
        Description: SDO .

        param slot: 0. type: uint32

        param node: 0. type: uint32

        param index: ( 10 )0. type:uint32

        param subindex: ( 10 ). type: uint32

        param aype: 1-bool 2-int8 3-int16 4-int32 5-uint8 6-uint16 7-uint32. type: int

        param Vvalue: . type: uint32

        Return: : int32

        '''
        ret = zauxdll.ZAux_BusCmd_SDOWrite(self.handle, ctypes.c_int(slot), ctypes.c_int(node), ctypes.c_int(index),
                                           ctypes.c_int(subindex), ctypes.c_int(aype), ctypes.c_int(Vvalue))
        return ret

    def ZAux_BusCmd_SDOReadAxis(self, iaxis, index, subindex, aype):
        '''
        Description: SDO .

        param iaxis: . type: uint32

        param index: . type: uint32

        param subindex: . type: uint32

        param aype: 1-bool 2-int8 3-int16 4-int32 5-uint8 6-uint16 7-uint32. type: uint32

        Return: , . int32,int32

        '''
        value = (ctypes.c_int)()
        ret = zauxdll.ZAux_BusCmd_SDOReadAxis(self.handle, ctypes.c_int(iaxis), ctypes.c_int(index),
                                              ctypes.c_int(subindex), ctypes.c_int(aype), ctypes.byref(value))
        return ret, value

    def ZAux_BusCmd_SDOWriteAxis(self, iaxis, index, subindex, aype, Vvalue):
        '''
        Description: SDO .

        param iaxis: . type: uint32

        param index: . type: uint32

        param subindex: . type: uint32

        param aype: 1-bool 2-int8 3-int16 4-int32 5-uint8 6-uint16 7-uint32. type: uint32

        param Vvalue: . type: uint32

        Return: . type:int32

        '''
        ret = zauxdll.ZAux_BusCmd_SDOWriteAxis(self.handle, ctypes.c_int(iaxis), ctypes.c_int(index),
                                               ctypes.c_int(subindex), ctypes.c_int(aype), ctypes.c_int(Vvalue))
        return ret

    def ZAux_BusCmd_RtexRead(self, iaxis, ipara):
        '''
        Description:Rtex .

        param iaxis: . type: uint32

        param ipara: *256 + Pr7.11-ipara = 7*256+11. type: uint32

        Return: , . type:int32,float

        '''
        value = (ctypes.c_float)()
        ret = zauxdll.ZAux_BusCmd_RtexRead(self.handle, ctypes.c_uint(iaxis), ctypes.c_int32(ipara),
                                           ctypes.byref(value))
        return ret, value

    def ZAux_BusCmd_RtexWrite(self, iaxis, ipara, vvalue):
        '''
        Description:Rtex .

        param iaxis: . type: uint32

        param ipara: *256 + Pr7.11-ipara = 7*256+11. type: uint32

        param vvalue: . type: float

        Return: . type:int32

        '''
        ret = zauxdll.ZAux_BusCmd_RtexWrite(self.handle, ctypes.c_uint(iaxis), ctypes.c_uint(ipara),
                                            ctypes.c_float(vvalue))
        return ret

    def ZAux_BusCmd_SetDatumOffpos(self, iaxis, fValue):
        '''
        Description: .

        param iaxis: . type: uint32

        param fValue: . type: float

        Return: . type:int32

        '''
        ret = zauxdll.ZAux_BusCmd_SetDatumOffpos(
            self.handle, ctypes.c_uint(iaxis), ctypes.c_float(fValue))
        return ret

    def ZAux_BusCmd_GetDatumOffpos(self, iaxis):
        '''
        Description: .

        param iaxis: . type: uint32

        Return: , . type:int32,float

        '''
        value = (ctypes.c_float)()
        ret = zauxdll.ZAux_BusCmd_GetDatumOffpos(
            self.handle, ctypes.c_uint(iaxis), ctypes.byref(value))
        return ret, value

    def ZAux_BusCmd_Datum(self, iaxis, homemode):
        '''
        Description: .

        param iaxis: . type: uint32

        param homemode: , . type: uint32

        Return: . type:int32

        '''
        ret = zauxdll.ZAux_BusCmd_Datum(
            self.handle, ctypes.c_uint(iaxis), ctypes.c_uint(homemode))
        return ret

    def ZAux_BusCmd_GetHomeStatus(self, iaxis):
        '''
        Description: .

        param iaxis: . type: uint32

        Return: , 0- 1 . type:int32,uint32

        '''
        value = (ctypes.c_int)()
        ret = zauxdll.ZAux_BusCmd_GetHomeStatus(
            self.handle, ctypes.c_uint(iaxis), ctypes.byref(value))
        return ret, value

    def ZAux_BusCmd_DriveClear(self, iaxis, mode):
        '''
        Description: .

        param iaxis: . type: uint32

        param mode: 0- 1- 2- . type: uint32

        Return: . type:int32

        '''
        ret = zauxdll.ZAux_BusCmd_DriveClear(
            self.handle, ctypes.c_uint(iaxis), ctypes.c_uint(mode))
        return ret

    def ZAux_BusCmd_GetDriveTorque(self, iaxis):
        '''
        Description: DRIVE_PROFILE .

        param iaxis: . type: int

        Return: , . type:int32,int

        '''
        value = (ctypes.c_int)()
        ret = zauxdll.ZAux_BusCmd_GetDriveTorque(
            self.handle, ctypes.c_uint(iaxis), ctypes.byref(value))
        return ret, value

    def ZAux_BusCmd_SetMaxDriveTorque(self, iaxis, piValue):
        '''
        Description: DRIVE_PROFILE .

        param iaxis: . type: int

         param piValue: . type: int

        Return: . type:int32

        '''
        ret = zauxdll.ZAux_BusCmd_SetMaxDriveTorque(
            self.handle, ctypes.c_uint(iaxis), ctypes.c_uint(piValue))
        return ret

    def ZAux_BusCmd_GetMaxDriveTorque(self, iaxis):
        '''
        Description: DRIVE_PROFILE .

        param iaxis: . type: int

        Return: , . type:int32,int

        '''
        value = (ctypes.c_int)()
        ret = zauxdll.ZAux_BusCmd_GetMaxDriveTorque(
            self.handle, ctypes.c_uint(iaxis), ctypes.byref(value))
        return ret, value

    def ZAux_Direct_SetDAC(self, iaxis, fValue):
        '''
        Description: , DRIVE_PROFILE ATYPE

        param iaxis: . type: int

         param piValue: . type: float

        Return: . type:int32

        '''
        ret = zauxdll.ZAux_Direct_SetDAC(
            self.handle, ctypes.c_uint(iaxis), ctypes.c_float(fValue))
        return ret

    def ZAux_Direct_GetDAC(self, iaxis):
        '''
        Description: , DRIVE_PROFILE ATYPE.

        param iaxis: . type: int

        Return: , . type:int32,float

        '''
        value = (ctypes.c_float)()
        ret = zauxdll.ZAux_Direct_GetDAC(
            self.handle, ctypes.c_uint(iaxis), ctypes.byref(value))
        return ret, value

    def ZAux_BusCmd_InitBus(self):
        '''
        Description: ( Zmotion tools ).

        Return: . type:int32

        '''
        ret = zauxdll.ZAux_BusCmd_InitBus(self.handle)
        return ret

    def ZAux_BusCmd_GetInitStatus(self):
        '''
        Description: ( Zmotion tools ).

        Return: ,0- 1 . type:int32,int

        '''
        value = (ctypes.c_int)()
        ret = zauxdll.ZAux_BusCmd_GetInitStatus(
            self.handle, ctypes.byref(value))
        return ret, value

    def ZAux_Direct_GetInMulti(self, startio, endio):
        '''
        Description: .

        param startio:IO . type: int

        param endio:IO . type: int

        Return: , . 32 . type:int32,int32

        '''
        value = (ctypes.c_int)()
        ret = zauxdll.ZAux_Direct_GetInMulti(self.handle, ctypes.c_uint(startio), ctypes.c_uint(endio),
                                             ctypes.byref(value))
        return ret, value

    def ZAux_SetTimeOut(self, timems):
        '''
        Description: .

        param timems: MS. type: int

        Return: . type:int32

        '''
        ret = zauxdll.ZAux_SetTimeOut(self.handle, ctypes.c_uint(timems))
        return ret

    def ZAux_Direct_HwPswitch2(self, Axisnum, Mode, Opnum, Opstate, ModePara1, ModePara2, ModePara3, ModePara4):
        '''
        Description: 2 4 , 20170513 . ZMC306E\\306N .

        param Axisnum: . type: int

        param Mode: 1- . type: int
                         2- .
                         3- .
                         4- , .
                         5- , .
                         6- , , HW_TIMER

        param Opnum: .4 out 0- . type: int

        param Opstate: . 0- 1- . type: int

        param ModePara1: . type: float

        param ModePara2: . type: float

        param ModePara3: . type: float

        param ModePara4: . type: float

        Return: . type:int32

        '''
        ret = zauxdll.ZAux_Direct_HwPswitch2(self.handle, ctypes.c_int(Axisnum), ctypes.c_int(Mode),
                                             ctypes.c_int(Opnum), ctypes.c_int(
                                                 Opstate), ctypes.c_float(ModePara1),
                                             ctypes.c_float(
                                                 ModePara2), ctypes.c_float(ModePara3),
                                             ctypes.c_float(ModePara4))
        return ret

    def ZAux_Direct_SetOutMulti(self, iofirst, ioend, istate):
        '''
        Description:IO .

        param iofirst:IO . type: int

        param ioend:IO . type: int

        param istate:. ,istate , UNIT 32 ( ). type: int32

        Return: , . type:int32

        '''
        arry = (ctypes.c_uint32 * len(istate))(*istate)
        ret = zauxdll.ZAux_Direct_SetOutMulti(
            self.handle, ctypes.c_uint(iofirst), ctypes.c_int(ioend), arry)
        return ret

    def ZAux_Direct_GetOutMulti(self, iofirst, ioend):
        '''
        Description:IO .

        param iofirst:IO . type: int

        param ioend:IO . type: int

        Return: , . type:int32

        '''
        value = (ctypes.c_int)()
        ret = zauxdll.ZAux_Direct_GetOutMulti(self.handle, ctypes.c_uint(iofirst), ctypes.c_int(ioend),
                                              ctypes.byref(value))
        return ret, value

    def ZAux_Direct_MultiMove(self, iMoveLen, imaxaxises, piAxislist, pfDisancelist):
        '''
        Description: .

        param iMoveLen: . type: int

        param imaxaxises: . type: int

        param piAxislist: . type: int

        param pfDisancelist: . type: float

        Return: . type:int32

        '''
        value = (ctypes.c_int * len(piAxislist))(*piAxislist)
        b = (ctypes.c_float * len(pfDisancelist))(*pfDisancelist)
        ret = zauxdll.ZAux_Direct_MultiMove(
            self.handle, iMoveLen, imaxaxises, value, b)
        return ret

    def ZAux_Direct_MultiMoveAbs(self, iMoveLen, imaxaxises, piAxislist, pfDisancelist):
        '''
        Description: .

        param iMoveLen: . type: int

        param imaxaxises: . type: int

        param piAxislist: . type: int

        param pfDisancelist: . type: float

        Return: . type:int32

        '''
        value = (ctypes.c_int * len(piAxislist))(*piAxislist)
        b = (ctypes.c_float * len(pfDisancelist))(*pfDisancelist)
        ret = zauxdll.ZAux_Direct_MultiMoveAbs(
            self.handle, iMoveLen, imaxaxises, value, b)
        return ret

    def ZAux_Direct_MultiMovePt(self, iMoveLen, imaxaxises, piAxislist, pTickslist, pfDisancelist):
        '''
        Description: PT .

        param iMoveLen: . type: int

        param imaxaxises: . type: int

        param piAxislist: . type: int

        param piAxislist: . type: int

        param pfDisancelist: . type: float

        Return: . type:int32

        '''
        value = (ctypes.c_int * len(piAxislist))(*piAxislist)
        b = (ctypes.c_float * len(pfDisancelist))(*pfDisancelist)
        a = (ctypes.c_float * len(pTickslist))(*pTickslist)
        ret = zauxdll.ZAux_Direct_MultiMovePt(
            self.handle, iMoveLen, imaxaxises, value, a, b)
        return ret

    def ZAux_Direct_MultiMovePtAbs(self, iMoveLen, imaxaxises, piAxislist, pTickslist, pfDisancelist):
        '''
        Description: PT .

        param iMoveLen: . type: int

        param imaxaxises: . type: int

        param piAxislist: . type: int

        param piAxislist: . type: int

        param pfDisancelist: . type: float

        Return: . type:int32

        '''
        value = (ctypes.c_int * len(piAxislist))(*piAxislist)
        b = (ctypes.c_float * len(pfDisancelist))(*pfDisancelist)
        a = (ctypes.c_float * len(pTickslist))(*pTickslist)
        ret = zauxdll.ZAux_Direct_MultiMovePtAbs(
            self.handle, iMoveLen, imaxaxises, value, a, b)
        return ret

    def ZAux_ZarDown(self, Filename, run_mode):
        '''
        Description: ZAR .

        param Filename:BAS . type: sting

        param run_mode: 0-RAM 1-ROM. type: int32

        Return: . type:int32

        '''
        _str = Filename.encode('utf-8')
        ret = zauxdll.ZAux_ZarDown(self.handle, _str, ctypes.c_int32(run_mode))
        return ret

    def ZAux_SetRtcTime(self, RtcDate, RtcTime):
        '''
        Description: RTC .

        param RtcDate: YYMMDD. type: sting

        param RtcTime: HHMMSS. type: sting

        Return: . type:int32

        '''
        _STR = RtcDate.encode('utf-8')
        _STB = RtcTime.encode('utf-8')
        ret = zauxdll.ZAux_SetRtcTime(self.handle, _STR, _STB)
        return ret

    def ZAux_FastOpen(self, type, pconnectstring, uims):
        '''
        Description: , .

        param type: 1-COM 2-ETH 3- USB 4-PCI. type: int

        param pconnectstring: pconnectstring COM \\IP . type: sting

        param uims: uims. type:int

        Return: . type:int32

        '''
        ip_bytes = pconnectstring.encode('utf-8')
        ret = zauxdll.ZAux_FastOpen(
            type, ip_bytes, uims, ctypes.pointer(self.handle))
        return ret

    def ZAux_Direct_UserDatum(self, iaxis, imode, HighSpeed, LowSpeed, DatumOffset):
        '''
        Description: .

        param iaxis: . type: int

        param imode: . type: int

        param HighSpeed: . type:float

        param LowSpeed: . type:float

        param DatumOffset: . type:float

        Return: . type:int32

        '''
        ret = zauxdll.ZAux_Direct_UserDatum(self.handle, ctypes.c_int(iaxis), ctypes.c_int(imode),
                                            ctypes.c_float(
                                                HighSpeed), ctypes.c_float(LowSpeed),
                                            ctypes.c_float(DatumOffset))
        return ret

    def ZAux_Direct_Pitchset(self, iaxis, iEnable, StartPos, maxpoint, DisOne, TablNum, pfDisancelist):
        '''
        Description: , .

        param iaxis: . type: int

        param iEnable: . type: int

        param StartPos: MPOS . type:float

        param maxpoint: . type:uint32

        param DisOne: . type:float

        param TablNum: TABLE . type:uint32

        param pfDisancelist: . type:float

        Return: . type:int32

        '''
        value = (ctypes.c_int * len(pfDisancelist))(*pfDisancelist)
        ret = zauxdll.ZAux_Direct_Pitchset(self.handle, ctypes.c_int(iaxis), ctypes.c_int(iEnable),
                                           ctypes.c_float(StartPos), ctypes.c_int(
                                               maxpoint), ctypes.c_float(DisOne),
                                           ctypes.c_int(TablNum), value)
        return ret

    def ZAux_Direct_Pitchset2(self, iaxis, iEnable, StartPos, maxpoint, DisOne, TablNum, pfDisancelist, RevTablNum,
                              RevpfDisancelist):
        '''
        Description: , .

        param iaxis: . type: int

        param iEnable: . type: int

        param StartPos: MPOS . type:float

        param maxpoint: . type:uint32

        param DisOne: . type:float

        param TablNum: TABLE . type:uint32

        param pfDisancelist: . type:float

        param RevTablNum: TABLE . type:uint32

        param RevpfDisancelist: . type:float

        Return: . type:int32

        '''
        value = (ctypes.c_int * len(pfDisancelist))(*pfDisancelist)
        b = (ctypes.c_int * len(RevpfDisancelist))(*RevpfDisancelist)
        ret = zauxdll.ZAux_Dire

    #
    # itchset2(self.handle, ctypes.c_int(iaxis), ctypes.c_int(iEnable),
    #          ctypes.c_float(StartPos), ctypes.c_int(maxpoint), ctypes.c_float(DisOne),
    #          ctypes.c_int(TablNum), value, ctypes.c_int(RevTablNum), b)
    #     return ret

# ''''''


def ZAux_CycleUpEnable(self, cycleindex, fintervalms, psetesname):
    # '''
    # Description: .
    #
    # param cycleindex: , 0- -1. type: uint32
    #
    # param fintervalms: , ms , SERVO_PERIOD. type: int
    #
    # param psetesname: , : 1, 2(index), 3(index, numes). type:sting
    #
    # Return: . type:int32
    #
    # '''
    _str = psetesname.encode('utf-8')
    ret = zauxdll.ZAux_CycleUpEnable(self.handle, ctypes.c_int(
        cycleindex), ctypes.c_float(fintervalms), _str)
    return ret


def ZAux_CycleUpDisable(self, cycleindex):
    # '''
    # Description: .
    #
    # param cycleindex: , 0- -1. type: uint32
    #
    # Return: . type:int32
    #
    # '''

    ret = zauxdll.ZAux_CycleUpDisable(self.handle, ctypes.c_int(cycleindex))
    return ret


def ZAux_CycleUpGetRecvTimes(self, cycleindex):
    '''
    Description: , . .

    param cycleindex: , 0- -1. type: uint32

    Return: . type:int32

    '''

    ret = zauxdll.ZAux_CycleUpGetRecvTimes(
        self.handle, ctypes.c_int(cycleindex))
    return ret


def ZAux_CycleUpForceOnce(self, cycleindex):
    '''
    Description: , idle ..

    param cycleindex: , 0- -1. type: uint32

    Return: . type:int32

    '''
    ret = zauxdll.ZAux_CycleUpGetRecvTimes(
        self.handle, ctypes.c_int(cycleindex))
    return ret


def ZAux_CycleUpReadBuff(self, cycleindex, psetname, isetindex):
    '''
    Description: ..

    param cycleindex: -1, cycle . type: uint32

    param psetname: . type:string

    param isetindex: . type: uint32

    Return: , . type:int32,double

    '''
    _str = psetname.encode('utf-8')
    value = (ctypes.c_double)()
    ret = zauxdll.ZAux_CycleUpReadBuff(self.handle, ctypes.c_int32(cycleindex), _str, ctypes.c_int32(isetindex),
                                       ctypes.byref(value))
    return ret, value


def ZAux_CycleUpReadBuffInt(self, cycleindex, psetname, isetindex):
    '''
    Description: .

    param cycleindex: -1, cycle . type: uint32

    param psetname: . type:string

    param isetindex: . type: uint32

    Return: , . type:int32,int32

    '''
    _str = psetname.encode('utf-8')
    value = (ctypes.c_int32)()
    ret = zauxdll.ZAux_CycleUpReadBuffInt(self.handle, ctypes.c_int32(cycleindex), _str, ctypes.c_int32(isetindex),
                                          ctypes.byref(value))
    return ret, value


def ZAux_Direct_MultiLineN(self, imode, iMoveLen, imaxaxises, piAxislist, pfDisancelist):
    '''
    Description: .

    :param imode:bit0- bifabs
                 bit1- bifsp
                 bit2- bifresume
                 bit3- bifmovescan . type: int

    param iMoveLen: . type: int

    param imaxaxises: . type:int

    param piAxislist: . type:uint32

    param pfDisancelist: iMoveLen * imaxaxises. type:float

    Return: , . type:int32,int

    '''
    a = (ctypes.c_int * len(piAxislist))(*piAxislist)
    b = (ctypes.c_int * len(pfDisancelist))(*pfDisancelist)
    ret = zauxdll.ZAux_Direct_MultiLineN(self.handle, ctypes.c_int(imode), ctypes.c_int(iMoveLen),
                                         ctypes.c_int(imaxaxises), a, b)
    return ret


def ZAux_Direct_MoveSync(self, imode, synctime, syncposition, syncaxis, imaxaxises, piAxislist, pfDisancelist):
    '''
    Description: .

    param imode: -1 -2 0- 10- 20- -angle: type: float

    param synctime: . type: int

    param syncposition: ,ms , , BASE .0 , . type:int

    param syncaxis: . type:uint32

    param imaxaxises: . type:int

    param piAxislist: . type:int

    param pfDisancelist: . type:float

    Return: . type:int32

    '''
    a = (ctypes.c_int * len(piAxislist))(*piAxislist)
    b = (ctypes.c_int * len(pfDisancelist))(*pfDisancelist)
    ret = zauxdll.ZAux_Direct_MoveSync(self.handle, ctypes.c_int(imode), ctypes.c_int(synctime),
                                       ctypes.c_int(syncposition), ctypes.c_int(
                                           syncaxis), ctypes.c_int(imaxaxises),
                                       a, b)
    return ret


def ZAux_Direct_MoveCancel(self, base_axis, Cancel_Axis, iMode):
    '''
    Description: , .

    param base_axis: . type: int32

    param Cancel_Axis: . type: int32

    param iMode: . type:int
                0
                1
                2
                3

    Return: . type:int32

    '''
    ret = zauxdll.ZAux_Direct_MoveCancel(self.handle, ctypes.c_int(base_axis), ctypes.c_int(Cancel_Axis),
                                         ctypes.c_int(iMode))
    return ret


def ZAux_Direct_CycleRegist(self, iaxis, imode, iTabStart, iTabNum):
    '''
    Description: .

    param iaxis: . type: int

    param imode: . type: int

    param iTabStart: table , table , , = numes-1, . type:int

    param iTabNum: table . type:int

    Return: . type:int32

    '''
    ret = zauxdll.ZAux_Direct_CycleRegist(self.handle, ctypes.c_int(iaxis), ctypes.c_int(imode),
                                          ctypes.c_int(iTabStart), ctypes.c_int(iTabNum))
    return ret


def ZAux_BusCmd_NodePdoWrite(self, inode, index, subindex, type, vvalue):
    '''
    Description:Pdo .

    param inode: . type: int32

    param index: . type: int32

    param subindex: . type:uint32

    param type: . type:uint32

    param vvalue: . type:int

    Return: . type:int32

    '''
    ret = zauxdll.ZAux_BusCmd_NodePdoWrite(self.handle, ctypes.c_int(inode), ctypes.c_int(index),
                                           ctypes.c_int(subindex), ctypes.c_int(type), ctypes.c_int(vvalue))
    return ret


def ZAux_BusCmd_NodePdoRead(self, inode, index, subindex, type):
    '''
    Description:Pdo .

    param inode: . type: int32

    param index: . type: int32

    param subindex: . type:uint32

    param type: . type:uint32

    param vvalue: . type:int

    Return: , . type:int32,int

    '''
    value = (ctypes.c_int)()
    ret = zauxdll.ZAux_BusCmd_NodePdoRead(self.handle, ctypes.c_int(inode), ctypes.c_int(index),
                                          ctypes.c_int(subindex), ctypes.c_int(type), ctypes.byref(value))
    return ret, value

# #
#
# Czauxdll=ZAUXDLL()
# Czauxdll.ZAux_OpenEth("192.0.2.22")


# ret=Czauxdll.ZAux_Modbus_Set0x(20000,4,[15])

# print(ret)


#
#


# for vr in ip:


#     print(vr)
