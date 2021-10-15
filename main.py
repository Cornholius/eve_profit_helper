import json
import re
import os
from tests import CheckSettings
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from sys import exit, argv
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QFileDialog
from PyQt5.uic import loadUi
from PyQt5.QtCore import Qt, QThread


# Выставление дефолтных значений если настройки невалидны
check = CheckSettings()
check.broker_tax()
check.sell_tax()
check.logs_path()
check.opacity()
check.renew_settings()
settings1 = check.load_settings()


class MyHandler(FileSystemEventHandler):
    # Класс следит за созданием лога маркета и вынимает нужную инфу

    def __init__(self):
        self.count = [0]

    def on_any_event(self, event):
        self.count.append(os.path.getsize(event.src_path))
        if self.count[-1] == self.count[-2]:
            mainWindow.get_values(event.src_path)


class Warden(QThread):
    # Отдельный поток который запускает отслеживание папки маркета

    def __init__(self, parent=None):
        super(Warden, self).__init__(parent)

    def run(self):
        event_handler = MyHandler()
        observer = Observer()
        observer.schedule(event_handler, check.settings["logs_path"], recursive=False)
        observer.start()


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()
        loadUi('eve_profit_helper_mainWindow2.ui', self)
        self.settings_btn.clicked.connect(SettingsWindow.show_window)
        self.on_error.setText(' '.join(check.settings['error']))

    def set_values(self, sell, buy, profit):
        self.sell_price_value.setText(f'{sell:,.2f}'.replace(',', ' '))
        self.buy_price_value.setText(f'{buy:,.2f}'.replace(',', ' '))
        self.profit_value.setText(f'{profit:,.2f}'.replace(',', ' '))
        if profit < 0:
            self.profit_value.setStyleSheet('color: #cc0000')
        else:
            self.profit_value.setStyleSheet('color: #008000')

    # Получаем значения sell и buy ордеров и добавляем шаг ставки
    def get_values(self, file):
        with open(file, 'r') as f:
            lines = f.readlines()
            sell = float(lines[1].split(',')[0])
            for i in lines:
                if re.search(r'\bTrue\b', i):
                    buy = float(i.split(',')[0])
                    break

        str_sell_price = format(sell, '.2f')[:5]
        str_buy_price = format(buy, '.2f')[:5]
        sell_price_with_bid = 0
        buy_price_with_bid = 0

        # если цена выше 10000
        if '.' not in str_sell_price and '.' not in str_buy_price:
            tail_of_sell_price = len(str(int(sell))) - 4
            tail_of_buy_price = len(str(int(buy))) - 4
            str_sell_price, str_buy_price = str_sell_price[:4], str_buy_price[:4]
            sell_price_with_bid = str(int(str_sell_price) - 1) + '0' * tail_of_sell_price
            buy_price_with_bid = str(int(str_buy_price) + 1) + '0' * tail_of_buy_price

        # если цена от 1000 до 9999
        if '.' in str_sell_price[-1] and '.' in str_buy_price[-1]:
            str_sell_price, str_buy_price = str_sell_price[:4], str_buy_price[:4]
            sell_price_with_bid = int(str_sell_price) + 1
            buy_price_with_bid = int(str_buy_price) + 1

        # если цена от 100 до 1000
        if '.' in str_sell_price[-2] and '.' in str_buy_price[-2]:
            sell_price_with_bid = round(float(str_sell_price) + 0.1, 1)
            buy_price_with_bid = round(float(str_buy_price) + 0.1, 1)

        # если цена от 1 до 100
        if '.' in str_sell_price[:3] and '.' in str_buy_price[:3]:
            sell_price_with_bid = sell + 0.01
            buy_price_with_bid = buy + 0.01

        sell_broker = (float(sell_price_with_bid) / 100) * float(check.settings['broker_tax'])
        buy_broker = (float(buy_price_with_bid) / 100) * float(check.settings['broker_tax'])
        sell_tax = (float(sell_price_with_bid) / 100) * float(check.settings['sell_tax'])
        sell_final = sell - sell_tax - sell_broker
        buy_final = buy + buy_broker
        profit = sell_final - buy_final
        self.set_values(float(sell_price_with_bid), float(buy_price_with_bid), profit)


class SettingsWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super(SettingsWindow, self).__init__()
        loadUi('eve_profit_helper_settings.ui', self)
        self.save_and_exit_btn.clicked.connect(self.save_and_exit)
        self.market_logs_btn.clicked.connect(self.find_logs_path)
        self.sell_tax_value.setValue(check.settings['sell_tax'])
        self.broker_tax_value.setValue(check.settings['broker_tax'])
        self.on_top_checkBox.setChecked(bool(check.settings['always_on_top']))
        self.market_logs_path.setText(check.settings['logs_path'])
        self.opacity_slider.setRange(10, 100)
        self.opacity_slider.setValue(int(check.settings['opacity'] * 100))
        self.opacity_slider.valueChanged[int].connect(self.set_opacity)

    def show_window(self):
        settingsWindow_widget.show()
        mainWindow_widget.hide()

    def find_logs_path(self):
        folder_path = QFileDialog.getExistingDirectory()
        self.market_logs_path.setText(folder_path)
        with open(check.settings_path, 'r') as f:
            data = json.load(f)
        data['logs_path'] = folder_path
        with open(check.settings_path, 'w') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    
    def set_opacity(self):
        mainWindow_widget.setWindowOpacity(float(self.opacity_slider.value() / 100))
        settingsWindow_widget.setWindowOpacity(float(self.opacity_slider.value() / 100))

    def save_and_exit(self):
        data = check.load_settings()
        data['broker_tax'] = self.broker_tax_value.value()
        data['sell_tax'] = self.sell_tax_value.value()
        data['always_on_top'] = self.on_top_checkBox.isChecked()
        data['opacity'] = float(self.opacity_slider.value() / 100)
        check.save_settings(data)
        check.settings = check.load_settings()
        settingsWindow_widget.hide()
        mainWindow_widget.show()


app = QtWidgets.QApplication(argv)

# Создаём главное окно и окно настроек
mainWindow = MainWindow()
mainWindow_widget = QtWidgets.QStackedWidget()
mainWindow_widget.addWidget(mainWindow)

settingsWindow = SettingsWindow()
settingsWindow_widget = QtWidgets.QStackedWidget()
settingsWindow_widget.addWidget(settingsWindow)

# Вешаем на окна нужные нам флаги
mainWindow_widget.setWindowOpacity(check.settings['opacity'])
mainWindow_widget.setWindowFlag(Qt.FramelessWindowHint)
settingsWindow_widget.setWindowOpacity(check.settings['opacity'])
if check.settings['always_on_top']:
    mainWindow_widget.setWindowFlag(Qt.WindowStaysOnTopHint)
    settingsWindow_widget.setWindowFlag(Qt.WindowStaysOnTopHint)

mainWindow_widget.show()
warden = Warden()
warden.start()
exit(app.exec_())
