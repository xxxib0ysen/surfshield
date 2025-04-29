from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QProgressBar
from PyQt5.QtCore import Qt

class SplashWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setFixedSize(400, 300)
        self.setStyleSheet("background-color: white;")

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        self.label_title = QLabel("正在启动...")
        self.label_title.setAlignment(Qt.AlignCenter)
        self.label_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #333;")

        self.label_step = QLabel("初始化中...")
        self.label_step.setAlignment(Qt.AlignCenter)
        self.label_step.setStyleSheet("font-size: 14px; color: #666;")

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid grey;
                border-radius: 5px;
                background-color: #f0f0f0;
            }
            QProgressBar::chunk {
                background-color: #0078D7;
                width: 20px;
            }
        """)

        layout.addStretch()
        layout.addWidget(self.label_title)
        layout.addStretch()
        layout.addWidget(self.label_step)
        layout.addWidget(self.progress_bar)

        self.setLayout(layout)

    def set_progress(self, value: int, text: str):
        self.progress_bar.setValue(value)
        self.label_step.setText(text)

    def finish(self):
        self.close()