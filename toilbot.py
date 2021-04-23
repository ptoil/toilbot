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
#	if message.channel != ctx.channel:
#		await bot.process_commands(message)
#		return

	await bot.process_commands(message)

class Tea:

	def __init__(self, ctx):
		self.ctx = ctx
		self.phrase = ""
		self.word = ""
		self.timeCounter = 0
		self.roundOver = 0
		self.startGame()

	async def startGame(self):
		scores = {}
		self.phrase = self.generateWord()
		self.timer("Type the longest word containing: **" + phrase + "**")
		



	def generateWord(self):
		rawWords = open("collins_scrabble.txt", "r").read()
		wordsList = rawWords.split("\n")
		belowThreshold = 1
		while belowThreshold == 1:
			randWord = wordsList[random.randint(0, len(wordsList)-1)]
			randIndex = random.randint(0, len(randWord)-3)
			phrase = randWord[randIndex:randIndex+3]
			frequency = rawWords.count(phrase)
			if (frequency > freqThreshold): #make sure phrase appears enough times
				self.phrase = phrase
				self.word = randWord
				belowThreshold = 0
#			print(f"word: {randWord}\nindex: {randIndex}\nphrase: {phrase}\nfrequency: {frequency}")

	def timer(self, startMsg):
		async def background_counter(ctx):
			await bot.wait_until_ready()
			counterMessage = None
			global moons
			while not bot.is_closed():
				if self.timeCounter == 9:
					return
				elif self.timeCounter == 0:
					await ctx.send(startMsg)
					counterMessage = await ctx.send(moons[self.timeCounter])
				else:
					await counterMessage.edit(content=moons[self.timeCounter])
				await asyncio.sleep(1)
				self.timeCounter += 1
		bot.loop.create_task(background_counter(self.ctx))

@bot.command()
async def teatest(ctx):
	tea1 = Tea(ctx)
	return 0






@bot.command(aliases=["moontea"])
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