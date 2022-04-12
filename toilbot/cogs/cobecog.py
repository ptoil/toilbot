#renamed to cobecog due to matching name to the cobe directory
import discord
from discord.ext import commands

from .exceptions import *

from cobe.brain import Brain
import os
import time
import pickle

class Cobe(commands.Cog):

	def __init__(self, bot):
		self.bot = bot
		self.brains = {}        #{brainID : Brain}
		self.brainPerGuild = {} #{guild.id : brainID}
		self.cooldown = 0

	def saveBrains(self):
		pickle.dump(self.brainPerGuild, open("saves/brainPerGuild.pickle", "wb"))

	@commands.Cog.listener()
	async def on_ready(self):
		try:
			self.brainPerGuild = pickle.load(open("saves/brainPerGuild.pickle", "rb"))
		except FileNotFoundError:
			pickle.dump(self.brainPerGuild, open("saves/brainPerGuild.pickle", "wb"))

		if not os.path.exists("cogs/cobe"):
			os.makedirs("cogs/cobe")
		for brainID in self.brainPerGuild.values():
			if brainID not in self.brains.keys():
				self.brains[brainID] = Brain(f"cogs/cobe/cobe-{brainID}.brain")
				if self.bot.printDebugMessages: print(f"brain loaded: id={brainID}")

	@commands.Cog.listener()
	async def on_message(self, message):
		if message.author == self.bot.user:
			return
		if message.guild.id in self.brainPerGuild.keys():
			msg = self.formatMessage(message)
			if msg is not None:
				self.brains[self.brainPerGuild[message.guild.id]].learn(msg)

		ctx = await self.bot.get_context(message)
		try:
			if await ChannelCheck.in_toilbot_channel().predicate(ctx) and self.bot.user in message.mentions and self.cooldown < time.time():
				if message.guild.id not in self.brainPerGuild.keys():
					await ctx.send("In order for toilbot to reply, a brain needs to be selected. Ping ptoil to fix this.")
					return
				self.cooldown = time.time() + 1
				reply = self.brains[self.brainPerGuild[message.guild.id]].reply(msg)
				reply = reply[0:1999] #2000 character limit
				await message.channel.send(reply)
		except: #cogs.exceptions.NotInToilbotChannel
			pass

	def formatMessage(self, message): #return None if message should be skipped
		if message.author.id != self.bot.user.id and message.content != "" and message.content[0] != '.' and message.content[0] != ',':
			if len(message.content) <= 500 and len(message.content.split()) <= 100: #no more than 500 characters or 100 words
				msg = message.content
				msg = msg.replace(f"<@!{self.bot.user.id}>", "", 1)
				msg = msg.replace(f"<@{self.bot.user.id}>", "", 1)  #remove first @toilbot ping
				msg = msg.replace("@everyone", "everyone")          #remove @everyone
				if self.bot.printDebugMessages: print(f"\"{msg}\" learned")
				return msg
		#else
		if self.bot.printDebugMessages: print(f"\"{message.content}\" skipped")
		else: print("dies of cringe")
		return None
			

	@commands.command()
	@commands.is_owner()
	async def loadbrain(self, ctx):
		c = 0
		learned = 0
		currentChannel = ""
		prog = await ctx.send(f"Currently reading {currentChannel}. {c} messages read, {learned} messages learned.")
		print(f"Loading brain in {ctx.guild.name} ({ctx.guild.id})")
		for channel in ctx.guild.channels:
			if isinstance(channel, discord.TextChannel):
				currentChannel = channel.name
				await prog.edit(f"Currently reading {currentChannel}. {c} messages read, {learned} messages learned.")
				try:
					async for message in channel.history(limit=None):
						msg = self.formatMessage(message)
						if msg is not None:
							self.brains[self.brainPerGuild[ctx.guild.id]].learn(msg)
							learned += 1						
						c += 1
						if c % 1000 == 0:
							await prog.edit(f"Currently reading {currentChannel}. {c} messages read, {learned} messages learned.")
				except discord.Forbidden:
					print(f"skipped: https://discord.com/channels/{message.guild.id}/{message.channel.id}/{message.id}")
		await ctx.send(f"Done! {c} total messages read. {learned} messages learned.")
		print(f"Done! {c} total messages read. {learned} messages learned. {ctx.guild.name} ({ctx.guild.id})")

	@commands.command()
	@commands.is_owner()
	async def setbrain(self, ctx, brainID):
		self.brainPerGuild[ctx.guild.id] = brainID
		if brainID not in self.brains.keys():
			self.brains[brainID] = Brain(f"cogs/cobe/cobe-{brainID}.brain")
			if self.bot.printDebugMessages: print(f"brain loaded: id={brainID}")
		self.saveBrains()
		await ctx.send(f"Brain set for this server.")

def setup(bot):
	bot.add_cog(Cobe(bot))
