import json
import os
from tests import CheckSettings
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from sys import exit, argv
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QFileDialog, QApplication
from PyQt5.uic import loadUi
from PyQt5.QtCore import Qt, QThread
from time import sleep


# Выставление дефолтных значений если настройки невалидны
check = CheckSettings()
check.broker_tax()
check.sell_tax()
check.logs_path()
check.opacity()
check.renew_settings()


# Класс следит за созданием лога Маркета и вынимает нужную инфу
class MyHandler(FileSystemEventHandler):

    def __init__(self):
        self.count = [0]

    def on_modified(self, event):
        self.count.append(os.path.getsize(event.src_path))
        if self.count[-1] == self.count[-2]:
            print('file finished')
            sleep(0.3)
            with open(event.src_path, 'r') as file:
                mainWindow.file_with_prices = file.readlines()
            self.count = [0]
            sleep(0.2)
            mainWindow.get_values()


# Отдельный поток который запускает отслеживание папки маркета
class Warden(QThread):

    def __init__(self, parent=None):
        super(Warden, self).__init__(parent)
        self.observer = Observer()

    def run(self):
        event_handler = MyHandler()
        self.observer.schedule(event_handler, check.settings["logs_path"], recursive=False)
        self.observer.start()
        try:
            while self.observer.is_alive():
                self.observer.join(1)
        finally:
            self.observer.stop()
            self.observer.join()


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()
        loadUi('ui/mainWindow.ui', self)
        self.sell = self.buy = self.profit = self.broker_fee = self.sales_tax = self.margin = 0
        self.sell_price = self.buy_price = 0.0
        self.file_with_prices = []
        self.settings_btn.clicked.connect(SettingsWindow.show_window)
        self.quick_sale_btn.clicked.connect(self.quick_sale)
        self.rtfm.clicked.connect(RtfmWindow.show_window)
        self.copy_sell_price_btn.clicked.connect(lambda: self.copy_to_clopboard(self.sell_price))
        self.copy_buy_price_btn.clicked.connect(lambda: self.copy_to_clopboard(self.buy_price))
        self.check_quick_sale_btn_color()

    def copy_to_clopboard(self, data):
        QApplication.clipboard().setText(str(data))

    def check_quick_sale_btn_color(self):
        if check.settings['quick_sale']:
            self.quick_sale_btn.setStyleSheet(f'background-color: #C23333;border: 1px solid;border-radius: 6px;')
        else:
            self.quick_sale_btn.setStyleSheet(f'background-color: #B1DA3F;border: 1px solid;border-radius: 6px;')

    def quick_sale(self):
        if check.settings['quick_sale']:
            check.settings['quick_sale'] = False
        else:
            check.settings['quick_sale'] = True
        check.renew_settings()
        self.check_quick_sale_btn_color()

    def find_prices_in_file(self, sell_radius):
        sell_price = True
        for i in self.file_with_prices:
            line = i.split(",")
            if line[7] == 'False' and int(line[-2]) == sell_radius and sell_price:
                print(line)
                self.sell = float(line[0])
                print('found sell price', self.sell)
                sell_price = False
            if line[7] == 'True' and ((int(line[3]) - int(line[-2])) >= 0 or line[3] == '32767'):
                print(line)
                self.buy = float(line[0])
                print('found buy price', self.buy)
                break
            # break

    # подставляем цены в окно программы
    def set_values(self):
        self.sell_price_value.setText(f'{float(self.sell_price):,.2f}'.replace(',', ' '))
        self.buy_price_value.setText(f'{float(self.buy_price):,.2f}'.replace(',', ' '))
        self.broker_fee_value.setText(f'-{self.broker_fee:,.2f}'.replace(',', ' '))
        self.sales_tax_value.setText(f'-{self.sales_tax:,.2f}'.replace(',', ' '))
        self.profit_value.setText(f'{self.profit:,.2f}'.replace(',', ' '))
        self.margin_value.setText(f'{round(self.margin, 2)}%')
        if self.profit < 0:
            self.profit_value.setStyleSheet('color: #cc0000')
            self.margin_value.setStyleSheet('color: #cc0000')
        else:
            self.profit_value.setStyleSheet('color: #008000')
            self.margin_value.setStyleSheet('color: #008000')

        self.broker_fee_value.setStyleSheet('color: #cc0000')
        self.sales_tax_value.setStyleSheet('color: #cc0000')

    # Получаем значения sell и buy ордеров и добавляем шаг ставки
    def get_values(self):
        print('get values')
        self.find_prices_in_file(check.settings['sell_radius'])
        # self.find_prices_in_file(check.settings['buy_radius'])
        str_sell_price = format(self.sell, '.2f')[:5]
        str_buy_price = format(self.buy, '.2f')[:5]
        sell_price_with_bid = float(0)
        buy_price_with_bid = float(0)
        print("str_sell_price", str_sell_price)
        print("str_buy_price", str_buy_price)

        # если цена выше 10000
        if '.' not in str_sell_price and '.' not in str_buy_price:
            tail_of_sell_price = len(str(int(self.sell))) - 4
            tail_of_buy_price = len(str(int(self.buy))) - 4
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
            sell_price_with_bid = self.sell + 0.01
            buy_price_with_bid = self.buy + 0.01

        if check.settings['quick_sale']:
            broker_tax = 0
        else:
            broker_tax = float(check.settings['broker_tax'])
        sell_tax = float(check.settings['sell_tax'])

        #   готовые цены для выставления ордера
        self.sell_price = float(sell_price_with_bid)
        self.buy_price = float(buy_price_with_bid)
        self.broker_fee = self.sell_price * broker_tax / 100
        self.sales_tax = self.sell_price * sell_tax / 100
        self.profit = self.sell_price - self.broker_fee - self.sales_tax - (self.buy_price + self.buy_price * 0.0138)
        self.margin = (self.sell_price - self.buy_price - self.broker_fee - self.sales_tax) / self.sell_price * 100
        self.set_values()
        print('buy_price', self.buy_price)
        print('sell_price', self.sell_price)


class SettingsWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super(SettingsWindow, self).__init__()
        loadUi('ui/settings.ui', self)
        self.save_and_exit_btn.clicked.connect(self.save_and_exit)
        self.market_logs_btn.clicked.connect(self.find_logs_path)
        self.sell_tax_value.setValue(check.settings['sell_tax'])
        self.broker_tax_value.setValue(check.settings['broker_tax'])
        self.sell_order_radius_count.setValue(check.settings['sell_radius'])
        self.buy_order_radius_count.setValue(check.settings['buy_radius'])
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
        data['sell_radius'] = self.sell_order_radius_count.value()
        data['buy_radius'] = self.buy_order_radius_count.value()
        data['always_on_top'] = self.on_top_checkBox.isChecked()
        data['opacity'] = float(self.opacity_slider.value() / 100)
        check.save_settings(data)
        check.settings = check.load_settings()
        settingsWindow_widget.hide()
        mainWindow_widget.show()


class RtfmWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super(RtfmWindow, self).__init__()
        loadUi('ui/rtfm.ui', self)
        self.ok_btn.clicked.connect(self.go_back)

    def show_window(self):
        rtfmWindow_widget.show()
        mainWindow_widget.hide()
    
    def go_back(self):
        rtfmWindow_widget.hide()
        mainWindow_widget.show()


app = QtWidgets.QApplication(argv)

# Создаём все окна
mainWindow = MainWindow()
mainWindow_widget = QtWidgets.QStackedWidget()
mainWindow_widget.addWidget(mainWindow)

settingsWindow = SettingsWindow()
settingsWindow_widget = QtWidgets.QStackedWidget()
settingsWindow_widget.addWidget(settingsWindow)

rtfmWindow = RtfmWindow()
rtfmWindow_widget = QtWidgets.QStackedWidget()
rtfmWindow_widget.addWidget(rtfmWindow)

# Вешаем на окна нужные нам флаги
mainWindow_widget.setWindowOpacity(check.settings['opacity'])
mainWindow_widget.setWindowFlags(Qt.CustomizeWindowHint | Qt.WindowMinimizeButtonHint | Qt.WindowCloseButtonHint | Qt.FramelessWindowHint)
# mainWindow_widget.setWindowFlags(Qt.FramelessWindowHint)
settingsWindow_widget.setWindowFlags(Qt.CustomizeWindowHint | Qt.WindowMinimizeButtonHint)
rtfmWindow_widget.setWindowFlags(Qt.CustomizeWindowHint | Qt.WindowMinimizeButtonHint)
settingsWindow_widget.setWindowOpacity(check.settings['opacity'])
if check.settings['always_on_top']:
    mainWindow_widget.setWindowFlag(Qt.WindowStaysOnTopHint)
    settingsWindow_widget.setWindowFlag(Qt.WindowStaysOnTopHint)

mainWindow_widget.show()
warden = Warden()
warden.start()
exit(app.exec_())
