import telebot
import speech_recognition as sr  
import torch
import torchaudio
from torchaudio.transforms import MelSpectrogram  

bot = telebot.TeleBot("6804743920:AAGRDbPzDL84SGTGRrg509-uFUz6eUoiW8c")

# Model and training 
vocab = ["hi", "hello", "goodbye", "how", "are", "you", "doing", "thanks", "thank", "bye"]
text_to_idx = {word: i for i, word in enumerate(vocab)}

model = torch.nn.LSTM(input_size=40, hidden_size=20, num_layers=2, batch_first=True, dropout=0.1)
model.flatten_parameters()
optimizer = torch.optim.Adam(model.parameters()) 
loss_fn = torch.nn.CrossEntropyLoss()

mel_transform = MelSpectrogram(sample_rate=16000, n_mels=40)

def text_to_target(text):
    indexes = [text_to_idx.get(word, len(vocab)-1) for word in text.split(" ")]
    return torch.tensor(indexes)

def get_features(file):
    waveform, _ = torchaudio.load(file)
    return mel_transform(waveform)

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id,  
        "Hi! I'm a bot that can learn from your voice. Send me a voice message and text of what you said to train me.")

@bot.message_handler(content_types=['voice']) 
def handle_voice(message):
    file_info = bot.get_file(message.voice.file_id)
    file = bot.download_file(file_info.file_path)
    
    try:
        features = get_features(file)
    except Exception as e:
        bot.reply_to(message, "Error getting audio features: " + str(e)) 
        return
    
    recognizer = sr.Recognizer()
    try:
        with sr.AudioFile(file) as source:
            audio = recognizer.record(source)  
        text = recognizer.recognize_google(audio) 
    except Exception as e:  
        bot.reply_to(message, "Error recognizing text: " + str(e))
        return
            
    try:
        targets = text_to_target(text) 
    except Exception as e:
        bot.reply_to(message, "Error converting text: " + str(e))
        return
            
    loss = train_step(features, targets)
            
    bot.reply_to(message, f"Thanks for the audio! Loss after training: {loss:.3f}")
    
def train_step(inputs, targets):
    outputs = model(inputs.unsqueeze(0))
    loss = loss_fn(outputs.transpose(1, 2), targets.unsqueeze(0))
    
    model.zero_grad()
    loss.backward()
    optimizer.step()
    
    return loss.item()
    
bot.polling()
