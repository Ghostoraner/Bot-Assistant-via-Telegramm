import telebot
import __logging__ as log
import __assistant_gpt__ as assistant
import __working_search__

working_search=__working_search__.working_search()
protect=dict()
user_msg_assistant=dict()

logger=log.Logger()
bot = telebot.TeleBot("7852439023:AAHhHkQ-vli6qJhytR-zJl9FOIgWVogfk0c")
# Bot user name @name_itfriends_bot
@bot.message_handler(content_types=['text'])
def Assistant_Exchange(message):
    text=str()
    markup = telebot.types.ReplyKeyboardMarkup(True)
    if message.text in ["/start","Back"]:
        text+="Hi, I Assistant Exchange Bot\nPlace select function"
        markup.add(
            telebot.types.KeyboardButton("Assistant GPT"),
            telebot.types.KeyboardButton("Working Search"),
            telebot.types.KeyboardButton("Tasks"),
            telebot.types.KeyboardButton("Planers"),
            telebot.types.KeyboardButton("Setting"),
            telebot.types.KeyboardButton("Info")
        )
        protect[f"{message.chat.id}"]=True
    elif message.text=="Assistant GPT" and protect[f"{message.chat.id}"]==True:
        text+="Place enter message to gpt"
        markup.add(
            telebot.types.KeyboardButton("Back")
        )
    else:
        text=assistant.Assistant(message.text).__result__()
        markup.add(
            telebot.types.KeyboardButton("Back")
        )
    bot.send_message(message.chat.id,text,reply_markup=markup)
if __name__ == '__main__':
    logger.info('Started Assistant Exchange')
    bot.infinity_polling()
