import serial
import time
import os.path
from datetime import datetime
import requests
from requests.structures import CaseInsensitiveDict
import importlib
import configparser


class RadioAlarmService:
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read('config/config.ini')
        self.plugins = self.get_plugins()
        self.serial = self.get_serial()
        self.alarm = Alarm()

    def get_plugins(self):
        active_plugins = []
        for key in list(self.config['Plugins'].keys()):
            if self.config['Plugins'].getboolean(key):
                active_plugins.append(key)
        return active_plugins

    def get_serial(self):
        s = serial.Serial()
        s.port = self.config['RadioAlarmService']['serial_port']
        s.baudrate = self.config['RadioAlarmService']['serial_baudrate']
        s.parity = serial.PARITY_NONE
        s.stopbits = serial.STOPBITS_ONE
        s.bytesize = serial.EIGHTBITS
        s.timeout = None

        if os.path.exists(self.serial.port):
            print('Serial Port {0} exists.'.format(self.serial_port))
            s.open()
            print('Serial Port {0} is open.'.format(s.name))
        return s

    def run(self):
        try:
            while self.serial.isOpen():
                # if serial data available
                if self.serial.inWaiting():
                    # read until stop byte
                    message = self.serial.read_until(b'\x00').decode('iso_8859_1', 'ignore')  # bytes decoded to str
                    self.log(message)

                # if alarm exits and timeout expired
                if self.alarm and (datetime.now() - self.alarm.last_update) > self.config['RadioAlarmService']['alarm_timeout']:
                    self.process_plugins()
                    self.alarm = None

                time.sleep(0.100)
        except serial.SerialException as e:
            self.serial.close()

    def log(self, message):
        f = open('logs/message.log', 'a')
        f.write('{0}: {1}\n'.format(datetime.now(), message))
        f.close()

    def process_plugins(self):
        alarm_data = self.alarm.get_data()
        for plugin in self._plugins:
            plugin.process(self.config, alarm_data)


class Alarm:
    def __init__(self):
        self.complete = False
        self.last_update = None

    def add_message(self, message):
        self.last_update = datetime.now()
