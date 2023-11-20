import json
import sys
import random
import requests
import os
import numpy as np
import torch

def send_msg(msg):
    url = "https://hooks.slack.com/services/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"
    message = ("Test Message\n" + msg) 
    title = (f"Test Title :zap:")
    slack_data = {
        "username": "leak-info-notification", 
        "icon_emoji": ":satellite:",
        "channel" : "#leak-info-notification",
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
    response = requests.post(url, data=json.dumps(slack_data), headers=headers)
    if response.status_code != 200:
        raise Exception(response.status_code, response.text)
    

msg=""
send_msg(msg)