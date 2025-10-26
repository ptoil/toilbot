#renamed to cobecog due to matching name to the cobe directory
import discord
from discord.ext import commands

import cogs.database as db
from cobe.brain import Brain
import os
import time

class Cobe(commands.Cog):

	def __init__(self, bot):
		self.bot = bot
		self.cooldown = 0


	@commands.Cog.listener()
	async def on_ready(self):
		if not os.path.exists("cogs/brains"):
			os.makedirs("cogs/brains")

		for guild in self.bot.guilds:
			db.addGuild(guild.id)

	@commands.Cog.listener()
	async def on_message(self, message):
		if message.author == self.bot.user or message.content.startswith(self.bot.command_prefix):
			return
		brain = db.getGuildsBrain(message.guild.id)
		if brain is not None:
			msg = self.formatMessage(message)
			if msg is not None:
				Brain(f"cogs/brains/cobe-{brain}.brain").learn(msg)

		if self.bot.user in message.mentions and message.channel.can_send() and self.cooldown < time.time():
			brain = db.getGuildsBrain(message.guild.id)
			if brain is None:
				ctx = await self.bot.get_context(message)
				await ctx.send("In order for toilbot to reply, a brain needs to be selected. Ping ptoil to fix this.")
				return
			else:
				self.cooldown = time.time() + 1
				reply = Brain(f"cogs/brains/cobe-{brain}.brain").reply(msg)
				reply = reply[0:1999] #2000 character limit
				await message.channel.send(reply)

	def formatMessage(self, message): #return None if message should be skipped
		if message.author.id != self.bot.user.id and message.content != "" and len(message.content) <= 500 and len(message.content.split()) <= 100: #no more than 500 characters or 100 words
			msg = message.content
			msg = msg.replace(f"<@!{self.bot.user.id}>", "", 1)
			msg = msg.replace(f"<@{self.bot.user.id}>", "", 1)  #remove first @toilbot ping
			msg = msg.replace("@everyone", "everyone")          #remove @everyone
			if self.bot.printDebugMessages: print(f"\"{msg}\" learned")
			return msg
		#else
		if self.bot.printDebugMessages: print(f"\"{message.content}\" skipped")
		return None
			
	""" #disabled for now, hasnt been updated to use db
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
	"""

	@commands.command()
	@commands.is_owner()
	async def setbrain(self, ctx, brainID):
		db.setGuildsBrain(ctx.guild.id, brainID)
		await ctx.send(f"Brain set for this server.")

	@commands.command()
	@commands.is_owner()
	async def currentbrain(self, ctx):
		brain = db.getGuildsBrain(ctx.guild.id)
		if brain:
			await ctx.send(f"Brain for this server is: {brain}")
		else:
			await ctx.send("Brain is not set for this guild.")

	@commands.command()
	@commands.is_owner()
	async def unsetbrain(self, ctx):
		brain = db.getGuildsBrain(ctx.guild.id)
		if not brain:
			await ctx.send("Brain is not set for this guild.")
		else:
			db.setGuildsBrain(ctx.guild.id, None)
			await ctx.send(f"Brain was {brain}. It is now unset.")

def setup(bot):
	bot.add_cog(Cobe(bot))
