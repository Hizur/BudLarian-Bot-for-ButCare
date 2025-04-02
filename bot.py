# bot.py
import discord
from discord.ext import commands
import logging
import os
from config import BOT_TOKEN, TEST_GUILD_ID, JSON_FILE_PATH, CLINICS_FILE_PATH, LOG_LEVEL
from data_loader import load_strains_data, load_clinics_data
from strains_commands import register_strain_commands
from clinic_commands import register_clinic_commands
from utils import ensure_file_exists

# --- Ensure logs directory exists ---
if not os.path.exists("logs"):
    os.makedirs("logs")

# --- Setup Logging ---
logging.basicConfig(
    level=LOG_LEVEL,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("logs/bot.log", encoding='utf-8')
    ]
)
logger = logging.getLogger('cannabis_clinic_bot')

# --- Ensure Required Files Exist ---
ensure_file_exists(JSON_FILE_PATH, default_content="[]")
ensure_file_exists(CLINICS_FILE_PATH, default_content="[]")

# --- Load Data ---
try:
    strains_data = load_strains_data(JSON_FILE_PATH) or []
except Exception as e:
    logger.error(f"Error loading strains data: {e}")
    strains_data = []

try:
    clinics_data = load_clinics_data(CLINICS_FILE_PATH) or []
except Exception as e:
    logger.error(f"Error loading clinics data: {e}")
    clinics_data = []

# --- Discord Bot Setup ---
intents = discord.Intents.default()
intents.message_content = True
client = commands.Bot(command_prefix="!", intents=intents)
tree = client.tree

@client.event
async def on_ready():
    print(f"Zalogowano jako {client.user}.")
    logger.info(f"Zalogowano jako {client.user}.")
    
    test_guild = discord.Object(id=TEST_GUILD_ID) if TEST_GUILD_ID else None

    try:
        logger.info("Clearing all commands before registration...")
        client.tree.clear_commands(guild=None)
        if test_guild:
            client.tree.clear_commands(guild=test_guild)

        logger.info("Registering commands...")
        register_strain_commands(client, tree, strains_data)
        register_clinic_commands(client, tree, clinics_data)

        logger.info("Syncing commands with Discord...")
        if test_guild:
            await client.tree.sync(guild=test_guild)
        await client.tree.sync()
        logger.info("Commands synced successfully.")
    except Exception as e:
        logger.error(f"Error during command registration or syncing: {e}")

if __name__ == "__main__":
    try:
        logger.info("Starting Discord bot...")
        client.run(BOT_TOKEN)
    except discord.errors.LoginFailure:
        logger.error("Invalid Discord token. Please check your token in config.py")
        exit(1)
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
        exit(1)