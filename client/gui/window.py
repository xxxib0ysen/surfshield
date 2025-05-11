import os
import sys
import webbrowser
from PyQt5.QtWidgets import (
    QWidget, QLabel, QPushButton, QHBoxLayout, QVBoxLayout,
    QFrame, QGridLayout, QSizePolicy
)
from PyQt5.QtCore import Qt
from client.config import config
from client.gui.info import bind_terminal_info, bind_runtime_info
from client.gui.intercept_info import bind_intercept_info


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        # 窗口标题与尺寸
        self.setWindowTitle("上网行为管控")
        self.resize(800, 600)
        self.setMinimumSize(600, 400)

        # 初始化界面布局
        self.init_ui()

        # 绑定信息
        bind_terminal_info(self)
        bind_runtime_info(self)
        bind_intercept_info(self)

    # 初始化所有界面元素
    def init_ui(self):
        main_layout = QVBoxLayout(self)

        # 顶部信息栏
        top_grid = QGridLayout()
        self.label_terminal_id = QLabel("终端ID:")
        self.label_username = QLabel("用户名:")
        self.label_ip = QLabel("IP:")
        for i, label in enumerate([self.label_terminal_id, self.label_username, self.label_ip]):
            top_grid.addWidget(label, 0, i)
            label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        # 顶部提示
        prompt_label = QLabel("正在后台运行... 工作时间请勿关闭")
        prompt_label.setAlignment(Qt.AlignCenter)
        prompt_label.setStyleSheet(f"font-weight: bold; font-size: 16px; margin: 5px;")

        # 中间主体区域
        middle_layout = QHBoxLayout()

        # 左栏 - 模块状态
        left_layout = QVBoxLayout()
        self.label_web_block = QLabel("网站拦截启动中")
        self.label_process_block = QLabel("进程拦截启动中")
        self.label_behavior_block = QLabel("实时管控启动中")
        for label in [self.label_web_block, self.label_process_block, self.label_behavior_block]:
            label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
            left_layout.addWidget(label)
        left_layout.addStretch()

        # 中栏 - 拦截统计与规则
        center_layout = QVBoxLayout()
        self.label_today_block = QLabel("今日拦截次数：0")
        self.label_total_block = QLabel("总共拦截次数：0")
        self.label_web_rule = QLabel("网站规则：0条，最后同步：--")
        self.label_process_rule = QLabel("进程规则：0条，最后同步：--")
        for label in [self.label_today_block, self.label_total_block, self.label_web_rule, self.label_process_rule]:
            label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
            center_layout.addWidget(label)
        center_layout.addStretch()

        # 右栏 - 版本信息
        right_layout = QVBoxLayout()
        version_title = QLabel("[版本信息]")
        self.label_version = QLabel(f"客户端版本号：{config.version}")
        self.label_run_days = QLabel("运行天数：--天")
        for label in [version_title, self.label_version, self.label_run_days]:
            label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
            right_layout.addWidget(label)
        right_layout.addStretch()

        # 分割线
        split1 = QFrame()
        split1.setFrameShape(QFrame.VLine)
        split1.setFrameShadow(QFrame.Sunken)
        split2 = QFrame()
        split2.setFrameShape(QFrame.VLine)
        split2.setFrameShadow(QFrame.Sunken)

        middle_layout.addLayout(left_layout, 1)
        middle_layout.addWidget(split1)
        middle_layout.addLayout(center_layout, 2)
        middle_layout.addWidget(split2)
        middle_layout.addLayout(right_layout, 1)

        # 按钮栏
        button_layout = QHBoxLayout()
        self.btn_check_update = QPushButton("检查更新")
        self.btn_open_logs = QPushButton("打开日志目录")
        self.btn_open_platform = QPushButton("打开管理平台")
        for btn in [self.btn_check_update, self.btn_open_logs, self.btn_open_platform]:
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        button_layout.addStretch()
        button_layout.addWidget(self.btn_check_update)
        button_layout.addWidget(self.btn_open_logs)
        button_layout.addWidget(self.btn_open_platform)
        button_layout.addStretch()

        self.btn_check_update.clicked.connect(self.check_update)
        self.btn_open_logs.clicked.connect(self.open_logs_dir)
        self.btn_open_platform.clicked.connect(self.open_platform_url)

        # 底部状态栏
        bottom_layout = QHBoxLayout()
        self.label_time = QLabel("当前时间：--")
        self.label_redis_status = QLabel("redis连接：检测中...")
        self.label_server_status = QLabel("服务器连接：检测中...")
        bottom_layout.addWidget(self.label_time)
        bottom_layout.addStretch()
        bottom_layout.addWidget(QLabel("Redis连接："))
        bottom_layout.addWidget(self.label_redis_status)
        bottom_layout.addSpacing(20)
        bottom_layout.addWidget(QLabel("服务器连接："))
        bottom_layout.addWidget(self.label_server_status)

        # 组装主布局
        main_layout.addLayout(top_grid)
        main_layout.addSpacing(10)
        main_layout.addWidget(prompt_label)
        main_layout.addSpacing(10)
        main_layout.addLayout(middle_layout)
        main_layout.addSpacing(20)
        main_layout.addLayout(button_layout)
        main_layout.addSpacing(10)
        main_layout.addLayout(bottom_layout)

    # 打开日志目录
    def get_log_dir(self):
        if getattr(sys, 'frozen', False):  # 如果是打包后的 exe 运行
            base_path = os.path.dirname(sys.executable)
        else:
            base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))

        log_dir = os.path.join(base_path, "logs")
        return log_dir

    def open_logs_dir(self):
        try:
            path = self.get_log_dir()
            if not os.path.exists(path):
                os.makedirs(path)
            os.startfile(path)
        except Exception as e:
            print(f"打开日志目录失败: {e}")

    # 打开管理平台
    def open_platform_url(self):
        try:
            webbrowser.open(config.server_url)
        except Exception as e:
            print(f"打开平台失败: {e}")


    # 检查更新（预留）
    def check_update(self):
        pass
