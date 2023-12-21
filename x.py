import telebot
from telebot import types
import tempfile
import os
from pytube import YouTube
# ffmpeg-python package should be imported as ffmpeg, not ffmpeg
# Check if pysubs2 is necessary as it's not used in extracting subtitles from videos directly
# import pysubs2

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
        if "youtube.com" in video_url or "youtu.be" in video_url: # Added "youtu.be" condition for shortened URLs
            temp_dir = tempfile.mkdtemp() # Use mkdtemp to create a temp directory
            temp_video_path = os.path.join(temp_dir, "video.mp4")  # Use the temp directory
            if download_youtube_video(video_url, temp_video_path):
                # Comments regarding subtitles extraction which is non-trivial with pytube alone
                # Subtitles extraction would require additional processing not shown in this code
                # The ffmpeg command attempts to copy subtitle streams from the input which might not exist
                # If the goal is to download auto-generated subtitles (closed captions), it will require a different approach
                # Assuming a function 'extract_subtitles' exists for subtitle extraction taking video path
                
                # Dummy function to represent subtitle extraction, replace with actual functionality
                def extract_subtitles(video_path):
                    # Placeholder for extracting subtitles
                    # This should be replaced with actual subtitle extraction logic
                    return "Subtitles extraction is not implemented."

                extracted_text = extract_subtitles(temp_video_path)

                # Clean up temporary files
                os.unlink(temp_video_path)  # delete temporary video file
                # Remove the entire directory now, not just files
                os.rmdir(temp_dir)

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
