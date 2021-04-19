# toilbot.py
import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

import random
import asyncio
import time

########## CONSTANTS

load_dotenv()
TOKEN = os.getenv('TOILBOT_TOKEN')

BOT_OWNER = 205908835435544577;

moons = [":full_moon:", ":waxing_gibbous_moon:", ":first_quarter_moon:", ":waxing_crescent_moon:", ":new_moon:", 
			 ":waning_crescent_moon:", ":last_quarter_moon:", ":waning_gibbous_moon:", ":full_moon:"]

#mixtea
freqThreshold = 500

emoji_first_place = "🥇"
emoji_second_place = "🥈"
emoji_third_place = "🥉"
emoji_check_mark = "✅"

########## END CONSTANTS

bot = commands.Bot(command_prefix='.')

@bot.event
async def on_ready():
	print(f'{bot.user} has connect to Discord!')


@bot.event
async def on_message(message):
	if message.author == bot.user:
		return
	if message.channel != ctx.channel:
		await bot.process_commands(message)
		return

class Tea:

	def __init__(self):


	def generateWord(self):
		wordsList = open("collins_scrabble.txt", "r").read().split("\n")
		belowThreshold = 1
		while belowThreshold == 1:
			randWord = wordsList[random.randint(0, len(wordsList)-1)]
			randIndex = random.randint(0, len(randWord)-3)
			phrase = randWord[randIndex:randIndex+3]
			frequency = wordsList.count(phrase)
			if (frequency > freqThreshold):
				belowThreshold = 0
#			await ctx.send(f"word: {randWord}\nindex: {randIndex}\nphrase: {phrase}\nfrequency: {frequency}")

	def timer(self):
		timeCounter = 0
		roundOver = 0
		async def background_counter():
			await bot.wait_until_ready()
			counterMessage = None
			nonlocal moons
			while not bot.is_closed():
				nonlocal timeCounter
				if timeCounter == 9:
					return
				elif timeCounter == 0:
					await ctx.send()








@bot.command(aliases=["moontea"])
async def moon(ctx):
	counterMessage = None
	counter = 0
	nonlocal moons
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
	else:
		await ctx.send(f"{ctx.author.mention} You don't have permission to use that command.")

@bot.command()
async def dodrop(ctx):
	await ctx.send(".drop")

@bot.command()
async def accountage(ctx):
	await ctx.send(f"{ctx.author.mention}'s account was made on {ctx.author.created_at}")

@bot.command()
async def shutdown(ctx, botName: str):
	if ctx.author.id == BOT_OWNER:
		if botName == "toilbot":
			await ctx.send("Shutting down")
			print("Bot was shutdown")
			await bot.logout()
	else:
		await ctx.send("You don't have permission to use that command.")

bot.run(TOKEN)