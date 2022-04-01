import sys
from PyQt5 import QtWidgets
import design
import requests
from PyQt5.QtCore import QTimer

class Client(QtWidgets.QMainWindow, design.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_message)
        self.timer.start(5000)
        self.setupUi(self)
        self.send.clicked.connect(self.send_message)
        
    def send_message(self):
        requests.post('http://localhost:5000/api/send_message/', data={'email': 'test@example.com', 'password': '123', 'chat_id': 1, 'message': self.message.text()})
        
    def update_message(self):
        data = requests.post('http://localhost:5000/api/chat_messages/', data={'email': 'test@example.com', 'password': '123', 'chat_id': 1}).json()
        data = data['data']['messages']
        print(data)
        self.textEdit.setText(data[-1][0])
        
def main():
    app = QtWidgets.QApplication(sys.argv)
    window = Client()
    window.show()
    app.exec_()
    
if __name__ == '__main__':
    main()