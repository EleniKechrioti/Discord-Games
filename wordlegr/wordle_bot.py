import discord
from discord import app_commands
from discord.ext import commands, tasks
import random
from datetime import datetime, timedelta
import dotenv
import os
from logic import check_guess, WORD_LENGTH
from wordlist import words as greek_words 
from wordlist import get_random_word       
import unicodedata

dotenv.load_dotenv()

try:
  TOKEN = os.getenv("DISCORD_TOKEN")
  GUILD_ID = int(os.getenv("GUILD_ID"))  
except ValueError:
    print("Please set the DISCORD_TOKEN and GUILD_ID environment variables.")
    exit(1)

intents = discord.Intents.default()
intents.members = True  
bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

user_sessions = {}
leaderboard = {}
user_streaks = {}
last_played = {}
daily_word = None
daily_word_date = None

emojis = {
    "correct": "🟩",
    "present": "🟨",
    "absent": "⬛"
}


def normalize_greek(text):
    """
    Removes accents from Greek characters and converts the text to lowercase.
    This ensures consistency for string comparison during word guessing.
    """
    text = unicodedata.normalize('NFD', text)
    text = ''.join(char for char in text if unicodedata.category(char) != 'Mn')
    return text.lower()

class WordleGame:
    """
    Represents a single Wordle game session for a user.
    Stores the target word, list of attempts, max allowed attempts, and completion status.
    """
    def __init__(self, target_word):
        self.target = target_word
        self.attempts = []
        self.max_attempts = 6
        self.completed = False

    def guess(self, word):
        """
        Accepts a guessed word, normalizes it, compares it with the target,
        stores the result, and marks the game as completed if the word is correct.
        """
        normalized_guess = normalize_greek(word)
        result = check_guess(normalized_guess, normalize_greek(self.target))
        self.attempts.append((word, result))
        if word == self.target:
            self.completed = True
        return result

@bot.event
async def on_ready():
    """
    Called when the bot is ready. Syncs commands with the server and starts the reminder task.
    """
    print(f"✅ Logged in as {bot.user}")
    try:
        synced = await tree.sync(guild=discord.Object(id=GUILD_ID))
        print(f"🔁 Synced {len(synced)} command(s).")
    except Exception as e:
        print(f"❌ Sync error: {e}")
    if not reminder_task.is_running():
        reminder_task.start()

@tree.command(name="wordlegr", description="Ξεκίνα ένα παιχνίδι Wordle στα Ελληνικά", guild=discord.Object(id=GUILD_ID))
async def start_wordle(interaction: discord.Interaction):
    """
    Starts a new Wordle session for the user if they haven't played today.
    Picks a new daily word if it's the first game of the day.
    """
    global daily_word, daily_word_date
    user_id = interaction.user.id
    today = datetime.utcnow().date()

    if user_id in last_played and last_played[user_id]["date"] == today:
        await interaction.response.send_message(
            "❌ Έχεις ήδη παίξει το σημερινό Wordle! Έλα πάλι αύριο.", ephemeral=True
        )
        return

    if daily_word_date != today:
        daily_word = get_random_word()
        daily_word_date = today
        print(f"📅 Νέα λέξη ημέρας: {daily_word}")

    user_sessions[user_id] = WordleGame(daily_word)
    last_played[user_id] = {
        "date": today,
        "time": datetime.utcnow(),
        "channel_id": interaction.channel.id
    }

    await interaction.response.send_message(
        "🎯 Ξεκίνησε το σημερινό Wordle! Χρησιμοποίησε `/guess λέξη` για να δοκιμάσεις."
    )


@tree.command(name="guess", description="Κάνε μια μαντεψιά 5-γράμματης λέξης", guild=discord.Object(id=GUILD_ID))
@app_commands.describe(word="Η λέξη που θες να δοκιμάσεις")
async def guess(interaction: discord.Interaction, word: str):
    """
    Handles a user's word guess. Validates input, updates their game state,
    tracks streaks, and sends appropriate responses based on game progress.
    """
    user_id = interaction.user.id

    if user_id not in user_sessions:
        await interaction.response.send_message("❌ Δεν έχεις ξεκινήσει ακόμα παιχνίδι. Γράψε `/wordlegr`.", ephemeral=True)
        return

    game = user_sessions[user_id]

    if game.completed:
        await interaction.response.send_message("✅ Έχεις ήδη βρει τη λέξη!", ephemeral=True)
        return

    if len(word) != WORD_LENGTH:
        await interaction.response.send_message("🚫 Η λέξη πρέπει να είναι **5 γράμματα**.", ephemeral=True)
        return

    word = word.lower()
    result = game.guess(word)
    result_display = ''.join([emojis[r] for r in result])

    if game.completed:
        leaderboard[user_id] = leaderboard.get(user_id, 0) + 1
        user_streaks[user_id] = user_streaks.get(user_id, 0) + 1
        last_played[user_id]["time"] = datetime.utcnow()
        await interaction.channel.send(f"🎉 Ο {interaction.user.display_name} βρήκε τη λέξη σε {len(game.attempts)} προσπάθειες!")
        await interaction.response.send_message(f"✅ Το βρήκες! ({result_display})", ephemeral=True)
        return

    if len(game.attempts) >= game.max_attempts:
        user_streaks[user_id] = 0
        game.completed = True
        await interaction.channel.send(f"❌ Τέλος παιχνιδιού. 🔚 Ο {interaction.user.display_name} έφτασε τις 6 προσπάθειες.")
        await interaction.response.send_message(f"Η λέξη ήταν: **{game.target}**", ephemeral=True)
        return

    await interaction.channel.send(f"🟢 Ο {interaction.user.display_name} έκανε νέα μαντεψιά!\n🔍 Μαντεψιά: {result_display}")
    await interaction.response.send_message(f"🔍 Μαντεψιά: **{word}**\n{result_display}", ephemeral=True)

@tree.command(name="leaderboard", description="Δες το leaderboard", guild=discord.Object(id=GUILD_ID))
async def show_leaderboard(interaction: discord.Interaction):
    """
    Displays the top players based on total wins and current streaks.
    """
    if not leaderboard:
        await interaction.response.send_message("📉 Κανένας δεν έχει βρει λέξη ακόμα.")
        return

    sorted_lb = sorted(leaderboard.items(), key=lambda x: x[1], reverse=True)
    entries = [f"<@{uid}>: {score} νίκες (🔥 streak: {user_streaks.get(uid, 0)})" for uid, score in sorted_lb[:10]]
    leaderboard_text = "\n".join(entries)
    await interaction.response.send_message(f"🏆 **Leaderboard**\n{leaderboard_text}")

@tasks.loop(hours=24)
async def reminder_task():
    """
    Loops every 24 hours to:
    - Remind users who haven't played in the last 24–48 hours.
    - Remove inactive sessions after 48 hours of inactivity.
    Sends reminder messages to the original channel where the user started their game.
    """
    now = datetime.utcnow()
    for user_id, data in list(last_played.items()):
        last_time = data["time"]
        channel_id = data["channel_id"]

        if timedelta(hours=24) <= (now - last_time) < timedelta(hours=48):
            try:
                channel = await bot.fetch_channel(channel_id)
                await channel.send(f"<@{user_id}> ⏰ Ήρθε η ώρα για το καθημερινό σου Wordle! Μην χάσεις το streak σου!")
            except Exception as e:
                print(f"❌ Could not send reminder to channel {channel_id} for user {user_id}: {e}")

        elif (now - last_time) >= timedelta(hours=48):
            print(f"🗑️ Resetting session for user {user_id} (inactivity)")
            user_sessions.pop(user_id, None)
            last_played.pop(user_id, None)


bot.run(TOKEN)
