from requests_html import HTMLSession, HTML

import pytz
import datetime
import time
import re
from collections import namedtuple
import urllib.request

tz = pytz.timezone("Europe/Moscow")

ThreadInfo = namedtuple('ThreadInfo', ['thread_number', 'timestamp', 'subject', 'text', 'op_files', 'link'])
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
def parse_threads(threads):
    parsed_data = []
    
    for thread in threads[1:]:  # offsetting one sticky thread on the top
        thread_number = thread.get('thread_num')
        thread_link = "2ch.hk/news/res/" + str(thread_number) + ".html"

        original_poster = thread.get('posts')[0]
        op_files = original_poster.get("files")
        subject = original_poster.get("subject")

        op_text = original_poster.get('comment')
        html_text = HTML(html=op_text)
        absolute_links = html_text.find('a')        
        
        # TODO: think what to do about this mess.
        for a in absolute_links:
            href = a.attrs["href"]     
            op_text = op_text.replace(href, ("[" + href + "](" + href + ")"))


        timestamp = datetime.datetime.fromtimestamp(original_poster.get("timestamp"))

        op_files = [op_file.get('path') for op_file in op_files] if op_files else None

        if timestamp > datetime.datetime.now() - datetime.timedelta(hours=1):
            parsed_data.append(ThreadInfo(
                                thread_number,
                                timestamp, 
                                subject, 
                                op_text, 
                                op_files, 
                                thread_link))
            print(thread_link)

    return parsed_data
    

if __name__ == "__main__":
    session = HTMLSession()
    r = session.get("https://2ch.hk/news/index.json", headers={"accept": "application/json"})
    threads = r.json().get("threads")
    
    parse_threads(threads)

