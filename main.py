import os
import time
from dotenv import load_dotenv
load_dotenv()
import discord
from discord.ext import commands
from keep_alive import keep_alive

intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# === KONFIGURACJA ===
ID_KANAŁU_SEARCH = 1367975025990307881     # #🔎search-club🔎
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

user_message_map = {}
emoji_cooldowns = {}  # (user_id, emoji): timestamp
COOLDOWN_SECONDS = 2 * 60 * 60  # 2 godziny

@bot.command()
async def setup_message(ctx):
    if ctx.channel.id != ID_KANAŁU_SEARCH:
        return

    msg_text = (
        "Good to hear you're looking for a club. Several teams are still looking for players. We'd love to help you find the perfect team for your skills and preferences.\n\n"
        "**What position you prefer to play? (you can choose multiple positions)**\n"
        "---------------------------------------------------------------------------------------------------------\n"
        "⌊🧤⌉ - If you're a GK\n"
        "---------------------------------------------------------------------------------------------------------\n"
        "⌊🧱⌉ - If you're a CB\n"
        "---------------------------------------------------------------------------------------------------------\n"
        "⌊👟⌉ - If you're a CM\n"
        "---------------------------------------------------------------------------------------------------------\n"
        "⌊⚽⌉ - If you're a ST\n"
        "---------------------------------------------------------------------------------------------------------\n"
        f"**Please delete your reactions after you find a club as this will remove your application from the {bot.get_channel(ID_KANAŁU_FREE_AGENTS).mention}**\n"
        f"**IMPORTANT: First you must have a ⟪🎮⟫ PLAYER role to find a club. You can get it in {bot.get_channel(ID_KANAŁU_AUTOROLE).mention}**"
    )

    message = await ctx.send(msg_text)

    for emoji in ROLE_MAP.keys():
        await message.add_reaction(emoji)

@bot.event
async def on_raw_reaction_add(payload):
    if payload.user_id == bot.user.id:
        return
    if payload.channel_id != ID_KANAŁU_SEARCH:
        return

    emoji = payload.emoji.name
    if emoji not in ROLE_MAP:
        return

    guild = bot.get_guild(payload.guild_id)
    user = guild.get_member(payload.user_id)

    required_role = discord.utils.get(guild.roles, name=REQUIRED_ROLE_NAME)
    if required_role not in user.roles:
        return

    now = time.time()
    cooldown_key = (payload.user_id, emoji)
    last_used = emoji_cooldowns.get(cooldown_key, 0)

    if now - last_used < COOLDOWN_SECONDS:
        remaining = int((COOLDOWN_SECONDS - (now - last_used)) // 60)
        try:
            await user.send(
                f"⏳ You can only apply for **{emoji}** once every 2 hours. Please wait {remaining} more minutes.\n"
                "--------------------------------------------------------------------------------------------------------"
            )
        except discord.Forbidden:
            pass
        return

    role_name = ROLE_MAP[emoji]
    role = discord.utils.get(guild.roles, name=role_name)
    free_agents_channel = guild.get_channel(ID_KANAŁU_FREE_AGENTS)

    if role:
        msg = await free_agents_channel.send(
            f"{user.mention} looking for a club {role.mention}\n"
            "--------------------------------------------------------------------------------------------------------"
        )
        user_message_map[(payload.user_id, emoji)] = msg.id
        emoji_cooldowns[cooldown_key] = now

        count = sum(1 for member in guild.members if role in member.roles)
        try:
            await user.send(f"""**Good! {count} teams are looking for players like you.**

**Wait a few hours/days and we will find the perfect club for you.**

If the number of clubs that need you is 0, there are probably no more free spots in the teams.
You can create your team in the {bot.get_channel(ID_KANAŁU_REGISTRATION).mention} and we will help you find players.
--------------------------------------------------------------------------------------------------------""")
        except discord.Forbidden:
            pass
    else:
        await free_agents_channel.send(f"{user.mention} looking for a club (role `{role_name}` not found!)")

@bot.event
async def on_raw_reaction_remove(payload):
    if payload.channel_id != ID_KANAŁU_SEARCH:
        return

    emoji = payload.emoji.name
    key = (payload.user_id, emoji)
    if key not in user_message_map:
        return

    message_id = user_message_map[key]
    guild = bot.get_guild(payload.guild_id)
    free_agents_channel = guild.get_channel(ID_KANAŁU_FREE_AGENTS)

    try:
        msg = await free_agents_channel.fetch_message(message_id)
        await msg.delete()
        del user_message_map[key]
    except discord.NotFound:
        pass

if __name__ == "__main__":
    keep_alive()
    bot.run(os.getenv("TOKEN"))
