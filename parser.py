import time
import pytz
from collections import namedtuple
from datetime import datetime, timedelta

import urllib.request
import bs4
from requests_html import HTMLSession, HTML

tz = pytz.timezone("Europe/Moscow")
ThreadInfo = namedtuple('ThreadInfo', ['thread_number','timestamp','subject','text','visual','thread_link'])

def parse():

    session = HTMLSession()

    r = session.get("https://2ch.hk/news/index.json", headers={"accept": "application/json"})

    threads = r.json().get("threads")

    parsed_data = []
    
    for thread in threads[1::]:

        timestamp = thread.get("posts")[0].get("timestamp")
        timestamp = datetime.fromtimestamp(timestamp).astimezone(tz)

        if timestamp > datetime.now().astimezone(tz) - timedelta(hours=1):
            
            thread_number = thread.get("thread_num")
            
            subject = thread.get("posts")[0].get("subject")

            text = thread.get("posts")[0].get("comment")
            text = HTML(html = text)
            links = text.find("a")
            text = text.html
            text = text.replace("<br>", "\n")

            text = bs4.BeautifulSoup(text, features="lxml").get_text()

            for link in links:
                href = link.attrs["href"]
                text = text.replace(href, ("[" + href + "](" + href + ")"))

            visual = thread.get("posts")[0].get("files")

            if len(visual) != 0:
                visual =  visual[0].get("path")
            else:
                visual = ""
                
            thread_link = "2ch.hk/news/res/" + str(thread_number) + ".html"
            
            parsed_data.append(ThreadInfo(thread_number, timestamp, subject, text, visual, thread_link))
            print(text)
        break
    return parsed_data
   

if __name__ == "__main__":
    parse()

