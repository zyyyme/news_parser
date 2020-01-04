from telegram.ext import Updater, CommandHandler, JobQueue
from telegram import ParseMode
from datetime import datetime, timedelta
import logging
from urllib.parse import urlparse
import os
import urllib
from parser import parse


def main():
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)
    logger = logging.getLogger(__name__)

    token_file = open("token", "r")

    TOKEN = str(token_file.read().strip())

    token_file.close()

    REQUEST_KWARGS={
        'proxy_url': 'socks5://orbtl.s5.opennetwork.cc:999',
        # Optional, if you need authentication:
        'urllib3_proxy_kwargs': {
            'username': '1305759',
            'password': 'ZJ0mPA1A',
        }
    }

    CHAT_ID = "@twochnews"
    IMAGE_EXTENSIONS = [".jpg", ".png"]
    ANIMATION_EXTENSIONS = [".gif"]
    VIDEO_EXTENSIONS = [".webm", ".mp4"]

    def start(update,context):
        
        update.message.reply_text("fuck off")
        

    def fetch_messages(update,context):
        if update.message.from_user.username == "zyyme":
            update.message.reply_text("Fetching")
            context.job_queue.run_repeating(parse_send_messages, 3600, \
            #first=datetime.now().replace(second=0, microsecond=0, minute=0) + timedelta(hours=1), context=update)
            first = datetime.now(), context = update)
        else:
            update.message.reply_text("fuck off")

    def parse_send_messages(context):
        threads = parse()

        for thread in threads:
            ext = os.path.splitext(urlparse(thread.visual).path)[1]  
            print(thread.visual, ext)    

            text = "*" + thread.subject + "* \n \n" + thread.text + "\n"
            text = [text[i:i+4096] for i in range(0,len(text), 4096)]
            text[-1] += "\n[**ТРЕД**](" + thread.thread_link + ")"

            urllib.request.urlretrieve("https://2ch.hk" + thread.visual, 'buffer' + ext)
            
            if ext in IMAGE_EXTENSIONS: 

                if len(text[0])>1024:
                    updater.bot.send_photo(chat_id = CHAT_ID, photo = open('buffer' + ext, 'rb'))
                    for chunk in text:
                        updater.bot.send_message(chat_id = CHAT_ID, text = chunk, parse_mode = ParseMode.MARKDOWN)
                else:
                    updater.bot.send_photo(chat_id = CHAT_ID, photo = open('buffer' + ext, 'rb'),\
                        caption = text[0], parse_mode = ParseMode.MARKDOWN)
            
            elif ext in ANIMATION_EXTENSIONS:

                if len(text[0])>1024:
                    updater.bot.send_animation(chat_id = CHAT_ID, animation = open('buffer' + ext, 'rb'))
                    for chunk in text:
                        updater.bot.send_message(chat_id = CHAT_ID, text = chunk, parse_mode = ParseMode.MARKDOWN)
                else:
                    updater.bot.send_animation(chat_id = CHAT_ID,\
                         animation = open('buffer' + ext, 'rb'),\
                              caption = text[0], parse_mode = ParseMode.MARKDOWN)
            
            elif ext in VIDEO_EXTENSIONS:
                if len(text[0])>1024:
                    updater.bot.send_video(chat_id = CHAT_ID, video = open('buffer' + ext, 'rb'))
                    for chunk in text:
                        updater.bot.send_message(chat_id = CHAT_ID, text = chunk, parse_mode = ParseMode.MARKDOWN)                
                else:
                    updater.bot.send_video(chat_id = CHAT_ID, video = open('buffer' + ext, 'rb'), \
                        caption = text[0], parse_mode = ParseMode.MARKDOWN)
            
            else:
            
                for chunk in text:
                    updater.bot.send_message(chat_id = CHAT_ID, text = chunk, parse_mode = ParseMode.MARKDOWN)
            
            os.remove("buffer" + ext)
            
    updater = Updater(TOKEN, use_context=True, request_kwargs=REQUEST_KWARGS)

    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(CommandHandler('fetch', fetch_messages, pass_job_queue=True))

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()