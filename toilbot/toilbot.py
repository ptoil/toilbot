import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

import traceback
from cogs.exceptions import *

import random
import asyncio
import time
import logging

########## CONSTANTS

load_dotenv()
TOKEN = os.getenv('TOILBOT_TOKEN')


#logging.basicConfig(level=logging.INFO)

BOT_OWNER = 205908835435544577


moons = [":full_moon:", ":waxing_gibbous_moon:", ":first_quarter_moon:", ":waxing_crescent_moon:", ":new_moon:", 
		 ":waning_crescent_moon:", ":last_quarter_moon:", ":waning_gibbous_moon:", ":full_moon:"]


########## END CONSTANTS

intents = discord.Intents(messages=True, members=True, guilds=True, reactions=True)
bot = commands.Bot(command_prefix='.', case_insensitive=True, intents=intents)


bot.load_extension("cogs.mixtea")
bot.load_extension("cogs.connectfour")
bot.load_extension("cogs.blackjack")
bot.load_extension("cogs.roles")

@bot.event
async def on_connect():
	print(f'{bot.user} has connected to Discord')

@bot.event
async def on_ready():
	print(f'{bot.user} is ready!')


@bot.event
async def on_command_error(ctx, error):
	if isinstance(error, NotInToilbotChannel):
		print(f"NotInToilbotChannel: {ctx.author.name}: {ctx.message.content}")
	else:
		print('Ignoring exception in command {}:'.format(ctx.command))
		print("".join(traceback.format_exception(type(error), error, error.__traceback__)))
		await ctx.send(f"<@205908835435544577> error pepew")


"""
@bot.event
async def on_message(message):
	if message.author == bot.user:
		return

	await bot.process_commands(message)
"""


@bot.command(aliases=["moontea"])
@ChannelCheck.in_toilbot_channel()
async def moon(ctx):
	counterMessage = None
	counter = 0
	global moons
	while not bot.is_closed():
		if counter == 0:
				counterMessage = await ctx.send(moons[counter])
		else:
			await counterMessage.edit(content=moons[counter])
		await asyncio.sleep(1)
		counter += 1
		if counter == 9:
			return;

@bot.command()
async def say(ctx, botName: str, *strInput: str):
	if ctx.author.id == BOT_OWNER:
		if (botName == "toilbot"):
			await ctx.send(" ".join(strInput))
			await ctx.message.delete()
	else:
		await ctx.send(f"{ctx.author.mention} You don't have permission to use that command.")

@bot.command()
async def shutdown(ctx, botName: str):
	if ctx.author.id == BOT_OWNER:
		if botName == "toilbot":
			await ctx.send("Shutting down")
			print("Bot was shutdown")
			await bot.close()
	else:
		await ctx.send("You don't have permission to use that command.")

bot.run(TOKEN)
