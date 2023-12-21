import telebot
import tempfile
import os
import shutil  # Import shutil for rmtree
from pytube import YouTube

bot = telebot.TeleBot("6804743920:AAGRDbPzDL84SGTGRrg509-uFUz6eUoiW8c")

def download_youtube_video(video_url, output_path):
    try:
        yt = YouTube(video_url)
        video_stream = yt.streams.filter(file_extension="mp4").first()
        video_stream.download(output_path)
        return True
    except Exception as e:
        print(f"An error occurred while downloading the video: {str(e)}")
        return False

@bot.message_handler(content_types=['text'])
def handle_text(message):
    try:
        video_url = message.text.strip()
        if "youtube.com" in video_url or "youtu.be" in video_url:
            # Use mkdtemp to create a temp directory
            temp_dir = tempfile.mkdtemp()
            temp_video_path = os.path.join(temp_dir, "video.mp4")  # Use the temp directory

            if download_youtube_video(video_url, temp_video_path):
                # Dummy function to represent subtitle extraction, replace with actual functionality
                def extract_subtitles(video_path):
                    # Placeholder for extracting subtitles
                    # This should be replaced with actual subtitle extraction logic
                    return "Subtitles extraction is not implemented."

                extracted_text = extract_subtitles(temp_video_path)

                # Clean up temporary files and the directory
                shutil.rmtree(temp_dir)

                bot.send_message(message.chat.id, extracted_text)
            else:
                bot.send_message(message.chat.id, "Failed to download the YouTube video.")
        else:
            bot.send_message(message.chat.id, "Please provide a valid YouTube video URL.")
    except Exception as e:
        error_message = f"An error occurred: {str(e)}"
        bot.send_message(message.chat.id, error_message)

# Start bot polling
bot.polling(non_stop=True, interval=0)
                                                  
