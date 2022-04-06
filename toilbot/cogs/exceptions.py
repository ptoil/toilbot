import discord
from discord.ext import commands

class NotInToilbotChannel(commands.CheckFailure):
	name = "NotInToilbotChannel"

class NotInToilbotOrCubingChannel(commands.CheckFailure):
	name = "NotInToilbotOrCubingChannel"

class NotOwnerOrGuildOwner(commands.CheckFailure):
	name = "NotOwnerOrGuildOwner"

class ChannelCheck:
	def in_toilbot_channel():
		async def predicate(ctx):
			if ctx.author.id == 205908835435544577: #doesnt apply to bot owner
				return True
			if ctx.guild.id == 734703203911729162 or ctx.guild.id == 948076562975170621: #only applies to ptoils server (or forevers server for now until i set up a command for it)
				if ctx.channel.name == "toilbot":
					return True
				else:
					raise NotInToilbotChannel()
			else:
				return True
		return commands.check(predicate)

	def in_toilbot_or_cubing_channel():
		async def predicate(ctx):
			if ctx.author.id == 205908835435544577: #doesnt apply to bot owner
				return True
			if ctx.guild.id == 734703203911729162: #only applies to ptoils server
				if ctx.channel.name == "toilbot" or ctx.channel.name == "cubing":
					return True
				else:
					raise NotInToilbotOrCubingChannel()
			else:
				return False #I only want this in my server
		return commands.check(predicate)

	def is_owner_or_guild_owner():
		async def predicate(ctx):
			if ctx.author.id == 205908835435544577: #ptoil
				return True
			elif ctx.author.id == ctx.guild.owner_id:
				return True
			else:
				raise NotOwnerOrGuildOwner()
		return commands.check(predicate)
