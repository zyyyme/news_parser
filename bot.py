import os
import sys
import logging
import datetime

import urllib
import telegram.constants

from PIL import Image
from telegram.ext import Updater, CommandHandler, JobQueue
from telegram import InputMediaAnimation, InputMediaPhoto, InputMediaVideo, ParseMode

from parser import parse_threads


def _retrieve_op_files(files):
    local_files = []
    
    if not files:
        return []
    
    for file in files:
        filename = file.split('/')[-1]
        urllib.request.urlretrieve("https://2ch.hk" + file, filename)
        
        local_files.append(filename)

    return local_files

def _compress_image(image):
    img = Image.open(file)
    img.save(file, optimize=True, quality=85)
    return open(file, 'rb')

def __prepare_media_files(op_files):
    media_group = []

    for file in op_files:
        extension = file.split('.')[-1]
        byte_file = open(file, 'rb')

        if extension in IMAGE_EXTENSIONS:
            if extension in IMAGE_EXTENSIONS and os.path.getsize(file) > telegram.constants.MAX_FILESIZE_UPLOAD / 8:
                byte_file = _compress_image(file)
            
            media_group.append(InputMediaPhoto(media=byte_file))
        elif extension in VIDEO_EXTENSIONS:
            media_group.append(InputMediaVideo(media=byte_file))
    
    return media_group


def __prepare_text_chunks(text):
    return [text[i:i + telegram.constants.MAX_MESSAGE_LENGTH] for i in range(0, len(text), telegram.constants.MAX_MESSAGE_LENGTH)]


def __get_sending_method(extension):
    image_mapper = [(ext, UPDATER.bot.send_photo) for ext in IMAGE_EXTENSIONS]
    animation_mapper = [(ext, UPDATER.bot.send_animation) for ext in ANIMATED_EXTENSIONS]
    video_mapper = [(ext, UPDATER.bot.send_video) for ext in VIDEO_EXTENSIONS]
    
    extension_to_method = dict(image_mapper + animation_mapper + video_mapper)
    return extension_to_method.get(extension)


def _send_op_files_and_text(op_files, text):
    send_with_media_group = False
    send_as_caption = True if len(text) <= telegram.constants.MAX_CAPTION_LENGTH else False
    send_as_one_chunk = True if len(text) <= telegram.constants.MAX_MESSAGE_LENGTH else False

    if len(op_files) > 1:
        send_with_media_group = True
        media_group = __prepare_media_files(op_files)
        sending_method = UPDATER.bot.send_media_group
    else:
        file = op_files[0]
        extension = file.split('.')[-1]

        if extension in IMAGE_EXTENSIONS and os.path.getsize(file) > telegram.constants.MAX_FILESIZE_UPLOAD / 8:
            byte_file = _compress_image(file)
        
        byte_file = open(file, 'rb')
        
        sending_method = __get_sending_method(extension)

    media_to_send = media_group if send_with_media_group else byte_file

    if send_as_caption:
        sending_method(CHAT_ID, media_to_send, caption=text, parse_mode=ParseMode.MARKDOWN, timeout=DEFAULT_TIMEOUT)
    elif send_as_one_chunk:
        sending_method(CHAT_ID, media_to_send, timeout=DEFAULT_TIMEOUT)
        UPDATER.bot.send_message(CHAT_ID, text, parse_mode=ParseMode.MARKDOWN, timeout=DEFAULT_TIMEOUT)
    else:
        text = __prepare_text_chunks(text)
        sending_method(CHAT_ID, media_to_send, timeout=DEFAULT_TIMEOUT)
        
        for chunk in text:
            UPDATER.bot.send_message(CHAT_ID, chunk, parse_mode=ParseMode.MARKDOWN, timeout=DEFAULT_TIMEOUT)
    
    for file in op_files:
        os.remove(file)


def send_messages(context):
    print('parsing')
    threads = parse_threads()
    for thread in threads:
        new_lines_before_link = '\n'

        if thread.text[-1] != '\n':
            new_lines_before_link += '\n'
        elif thread.text[-2] == '\n' and thread.text[-1] == '\n':
            new_lines_before_link = ''

        text = f"*{thread.subject}*\n\n" \
               f"{thread.text}{new_lines_before_link}" \
               f"[ТРЕД]({thread.link})"

        print('Text: ', text)
        
        op_files = _retrieve_op_files(thread.op_files)
        _send_op_files_and_text(op_files, text)
        

def fetch_messages(update, context):
    update.message.reply_text("Fetching")
    context.job_queue.run_repeating(send_messages, 60, first=datetime.datetime.now(), context=update)



if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
    logger = logging.getLogger(__name__)
    testing = True if len(sys.argv) > 1 and sys.argv[1] == 'localhost' else False
    with open('token', 'r') as token_file:
        TOKEN = str(token_file.read().strip())

    CHAT_ID = '@zxbmaskjdfhasgdkh' if testing else '@asdfasdfasdfsadfasdf'
    IMAGE_EXTENSIONS = ['jpg', 'jpeg', 'png', 'jfif']
    ANIMATED_EXTENSIONS = ['gif']
    VIDEO_EXTENSIONS = ['webm', 'mp4']
    DEFAULT_TIMEOUT = 60

    UPDATER = Updater(TOKEN, use_context=True)
    UPDATER.dispatcher.add_handler(CommandHandler('fetch', fetch_messages, pass_job_queue=True))
    
    if testing:
        print('===============================  TESTING  ===============================')
    
    print('Polling!')
    
    UPDATER.start_polling()
    UPDATER.idle()
