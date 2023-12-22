import telebot
from telebot import types
import cv2
import numpy as np
import pytesseract
import tempfile
import os
import re
from contextlib import contextmanager

# Make sure "YOUR_TELEGRAM_BOT_TOKEN" is replaced with your actual bot token.
bot = telebot.TeleBot("6804743920:AAGRDbPzDL84SGTGRrg509-uFUz6eUoiW8c")

@bot.message_handler(content_types=['video'])
def handle_video(message):
    try:
        # Restriction on video file size (>10MB)
        if message.video.file_size > 10 * 1024 * 1024:  # 10MB limit
            bot.send_message(message.chat.id, "The video is too large. Please upload a video smaller than 10MB.")
            return
        
        file_info = bot.get_file(message.video.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        nparr = np.frombuffer(downloaded_file, np.uint8)
        with temporary_file(nparr) as temp_filename:
            extracted_text = extract_text_from_video(temp_filename)
            bot.send_message(message.chat.id, '\n'.join(extracted_text) if extracted_text else "No text found.")
    except Exception as e:
        bot.send_message(message.chat.id, f"An error occurred: {e}")

@contextmanager
def temporary_file(nparr):
    # Creates a temporary file to save the video for processing.
    try:
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
        temp_file.write(nparr)
        temp_file.close()
        yield temp_file.name
    finally:
        if os.path.exists(temp_file.name):
            os.unlink(temp_file.name)

def extract_text_from_video(temp_filename, frame_limit_per_second=25):
    cap = cv2.VideoCapture(temp_filename)
    extracted_text = []
    fps = cap.get(cv2.CAP_PROP_FPS)  # Gets the frames per second of the video
    frame_interval = int(max(1, fps / frame_limit_per_second))  # Avoid division by zero

    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break

        frame_id = int(cap.get(cv2.CAP_PROP_POS_FRAMES))
        if frame_id % frame_interval == 0:
            # Process the frame for OCR
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            denoised_frame = cv2.fastNlMeansDenoising(gray_frame, None, 10, 10)
            _, binary_frame = cv2.threshold(denoised_frame, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            text = pytesseract.image_to_string(binary_frame, lang='rus', config='--psm 6')  # Adjust config if needed
            text = re.sub(r'[\W_]+', ' ', text, flags=re.UNICODE)
            extracted_text.append(text.strip())

    cap.release()
    # Postprocessing to remove duplicates and non-subtitle text
    return list(set(filter(None, extracted_text)))  # Remove empty strings and duplicates

# Start bot polling
bot.polling(non_stop=True, interval=0)
