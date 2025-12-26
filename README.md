# AUTOMOD COMMANDS ARE REAL!!!

### Example code:
```py
from asyncio import run as async_run
from autobot import AutoBot
from discord import GuildChannel, Intents
from discord.ext.commands import Context
from dotenv import load_dotenv
from os import get_env


bot: AutoBot = AutoBot(command_prefix = "test.", intents = Intents.default())

# Automod Command Registration
@bot.automod("!ping")
async def ping(channel: GuildChannel) -> None:
  await channel.send("Pong!")

# Automod Command Toggle
@bot.command()
async def automod_toggle(context: Context) -> None:
  await bot.automod_tree.enable(ping, guild = context.guild) # Make command active
  await bot.automod_tree.disable(ping, guild = context.guild) # Make command inactive

@lambda function: async_run(function())
async def main() -> None:
  load_dotenv()
  await bot.start(getenv("TOKEN"))
```