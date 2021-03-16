# cornbot.py
import os
from dotenv import load_dotenv

import math
import random
import re

import discord
from discord.ext import commands

########## CONSTANTS

load_dotenv()
TOKEN = os.getenv("CORNBOT_TOKEN")

botOwner = 205908835435544577;

cornFreq = 200

########## END CONSTANTS
########## VARIABLES

cornStorm = 0
reverseStorm = 0

goblinNum = -1

########## END VARIABLES

bot = commands.Bot(command_prefix='.')

@bot.event
async def on_ready():
	print(f'{bot.user} has connect to Discord!')

def cornRand (storm):
	if storm == 0:
		return random.randint(0, cornFreq)
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

	wendys = re.search("w+(e|.*)n+d+y+'*s*", message.content.lower())
	skz    = re.search("(skz)|(stray kids)", message.content.lower())
	ty     = re.search(".*( +|^)((ty)|(thx)|(thank)).*((bot)|(corn))", message.content.lower())

	if wendys is not None:
		await message.channel.send("NO WENDYS!!!")

	if skz is not None:
		await message.channel.send("stfu weeb")

	if ty is not None:
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

	if reverseStorm == 1:
		await message.channel.send(message.content[::-1])


	await bot.process_commands(message) #this fucking line is needed to stop the on_message function from preventing commands from being called


@bot.command(brief="Increases chance for a CORN message", description="Increases the chance from 1/200 to 1/10\nDoesn't do anything if the cornado is active\n(the chances are actually 1/201 and 1/11 but idc dont tell anyone)")
async def cornado(ctx):
	global cornStorm
	cornStorm = 1

@bot.command(brief="Lets you know if there is a cornado in effect", description="Says \"The skies are clear, sleep my child\" if there is no cornado in effect\nSays \"PANIC PANIC CORNADO IS HERE PANIC PANIC\" if there is a cornado in effect")
async def cornstatus(ctx):
	global cornStorm
	if cornStorm == 0:
		await ctx.send("The skies are clear, sleep my child")
	elif cornStorm == 1:
		await ctx.send("PANIC PANIC PANIC CORNADO IS HERE PANIC PANIC PANIC")

@bot.command(brief="Reverts Cornado", description="Decreases chance from 1/10 to 1/100\nDoesn't do anything if the cornado isn't active")
async def noplacelikehome(ctx):
	global cornStorm
	cornStorm = 0

@bot.command()
async def say(ctx, botName: str, *strInput: str):
	if ctx.author.id == botOwner:
		if (botName == "cornbot"):
			await ctx.send(" ".join(strInput))
	else:
		await ctx.send(f"{ctx.author.mention} You don't have permission to use that command.")

@bot.command()
async def dodrop(ctx):
	await ctx.send(".drop")

@bot.command(aliases=["g"])
async def goblin(ctx):
	goblinFile = open("goblins.txt", "r")
	goblins = goblinFile.read().split("\n")
	global goblinNum
	goblinNum = random.randint(0, len(goblins))
	await ctx.send(goblins[goblinNum])

@bot.command(aliases=["addg", "ag"])
async def addgoblin(ctx, link: str):
	goblinFile = open("goblins.txt", "a")
	goblinFile.write("\n" + link)
	goblinFile.close()
	await ctx.send("Goblin added")

@bot.command(aliases=["gcount", "gc"])
async def goblincount(ctx):
	goblinFile = open("goblins.txt", "r")
	goblins = goblinFile.read().split("\n")
	await ctx.send(len(goblins))

@bot.command(aliases=["viewg", "vg"])
async def viewgoblin(ctx, num: int):
	goblinFile = open("goblins.txt", "r")
	goblins = goblinFile.read().split("\n")
	if num < 1:
		await ctx.send("AHHHHHHHH")
	else:
		try:
			await ctx.send(goblins[num-1])
		except IndexError:
			await ctx.send("Goblin doesn't exist")

@bot.command(aliases=["deleteg", "delg", "dg"])
async def deletegoblin(ctx, num: int):
	goblinFile = open("goblins.txt", "r+")
	goblins = goblinFile.read().split("\n")
	goblinFile.seek(0)

	if num < 1:
		await ctx.send("AHHHHHHHH")
	else:
		try:
			del goblins[num-1]
			i = 0
			for gob in goblins:
				if (i ==0):
					i += 1
				else:
					goblinFile.write("\n")
				goblinFile.write(gob)
			goblinFile.truncate()
			goblinFile.close()
			await ctx.send("Goblin deleted")
		except IndexError:
			await ctx.send("Goblin doesn't exist")

@bot.command(aliases=["gnumber", "gnum", "gn"])
async def goblinnumber(ctx):
	global goblinNum
	if goblinNum == -1:
		await ctx.send("No goblins have been sent yet. lol you idiot")
	else:
		await ctx.send(goblinNum+1)

@bot.command()
async def reverse(ctx):
	global reverseStorm
	reverseStorm = 1

@bot.command()
async def forward(ctx):
	global reverseStorm
	reverseStorm = 0

@bot.command()
async def ping(ctx):
	await ctx.send(str(math.floor(bot.latency * 1000)) + "ms")

@bot.command(brief="Only usable by ptoil", description="You really have no idea what this does? It shuts down the bot duh\nThe command can only be used by ptoil")
async def shutdown(ctx, botName: str):
	if ctx.author.id == botOwner:
		if botName == "cornbot":
			await ctx.send("Shutting down")
			print("Bot was shutdown")
			await bot.logout()
	else:
		await ctx.send(f"{ctx.author.mention} You don't have permission to use that command.")


bot.run(TOKEN)