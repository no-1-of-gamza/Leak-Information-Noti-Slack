import time
import slack_messenger
import sys
import datetime
sys.path.append("crawler")

from crawler.darkweb import Crawler

class Main:
    def __init__(self):
        self.crawler = Crawler()
        self.messenger = slack_messenger.SlackMessenger()
        self.start_time = datetime.datetime.now()

    def print_welcome(self):
        welcome_message = r"""
   __        __       ___ ___     ____       __     
 /'_ `\    /'__`\   /' __` __`\  /\_ ,`\   /'__`\   
/\ \L\ \  /\ \L\.\_ /\ \/\ \/\ \ \/_/  /_ /\ \L\.\_ 
\ \____ \ \ \__/.\_\\ \_\ \_\ \_\  /\____\\ \__/.\_\
 \/___L\ \ \/__/\/_/ \/_/\/_/\/_/  \/____/ \/__/\/_/
   /\____/                                          
   \_/__/ 
__                          __              __              __                
/\ \                       /\ \            /\ \            /\ \__             
\ \ \         __      __   \ \ \/'\        \_\ \      __   \ \ ,_\     __     
 \ \ \  __  /'__`\  /'__`\  \ \ , <        /'_` \   /'__`\  \ \ \/   /'__`\   
  \ \ \L\ \/\  __/ /\ \L\.\_ \ \ \\`\     /\ \L\ \ /\ \L\.\_ \ \ \_ /\ \L\.\_ 
   \ \____/\ \____\\ \__/.\_\ \ \_\ \_\   \ \___,_\\ \__/.\_\ \ \__\\ \__/.\_\
    \/___/  \/____/ \/__/\/_/  \/_/\/_/    \/__,_ / \/__/\/_/  \/__/ \/__/\/_/
                                                                                             
        """
        print(welcome_message)  

    def crawler_start(self):
        alarm_data = self.crawler.start()
        return alarm_data

    def send_message(self, message):
        self.messenger.send_message(message)

if __name__ == "__main__":
    Main = Main()
    Main.print_welcome()
    print("---------------------------------------------------------")
    print(f"Program started at: {Main.start_time}")
    print("---------------------------------------------------------")

    while True:
        alarm_data = Main.crawler_start()

        if alarm_data:
            alarm_data = alarm_data[0]

            current_time = datetime.datetime.now()
            elapsed_time = current_time - Main.start_time

            slack_message = f"Domain: {alarm_data['domain']}\n" \
                            f"URL: {alarm_data['url']}\n" \
                            f"Status: {alarm_data['status']}\n" \
                            f"Deadline: {alarm_data['deadline']}\n" \
                            f"Description: {alarm_data['description']}\n" \
                            f"Uploaded Date: {alarm_data['uploaded_date']}\n" \
                            f"Updated Date: {alarm_data['updated_date']}\n" \
                            f"Start Time: {Main.start_time}\n" \
                            f"Elapsed Time: {elapsed_time}"

            Main.send_message(slack_message)
        else:
            current_time = datetime.datetime.now()
            elapsed_time = current_time - Main.start_time
            print(f"No alarm data found at: {current_time}, Elapsed Time: {elapsed_time}")

        time.sleep(10)
