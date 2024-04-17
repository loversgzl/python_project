import sys
from PyQt5.QtWidgets import QApplication, QDialog, QVBoxLayout, QPushButton

class NotificationDialog(QDialog):
    def __init__(self, notification_count):
        super().__init__()

        self.setWindowTitle(f"Notification {notification_count}")
        self.setGeometry(100, 100, 300, 100)

        # 创建关闭按钮
        self.close_button = QPushButton("Close", self)
        self.close_button.clicked.connect(self.accept)

        # 创建布局
        layout = QVBoxLayout(self)
        layout.addWidget(self.close_button)

class MainWindow(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Multiple Independent Dialogs")
        self.setGeometry(100, 100, 400, 200)

        # 创建按钮用于触发通知
        self.button = QPushButton("Show Dialog", self)
        self.button.clicked.connect(self.show_notification_dialog)

        # 创建布局
        layout = QVBoxLayout(self)
        layout.addWidget(self.button)

        # 用于记录弹窗的数量
        self.notification_count = 0

    def show_notification_dialog(self):
        # 增加弹窗数量
        self.notification_count += 1

        # 创建并显示通知弹窗
        notification_dialog = NotificationDialog(self.notification_count)
        notification_dialog.exec_()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
