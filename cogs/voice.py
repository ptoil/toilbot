import discord
from discord.ext import commands

import asyncio
import random
from os import listdir
from os.path import isfile, join
import time

class Voice(commands.Cog):

	def __init__(self, bot):
		self.bot = bot
		self.isRandoing = False
		self.context = None
		self.commandCooldown = {} #{user.id : }

	@commands.command()
	@commands.is_owner()
	async def joinVC(self, ctx):
		self.context = ctx
		vChannel = ctx.author.voice
		if vChannel is None:
			await ctx.send("Join a VC first")
			return False
		else:
			await vChannel.channel.connect()
			return True

	@commands.command()
	async def leaveVC(self, ctx):
		self.isRandoing = False
		if ctx.voice_client is not None:
			await ctx.voice_client.disconnect()
		else:
			await ctx.send("I'm not in a vc")

	@commands.command()
	async def randovc(self, ctx):
		if await self.joinVC(ctx):
			prevmp3 = None
			self.isRandoing = True
			while self.isRandoing:
				mp3list = [f for f in listdir("cogs/audio") if isfile(join("cogs/audio", f)) and f.endswith(".mp3")]
				mp3 = random.choice(mp3list)
				while prevmp3 is not None and mp3 == prevmp3:
					mp3 = random.choice(mp3list)
				prevmp3 = mp3
				while ctx.voice_client.is_playing():
					pass #wait until audio isnt playing
				ctx.voice_client.play(discord.FFmpegPCMAudio(source=f"cogs/audio/{mp3}"))
				print(mp3)
				await asyncio.sleep(random.randint(300, 600))

	def listdir(self):
		mp3list = [f for f in listdir("cogs/audio") if isfile(join("cogs/audio", f)) and f.endswith(".mp3")]
		mp3list = [mp3[:-4] for mp3 in mp3list]
		return mp3list

	@commands.command()
	async def audio(self, ctx, name):
		if ctx.author.id not in self.commandCooldown.keys():
			self.commandCooldown[ctx.author.id] = 0
		if self.commandCooldown[ctx.author.id] >= time.time() and not await self.bot.is_owner(ctx.author):
			secondsLeft = int(self.commandCooldown[ctx.author.id] - time.time())
			m, s = divmod(secondsLeft, 60)
			await ctx.message.reply(f"{m}m{s}s left until you can use this command again.")
		elif ctx.voice_client.is_playing():
			await ctx.message.reply("Already playing audio.")
		elif name in self.listdir():
			ctx.voice_client.play(discord.FFmpegPCMAudio(source=f"cogs/audio/{name}.mp3"))
			print(f"{name}.mp3 (audio command)")
			self.commandCooldown[ctx.author.id] = time.time()# + 60
		else:
			await ctx.message.reply("That audio does not exist.")

	@commands.command()
	async def countdown(self, ctx):
		for i in range(3, -1, -1):
			await ctx.send(i) if i > 0 else await ctx.send("GO!")
			await asyncio.sleep(1)

	@commands.command()
	async def listaudios(self, ctx):
		output = [""]
		c = 0
		for mp3 in sorted(self.listdir()):
			output[c] += mp3 + ", "
			if len(output[c]) > 1900:
				output.append("")
				c += 1
		for line in output:
			line = line[:-2]
			await ctx.send(line)

	@commands.Cog.listener()
	async def on_voice_state_update(self, member, before, after):
		evonyvc_id = 968938377355350096
		bludwig_id = 333857138982256642
		evonylore_id = 969429443783323678
		if member.id == bludwig_id and after.channel is not None and after.channel.id == evonyvc_id: #Bludwig enters evony vc
			if before.channel is not None:
				if before.channel.id != evonyvc_id:
					 await self.bot.get_channel(evonylore_id).send("https://cdn.discordapp.com/attachments/969429443783323678/1140398893138452601/makeitmeme_ms2r7.gif")
			else:
				await self.bot.get_channel(evonylore_id).send("https://cdn.discordapp.com/attachments/969429443783323678/1140398893138452601/makeitmeme_ms2r7.gif")

		if member.guild.voice_client is None: #bot isnt in VC
			return

		if before.channel == member.guild.voice_client.channel and after.channel is None:
			if len(before.channel.members) == 1:
				await asyncio.sleep(30)                            #wait a bit
				if len(before.channel.members) == 1:               #if vc still only the bot, then bot heads out
					await member.guild.voice_client.disconnect()
					self.isRandoing = False
					await self.context.send("aight ima head out")


def setup(bot):
		bot.add_cog(Voice(bot))