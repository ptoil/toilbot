import discord
from discord.ext import commands

from .exceptions import *

from cobe.brain import Brain
import os
import time

class Cobe(commands.Cog):

	def __init__(self, bot):
		self.bot = bot
		self.brains = {}
		self.cooldown = 0

	@commands.Cog.listener()
	async def on_ready(self):
		if not os.path.exists("cogs/cobe"):
			os.makedirs("cogs/cobe")
		for guild in self.bot.guilds:
			self.brains[guild.id] = Brain(f"cogs/cobe/cobe-{guild.id}.brain")

	@commands.Cog.listener()
	async def on_message(self, message):
		if message.author == self.bot.user:
			return

		m = message.content.replace(f"<@!{self.bot.user.id}>", "", 1)
		msgWithoutPing = m.replace(f"<@{self.bot.user.id}>", "", 1)
#		print(f"\"{msgWithoutPing}\" learned")
		self.brains[message.guild.id].learn(msgWithoutPing)

		if self.bot.user in message.mentions and self.cooldown < time.time():
			self.cooldown = time.time() + 5
			await message.channel.send(self.brains[message.guild.id].reply(msgWithoutPing))

	@commands.command()
	@commands.is_owner()
	async def loadbrain(self, ctx):
		c = 0
		learned = 0
		currentChannel = ""
		prog = await ctx.send(f"Currently reading {currentChannel}. {c} messages read, {learned} messages learned.")
		for channel in ctx.guild.channels:
			if isinstance(channel, discord.TextChannel):
				currentChannel = channel.name
				await prog.edit(f"Currently reading {currentChannel}. {c} messages read, {learned} messages learned.")
				async for message in channel.history(limit=None):
					if message.author.id != self.bot.user.id and message.content != "" and message.content[0] != '.' and message.content[0] != ',':
						msgWithoutPing = message.content.replace(f"<@!{self.bot.user.id}>", "")
						self.brains[ctx.guild.id].learn(msgWithoutPing)
						learned += 1
					else:
#						print(f"\"{msg.content}\" skipped")
						pass
					c += 1
					if c % 500 == 0:
						await prog.edit(f"Currently reading {currentChannel}. {c} messages read, {learned} messages learned.")
		await ctx.send(f"Done! {c} total messages read. {learned} messages learned.")

def setup(bot):
	bot.add_cog(Cobe(bot))
