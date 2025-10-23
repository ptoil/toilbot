import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import traceback
import asyncio
import cogs.constants as constants
import sqlite3

load_dotenv()
TOKEN = os.getenv("TOILBOT_TOKEN")
PREFIX = os.getenv("PREFIX")

bot = commands.Bot(command_prefix=PREFIX, case_insensitive=True, intents=discord.Intents.all())

@bot.event
async def on_connect():
	bot.printDebugMessages = False
	print(f"{bot.user} has connected to Discord")

@bot.event
async def on_ready():
	print(f"{bot.user} is ready!")

@bot.event
async def on_command_error(ctx, error):
	if isinstance(error, (
		commands.errors.CommandNotFound,
		commands.errors.MissingRequiredArgument,
		commands.errors.MemberNotFound)
	):
		pass
	elif isinstance(error, commands.errors.NotOwner):
		await ctx.send("Only ptoil has access to that command <:FUNgineer:918637730542522408>")
	elif isinstance(error, commands.errors.BotMissingPermissions):
		await ctx.send(error)
	else:
		print('Ignoring exception in command {}:'.format(ctx.command))
		print("".join(traceback.format_exception(type(error), error, error.__traceback__)))
		await ctx.send(f"<@205908835435544577> pepew\n{type(error)}: {error}")

@bot.event
async def process_commands(message):
#	if message.author.bot:
#		return

	ctx = await bot.get_context(message)
	await bot.invoke(ctx)

@bot.command(brief="moon cycle go brr")
async def moon(ctx):
	counterMessage = None
	counter = 0
	while not bot.is_closed():
		if counter == 0:
			counterMessage = await ctx.send(constants.MOONS[counter])
		else:
			await counterMessage.edit(content=constants.MOONS[counter])
		await asyncio.sleep(1)
		counter += 1
		if counter == 9:
			return

@bot.command()
@commands.is_owner()
async def sayy(ctx, *strInput: str):
	await ctx.send(" ".join(strInput))
	await ctx.message.delete()

@bot.command()
@commands.is_owner()
async def say(ctx, *strInput: str):
	await ctx.send(" ".join(strInput))

@bot.command()
async def sourcecode(ctx):
	await ctx.send("https://github.com/ptoil/toilbot")

@bot.command()
@commands.is_owner()
async def shutdown(ctx):
	await ctx.send("Shutting down")
	print("Bot was shutdown")
	await bot.close()

bot.load_extension("cogs.blackjack")   #done
bot.load_extension("cogs.cobecog")     #done
bot.load_extension("cogs.connectfour") #done
bot.load_extension("cogs.cubing")      #needs polish on queue
bot.load_extension("cogs.mixtea")      #needs rewrite, very bugged
bot.load_extension("cogs.roles")       #needs additional checks on role placement
#bot.load_extension("cogs.voice")      #broken

bot.run(TOKEN)
