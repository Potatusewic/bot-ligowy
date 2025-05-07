import os
import time
from dotenv import load_dotenv
import discord
from discord.ext import commands
from keep_alive import keep_alive
import logging

# Włącz logowanie błędów
logging.basicConfig(level=logging.DEBUG)

# Ładowanie zmiennych środowiskowych
load_dotenv()

# Sprawdź, czy token został załadowany z .env
TOKEN = os.getenv("TOKEN")
if not TOKEN:
    print("Błąd: Token bota nie został znaleziony w zmiennych środowiskowych!")
    exit(1)

# Konfiguracja bota
intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# === KONFIGURACJA ===
ID_KANAŁU_SEARCH = 1367975025990307881  # #🔎search-club🔎
ID_KANAŁU_FREE_AGENTS = 1258017564185989226  # #🗽free-agents🗽
ID_KANAŁU_AUTOROLE = 1367984711988940922
ID_KANAŁU_REGISTRATION = 1367982248841842790
REQUIRED_ROLE_NAME = "⟪🎮⟫ PLAYER"

ROLE_MAP = {
    "🧤": "⟪🧤⟫ SEARCH GK",
    "🧱": "⟪🧱⟫ SEARCH CB",
    "👟": "⟪👟⟫ SEARCH CM",
    "⚽": "⟪⚽⟫ SEARCH ST"
}

# Funkcja uruchamiająca bota
@bot.event
async def on_ready():
    print(f"Bot jest zalogowany jako {bot.user.name} ({bot.user.id})")
    print("Bot jest online!")
    
@bot.event
async def on_error(event, *args, **kwargs):
    # Zapisuje błąd do logów, jeśli coś pójdzie nie tak
    logging.error(f"Wystąpił błąd: {event} | {args} | {kwargs}")

# Sprawdzanie, czy bot działa
if __name__ == "__main__":
    try:
        keep_alive()  # Uruchom serwer Flask
        bot.run(TOKEN)  # Uruchom bota
    except discord.LoginFailure:
        print("Błąd logowania: Niewłaściwy token.")
    except Exception as e:
        print(f"Wystąpił nieoczekiwany błąd: {e}")

