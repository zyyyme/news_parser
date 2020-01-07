import time
import pytz
from collections import namedtuple
from datetime import datetime, timedelta

import urllib.request
import bs4
from requests_html import HTMLSession, HTML
from telegram.constants import MAX_MESSAGE_LENGTH

REQUEST_URL = "https://2ch.hk/news/index.json"

tz = pytz.timezone("Europe/Moscow")
ThreadInfo = namedtuple('ThreadInfo', ['thread_number','timestamp','subject','text','visual','thread_link'])


def __split_text_to_chunks(text):
    return [text[i:i+MAX_MESSAGE_LENGTH] for i in range(0,len(text), MAX_MESSAGE_LENGTH)]


def __format_text(text, subject, thread_link):
    text = "[" + subject + "](" + thread_link + ") \n \n" + text + "\n"
    text = __split_text_to_chunks(text)
    return text


def parse():

    session = HTMLSession()

    r = session.get(REQUEST_URL, headers={"accept": "application/json"})

    threads = r.json().get("threads")

    parsed_data = []
    
    for thread in threads[1::]:

        timestamp = thread.get("posts")[0].get("timestamp")
        timestamp = datetime.fromtimestamp(timestamp).astimezone(tz)

        if timestamp > datetime.now().astimezone(tz) - timedelta(hours=1):
            
            thread_number = thread.get("thread_num")
            
            thread_subject = thread.get("posts")[0].get("subject")

            text = thread.get("posts")[0].get("comment")
            text = HTML(html = text)
            links = text.find("a")
            text = text.html
            text = text.replace("<br>", "\n") # replacing line breaks to markdown ones
            text = bs4.BeautifulSoup(text, features="lxml").get_text()

            # replacing html links to markdown ones
            for link in links:
                href = link.attrs["href"]
                text = text.replace(href, ("[" + href + "](" + href + ")"))

            thread_files = thread.get("posts")[0].get("files")

            thread_files = [thread_file.get("path") for thread_file in thread_files] if thread_files else None
                
            thread_link = "2ch.hk/news/res/" + str(thread_number) + ".html"

            text = __format_text(text, subject, thread_link) if text else "\n"
            
            parsed_data.append(ThreadInfo(thread_number, timestamp, subject, text, visual, thread_link))
            print(text)
        
    return parsed_data
   

if __name__ == "__main__":
    parse()

