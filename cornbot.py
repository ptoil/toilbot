# cornbot.py
import os
import random

import discord
from discord.ext import commands
from dotenv import load_dotenv

########## CONSTANTS

load_dotenv()
TOKEN = os.getenv("CORNBOT_TOKEN")

botOwner = 205908835435544577;

########## END CONSTANTS


bot = commands.Bot(command_prefix='.')

@bot.event
async def on_ready():
	print(f'{bot.user} has connect to Discord!')

cornStorm = 0

def cornRand (storm):
	if storm == 0:
		return random.randint(0, 100)
	elif storm == 1:
		return random.randint(60, 70)
	else:
		print("ERROR: cornStorm is set to something other than 0 or 1")

@bot.event
async def on_message(message):
	if message.author == bot.user:
		return

	if message.content.lower() == "what does it stand for?":
		await message.channel.send("jaiya sucks")

	if "wendys" in message.content.lower() or "wendy's" in message.content.lower():
		await message.channel.send("NO WENDYS!!!")

	if "skz" in message.content.lower() or "stray kids" in message.content.lower():
		await message.channel.send("stfu weeb")

	if ("ty" in message.content.lower() or "thx" in message.content.lower() or "thank" in message.content.lower()) and ("bot" in message.content.lower() or bot.user in message.mentions):
		await message.channel.send("YOU'RE WELCOME " + message.author.display_name.upper())

	global cornStorm
	rand100 = cornRand(cornStorm)
	print(f"number is {rand100}")
	if rand100 == 69:
		words = message.content.split()
		randWord = random.randint(0, len(words)-1)
		words[randWord] = "CORN"
		cornText = " ".join(words)
		await message.channel.send(cornText)
	elif "rand" in message.content.lower():
		await message.channel.send(rand100)

	await bot.process_commands(message) #this fucking line is needed to stop the on_message function from preventing commands from being called


@bot.command()
async def shutdown(ctx):
	if ctx.author.id == botOwner:
		await ctx.send("Shutting down")
		await bot.logout()
	else:
		await ctx.send("You don't have permission to use that command.")

@bot.command()
async def cornado(ctx):
	global cornStorm
	cornStorm = 1

@bot.command()
async def noplacelikehome(ctx):
	global cornStorm
	cornStorm = 0

bot.run(TOKEN)