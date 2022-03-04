import discord
from discord.ext import commands

class NotInToilbotChannel(commands.CheckFailure):
	pass

class NotInToilbotOrCubingChannel(commands.CheckFailure):
	pass

class ChannelCheck:
	def in_toilbot_channel():
		async def predicate(ctx):
			if ctx.author.id == 205908835435544577: #doesnt apply to bot owner
				return True
			if ctx.guild.id == 734703203911729162: #only applies to ptoils server
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
				return True
		return commands.check(predicate)