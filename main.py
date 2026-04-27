import os
import telebot
from openai import OpenAI
from flask import Flask
from threading import Thread

# 1. Setup Environment Variables
BOT_TOKEN = os.environ.get('BOT_TOKEN')
HF_TOKEN = os.environ.get('HF_TOKEN')

# 2. Initialize Clients
bot = telebot.TeleBot(BOT_TOKEN)
client = OpenAI(
    base_url="https://router.huggingface.co/v1",
    api_key=HF_TOKEN
)

# 3. Flask Server for Render (Keep-Alive)
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

def run_flask():
    # Render provides a PORT environment variable
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# 4. Telegram Bot Logic
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    try:
        # Show "typing..." status while waiting for AI
        bot.send_chat_action(message.chat.id, 'typing')

        # Call Hugging Face Router
        chat_completion = client.chat.completions.create(
            model="deepseek-ai/DeepSeek-V3", # You can use the model name provided in your snippet
            messages=[
                {"role": "user", "content": message.text}
            ],
            max_tokens=500
        )

        # Get response text
        response_text = chat_completion.choices[0].message.content
        bot.reply_to(message, response_text)

    except Exception as e:
        print(f"Error: {e}")
        bot.reply_to(message, "Sorry, I'm having trouble processing that right now.")

# 5. Start both Flask and Bot
if __name__ == "__main__":
    # Start Flask in a separate thread
    flask_thread = Thread(target=run_flask)
    flask_thread.start()

    # Start Bot Polling
    print("Bot is starting...")
    bot.infinity_polling()
