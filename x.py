import telebot
from telebot import types
import cv2
import numpy as np
import pytesseract
import re
import tempfile
import os

bot = telebot.TeleBot("6804743920:AAGRDbPzDL84SGTGRrg509-uFUz6eUoiW8c")

# ... (other parts of your code)

@bot.message_handler(content_types=['video'])
def handle_video(message):
    try:
        file_info = bot.get_file(message.video.file_id)
        
        if message.video.file_size > 10 * 1024 * 1024:
            bot.send_message(message.chat.id, "The video is too large.")
            return
        
        downloaded_file = bot.download_file(file_info.file_path)
        nparr = np.frombuffer(downloaded_file, np.uint8)
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as temp_file:
            temp_file.write(nparr)
            temp_filename = temp_file.name

        cap = cv2.VideoCapture(temp_filename)
        extracted_text = []

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            # Crop to the lower part of the frame where subtitles usually are
            # You would have to determine these values by the resolution of your video
            h, w = frame.shape[:2]
            y1 = int(h * 0.8)  # start at 80% of the height
            y2 = h  # go to the bottom of the frame
            subtitle_frame = frame[y1:y2, 0:w]

            # Use pytesseract to extract text
            text = pytesseract.image_to_string(subtitle_frame, lang='eng')  # Assuming subtitles are in English

            # Clean and extract the text
            text = text.strip()  # Remove whitespace
            if text:  # If there's text, add it to the list
                extracted_text.append(text)

        cap.release()
        os.unlink(temp_filename)  # Delete the temporary file

        # Send the extracted text back as a message
        if not extracted_text:
            bot.send_message(message.chat.id, "No subtitles were found in the video.")
        else:
            bot.send_message(message.chat.id, '\n'.join(extracted_text))
    except Exception as e:
        bot.send_message(message.chat.id, f"An error occurred: {str(e)}")

# ... (rest of your code)

# Start bot polling
bot.polling(non_stop=True, interval=0)
