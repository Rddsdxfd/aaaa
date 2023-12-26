import telebot
from subtitle_parser import SubtitleParser

bot = telebot.TeleBot("6804743920:AAGRDbPzDL84SGTGRrg509-uFUz6eUoiW8c")

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Hello! Send me a video file and I will extract the subtitles.")

@bot.message_handler(content_types=['video']) 
def get_subtitles(message):
    try:
        video = bot.get_file(message.video.file_id)
        downloaded_video = bot.download_file(video.file_path)
        
        parser = SubtitleParser(downloaded_video)
        subtitles = parser.extract_subtitles()
        
        for text in subtitles:
            bot.send_message(message.chat.id, text)
            
    except Exception as e:
        bot.reply_to(message, 'Error processing video: ' + str(e))
        bot.reply_to(message, 'Please send file again or contact admin if issue persists.')

bot.polling()
