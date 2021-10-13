import json
import re
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from sys import exit, argv
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QDialog, QApplication, QFileDialog
from PyQt5.uic import loadUi
from PyQt5.QtCore import QTimer, Qt, QThread
from PyQt5.QtGui import QFontDatabase, QFont


# Загрузка сохранённых настроек
def load_settings():
    with open(settings_path, 'r') as conf:
        settings = json.load(conf)
        return settings


settings_path = os.path.abspath('config.json')
settings = load_settings()

# Выставление дефолтных значений если настройки невалидны
if not os.path.isdir(settings['logs_path']):
    with open(settings_path, 'w') as f:
        settings['logs_path'] = "C:/"
        json.dump(settings, f, ensure_ascii=False, indent=4)



class MyHandler(FileSystemEventHandler):
    # Класс следит за созданием лога маркета и вынимает нужную инфу

    def on_created(self, event):
        with open(event.src_path, 'r') as f:
            lines = f.readlines()
            sell_price = float(lines[1].split(',')[0])
            sell_broker = (sell_price / 100) * float(settings['broker_tax'])
            sell_tax = (sell_price / 100) * float(settings['sell_tax'])
            sell = sell_price - sell_tax - sell_broker

            for i in lines:
                if re.search(r'\bTrue\b', i):
                    buy_price = float(i.split(',')[0])
                    buy_broker = (buy_price / 100) * float(settings['broker_tax'])
                    buy = buy_price + buy_broker
                    profit = sell - buy
                    mainWindow.set_values(sell, buy, profit)
                    break


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()
        loadUi('eve_profit_helper_mainWindow.ui', self)
        self.settings_btn.clicked.connect(SettingsWindow.show_window)

    def set_values(self, sell, buy, profit):
        self.sell_price_value.setText(f'{sell:,.2f}'.replace(',', ' '))
        self.buy_price_value.setText(f'{buy:,.2f}'.replace(',', ' '))
        self.profit_value.setText(f'{profit:,.2f}'.replace(',', ' '))
        if profit < 0:
            self.profit_value.setStyleSheet('color: #cc0000')
        else:
            self.profit_value.setStyleSheet('color: #008000')

    def on_error(self, msg):
        self.on_error.setText(msg)


class SettingsWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super(SettingsWindow, self).__init__()
        loadUi('eve_profit_helper_settings.ui', self)
        self.save_and_exit_btn.clicked.connect(self.save_and_exit)
        self.market_logs_btn.clicked.connect(self.find_logs_path)
        self.sell_tax_value.setValue(settings['sell_tax'])
        self.broker_tax_value.setValue(settings['broker_tax'])
        self.on_top_checkBox.setChecked(bool(settings['always_on_top']))
        self.market_logs_path.setText(settings['logs_path'])
        self.opacity_slider.setRange(10, 100)
        self.opacity_slider.setValue(int(settings['opacity'] * 100))
        self.opacity_slider.valueChanged[int].connect(self.set_opacity)

    def show_window(self):
        settingsWindow_widget.show()
        mainWindow_widget.hide()

    def find_logs_path(self):
        folder_path = QFileDialog.getExistingDirectory()
        self.market_logs_path.setText(folder_path)
        with open(settings_path, 'r') as f:
            data = json.load(f)
        data['logs_path'] = folder_path
        with open(settings_path, 'w') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    
    def set_opacity(self):
        mainWindow_widget.setWindowOpacity(float(self.opacity_slider.value() / 100))
        settingsWindow_widget.setWindowOpacity(float(self.opacity_slider.value() / 100))

    def save_and_exit(self):
        with open(settings_path, 'r') as f:
            data = json.load(f)
        data['broker_tax'] = self.broker_tax_value.value()
        data['sell_tax'] = self.sell_tax_value.value()
        data['always_on_top'] = self.on_top_checkBox.isChecked()
        data['opacity'] = float(self.opacity_slider.value() / 100)

        with open(settings_path, 'w') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

        settingsWindow_widget.hide()
        mainWindow_widget.show()


class Warden(QThread):
    # Отдельный поток который следит за логами маркета
    def __init__(self, parent=None):
        super(Warden, self).__init__(parent)

    def run(self):
        event_handler = MyHandler()
        observer = Observer()
        observer.schedule(event_handler, settings["logs_path"], recursive=False)
        observer.start()



app = QtWidgets.QApplication(argv)

# Создаём главное окно и окно настроек
mainWindow = MainWindow()
mainWindow_widget = QtWidgets.QStackedWidget()
mainWindow_widget.addWidget(mainWindow)

settingsWindow = SettingsWindow()
settingsWindow_widget = QtWidgets.QStackedWidget()
settingsWindow_widget.addWidget(settingsWindow)

# Вешаем на окна нужные нам флаги
mainWindow_widget.setWindowOpacity(settings['opacity'])
settingsWindow_widget.setWindowOpacity(settings['opacity'])
if settings['always_on_top']:
    mainWindow_widget.setWindowFlag(Qt.WindowStaysOnTopHint)
    settingsWindow_widget.setWindowFlag(Qt.WindowStaysOnTopHint)

mainWindow_widget.show()



# event_handler = MyHandler()
# observer = Observer()
# observer.schedule(event_handler, settings["logs_path"], recursive=False)
#
#
# observer.start()
warden = Warden()
warden.start()
exit(app.exec_())
