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

botOwner = 205908835435544577;

#mixtea
freqThreshold = 500

emoji_first_place = "🥇"
emoji_second_place = "🥈"
emoji_third_place = "🥉"

########## END CONSTANTS

bot = commands.Bot(command_prefix='.')

@bot.event
async def on_ready():
	print(f'{bot.user} has connect to Discord!')


@bot.command()
async def longtea(ctx):
	wordFile = open("collins_scrabble.txt", "r")
	rawWords = wordFile.read()
	wordsList = rawWords.split("\n")

	gameCounter = 0
	while gameCounter < 5:
		longestCharacters = 0
		longestWord = ""
		longestUser = None
		phrase = ""
		
		belowThreshold = 1
		while belowThreshold == 1:
			randWord = wordsList[random.randint(0, len(wordsList)-1)]
			randIndex = random.randint(0, len(randWord)-3)
			phrase = randWord[randIndex:randIndex+3]
			frequency = rawWords.count(phrase)
			if (frequency > freqThreshold):
				belowThreshold = 0
#			await ctx.send(f"word: {randWord}\nindex: {randIndex}\nphrase: {phrase}\nfrequency: {frequency}")

		timeCounter = 0
		async def background_counter():
			await bot.wait_until_ready()
			counterMessage = None
			moons = [":full_moon:", ":waxing_gibbous_moon:", ":first_quarter_moon:", ":waxing_crescent_moon:", ":new_moon:", 
					 ":waning_crescent_moon:", ":last_quarter_moon:", ":waning_gibbous_moon:", ":full_moon:"]
			while not bot.is_closed():
				nonlocal timeCounter
				if gameCounter == 6:
					timeCounter = 9
				if timeCounter == 9:
					return
				elif timeCounter == 0:
						await ctx.send(f"Type the longest word containing: **{phrase}**")
						counterMessage = await ctx.send(moons[timeCounter])
				else:
					await counterMessage.edit(content=moons[timeCounter])
				await asyncio.sleep(1)
				timeCounter += 1
		bot.loop.create_task(background_counter())
		
		@bot.event
		async def on_message(message): #could make a general on_message, and have it check for a mixtea flag. if flag is active, then run the code below. would have to include above code too somehow
			if message.author == bot.user:
				return
			if message.channel != ctx.channel:
				await bot.process_commands(message)
				return

			if message.content.lower() == ".exitgame":
				await ctx.send("Game was quit.")
				nonlocal gameCounter
				gameCounter = 6
				return
			if timeCounter == 9:
				await bot.process_commands(message)
				return

			nonlocal longestCharacters
			nonlocal longestUser
			nonlocal longestWord
#			await ctx.send(f"longestCharacters: {longestCharacters}, longestUser: {longestUser}, phrase: {phrase}")
			if phrase.lower() in message.content.lower() and len(message.content) > longestCharacters:
				nonlocal wordsList
				if message.content.upper() in wordsList:
					longestCharacters = len(message.content)
					longestWord = message.content.upper()
					longestUser = message.author
					await message.add_reaction(emoji_first_place)
#					await message.channel.send(f"{message.content.lower()} posted by {longestUser} with {longestCharacters} characters")

		await asyncio.sleep(9)
		if gameCounter == 6:
			return
		elif longestUser == None:
			await ctx.send(f"Nobody wins the round. A word that would've been accepted is **{randWord}**.")
		else:
			await ctx.send(f":medal: {longestUser.mention} wins the round with the word: **{longestWord}**.")

		await asyncio.sleep(3)
		gameCounter += 1


@bot.command()
async def quicktea(ctx):
	wordFile = open("collins_scrabble.txt", "r")
	rawWords = wordFile.read()
	wordsList = rawWords.split("\n")

	gameCounter = 0
	while gameCounter < 5:
		quickArr = []
		phrase = ""
		
		belowThreshold = 1
		while belowThreshold == 1:
			randWord = wordsList[random.randint(0, len(wordsList)-1)]
			randIndex = random.randint(0, len(randWord)-3)
			phrase = randWord[randIndex:randIndex+3]
			frequency = rawWords.count(phrase)
			if (frequency > freqThreshold):
				belowThreshold = 0
#			await ctx.send(f"word: {randWord}\nindex: {randIndex}\nphrase: {phrase}\nfrequency: {frequency}")

		timeCounter = 0
		async def background_counter():
			await bot.wait_until_ready()
			counterMessage = None
			moons = [":full_moon:", ":waxing_gibbous_moon:", ":first_quarter_moon:", ":waxing_crescent_moon:", ":new_moon:", 
					 ":waning_crescent_moon:", ":last_quarter_moon:", ":waning_gibbous_moon:", ":full_moon:"]
			while not bot.is_closed():
				nonlocal timeCounter
				if gameCounter == 6:
					timeCounter = 9
				if timeCounter == 9:
					return
				elif timeCounter == 0:
						await ctx.send(f"Quickly type a word containing: **{phrase}**")
						counterMessage = await ctx.send(moons[timeCounter])
				else:
					await counterMessage.edit(content=moons[timeCounter])
				await asyncio.sleep(1)
				timeCounter += 1
		bot.loop.create_task(background_counter())
		
		@bot.event
		async def on_message(message): #could make a general on_message, and have it check for a mixtea flag. if flag is active, then run the code below. would have to include above code too somehow
			if message.author == bot.user:
				return
			if message.channel != ctx.channel:
				await bot.process_commands(message)
				return

			if message.content.lower() == ".exitgame":
				await ctx.send("Game was quit.")
				nonlocal gameCounter
				gameCounter = 6
				return
			if timeCounter == 9:
				await bot.process_commands(message)
				return

			if phrase.lower() in message.content.lower() and message.author not in quickArr:
				nonlocal wordsList
				if message.content.upper() in wordsList:
					quickArr.append(message.author)
					if len(quickArr) == 1:
						await message.add_reaction(emoji_first_place)
					elif len(quickArr) == 2:
						await message.add_reaction(emoji_second_place)
					else:
						await message.add_reaction(emoji_third_place)

		await asyncio.sleep(9)
		winOutput = ""
		if gameCounter == 6:
			return
		elif len(quickArr) == 0:
			winOutput = "Nobody wins the round. A word that would've been accepted is **" + randWord + "**."
		else:
			i = 0
			while i < len(quickArr):
				if i == 0:
					winOutput += ":emoji_first_place: " + quickArr[i].mention + " wins x points.\n"
				elif i == 1:
					winOutput += ":emoji_second_place: " + quickArr[i].mention + " wins x points.\n"
				else:
					winOutput += ":emoji_third_place: " + quickArr[i].mention + " wins x points.\n"
				i += 1
		await ctx.send(winOutput)
		await asyncio.sleep(3)
		gameCounter += 1


@bot.command()
async def manytea(ctx):
	wordFile = open("collins_scrabble.txt", "r")
	rawWords = wordFile.read()
	wordsList = rawWords.split("\n")

	gameCounter = 0
	while gameCounter < 5:
		longestCharacters = 0
		longestWord = ""
		longestUser = None
		phrase = ""
		
		belowThreshold = 1
		while belowThreshold == 1:
			randWord = wordsList[random.randint(0, len(wordsList)-1)]
			randIndex = random.randint(0, len(randWord)-3)
			phrase = randWord[randIndex:randIndex+3]
			frequency = rawWords.count(phrase)
			if (frequency > freqThreshold):
				belowThreshold = 0
#			await ctx.send(f"word: {randWord}\nindex: {randIndex}\nphrase: {phrase}\nfrequency: {frequency}")

		timeCounter = 0
		async def background_counter():
			await bot.wait_until_ready()
			counterMessage = None
			moons = [":full_moon:", ":waxing_gibbous_moon:", ":first_quarter_moon:", ":waxing_crescent_moon:", ":new_moon:", 
					 ":waning_crescent_moon:", ":last_quarter_moon:", ":waning_gibbous_moon:", ":full_moon:"]
			while not bot.is_closed():
				nonlocal timeCounter
				if gameCounter == 6:
					timeCounter = 9
				if timeCounter == 9:
					return
				elif timeCounter == 0:
						await ctx.send(f"Type the longest word containing: **{phrase}**")
						counterMessage = await ctx.send(moons[timeCounter])
				else:
					await counterMessage.edit(content=moons[timeCounter])
				await asyncio.sleep(1)
				timeCounter += 1
		bot.loop.create_task(background_counter())
		
		@bot.event
		async def on_message(message): #could make a general on_message, and have it check for a mixtea flag. if flag is active, then run the code below. would have to include above code too somehow
			if message.author == bot.user:
				return
			if message.channel != ctx.channel:
				await bot.process_commands(message)
				return

			if message.content.lower() == ".exitgame":
				await ctx.send("Game was quit.")
				nonlocal gameCounter
				gameCounter = 6
				return
			if timeCounter == 9:
				await bot.process_commands(message)
				return

			nonlocal longestCharacters
			nonlocal longestUser
			nonlocal longestWord
#			await ctx.send(f"longestCharacters: {longestCharacters}, longestUser: {longestUser}, phrase: {phrase}")
			if phrase.lower() in message.content.lower() and len(message.content) > longestCharacters:
				nonlocal wordsList
				if message.content.upper() in wordsList:
					longestCharacters = len(message.content)
					longestWord = message.content.upper()
					longestUser = message.author.mention
					await message.add_reaction(emoji_first_place)
#					await message.channel.send(f"{message.content.lower()} posted by {longestUser} with {longestCharacters} characters")

		await asyncio.sleep(9)
		if gameCounter == 6:
			return
		elif longestUser == None:
			await ctx.send(f"Nobody wins the round. A word that would've been accepted is **{randWord}**.")
		else:
			await ctx.send(f":medal: {longestUser} wins the round with the word: **{longestWord}**.")

		await asyncio.sleep(3)
		gameCounter += 1


@bot.command(aliases=["moontea"])
async def moon(ctx):
	counterMessage = None
	counter = 0
	moons = [":full_moon:", ":waxing_gibbous_moon:", ":first_quarter_moon:", ":waxing_crescent_moon:", ":new_moon:", 
			 ":waning_crescent_moon:", ":last_quarter_moon:", ":waning_gibbous_moon:", ":full_moon:"]
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
	if ctx.author.id == botOwner:
		if (botName == "toilbot"):
			await ctx.send(" ".join(strInput))
	else:
		await ctx.send(f"{ctx.author.mention} You don't have permission to use that command.")

@bot.command()
async def dodrop(ctx):
	await ctx.send(".drop")

@bot.command()
async def shutdown(ctx, botName: str):
	if ctx.author.id == botOwner:
		if botName == "toilbot":
			await ctx.send("Shutting down")
			await bot.logout()
	else:
		await ctx.send("You don't have permission to use that command.")

bot.run(TOKEN)