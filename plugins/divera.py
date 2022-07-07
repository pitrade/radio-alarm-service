from datetime import datetime
import requests
from requests.structures import CaseInsensitiveDict
import json


class Plugin:
    @staticmethod
    def process(self, config, alarm_data):
        url_alarm = "https://www.divera247.com/api/alarm"
        url_news = "https://www.divera247.com/api/news"
        api_key = config['Divera']['api_key']

        headers = CaseInsensitiveDict()
        headers["Content-Type"] = "application/json"

        text = alarm_data['text']
        if 'info' in alarm_data:
            text += ', ' + alarm_data['info'].rstrip(',')

        data = {
            "title": alarm_data['keyword'] if alarm_data['keyword'] else 'Info',
            "text": text,
            "address": self.get_address(alarm_data),
            "ric": ','.join(alarm_data['ric_list']),
            "accesskey": api_key
        }

        # print(json.dumps(data, ensure_ascii=False))

        resp = requests.post(url_alarm if alarm_data['keyword'] else url_news, headers=headers, data=json.dumps(data))
        print(resp.status_code)
        print(resp.content)

    @staticmethod
    def get_address(alarm_data):
        a = [alarm_data['street'], alarm_data['house_number'], alarm_data['quarter']]
        return ' '.join(filter(None, a))

