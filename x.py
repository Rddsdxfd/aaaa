import telebot
from telebot import types
import cv2
import numpy as np
import pytesseract
import tempfile
import os
import re
from contextlib import contextmanager

bot = telebot.TeleBot("6804743920:AAGRDbPzDL84SGTGRrg509-uFUz6eUoiW8c")

@bot.message_handler(content_types=['video'])
def handle_video(message):
    try:
        # Restriction on video file size (>10MB)
        if message.video.file_size > 10 * 1024 * 1024:  # 10MB limit
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("I understand", callback_data="understand"))
            bot.send_message(message.chat.id, "The video is too large.", reply_markup=markup)
            return
        
        file_info = bot.get_file(message.video.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        nparr = np.frombuffer(downloaded_file, np.uint8)
        with temporary_file(nparr) as temp_filename:
            extracted_text = extract_text_from_video(temp_filename)
            bot.send_message(message.chat.id, '\n'.join(extracted_text) if extracted_text else "No text found.")
    
    except Exception as e:
        bot.send_message(message.chat.id, f"Error: {e}")

@contextmanager
def temporary_file(nparr):
    try:
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
        temp_file.write(nparr)
        temp_file.close()
        yield temp_file.name
    finally:
        os.unlink(temp_file.name)

def extract_text_from_video(temp_filename, frame_limit_per_second=25):
    cap = cv2.VideoCapture(temp_filename)
    extracted_text = []
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_interval = int(fps / frame_limit_per_second)

    frame_count = 0
    while cap.isOpened():
        success, frame = cap.read()
        if not success: break

        # Preprocessing for subtitle detection here (resize, grayscale, thresholding, etc.)
        # ...

        frame_id = int(round(cap.get(cv2.CAP_PROP_POS_FRAMES)))
        if frame_id % frame_interval == 0:
            text = pytesseract.image_to_string(frame, lang='rus')
            text = re.sub(r'[\W_]+', ' ', text, flags=re.UNICODE)
            extracted_text.append(text.strip())
        
            frame_count += 1
            if frame_count >= frame_limit_per_second:
                break
    
    cap.release()
    # Postprocessing to remove duplicates and non-subtitle text
    return [line for line in set(extracted_text) if line]

# ... (rest of your code)

# Start bot polling
bot.polling(non_stop=True, interval=0)
        
