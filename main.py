import time
import telebot
from flask import Flask
from threading import Thread

# Initialize the bot
bot = telebot.TeleBot('6034033651:AAEgAKMJFoam1NdLSApB9ynBUck3NJJJKAk')

# Global variable to keep track of the current sequence number
current_number = 0
running = False

# Flask app for keeping the script alive
app = Flask('')

@app.route('/')
def home():
    return "Bot is running!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# Function to generate and send the sequence
def generate_sequence(chat_id, start_number):
    global current_number
    global running

    current_number = start_number - 1
    running = True

    while running:
        current_number += 1
        response = f"/get {current_number}"
        try:
            message = bot.send_message(chat_id, response)
        except telebot.apihelper.ApiTelegramException as e:
            if e.error_code == 429:
                retry_after = int(e.response.headers.get('Retry-After'))
                time.sleep(retry_after)
                continue
            else:
                raise

        time.sleep(1)

        with open("sequence_number.txt", "w") as file:
            file.write(str(current_number))

        # Schedule the next sequence after a fixed interval (e.g., 2 second)
        time.sleep(4)



# Handler for the /start command
@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.reply_to(message, "Hello! Mava start cheddama.")

# Handler for the /get command
@bot.message_handler(commands=['get'])
def handle_get(message):
    global running

    if not running:
        try:
            start_number = int(message.text.split()[1])
            generate_sequence(message.chat.id, start_number)
        except IndexError:
            bot.reply_to(
                message,
                "Invalid command. Please use /get <number> to start the sequence.")
        except ValueError:
            bot.reply_to(message, "Invalid number. Please use a valid integer.")
    else:
        bot.reply_to(
            message,
            "The bot is already running. Use /stop to stop the current sequence.")

# Handler for the /stop command
@bot.message_handler(commands=['stop'])
def handle_stop(message):
    global running
    running = False
    bot.reply_to(message, "The bot has been stopped.")

# Handler for any other message
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    bot.reply_to(message, "Invalid command. Please use /get <number> or /stop.")

# Start the bot
bot.polling()
