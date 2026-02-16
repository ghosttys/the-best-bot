import discord
from discord.ext import commands
import os
import random
import asyncio
import youtube_dl
from discord import FFmpegPCMAudio

# Load token from environment
TOKEN = os.environ['TOKEN']

# Intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.voice_states = True

# Bot prefix
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

# XP & Coins
xp = {}
coins = {}

# ===============================
# ON READY
# ===============================
@bot.event
async def on_ready():
    print(f"✅ Ghosttys bott Online: {bot.user}")

# ===============================
# MESSAGE HANDLER
# ===============================
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    user_id = message.author.id
    xp[user_id] = xp.get(user_id, 0) + 1
    coins[user_id] = coins.get(user_id, 0) + 1

    await bot.process_commands(message)

# ===============================
# COMMANDS
# ===============================
@bot.command()
async def help(ctx):
    await ctx.send("""
📖 Ghosttys bott Commands:

!ping
!level
!balance
!kick @user
!ban @user
!giveaway <minutes> <prize>
!join
!play <youtube link>
!stop
""")

@bot.command()
async def ping(ctx):
    await ctx.send(f"🏓 Pong! {round(bot.latency * 1000)}ms")

@bot.command()
async def level(ctx):
    await ctx.send(f"⭐ XP: {xp.get(ctx.author.id,0)}")

@bot.command()
async def balance(ctx):
    await ctx.send(f"💰 Coins: {coins.get(ctx.author.id,0)}")

# ===============================
# MODERATION
# ===============================
@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member):
    await member.kick()
    await ctx.send(f"✅ Kicked {member.mention}")

@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member):
    await member.ban()
    await ctx.send(f"✅ Banned {member.mention}")

# ===============================
# GIVEAWAY
# ===============================
@bot.command()
@commands.has_permissions(administrator=True)
async def giveaway(ctx, minutes: int, *, prize: str):
    msg = await ctx.send(f"🎉 GIVEAWAY 🎉\nPrize: {prize}\nReact 🎉\nEnds in {minutes} min")
    await msg.add_reaction("🎉")
    await asyncio.sleep(minutes*60)
    msg = await ctx.channel.fetch_message(msg.id)
    users = await msg.reactions[0].users().flatten()
    entries = [u for u in users if not u.bot]
    if not entries:
        await ctx.send("No entries")
        return
    winner = random.choice(entries)
    await ctx.send(f"🏆 {winner.mention} won **{prize}**")

# ===============================
# VOICE + MUSIC
# ===============================
@bot.command()
async def join(ctx):
    vc = ctx.author.voice.channel
    if not vc:
        await ctx.send("Join a voice channel first")
        return
    await vc.connect()
    await ctx.send("🎵 Joined VC")

@bot.command()
async def play(ctx, url: str):
    vc = ctx.voice_client
    if not vc:
        if ctx.author.voice:
            vc = await ctx.author.voice.channel.connect()
        else:
            await ctx.send("Join a voice channel first")
            return
    ydl_opts = {"format": "bestaudio"}
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        audio_url = info['url']
        source = FFmpegPCMAudio(audio_url)
        vc.play(source)
    await ctx.send("▶️ Playing")

@bot.command()
async def stop(ctx):
    vc = ctx.voice_client
    if vc:
        await vc.disconnect()
        await ctx.send("⏹️ Stopped")

# ===============================
# RUN BOT
# ===============================
bot.run(TOKEN)
