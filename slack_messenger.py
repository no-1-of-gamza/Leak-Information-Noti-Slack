import requests
import json
import sys
import time

class SlackMessenger:
    def __init__(self):
        self.webhook_url = "https://hooks.slack.com/services/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"

    def _get_current_time(self):
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

    def send_message(self, msg):
        timestamp = self._get_current_time()
        message = f"{timestamp}: {msg}"
        title = ":zap: Leak-Information-Notification :zap:"

        slack_data = {
            "username": "leak-info-notification",
            "icon_emoji": ":satellite:",
            "channel": "#leak-info-notification",
            "attachments": [
                {
                    "color": "#9733EE",
                    "fields": [
                        {
                            "title": title,
                            "value": message,
                            "short": "true",
                        }
                    ]
                }
            ]
        }

        byte_length = str(sys.getsizeof(slack_data))
        headers = {'Content-Type': "application/json", 'Content-Length': byte_length}
        
        response = requests.post(self.webhook_url, data=json.dumps(slack_data), headers=headers)
        
        if response.status_code != 200:
            raise Exception(response.status_code, response.text)

def main():
    messenger = SlackMessenger()

    message = "Test!"

    messenger.send_message(message)

if __name__ == "__main__":
    main()
