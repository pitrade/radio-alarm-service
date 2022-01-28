from datetime import datetime
import requests
from requests.structures import CaseInsensitiveDict
import json


class Plugin:
    @staticmethod
    def process(self, config, alarm_data):
        url = "https://connectapi.feuersoftware.com/interfaces/public/operation?updateStrategy=none"
        api_key = config['Feuersoftware']['api_key']

        headers = CaseInsensitiveDict()
        headers["Accept"] = "application/json"
        headers["Authorization"] = "Bearer " + api_key
        headers["Content-Type"] = "application/json"

        data = {
            "Start": alarm_data['datetime'].isoformat(),
            "Status": "new",
            "AlarmEnabled": "true",
            "Keyword": alarm_data['keyword'] if alarm_data['keyword'] else 'Info',
            "Facts": alarm_data['text'],
            "Ric": ','.join(alarm_data['ric_list']),
            "Address": {
                "Street": alarm_data['street'],
                "HouseNumber": alarm_data['house_number'],
                "City": alarm_data['city'] if alarm_data['city'] else config['Feuersoftware']['default_city'],
                "District": alarm_data['quarter']
            },
            "Properties": [
                {
                    "Key": "Alarmierte RICs",
                    "Value": ','.join(alarm_data['ric_name_list'])
                }
            ]
        }

        resp = requests.post(url, headers=headers, data=json.dumps(data))
        print(resp.status_code)
        print(resp.content)
