import os
import urllib
import logging
from urllib.parse import urlparse
from datetime import datetime, timedelta

from telegram import ParseMode
from telegram.constants import MAX_CAPTION_LENGTH, MAX_MESSAGE_LENGTH
from telegram.ext import Updater, CommandHandler, JobQueue

from parser import parse


def main():
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)
    logger = logging.getLogger(__name__)

    token_file = open("token", "r")

    TOKEN = str(token_file.read().strip())

    token_file.close()

    CHAT_ID = "@twochnews"
    DEFAULT_TIMEOUT = 60
    # TODO: convert webm to mp4
    IMAGE_EXTENSIONS = [".jpg", ".png"]
    ANIMATION_EXTENSIONS = [".gif"]
    VIDEO_EXTENSIONS = [".webm", ".mp4"]


    def __get_media(link, extension):
        urllib.request.urlretrieve("https://2ch.hk" + link, 'buffer' + extension)

    
    def __get_sending_method(ext):
        if ext in IMAGE_EXTENSIONS:
            return updater.bot.send_photo
        elif ext in ANIMATION_EXTENSIONS:
            return updater.bot.send_animation
        elif ext in VIDEO_EXTENSIONS:
            return updater.bot.send_video
        else:
            return None


    def start(update,context):
        update.message.reply_text("go away")
        

    def fetch_messages(update,context):
        if update.message.from_user.username == "zyyme":
            update.message.reply_text("Fetching")
            context.job_queue.run_repeating(parse_send_messages, 3600, \
            first=datetime.now().replace(second=0, microsecond=0, minute=0) + timedelta(hours=1), context=update)
        else:
            update.message.reply_text("go away")

    def parse_send_messages(context):
        threads = parse()

        for thread in threads:

            ext = os.path.splitext(urlparse(thread.files[0]).path)[1]  
            print(thread.files, ext)                

            if thread.files:
                __get_media(thread.files[0], ext)
            
            send_as_caption = True if len(thread.text[0]) <= MAX_CAPTION_LENGTH else False
            sending_method = __get_sending_method(ext)

            if sending_method:
                if send_as_caption:
                    sending_method(CHAT_ID, open("buffer" + ext, "rb"), caption=thread.text[0], parse_mode=ParseMode.MARKDOWN, timeout=DEFAULT_TIMEOUT)
                else:
                    sending_method(CHAT_ID, open("buffer" + ext, "rb"), timeout=DEFAULT_TIMEOUT)
                    for chunk in thread.text:
                        updater.bot.send_message(CHAT_ID, chunk, parse_mode=ParseMode.MARKDOWN, timeout=DEFAULT_TIMEOUT)
            else:
                for chunk in thread.text:
                    updater.bot.send_message(CHAT_ID, chunk, parse_mode=ParseMode.MARKDOWN, timeout=DEFAULT_TIMEOUT)

            
            os.remove("buffer" + ext)
            
    updater = Updater(TOKEN, use_context=True)

    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(CommandHandler('fetch', fetch_messages, pass_job_queue=True))

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()