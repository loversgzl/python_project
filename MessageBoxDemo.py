import sys
import time

from PyQt5.QtWidgets import QApplication, QMessageBox, QPushButton, QVBoxLayout, QWidget
from PyQt5.QtCore import QTimer
import threading

class MainWindow(QWidget):
    def show_notification(self, text):
        # 显示通知
        self.notification_box = QMessageBox(self)
        self.notification_box.setWindowTitle("Notification")
        self.notification_box.setIcon(QMessageBox.Information)
        self.notification_box.setText(text)
        self.notification_box.show()
class ThreadBox:
    def createThread(self):
        print("弹窗")
        text = "文本文本文本文本文本文本"
        thread = threading.Thread(target=self.showBox, args=(text,))
        thread.start()

        for i in range(5):
            print("进行其它活动，模拟运行三秒")
            time.sleep(3)
    def showBox(self, text):
        app = QApplication(sys.argv)
        window = MainWindow()
        window.show_notification(text)
        sys.exit(app.exec_())

if __name__ == "__main__":
    ThreadBox = ThreadBox()
    for i in range(10):
        ThreadBox.createThread()
