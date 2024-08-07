import os
import json


class CheckSettings:

    def __init__(self):
        self.settings_path = os.path.abspath('config.json')
        self.settings = self.load_settings()
        self.errors = []

    def load_settings(self):
        with open(self.settings_path, 'r') as conf:
            settings = json.load(conf)
            return settings

    def renew_settings(self):
        self.settings['error'] = self.errors
        with open(self.settings_path, 'w') as conf:
            json.dump(self.settings, conf, ensure_ascii=False, indent=4)
        self.load_settings()

    def save_settings(self, sett):
        with open(self.settings_path, 'w') as conf:
            json.dump(sett, conf, ensure_ascii=False, indent=4)

    def broker_tax(self):
        try:
            float(self.settings['broker_tax'])
        except Exception:
            self.settings['broker_tax'] = 0.0
            self.errors.append('Выстави налог брокера')

    def sell_tax(self):
        try:
            float(self.settings['sell_tax'])
        except Exception:
            self.settings['sell_tax'] = 0.0
            self.errors.append('Выстави налог на продажу')

    def logs_path(self):
        if not os.path.isdir(self.settings['logs_path']):
            self.settings['logs_path'] = "C:/"
            self.errors.append('не задан путь к логам')

    def opacity(self):
        try:
            float(self.settings['opacity'])
        except Exception:
            self.settings['opacity'] = 1.0
