import telebot
import tempfile
import os
import shutil
import youtube_dl

bot = telebot.TeleBot("6804743920:AAGRDbPzDL84SGTGRrg509-uFUz6eUoiW8c")

def download_youtube_video(video_url, output_path):
    try:
        ydl_opts = {'outtmpl': output_path}
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])
        return True
    except Exception as e:
        print(f"An error occurred while downloading the video: {str(e)}")
        return False

def extract_subtitles(video_url):
    try:
        ydl_opts = {
            'writesubtitles': True,
            'subtitlelangs': ['en'],  # You can specify the language of subtitles
            'skip_download': True,
        }
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            result = ydl.extract_info(video_url, download=False)
            return result['subtitles']['en'][0]['content'] if 'subtitles' in result else "No subtitles found."
    except Exception as e:
        print(f"An error occurred while extracting subtitles: {str(e)}")
        return "Subtitles extraction failed."

@bot.message_handler(content_types=['text'])
def handle_text(message):
    try:
        video_url = message.text.strip()
        if "youtube.com" in video_url or "youtu.be" in video_url:
            temp_dir = tempfile.mkdtemp()
            temp_video_path = os.path.join(temp_dir, "video.mp4")

            if download_youtube_video(video_url, temp_video_path):
                extracted_text = extract_subtitles(video_url)

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

