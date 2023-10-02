import telebot
from utils import get_environment_variable

import os
import requests
import openai



def transcribe_audio_with_openai(audio_file, model="whisper-1"):
    transcript = openai.Audio.transcribe(model, audio_file)
    return transcript.to_dict()["text"]

def get_telegram_file_url(bot_token:str, file_info):
    return f"https://api.telegram.org/file/bot{bot_token}/{file_info.file_path}"

def download_file(file_url:str, savedir:str):
    exists = os.path.exists(savedir)
    if not exists:
        os.makedirs(savedir)         
    response = requests.get(file_url, allow_redirects=True)
    if response.ok: 
        filename = _get_filename_from_url(file_url)
        savepath = f"{savedir}/{filename}"
        open(savepath,'wb').write(response.content)
        return savepath
    
def _get_filename_from_url(url:str):
    return url.split('/')[-1]


from langchain import PromptTemplate, LLMChain

from langchain.chat_models import ChatOpenAI


BOT_TOKEN = get_environment_variable("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

def summarize_text(text):
    template = """Resumen el siguiente texto de forma que me des los puntos principales que se tratan en el texto: {text}.
    Dame la respuesta enumerando los diferentes puntos. Answer:"""
    
    prompt = PromptTemplate(template = template, input_variables = ['text'])

    model_name = "gpt-3.5-turbo"
    model = ChatOpenAI(model_name=model_name)

    llm_chain = LLMChain(
        prompt=prompt,
        llm=model
    )

    return llm_chain.run(text)

@bot.message_handler(commands=['start', 'hi'])
def send_welcome(message: telebot.types.Message):
    """
    Respond to the '/start' and '/hi' commands with a welcome message.

    Args:
        message (telebot.types.Message): The message object representing the user's command.
    """
    welcome_message = "Hola, si has llegado hasta aquí es que ya soy un bot súper inteligente... ¡Ahora además puedo entender tus audios y transcribirlos (/transcribe)! ¡Haz la prueba y envíame uno! 😊"
    bot.reply_to(message, welcome_message)


@bot.message_handler(commands=['end', 'bye'])
def send_goodbye(message: telebot.types.Message):
    """
    Respond to the '/end' and '/bye' commands with a welcome message.

    Args:
        message (telebot.types.Message): The message object representing the user's command.
    """
    goodbye_message = "Chao, espero que la última demo haya salido bien 🤗"
    bot.reply_to(message, goodbye_message)

@bot.message_handler(content_types=['voice', 'video_note'])
def handle_voice_message(message):
    file_info = bot.get_file(message.voice.file_id)
    audio_url = get_telegram_file_url(bot.token, file_info)
    save_dir = "../data/audios/"
    audio_filepath = download_file(audio_url, save_dir)
    audio_file= open(audio_filepath, "rb")
    text = transcribe_audio_with_openai(audio_file)
    bot.reply_to(message, f"Me integraré con la demo 2 con este texto: {text}")

@bot.message_handler(commands=['transcribe'])
def handle_audio_transcription(message):
    transcribe_audio_message = "¡Perfecto! Envíame el audio que deseas transcribir 🔊✍️"
    msg = bot.reply_to(message, transcribe_audio_message)
    bot.register_next_step_handler(msg, transcribe_audio)

def transcribe_audio(message):
    file_info = bot.get_file(message.audio.file_id)
    audio_url = get_telegram_file_url(bot.token, file_info)
    save_dir = "../data/audios/"
    audio_filepath = download_file(audio_url, save_dir)
    audio_file= open(audio_filepath, "rb")
    text = transcribe_audio_with_openai(audio_file)
    bot.reply_to(message, f"Aquí está tu transcripción: \n {text}. \n ¿Quieres hacer algo más con ella? 🧐")
    bot.register_next_step_handler(message, handle_transcription_tasks, transcription=text)

def handle_transcription_tasks(message, transcription):
    task = message.text
    if task == "Resumir":
        summary = summarize_text(transcription)
        bot.reply_to(message, f"Aquí está el resumen: \n {summary}")
    else:
        bot.reply_to("¡Perfecto!")

bot.enable_save_next_step_handlers(delay=2)
bot.load_next_step_handlers()
bot.infinity_polling()