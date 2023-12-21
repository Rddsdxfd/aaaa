import telebot
from telebot import types
import tempfile
import os
import ffmpeg
import pysubs2

bot = telebot.TeleBot("6804743920:AAGRDbPzDL84SGTGRrg509-uFUz6eUoiW8c")

# ... (other parts of your code)

@bot.message_handler(content_types=['video'])
def handle_video(message):
    try:
        file_info = bot.get_file(message.video.file_id)
        
        if message.video.file_size > 10 * 1024 * 1024:
            bot.send_message(message.chat.id, "The video is too large. Please send a video that is less than 10 MB.")
            return
        
        downloaded_file = bot.download_file(file_info.file_path)
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as temp_video_file:
            temp_video_file.write(downloaded_file)
            temp_video_filename = temp_video_file.name
            
            # Extracting subtitles with ffmpeg
            with tempfile.NamedTemporaryFile(delete=False, suffix='.srt') as temp_subtitle_file:
                temp_subtitle_filename = temp_subtitle_file.name

                # Run FFmpeg to extract subtitles if they exist
                ffmpeg.input(temp_video_filename).output(temp_subtitle_filename, map='s:h', scodec='copy').run()

                if os.path.getsize(temp_subtitle_filename) > 0:
                    subs = pysubs2.load(temp_subtitle_filename, encoding='utf-8')
                    extracted_text = '\n\n'.join(sub_event.text for sub_event in subs)
                else:
                    extracted_text = "No subtitles were found in the video."

        os.unlink(temp_video_filename)  # Delete the temporary video file
        os.unlink(temp_subtitle_filename)  # Delete the temporary subtitle file

        bot.send_message(message.chat.id, extracted_text)
    except Exception as e:
        error_message = f"An error occurred while processing the video. Error details: {str(e)}"
        bot.send_message(message.chat.id, error_message)

# ... (rest of your code)

# Start bot polling
bot.polling(non_stop=True, interval=0)
