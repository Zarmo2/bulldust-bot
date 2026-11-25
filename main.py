import os
import random
from collections import Counter

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters
)

BOT_TOKEN = os.getenv("BOT_TOKEN")

WORDS = [
    "CAT", "DOG", "SUN", "CAR", "BOX",
    "BAT", "HAT", "CUP", "PEN", "MAP",
    "BED", "BUS", "COW", "FOX", "PIG",
    "JAM", "EGG", "SKY", "RED", "FUN"
]

scores = {}

def main_menu():
    keyboard = [
        [InlineKeyboardButton("🎮 Play Game", callback_data="play")],
        [InlineKeyboardButton("📖 How to Play", callback_data="help")],
        [InlineKeyboardButton("🏆 Leaderboard", callback_data="leaderboard")],
        [InlineKeyboardButton("ℹ️ About BullDust", callback_data="about")]
    ]
    return InlineKeyboardMarkup(keyboard)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["game"] = None

    await update.message.reply_text(
        "🎉 Welcome to BULLDUST!\n\n"
        "Think fast, guess smart and earn points!\n\n"
        "Choose an option below:",
        reply_markup=main_menu()
    )


async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    name = query.from_user.first_name

    if query.data == "play":
        word = random.choice(WORDS)

        context.user_data["game"] = {
            "word": word,
            "attempts": 0
        }

        await query.edit_message_text(
            "🎮 NEW CHALLENGE!\n\n"
            "I have chosen a secret THREE-LETTER word.\n"
            "You have 6 attempts to find it.\n\n"
            "Send your first guess!"
        )

    elif query.data == "help":
        await query.edit_message_text(
            "📖 HOW TO PLAY BULLDUST\n\n"
            "1. Tap Play Game.\n"
            "2. Guess a three-letter word.\n"
            "3. You have 6 attempts.\n"
            "4. 🟩 means correct letter and position.\n"
            "5. 🟨 means correct letter, wrong position.\n"
            "6. ⬜ means the letter is not in the word.\n\n"
            "Guess correctly to earn 10 points!",
            reply_markup=main_menu()
        )

    elif query.data == "about":
        await query.edit_message_text(
            "ℹ️ ABOUT BULLDUST\n\n"
            "BullDust is a fun word-guessing game.\n"
            "Challenge your vocabulary, think carefully "
            "and climb the leaderboard!",
            reply_markup=main_menu()
        )

    elif query.data == "leaderboard":
        if not scores:
            text = "🏆 LEADERBOARD\n\nNo scores yet. Be the first to play!"
        else:
            ranking = sorted(
                scores.items(),
                key=lambda item: item[1]["points"],
                reverse=True
            )[:10]

            text = "🏆 LEADERBOARD\n\n"
            for position, (player_id, data) in enumerate(ranking, 1):
                text += f"{position}. {data['name']} — {data['points']} points\n"

        await query.edit_message_text(
            text,
            reply_markup=main_menu()
        )


async def guess(update: Update, context: ContextTypes.DEFAULT_TYPE):
    game = context.user_data.get("game")

    if not game:
        await update.message.reply_text(
            "Start a new challenge by tapping Play Game.",
            reply_markup=main_menu()
        )
        return

    word = game["word"]
    guess_word = update.message.text.strip().upper()

    if len(guess_word) != 3 or not guess_word.isalpha():
        await update.message.reply_text(
            "Please enter a valid THREE-LETTER word."
        )
        return

    game["attempts"] += 1

    remaining = Counter(word)
    result = ["⬜"] * 3

    for i in range(3):
        if guess_word[i] == word[i]:
            result[i] = "🟩"
            remaining[guess_word[i]] -= 1

    for i in range(3):
        if result[i] != "🟩" and remaining[guess_word[i]] > 0:
            result[i] = "🟨"
            remaining[guess_word[i]] -= 1

    feedback = " ".join(result)

    if guess_word == word:
        user_id = update.effective_user.id
        name = update.effective_user.first_name

        if user_id not in scores:
            scores[user_id] = {"name": name, "points": 0}

        scores[user_id]["name"] = name
        scores[user_id]["points"] += 10

        context.user_data["game"] = None

        await update.message.reply_text(
            f"🎉 BRILLIANT! You got it!\n\n"
            f"The word was {word}.\n"
            f"You earned 10 points!\n\n"
            f"Your total score: {scores[user_id]['points']}",
            reply_markup=main_menu()
        )

    elif game["attempts"] >= 6:
        context.user_data["game"] = None

        await update.message.reply_text(
            f"😢 Game Over!\n\n"
            f"The correct word was {word}.\n"
            f"Better luck next time!",
            reply_markup=main_menu()
        )

    else:
        attempts_left = 6 - game["attempts"]

        await update.message.reply_text(
            f"{feedback}\n\n"
            f"Attempts left: {attempts_left}\n"
            f"Try again!"
        )


def main():
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN environment variable is missing!")

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(buttons))
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, guess)
    )

    print("BullDust is running!")

    app.run_polling()


if __name__ == "__main__":
    main()
