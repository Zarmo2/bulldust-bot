import os
import random

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)

TOKEN = os.getenv("BOT_TOKEN")

WORDS = [
    "APPLE", "GRAPE", "MANGO", "BRAIN", "PLANT",
    "TIGER", "HOUSE", "WATER", "LIGHT", "DREAM",
    "SMILE", "CHAIR", "MUSIC", "EARTH", "CLOUD",
    "TRAIN", "STONE", "GREEN", "SWEET", "CROWN",
    "FLAME", "HEART", "RIVER", "WORLD", "NIGHT",
    "SPACE", "POWER", "HAPPY", "QUEEN", "SMART",
    "PEACE", "FAITH", "GHOST", "FRUIT", "MONEY",
    "GRASS", "BREAD", "SNAKE", "BEACH", "PLANE",
    "SHEEP", "TOWER", "PLATE", "BRAVE", "CRANE",
    "SHIRT", "PHONE", "TABLE", "MOUSE", "LEMON",
    "PEACH", "MELON", "BERRY", "OLIVE", "PILOT",
    "ROBOT", "LASER", "MAGIC", "NURSE", "JUDGE",
    "ACTOR", "WRITE", "LEARN", "TEACH", "THINK",
    "GUESS", "SOLVE", "QUICK", "SHARP", "SOUND",
    "VOICE", "RADIO", "VIDEO", "PHOTO", "MARCH",
    "APRIL", "PLUMS", "MONTH", "MORAL", "HONOR",
    "TRUST", "LOYAL", "ANGEL", "DEVIL", "CLEAN",
    "FRESH", "SLEEP", "STORM", "CYCLE", "SOUTH",
    "NORTH", "EASTS", "WESTS", "CANDY", "SUGAR",
    "HONEY", "CREAM", "SPICE", "BLACK", "WHITE",
    "BROWN", "DAILY"
]

games = {}
scores = {}
players = {}


def main_menu():
    keyboard = [
        [
            InlineKeyboardButton("🎮 PLAY GAME", callback_data="play"),
            InlineKeyboardButton("👤 MY SCORE", callback_data="score")
        ],
        [
            InlineKeyboardButton("🏆 LEADERBOARD", callback_data="leaderboard")
        ],
        [
            InlineKeyboardButton("📖 HOW TO PLAY", callback_data="help"),
            InlineKeyboardButton("ℹ️ ABOUT", callback_data="about")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🧠 WELCOME TO BRAINBATTLE!\n\n"
        "Think fast. Play smart. Become a champion!\n\n"
        "Challenge yourself with exciting word puzzles "
        "and earn points for every victory.\n\n"
        "Are you ready to test your brain?",
        reply_markup=main_menu()
    )


async def show_leaderboard(message):
    if not scores:
        await message.reply_text(
            "🏆 LEADERBOARD\n\n"
            "No champions yet!\n"
            "Play a game and be the first.",
            reply_markup=main_menu()
        )
        return

    ranking = sorted(
        scores.items(),
        key=lambda item: item[1],
        reverse=True
    )

    result = "🏆 BRAINBATTLE LEADERBOARD\n\n"

    for position, (player_id, score) in enumerate(ranking[:10], 1):
        name = players.get(player_id, "Player")
        result += f"{position}. {name}: {score} points\n"

    await message.reply_text(
        result,
        reply_markup=main_menu()
    )


async def leaderboard_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await show_leaderboard(update.message)


async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    players[user_id] = query.from_user.first_name

    if query.data == "play":
        games[user_id] = {
            "word": random.choice(WORDS),
            "attempts": 0,
            "hint_used": False
        }

        await query.message.reply_text(
            "🎯 NEW CHALLENGE!\n\n"
            "Discover the mystery five-letter word.\n"
            "You have ten attempts.\n\n"
            "🟩 Correct letter and position.\n"
            "🟨 Correct letter, wrong position.\n"
            "⬛ Letter not in the word.\n\n"
            "Enter your five-letter guess!",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("💡 GET A HINT", callback_data="hint")]
            ])
        )

    elif query.data == "hint":
        if user_id not in games:
            await query.message.reply_text("Start a game first!")
            return

        game = games[user_id]

        if game["hint_used"]:
            await query.message.reply_text(
                "You've already used your hint!"
            )
            return

        game["hint_used"] = True

        await query.message.reply_text(
            f"💡 HINT: The mystery word begins with '{game['word'][0]}'!"
        )

    elif query.data == "help":
        await query.message.reply_text(
            "📖 HOW TO PLAY BRAINBATTLE\n\n"
            "1. Press PLAY GAME.\n"
            "2. Guess the hidden five-letter word.\n"
            "3. You have ten attempts.\n"
            "4. Use the coloured clues to guide you.\n"
            "5. You can use one hint per game.\n"
            "6. Guess correctly to earn 10 points!\n\n"
            "Good luck, champion!",
            reply_markup=main_menu()
        )

    elif query.data == "about":
        await query.message.reply_text(
            "🧠 ABOUT BRAINBATTLE\n\n"
            "BrainBattle is a fun word puzzle game "
            "designed to challenge your vocabulary, "
            "thinking and problem-solving skills.\n\n"
            "Think fast. Play smart. Become a champion!",
            reply_markup=main_menu()
        )

    elif query.data == "score":
        score = scores.get(user_id, 0)

        await query.message.reply_text(
            f"👤 PLAYER PROFILE\n\n"
            f"Name: {query.from_user.first_name}\n"
            f"Total points: {score}\n\n"
            "Keep playing to improve your score!",
            reply_markup=main_menu()
        )

    elif query.data == "leaderboard":
        await show_leaderboard(query.message)


async def guess(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    word = update.message.text.upper().strip()

    if user_id not in games:
        await update.message.reply_text(
            "You don't have an active game.\n"
            "Press /start to open the main menu."
        )
        return

    if len(word) != 5 or not word.isalpha():
        await update.message.reply_text(
            "⚠️ Enter exactly five letters."
        )
        return

    game = games[user_id]
    answer = game["word"]
    game["attempts"] += 1

    result = ""

    for i, letter in enumerate(word):
        if letter == answer[i]:
            result += "🟩"
        elif letter in answer:
            result += "🟨"
        else:
            result += "⬛"

    if word == answer:
        scores[user_id] = scores.get(user_id, 0) + 10
        del games[user_id]

        await update.message.reply_text(
            f"🎉 BRILLIANT! YOU WON!\n\n"
            f"The mystery word was {answer}.\n"
            f"🏆 You earned 10 points!\n"
            f"⭐ Total points: {scores[user_id]}",
            reply_markup=main_menu()
        )
        return

    if game["attempts"] >= 10:
        del games[user_id]

        await update.message.reply_text(
            f"😅 GAME OVER!\n\n"
            f"The mystery word was {answer}.\n"
            "Better luck next time!",
            reply_markup=main_menu()
        )
        return

    await update.message.reply_text(
        f"{result}\n\n"
        f"Attempt {game['attempts']} of 10.\n"
        "Try another word!"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Use /start to open BrainBattle and explore the menu."
    )


def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("leaderboard", leaderboard_command))

    app.add_handler(CallbackQueryHandler(buttons))

    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, guess)
    )

    print("BrainBattle is running!")

    app.run_polling()


if __name__ == "__main__":
    main()
