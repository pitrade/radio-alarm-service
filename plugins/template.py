class Plugin:
    @staticmethod
    def process(self, config, alarm_data):
        # do something
        print('RICs: {0}'.format(alarm_data['ric_list']))
        return
