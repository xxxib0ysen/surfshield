from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QSizePolicy, QApplication, QMessageBox

from client.config.logger import logger


def get_dpi_scale():
    screen = QApplication.primaryScreen()
    dpi = screen.logicalDotsPerInch()
    return dpi / 96.0  # 96dpi 是标准

class InviteCodeDialog(QDialog):
    def __init__(self):
        super().__init__()

        # 基础属性
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.Dialog)
        self.setWindowModality(Qt.ApplicationModal)
        self.setWindowTitle("填写邀请码")
        self.dpi_scale = get_dpi_scale()

        # 根据 DPI 缩放窗口大小
        base_width = 300
        base_height = 150
        self.setFixedSize(int(base_width * self.dpi_scale), int(base_height * self.dpi_scale))

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(int(10 * self.dpi_scale))

        # 标签
        self.label = QLabel("请输入组织邀请码：")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet(f"font-size: {int(14 * self.dpi_scale)}px; font-weight: bold;")
        layout.addWidget(self.label)

        # 输入框
        self.input = QLineEdit()
        self.input.setPlaceholderText("由管理员提供")
        self.input.setStyleSheet(f"font-size: {int(13 * self.dpi_scale)}px;")
        self.input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        layout.addWidget(self.input)

        # 按钮
        self.btn_ok = QPushButton("确定")
        self.btn_cancel = QPushButton("取消")

        btn_height = int(30 * self.dpi_scale)
        self.btn_ok.setFixedHeight(btn_height)
        self.btn_cancel.setFixedHeight(btn_height)

        layout.addWidget(self.btn_ok)
        layout.addWidget(self.btn_cancel)

        self.setLayout(layout)

        # 信号连接
        self.btn_ok.clicked.connect(self.on_ok_clicked)
        self.btn_cancel.clicked.connect(self.reject)

        self.input.returnPressed.connect(self.on_ok_clicked)

        # 启动后焦点自动在输入框
        self.input.setFocus()

    def on_ok_clicked(self):
        from client.agent.terminal.register import register_terminal, set_terminal_id
        group_code = self.input.text().strip()
        if not group_code:
            show_error_message("请输入邀请码后再提交！")
            return

        try:
            terminal_id = register_terminal(group_code)
            if terminal_id:
                set_terminal_id(terminal_id)
                show_success_message("终端注册成功！")
                self.accept()
            else:
                show_error_message("注册失败，请检查邀请码或网络连接")
        except Exception as e:
            logger.error(f"[注册异常] {e}")
            show_error_message("注册失败，请检查网络或联系管理员！")

def show_error_message(message: str):
    box = QMessageBox()
    box.setWindowFlags(Qt.WindowStaysOnTopHint)
    box.setWindowTitle("错误")
    box.setIcon(QMessageBox.Critical)
    box.setText(message)
    box.setStandardButtons(QMessageBox.Ok)
    box.exec_()

def show_success_message(message: str):
    box = QMessageBox()
    box.setWindowFlags(Qt.WindowStaysOnTopHint)
    box.setWindowTitle("成功")
    box.setIcon(QMessageBox.Information)
    box.setText(message)
    box.setStandardButtons(QMessageBox.Ok)
    box.exec_()
