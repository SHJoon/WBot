import asyncio
import discord
from discord import app_commands
from discord.ext import commands, tasks
import os

from cogs.QueueCog import QueueCog
from cogs.UtilityCog import UtilityCog

intents = discord.Intents.all()

prefixes = ["!", "."]

bot = commands.Bot(command_prefix=prefixes, case_insensitive=True, intents=intents)

@bot.event
async def on_ready():
    print(bot.user.name)
    print(bot.user.id)
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(e)


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    await bot.process_commands(message)

token = None

if "BOT_KEY" in os.environ:
    token = os.environ["BOT_KEY"]
elif os.path.isfile("key"):
    with open("key", "r") as f:
        token = f.read().strip().strip("\n")

if token == None:
    print("No token found")
    exit


async def load():
    await bot.add_cog(QueueCog(bot))
    await bot.add_cog(UtilityCog(bot))

async def main():
    await load()
    await bot.start(token)

asyncio.run(main())