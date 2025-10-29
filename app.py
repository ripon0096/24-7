import telebot
import random
import re
import requests
import time
from telebot import types

# Your Telegram Bot Token
TOKEN = "8360214389:AAHziXscaSDtLvXF8uDBrsN5v13noKbGBuU"
CHANNELS = ["@BotSeller25", "@DailyEarningTips25"]  # Your channel usernames

bot = telebot.TeleBot(TOKEN)

# Function to check if user is subscribed to all channels
def is_subscribed(user_id):
    for channel in CHANNELS:
        try:
            response = requests.get(f"https://api.telegram.org/bot{TOKEN}/getChatMember?chat_id={channel}&user_id={user_id}")
            data = response.json()
            status = data.get("result", {}).get("status", "")
            if status not in ["member", "administrator", "creator"]:
                return False
        except:
            return False
    return True

# Function to generate fake Canadian address
def generate_fake_address():
    # Canadian city names
    streets = ["201 James St N", "123 Maple Ave", "567 Oak St", "890 Pine Rd", "303 Birch St"]
    cities = ["Hamilton", "Toronto", "Vancouver", "Montreal", "Ottawa"]
    provinces = ["Ontario", "Quebec", "British Columbia", "Nova Scotia", "Alberta"]
    postal_codes = ["L8R 2L2", "M5A 1A1", "V6B 1A1", "H3B 1X9", "K1A 0B1"]

    # Select a random Canadian address
    street = random.choice(streets)
    city = random.choice(cities)
    province = random.choice(provinces)
    postal_code = random.choice(postal_codes)

    # Format the address string
    return f"Street: {street}\nCity/Town: {city}\nState/Province/Region: {province}\nZip/Postal Code: {postal_code}\nCountry: Canada 🇨🇦"

# Credit Card Number Generator Function
def generate_cc(bin_format):
    cc_number = bin_format
    while len(cc_number) < 15:  # 15 digit (16th digit will be the checksum)
        cc_number += str(random.randint(0, 9))

    # Calculate final digit using Luhn Algorithm
    def luhn_checksum(card_number):
        def digits_of(n):
            return [int(d) for d in str(n)]
        digits = digits_of(card_number)
        odd_digits = digits[-1::-2]
        even_digits = digits[-2::-2]
        checksum = sum(odd_digits)
        for d in even_digits:
            checksum += sum(digits_of(d * 2))
        return checksum % 10

    last_digit = (10 - luhn_checksum(cc_number)) % 10
    full_card_number = cc_number + str(last_digit)  # 16 digit card number

    # Generate Random Expiry Date (MM/YY) between 2025-2034
    mm = str(random.randint(1, 12)).zfill(2)

    # Random year selection from 2025 to 2034
    yy = random.choice([25, 26, 27, 28, 29, 30, 31, 32, 33, 34])  # Selects a random year from this list

    # Full year (YYYY) with last two digits (25, 26, ..., 34)
    full_year = "20" + str(yy)

    # Generate Random CVC (CVV)
    cvc = str(random.randint(100, 999))

    # Return the card in the format you requested: `5195352404245200|07|2031|242`
    return f"`{full_card_number}|{mm}|{full_year}|{cvc}`"

# Start Command
@bot.message_handler(commands=['start'])
def welcome_user(message):
    user_id = message.from_user.id
    chat_id = message.chat.id

    if not is_subscribed(user_id):
        # Create buttons for both channels and verify button
        markup = types.InlineKeyboardMarkup(row_width=2)
        join_button1 = types.InlineKeyboardButton("Join Now", url=f"https://t.me/{CHANNELS[0][1:]}")
        join_button2 = types.InlineKeyboardButton("Join Now", url=f"https://t.me/{CHANNELS[1][1:]}")
        verify_button = types.InlineKeyboardButton("✅ Verify", callback_data="verify")
        markup.add(join_button1, join_button2)
        markup.add(verify_button)

        bot.reply_to(
            message,
            f"✅ You must join our channels to use this bot!\n\n"
            f"👇 Join both channels and click Verify button:",
            reply_markup=markup
        )
        return

    welcome_message = (
        "🚀 Welcome to the Card Generator Bot!\n\n"
        "To generate a card use .gen BIN\n"
        "Example:  .gen 414720\n\n"
        "You will receive 10 generated cards each time!"
    )

    bot.reply_to(message, welcome_message)

# Callback query handler for verify button
@bot.callback_query_handler(func=lambda call: call.data == "verify")
def verify_subscription(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    message_id = call.message.message_id

    if is_subscribed(user_id):
        bot.delete_message(chat_id, message_id)
        bot.send_message(
            chat_id,
            "✅ You have successfully joined both channels!\n\n"
            "To generate a card use: .gen BIN\n"
            "Example: .gen 414720"
        )
    else:
        bot.answer_callback_query(call.id, "❌ You must join both channels first!", show_alert=True)

# Command Handler for .gen
@bot.message_handler(func=lambda message: message.text.startswith(".gen"))
def send_cc(message):
    user_id = message.from_user.id
    chat_id = message.chat.id

    if not is_subscribed(user_id):
        # Create buttons for both channels and verify button
        markup = types.InlineKeyboardMarkup(row_width=2)
        join_button1 = types.InlineKeyboardButton("Join Now", url=f"https://t.me/{CHANNELS[0][1:]}")
        join_button2 = types.InlineKeyboardButton("Join Now", url=f"https://t.me/{CHANNELS[1][1:]}")
        verify_button = types.InlineKeyboardButton("✅ Verify", callback_data="verify")
        markup.add(join_button1, join_button2)
        markup.add(verify_button)

        bot.reply_to(
            message,
            f"❌ You must join our channels to use this bot!\n\n"
            f"📢 Channel 1: {CHANNELS[0]}\n"
            f"📢 Channel 2: {CHANNELS[1]}\n\n"
            f"👇 Join both channels and click Verify button:",
            reply_markup=markup
        )
        return

    try:
        text = message.text.split(" ")
        if len(text) < 2:
            bot.reply_to(message, "Please provide a BIN number! Example: `.gen 414720`")
            return

        bin_number = text[1]
        if not re.match(r"^\d{6,9}$", bin_number):
            bot.reply_to(message, "Invalid BIN! It must be between 6 and 9 digits long.")
            return

        # Generate cards
        generated_cards = [generate_cc(bin_number) for _ in range(10)]

        # Get fake Canadian address
        fake_address = generate_fake_address()

        # Response
        response = "**✅ Your generated cards are:**\n\n" + "\n".join(generated_cards) + "\n\n"
        response += f"{fake_address}"

        bot.reply_to(message, response, parse_mode="Markdown")
    except Exception as e:
        bot.reply_to(message, "❌ Something went wrong! Please try again later.")

# Start the bot
print("Bot is running...")
bot.polling()
