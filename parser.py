from requests_html import HTMLSession, HTML

import datetime
import time
import re
from collections import namedtuple

import pytz
import urllib.request
from bs4 import BeautifulSoup

tz = pytz.timezone("Europe/Moscow")
ThreadInfo = namedtuple('ThreadInfo', ['thread_number','timestamp','subject','text','visual','thread_link'])

ThreadInfo = namedtuple('ThreadInfo', ['thread_number', 'timestamp', 'subject', 'text', 'op_files', 'link'])
'''
    TODO: maybe allow bot to only show political news
    FIXME: fix markdown breaking posts this ain't good
'''
def parse_threads(threads=None):
    if not threads:
        session = HTMLSession()
        r = session.get("https://2ch.hk/news/index.json", headers={"accept": "application/json"})
        threads = r.json().get("threads")
    
    with open('previously_parsed.list', 'r+') as f:
        previously_parsed = f.read().split(',')

        if not previously_parsed:
            previously_parsed = []

    parsed_data = []
    
    for thread in threads[1:]:  # offsetting one sticky thread on the top
        thread_number = thread.get('thread_num')
        thread_link = "https://2ch.hk/news/res/" + str(thread_number) + ".html"

        original_poster = thread.get('posts')[0]
        timestamp = datetime.datetime.fromtimestamp(original_poster.get("timestamp"))

        if thread_number not in previously_parsed and timestamp > datetime.datetime.now() - datetime.timedelta(hours=1):
            op_files = original_poster.get("files")
            subject = original_poster.get("subject")
            
            # TODO: https://pypi.org/project/html2text/
            
            op_text = original_poster.get('comment').replace('<br>', '\n') # changing 2ch <br> tags to \n to maintain new lines
            op_text = BeautifulSoup(op_text, "lxml").text  # cleaning text of html tags
            op_text = re.sub(r'^https?:\/\/.*[\r\n]*', '', op_text, flags=re.MULTILINE) # removing links

            op_files = [op_file.get('path') for op_file in op_files] if op_files else None

            previously_parsed.append(thread_number)
            parsed_data.append(ThreadInfo(
                                thread_number,
                                timestamp, 
                                subject, 
                                op_text, 
                                op_files, 
                                thread_link))
    
    with open('previously_parsed.list', 'w+') as f:
        f.write(','.join(previously_parsed))
    
    print('Parsed data: ', parsed_data)
    return parsed_data
    

if __name__ == "__main__":
    session = HTMLSession()
    r = session.get("https://2ch.hk/news/index.json", headers={"accept": "application/json"})
    threads = r.json().get("threads")
    
    parse_threads(threads)

