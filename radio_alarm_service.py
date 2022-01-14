import serial
import time
import os.path
from datetime import datetime
import importlib
import configparser


class RadioAlarmService:
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read('config/config.ini')
        self.plugins = []
        self.serial = None
        self.set_plugins()
        self.set_serial()
        self.alarm = Alarm()  # empty

    def set_plugins(self):
        for key in list(self.config['Plugins'].keys()):
            if self.config['Plugins'].getboolean(key):
                self.plugins.append(importlib.import_module('plugins.' + key, '.').Plugin())

    def set_serial(self):
        self.serial = serial.Serial()
        self.serial.port = self.config['RadioAlarmService']['serial_port']
        self.serial.baudrate = self.config['RadioAlarmService']['serial_baudrate']
        self.serial.parity = serial.PARITY_NONE
        self.serial.stopbits = serial.STOPBITS_ONE
        self.serial.bytesize = serial.EIGHTBITS
        self.serial.timeout = None

        if os.path.exists(self.serial.port):
            print('Serial Port {0} exists.'.format(self.serial.port))
            self.serial.open()
            print('Serial Port {0} is open.'.format(self.serial.name))

    def run(self):
        try:
            while self.serial.isOpen():
                # if serial data available or alarm data empty
                if self.serial.inWaiting() or not self.alarm.data:
                    # read until stop byte (blocks process)
                    message = self.serial.read_until(b'\x00').decode('iso_8859_1')  # bytes decoded to str
                    self.log(message)
                    self.alarm.add(message)

                # if alarm exits and timeout expired
                if self.alarm.last_update and (datetime.now() - self.alarm.last_update).total_seconds() > float(self.config['RadioAlarmService']['alarm_timeout']):
                    self.process_plugins()
                    self.alarm = Alarm()

                time.sleep(0.010)
        except serial.SerialException as e:
            self.serial.close()

    @staticmethod
    def log(message):
        f = open('logs/message.log', 'a')
        f.write('{0}: {1}\n'.format(datetime.now(), message))
        f.close()

    def process_plugins(self):
        for plugin in self.plugins:
            plugin.process(plugin, self.config, self.alarm.data)


class Alarm:
    def __init__(self):
        self.data = {}
        self.last_update = None

    def add(self, message):
        # message = message.replace('/', ' #, B1, Fw Adelheidsdorf, , Schulstraße 13,  ,         , Adelheidsdorf, Adelheidsdorf, , testtest test,')
        message = message.replace('/', '')
        self.last_update = datetime.now()
        lines = message.splitlines()  # lines[0] is empty
        t = lines[3].split(": #")
        text = t[1].split(",", 11)  # text[6] = ?
        address = text[4].strip().split(' ', 1)

        if not self.data:
            self.data['created_at'] = datetime.now()
            self.data['datetime'] = datetime.strptime(lines[1], '%H:%M %d.%m.%y')
            self.data['ric_list'] = []
            self.data['ric_name_list'] = []
            self.data['keyword'] = text[1].strip()
            self.data['object_number'] = text[0].strip()
            self.data['object'] = text[2].strip()
            self.data['sub_object'] = text[3].strip()
            self.data['street'] = address[0].strip()
            self.data['house_number'] = address[1].strip() if len(address) > 0 else None
            self.data['quarter'] = text[7].strip()
            self.data['city'] = text[8].strip()
            self.data['place'] = text[9].strip()
            self.data['route'] = text[5].strip()
            self.data['text'] = text[10].strip()
            self.data['info'] = text[11].strip()

        self.data['ric_list'].append(lines[2].strip())
        self.data['ric_name_list'].append(t[0].strip())
