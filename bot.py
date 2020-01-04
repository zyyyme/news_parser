from telegram.ext import Updater, CommandHandler, JobQueue
from telegram import InputMediaAnimation, InputMediaPhoto, InputMediaVideo, ParseMode
import logging
import urllib
from datetime import datetime
from parser import parse_threads
import os


def _retrieve_op_files(files):
    local_files = []
    
    if not files:
        return []
    
    for file in files:
        filename = file.split('/')[-1]
        urllib.request.urlretrieve("https://2ch.hk" + file, filename)
        
        local_files.append(filename)

    return local_files

def _send_op_files_and_text(op_files, text):
    send_with_media_group = False
    media_group = []

    if len(op_files) > 1:
        send_with_media_group = True

    for file in op_files:
        extension = file.split('.')[-1]
        byte_file = open(file, 'rb')

        if send_with_media_group:
            if extension in IMAGE_EXTENSIONS:
                media_group.append(InputMediaPhoto(media=byte_file))
            elif extension in ANIMATED_EXTENSIONS:
                media_group.append(InputMediaAnimation(media=byte_file))
            elif extension in VIDEO_EXTENSIONS:
                media_group.append(InputMediaVideo(media=byte_file))
        else:
            if extension in IMAGE_EXTENSIONS:
                UPDATER.bot.send_photo(chat_id=CHAT_ID, 
                                       photo=byte_file)
            elif extension in ANIMATED_EXTENSIONS:
                UPDATER.bot.send_animation(chat_id=CHAT_ID,
                                           animation=byte_file)    
            elif extension in VIDEO_EXTENSIONS:
                UPDATER.bot.send_video(chat_id=CHAT_ID,
                                       video=byte_file)

    if send_with_media_group:
        UPDATER.bot.send_media_group(chat_id=CHAT_ID,
                                     media=media_group, timeout=30)

    for file in op_files:
        os.remove(file)
    
    UPDATER.bot.send_message(chat_id=CHAT_ID, text=text, parse_mode=ParseMode.MARKDOWN, timeout=30)


def send_messages(context):
    print('parsing')
    threads = parse_threads()
    for thread in threads:
        text = f"*{thread.subject}*\n\n" \
               f"{thread.text}\n" \
               f"[ТРЕД]({thread.link})"
        
        op_files = _retrieve_op_files(thread.op_files)
        _send_op_files_and_text(op_files, text)
        

def fetch_messages(update, context):
    update.message.reply_text("Fetching")
    context.job_queue.run_repeating(send_messages, 3600, first=datetime.now(), context=update)


if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
    logger = logging.getLogger(__name__)

    with open('token', 'r') as token_file:
        TOKEN = str(token_file.read().strip())

    REQUEST_KWARGS={
        'proxy_url': 'socks5://orbtl.s5.opennetwork.cc:999',
        'urllib3_proxy_kwargs': {
            'username': '1305759',
            'password': 'ZJ0mPA1A',
        }
    }

    CHAT_ID = '@asdfasdfasdfsadfasdf'
    IMAGE_EXTENSIONS = ['jpg', 'jpeg', 'png']
    ANIMATED_EXTENSIONS = ['gif']
    VIDEO_EXTENSIONS = ['webm', 'mp4']

    UPDATER = Updater(TOKEN, use_context=True, request_kwargs=REQUEST_KWARGS)
    UPDATER.dispatcher.add_handler(CommandHandler('fetch', fetch_messages, pass_job_queue=True))

    print('Polling!')
    
    UPDATER.start_polling()
    UPDATER.idle()
