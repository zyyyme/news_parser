from requests_html import HTMLSession, HTML

import pytz
from datetime import datetime
import time
import re
from Thread import Thread
import urllib.request

tz = pytz.timezone("Europe/Moscow")

'''
TODO:
get text of thread, get image link,
check if the thread creation time is within given time,

JSON Structure:

posts: list of posts
each post : comment (text of post), date, files (image/video attached), subject
thread_num

What is needed for a thread object:

Text, visuals (if present), thread number, date published


'''
def parse():

    session = HTMLSession()

    r = session.get("https://2ch.hk/news/index.json", headers={"accept": "application/json"})

    threads = r.json().get("threads")

    parsed_data = []
    pattern = r'^[\d\w]+\.[\w]+\/[.]+'
    
    for thread in threads:
        
        text = thread.get("posts")[0].get("comment")
        sources = HTML(html = text).absolute_links
        text = HTML(html = text)
        text2 = text.text
        for a in text.find("a"):
            href = a.attrs["href"]
            # print(href)
     
            text2 = text2.replace(href, ("[" + href + "](" + href + ")"))


        # print(text2)
        text = text2
        visual = thread.get("posts")[0].get("files")

        subject = thread.get("posts")[0].get("subject")

        thread_num = thread.get("thread_num")

        timestamp = thread.get("posts")[0].get("timestamp")
        timestamp = int(time.mktime(datetime.fromtimestamp(timestamp).astimezone(tz).timetuple()))
        # print(subject)
        
        link = "2ch.hk/news/res/" + str(thread_num) + ".html"

        if len(visual) != 0:
            visual =  visual[0].get("path")
        else:
            visual = ""

        if timestamp > (int(time.mktime(datetime.now().astimezone(tz).timetuple()))-3600):
            parsed_data.append(Thread(thread_num,timestamp, subject, text, sources, visual, link))
            print(link)

    return parsed_data





    

if __name__ == "__main__":
    parse()

