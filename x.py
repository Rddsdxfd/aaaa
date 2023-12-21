import telebot
from telebot import types
import cv2
import numpy as np
import requests
import tempfile
import os
import hashlib

bot = telebot.TeleBot("6804743920:AAGRDbPzDL84SGTGRrg509-uFUz6eUoiW8c")
ocr_api_key = "K83630869488957"

@bot.message_handler(content_types=['video'])
def handle_video(message):
    try:
        file_info = bot.get_file(message.video.file_id)
        
        if message.video.file_size > 10 * 1024 * 1024:
            bot.reply_to(message, "The video is too large.")
            return
        
        downloaded_file = bot.download_file(file_info.file_path)
        nparr = np.frombuffer(downloaded_file, np.uint8)
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as temp_video_file:
            temp_video_file.write(nparr)
            temp_video_file_path = temp_video_file.name
        
        cap = cv2.VideoCapture(temp_video_file_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        delay = int(1000 / fps) if fps > 0 else 0
        
        extracted_text = []
        seen_hashes = set()

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            frame_hash = hashlib.md5(frame.tobytes()).hexdigest()
            if frame_hash in seen_hashes:
                continue
            seen_hashes.add(frame_hash)

            h, w = frame.shape[:2]
            subtitle_frame = frame[int(h * 0.8):h, 0:w]

            with tempfile.NamedTemporaryFile(suffix='.jpg') as temp_image_file:
                cv2.imwrite(temp_image_file.name, subtitle_frame)
                temp_image_file.seek(0)
                response = requests.post(
                    'https://api.ocr.space/parse/image',
                    files={'image': temp_image_file},
                    data={'apikey': ocr_api_key}
                )
                result = response.json()

                # Check if 'ParsedResults' exists and is not empty
                if 'ParsedResults' in result and result['ParsedResults']:
                    parsed_text = result['ParsedResults'][0].get('ParsedText', '')
                    
                    # Check if 'ParsedText' is not empty
                    if parsed_text:
                        extracted_text.append(parsed_text)

            # Enforce the frame rate restriction
            cv2.waitKey(delay)

        cap.release()
        os.unlink(temp_video_file_path)

        chunk_size = 4096  # Define your desired chunk size

        if not extracted_text:
            bot.reply_to(message, "No subtitles were found in the video.")
        else:
            for chunk in [extracted_text[i:i+chunk_size] for i in range(0, len(extracted_text), chunk_size)]:
                bot.reply_to(message, '\n'.join(chunk))
    except Exception as e:
        bot.reply_to(message, f"An error occurred: {str(e)}")

bot.polling(non_stop=True, interval=0)

