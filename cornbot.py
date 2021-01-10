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

cornFreq = 200

########## END CONSTANTS


bot = commands.Bot(command_prefix='.')

@bot.event
async def on_ready():
	print(f'{bot.user} has connect to Discord!')

cornStorm = 0

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
	if message.channel.name == "bot-testing":
		await bot.process_commands(message)
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

@bot.command()
async def goblin(ctx):
	goblinFile = open("goblins.txt", "r")
	goblins = goblinFile.read().split("\n")
	await ctx.send(random.choice(goblins))

@bot.command()
async def addgoblin(ctx, link: str):
	goblinFile = open("goblins.txt", "a")
	goblinFile.write("\n" + link)
	goblinFile.close()
	

@bot.command(brief="Only usable by ptoil", description="You really have no idea what this does? It shuts down the bot duh\nThe command can only be used by ptoil")
async def shutdown(ctx, botName: str):
	if ctx.author.id == botOwner:
		if botName == "cornbot":
			await ctx.send("Shutting down")
			await bot.logout()
	else:
		await ctx.send(f"{ctx.author.mention} You don't have permission to use that command.")


bot.run(TOKEN)