from langchain import PromptTemplate, LLMChain
from langchain.chains import ConversationChain
from langchain.chat_models import ChatOpenAI
import telebot

from utils import get_environment_variable


BOT_TOKEN = get_environment_variable("BOT_TOKEN")
OPENAI_API_KEY = get_environment_variable("OPENAI_API_KEY")

START_COMMANDS = ["start", "hi"]
END_COMMANDS = ["end", "bye"]

bot = telebot.TeleBot(BOT_TOKEN)

conversations = {}

@bot.message_handler(commands=START_COMMANDS)
def send_welcome(message: telebot.types.Message):
    """
    Respond to the '/empezar' and '/hola' commands with a welcome message.

    Args:
        message (telebot.types.Message): The message object representing the user's command.
    """
    welcome_message = "Hola, soy un bot inteligente. Hablemos de lo que quieras 😊"
    bot.reply_to(message, welcome_message)


@bot.message_handler(commands=END_COMMANDS)
def send_goodbye(message: telebot.types.Message):
    """
    Respond to the '/end' and '/bye' commands with a welcome message.

    Args:
        message (telebot.types.Message): The message object representing the user's command.
    """
    user_id = message.chat.id
    if user_id in conversations:
     del conversations[user_id]  
    goodbye_message = "Chao, ¡nos vemos pronto! 😉"
    bot.reply_to(message, goodbye_message)


@bot.message_handler(content_types=["text"])
def process_openai_step(message: telebot.types.Message):
    """
    Process the message and respond using OpenAI

    Args:
        message (Message): The user's message.
    Returns:
        None
    """
    try:
        user_id = message.chat.id
        msg_text = message.text

        if user_id not in conversations:
            chat = ChatOpenAI(model_name="gpt-3.5-turbo", openai_api_key=OPENAI_API_KEY)            
            conversations[user_id] =  ConversationChain(llm=chat)
        conversation = conversations[user_id]

        reply_message = conversation.run(msg_text)
        msg = bot.reply_to(message, reply_message)

    except Exception as e:
        bot.reply_to(message, 'Upsi, ha debido de haber algún problema')


bot.enable_save_next_step_handlers(delay=2)
bot.load_next_step_handlers()
bot.infinity_polling()
