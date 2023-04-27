from datetime import datetime, timedelta
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, ConversationHandler, MessageHandler, Filters
import cv2 as cv
import numpy  as np
import serial
import time
print("-----------------------------------------|")
print('|                                        |')
print("|            TRAVERSIFY                  |")
print('|                                        |')
print("|----------------------------------------|")
print()
queue=[]
ard=serial.Serial("COM5",9600)
print("Starting the server and  connected to the microcontroller")
for i in range(10):
    print(".")
    time.sleep(0.2)
print('Server started ,Bot is online now')

TOKEN = "6128687544:AAGCwXVjOeYUPSbGBQ4qkVJU5ab9R8Yi-Bo"
logged = set()
PASSWORD, CHOOSING = range(2)
ban_list = []
sessionLimit=(60*30)

def check_password(update, context):
    if len(logged)>1:
        update.message.reply_text("User limit exceeded ,only 3 user can access the bot at time ")
        return ConversationHandler.END

    password = "mypassword"
    user_password = update.message.text
    if user_password == password:
        logged.add(update.message.chat_id)
        update.message.reply_text("Password correct! Please choose one of the following options:",
                                  reply_markup=ReplyKeyboardMarkup(
                                      [['Light on', 'Light off'], ['Cam 1'], ['logout', 'Automode'],
                                       ['Fan on', 'Fan off']], one_time_keyboard=False))
        context.user_data['session_start_time'] = datetime.now()
        return CHOOSING
    else:
        if 'attempts' not in context.chat_data:
            context.chat_data['attempts'] = 1
        else:
            context.chat_data['attempts'] += 1
        if context.chat_data['attempts'] >= 3:
            ban_list.append(update.effective_chat.id)
            update.message.reply_text("You have entered the wrong password too many times. You are now banned.")
            return ConversationHandler.END
        else:
            update.message.reply_text("Wrong password. Please try again.")
            return PASSWORD


# Define the function to handle the choices
def choices(update, context):
    choice = update.message.text
    id = update.message.chat_id
    if (id not in logged):
        update.message.reply_text("You are not logged in ,please login by clicking :- /start ")
        return ConversationHandler.END
    session_start_time = context.user_data.get('session_start_time')
    if session_start_time is None or datetime.now() > session_start_time + timedelta(seconds=sessionLimit):
        update.message.reply_text(
            "Your session has expired. Please log in again to continue,click here to login /start .")
        return ConversationHandler.END
    queue.append(choice)

        if choices== 'Light on':
            update.message.reply_text("You turned the light on.")
            write(str(4))
        elif choice == 'Light off':
            update.message.reply_text("You turned the light off.")
            write(str(4))
        elif choice == 'Cam 1':
            update.message.reply_text("sending you pic in 5 seconds.")
            Takephoto(update, context)
        elif choice == 'Automode':
            update.message.reply_text("You enabled automatic mode.")
        elif choice == 'Fan on':update.message.reply_text("You turned the fan on.")

        elif choice == 'Fan off':
            update.message.reply_text("You turned the fan off.")
        elif choice == 'logout':
            logged.remove(id)
            update.message.reply_text('you logged out,see you later ')


def unknown(update, context):
    if update.effective_chat.id in ban_list:
        update.message.reply_text("You are no longer registered.")
    else:
        update.message.reply_text("Sorry, I didn't understand that command.")


# Define the function to start the conversation
def start(update, context):
    update.message.reply_text("Please enter the password:")
    return PASSWORD


def cancel(update, context):
    user = update.message.from_user
    update.message.reply_text("Conversation canceled.",
                              reply_markup=ReplyKeyboardRemove())


# return ConversationHandler.END
def Takephoto(update,context):
    cam = cv.VideoCapture(0)
    res, im = cam.read()
    if res:
        cam.release()
        v,en=cv.imencode(".jpg",im)
        pb=np.array(en).tobytes()
        ci=update.message.chat_id
        context.bot.send_photo(chat_id=ci,photo=pb)
        print("photo taken and send ")
    else:
        update.message.reply_text("try again after 10 seconds ")

def write(cmd):
    ard.write(cmd.encode())
def read ():
    data=ard.readline().decode("utf-8").strip()
    return data

# Define the main function
def main():

    updater = Updater(TOKEN, use_context=True)

    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            PASSWORD: [MessageHandler(Filters.text & ~Filters.command, check_password)],
            CHOOSING: [
                MessageHandler(Filters.regex('^(Light on|Light off|Cam 1|/start|Automode|Fan on|Fan off|logout)$'),
                               choices)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dp.add_handler(conv_handler)
    updater.start_polling()
    updater.idle()


if __name__=="__main__":
    main()
