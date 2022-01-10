import serial
import time
import os.path
import datetime
import requests
from requests.structures import CaseInsensitiveDict
import importlib
import configparser


class RadioAlarmService:
    def __init__(self):
        config = configparser.ConfigParser()
        config.read('config/config.ini')
        self.serial_port = config['RadioAlarmService']['serial_port']
        self.serial_baudrate = config['RadioAlarmService']['serial_baudrate']

    def run(self):
        while True:
            if os.path.exists(self.serial_port):
                print('Serial Port {0} exists.'.format(self.serial_port))

                s = serial.Serial()
                s.port = self.serial_port
                s.baudrate = self.serial_baudrate
                s.parity = serial.PARITY_NONE
                s.stopbits = serial.STOPBITS_ONE
                s.bytesize = serial.EIGHTBITS
                s.timeout = None
                s.open()

                print('Serial Port {0} is open.'.format(s.name))

                try:
                    while True:
                        # print('try to read from serial')
                        if s.inWaiting():
                            # read until stop byte
                            message = s.read_until(b'\x00').decode('iso_8859_1', 'ignore')  # .encode('utf-8')
                            message = message.rstrip()  # remove newline on right end
                            self.log(message)
                        time.sleep(0.100)
                except serial.SerialException as e:
                    s.close()
                except KeyboardInterrupt:
                    s.close()
            time.sleep(5)

    def log(self, message):
        f = open('message.log', 'a')
        f.write('{0}: {1}\n'.format(datetime.datetime.now(), message))
        f.close()

