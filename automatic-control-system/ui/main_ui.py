import os
import sys
from datetime import datetime

import pandas as pd
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QFileDialog, QMainWindow

from client.master_control_client import MasterControlClient
from client.station_info import station_info
from ui.controllers.info_presenter import build_station_info_sections
from ui.controllers.task_selection import (
    STEP_LABELS,
    SelectionState,
    describe_selection,
)
from ui.info_window import Ui_Form
from ui.main_window import Ui_MainWindow
from ui.tcp_window import Ui_TCPSettings
from utils.task_utils import (
    calc_liquid_comsumption,
    calc_solid_comsumption,
    split_task,
)


ui_path = os.path.dirname(os.path.abspath(__file__))


class TCPWindow(QMainWindow, Ui_TCPSettings):
    def __init__(self, station_name, socket_info):
        super().__init__()
        self.setupUi(self)
        self.update_window(station_name, socket_info)
        self.confirm.clicked.connect(self.submit)
        self.cancel.clicked.connect(self.close)

    def submit(self):
        """Close the TCP settings window after confirmation."""
        self.close()

    def update_window(self, station_name, socket_info):
        """Refresh the displayed station name, IP address, and port."""
        self.setWindowTitle(station_name)
        ip_addr, port = socket_info
        ip_list = ip_addr.split(".")
        self.i1.setText(ip_list[0])
        self.i2.setText(ip_list[1])
        self.i3.setText(ip_list[2])
        self.i4.setText(ip_list[3])
        self.port.setText(str(port))


class InfoWindow(QMainWindow, Ui_Form):
    def __init__(self, station_info):
        super().__init__()
        self.setupUi(self)
        self.update_window(station_info)

    def update_window(self, station_info):
        """Populate the station information view from the current status snapshot."""
        sections = build_station_info_sections(station_info)

        if "liquid_station" in sections:
            self.l1.setPlainText(sections["liquid_station"][0])
            self.l2.setPlainText(sections["liquid_station"][1])
            self.l3.setPlainText(sections["liquid_station"][2])
            self.l4.setPlainText(sections["liquid_station"][3])
        if "solid_station" in sections:
            self.s1.setPlainText(sections["solid_station"][0])
            self.s2.setPlainText(sections["solid_station"][1])
            self.s3.setPlainText(sections["solid_station"][2])
        if "reactor_station" in sections:
            self.rs1.setPlainText(sections["reactor_station"][0])
            self.rs2.setPlainText(sections["reactor_station"][1])
        if "rack_info" in sections:
            self.r1.setPlainText(sections["rack_info"][0])
            self.r2.setPlainText(sections["rack_info"][1])
            self.r3.setPlainText(sections["rack_info"][2])
            self.r4.setPlainText(sections["rack_info"][3])
        if "mobile_station" in sections:
            self.m1.setPlainText(sections["mobile_station"][0])
            self.m2.setPlainText(sections["mobile_station"][1])
            self.m3.setPlainText(sections["mobile_station"][2])
        if "peptide_station" in sections:
            self.p1.setPlainText(sections["peptide_station"][0])
            self.p2.setPlainText(sections["peptide_station"][1])


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.master_control_client = MasterControlClient()
        self.pre.stateChanged.connect(self.update_pre)
        self.post.stateChanged.connect(self.update_post)
        self.t1.clicked.connect(self.open_tcp_settings)
        self.t2.clicked.connect(self.open_tcp_settings)
        self.t3.clicked.connect(self.open_tcp_settings)
        self.t4.clicked.connect(self.open_tcp_settings)
        self.t5.clicked.connect(self.open_tcp_settings)
        self.s1.clicked.connect(self.open_info_window)
        self.s2.clicked.connect(self.open_info_window)
        self.s3.clicked.connect(self.open_info_window)
        self.s4.clicked.connect(self.open_info_window)
        self.s5.clicked.connect(self.open_info_window)
        self.stop1.clicked.connect(self.stop_solid)
        self.stop2.clicked.connect(self.stop_liquid)
        self.stop3.clicked.connect(self.stop_mobile)
        self.stop4.clicked.connect(self.stop_peptide)
        self.stop5.clicked.connect(self.stop_reactor)
        self.start.clicked.connect(self.toggle)
        self.emergency.clicked.connect(self.e_stop)
        self.file.clicked.connect(self.open_file)
        self.tcp_settings_window = None
        self.info_window = None
        self.child_windows = []
        self.is_load_file = False
        self.is_task_started = False

    def closeEvent(self, event):
        """Close all child windows before exiting the main window."""
        for window in self.child_windows:
            window.close()
        event.accept()

    def hide_frame(self):
        self.h11.hide()
        self.h12.hide()
        self.h21.hide()
        self.h22.hide()
        self.h31.hide()
        self.h32.hide()
        self.h41.hide()
        self.r11.hide()
        self.r12.hide()
        self.r21.hide()
        self.r22.hide()

    def update_pre(self):
        """Mirror the pre-reaction group state to the linked step checkboxes."""
        state = self.pre.isChecked()
        for checkbox in [self.c6, self.c7, self.c8, self.c9]:
            checkbox.setChecked(state)
        if state:
            if not self.post.isChecked():
                self.c1.setChecked(False)
                self.c2.setChecked(False)
                self.c3.setChecked(False)
                self.c4.setChecked(False)
                self.c5.setChecked(False)
                self.c10.setChecked(False)
                self.c11.setChecked(False)
                self.c12.setChecked(False)

            self.c1.setEnabled(False)
            self.c2.setEnabled(False)
            self.c3.setEnabled(False)
            self.c4.setEnabled(False)
            self.c5.setEnabled(False)
            self.c6.setEnabled(False)
            self.c7.setEnabled(False)
            self.c8.setEnabled(False)
            self.c9.setEnabled(False)
            self.c10.setEnabled(False)
            self.c11.setEnabled(False)
            self.c12.setEnabled(False)
        else:
            if not self.post.isChecked():
                self.c1.setEnabled(True)
                self.c2.setEnabled(True)
                self.c3.setEnabled(True)
                self.c4.setEnabled(True)
                self.c5.setEnabled(True)
                self.c6.setEnabled(True)
                self.c7.setEnabled(True)
                self.c8.setEnabled(True)
                self.c9.setEnabled(True)
                self.c10.setEnabled(True)
                self.c11.setEnabled(True)
                self.c12.setEnabled(True)

    def update_post(self):
        """Mirror the post-reaction group state to the linked step checkboxes."""
        state = self.post.isChecked()
        self.c1.setChecked(state)
        self.c2.setChecked(state)
        self.c3.setChecked(state)
        self.c4.setChecked(state)
        self.c5.setChecked(state)
        self.c10.setChecked(state)
        self.c11.setChecked(state)
        self.c12.setChecked(state)
        if not self.pre.isChecked():
            self.c6.setChecked(False)
            self.c7.setChecked(False)
            self.c8.setChecked(False)
            self.c9.setChecked(False)
        if state:
            self.c1.setEnabled(False)
            self.c2.setEnabled(False)
            self.c3.setEnabled(False)
            self.c4.setEnabled(False)
            self.c5.setEnabled(False)
            self.c6.setEnabled(False)
            self.c7.setEnabled(False)
            self.c8.setEnabled(False)
            self.c9.setEnabled(False)
            self.c10.setEnabled(False)
            self.c11.setEnabled(False)
            self.c12.setEnabled(False)
        else:
            if not self.pre.isChecked():
                self.c1.setEnabled(True)
                self.c2.setEnabled(True)
                self.c3.setEnabled(True)
                self.c4.setEnabled(True)
                self.c5.setEnabled(True)
                self.c6.setEnabled(True)
                self.c7.setEnabled(True)
                self.c8.setEnabled(True)
                self.c9.setEnabled(True)
                self.c10.setEnabled(True)
                self.c11.setEnabled(True)
                self.c12.setEnabled(True)

    def open_tcp_settings(self):
        """Open the TCP settings window for the clicked station."""
        button = self.sender()
        if button == self.t1:
            sock_info = station_info["solid_station"]
            station_name = "Solid Station"
        elif button == self.t2:
            sock_info = station_info["liquid_station"]
            station_name = "Liquid Station"
        elif button == self.t3:
            sock_info = station_info["mobile_robot"]
            station_name = "Mobile Station"
        elif button == self.t4:
            sock_info = station_info["reactor_station"]
            station_name = "Reactor Station"
        elif button == self.t5:
            sock_info = station_info["peptide_station"]
            station_name = "Peptide Station"
        if self.tcp_settings_window is None:
            self.tcp_settings_window = TCPWindow(station_name, sock_info)
            self.child_windows.append(self.tcp_settings_window)
        else:
            self.tcp_settings_window.update_window(station_name, sock_info)
        self.tcp_settings_window.show()

    def open_info_window(self):
        """Open the station information window."""
        station_status = self.master_control_client.init_status()
        if self.info_window is None:
            self.info_window = InfoWindow(station_status)
            self.child_windows.append(self.info_window)
        else:
            self.info_window.update_window(station_status)
        self.info_window.show()

    def format_message(self, message):
        """Apply the dashboard timestamp format to a status message."""
        now = datetime.now()
        timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
        message = f"{timestamp} -> {message}"
        return message

    def append_status(self, message: str) -> None:
        """Append a formatted status line to the details panel."""
        self.details.appendPlainText(self.format_message(message))

    def _step_state(self) -> dict[str, bool]:
        """Return the current manual-step checkbox state."""
        return {
            "c1": self.c1.isChecked(),
            "c2": self.c2.isChecked(),
            "c3": self.c3.isChecked(),
            "c4": self.c4.isChecked(),
            "c5": self.c5.isChecked(),
            "c6": self.c6.isChecked(),
            "c7": self.c7.isChecked(),
            "c8": self.c8.isChecked(),
            "c9": self.c9.isChecked(),
            "c10": self.c10.isChecked(),
            "c11": self.c11.isChecked(),
            "c12": self.c12.isChecked(),
        }

    def toggle(self):
        """Toggle between starting and stopping the task."""
        if self.is_task_started:
            self.stop_task()
        else:
            self.start_task()

    def e_stop(self):
        """Log emergency-stop interaction in the details panel."""
        if self.is_task_started:
            self.append_status("Emergency stop button pressed")
        else:
            self.append_status("No task is currently running")

    def start_task(self):
        """Start the selected task workflow."""
        selection = describe_selection(
            SelectionState(
                is_file_loaded=self.is_load_file,
                pre_selected=self.pre.isChecked(),
                post_selected=self.post.isChecked(),
                steps=self._step_state(),
            )
        )
        self.append_status(selection.message)
        if not selection.is_valid:
            return
        self.is_task_started = True
        self.start.setText("Pause Task")
        self.start.setIcon(QIcon(os.path.join(ui_path, "icon/pause.png")))

    def stop_task(self):
        """Stop the running task workflow."""
        self.is_task_started = False
        self.start.setText("Start Task")
        self.start.setIcon(QIcon(os.path.join(ui_path, "icon/running.png")))
        self.append_status("Task stopped")

    def stop_liquid(self):
        self.append_status("Liquid station emergency stop button was pressed")

    def stop_solid(self):
        self.append_status("Solid station emergency stop button was pressed")

    def stop_mobile(self):
        self.append_status("Mobile station emergency stop button was pressed")

    def stop_peptide(self):
        self.append_status("Peptide station emergency stop button was pressed")

    def stop_reactor(self):
        self.append_status("Reactor station emergency stop button was pressed")

    def task_details(self, task_df):
        task_num = len(task_df)

    def open_file(self):
        """Prompt the user for a task spreadsheet and summarize it in the UI."""
        file_path, _ = QFileDialog.getOpenFileName(self, "Select file")
        if file_path.endswith(".xlsx"):
            self.append_status(f"Task file: {file_path}")
            task_file_name = os.path.basename(file_path)
            self.task.appendPlainText(f"Task file name:\n{task_file_name}")
            self.task_df = pd.read_excel(file_path)
            solid_task_df, liquid_task_df = split_task(file_path)
            liquid_consumption = calc_liquid_comsumption(liquid_task_df)
            solid_consumption = calc_solid_comsumption(solid_task_df)
            self.task.appendPlainText(f"Number of tasks:\n{len(self.task_df)} pcs")
            self.task.appendPlainText(
                f"Liquid consumption summary:\n{liquid_consumption}"
            )
            self.task.appendPlainText(
                f"Solid consumption summary:\n{solid_consumption}"
            )
            self.is_load_file = True
        else:
            self.append_status(
                "Please select a valid task file, for example: tasks.xlsx"
            )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
