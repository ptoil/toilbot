import discord
from discord.ext import commands
from .exceptions import *

from pyTwistyScrambler import scrambler333, scrambler222, scrambler444, scrambler555
import datetime
import pickle
import re
import bisect
from table2ascii import table2ascii as t2a, PresetStyle, Alignment

class Cubing(commands.Cog):

	def __init__(self, bot):
		self.bot = bot
		self.players = {}
		try:
			self.players = pickle.load(open("saves/players.pickle", "rb"))
		except FileNotFoundError:
			pickle.dump(self.players, open("saves/players.pickle", "wb"))

		self.lastDay = { #last day a daily scramble was created
			"2x2" : 0,
			"3x3" : 0,
			"4x4" : 0,
			"5x5" : 0,
		}
		self.threads = {} #threads for different cubes {"3x3", discord.Thread}
		self.lbMessages = {} #the message in each thread that displays the leaderboard {cube, discord.Message}
		self.dailyScores = {} #dict holding sorted lists holding tuples {cube, [(user, float(time), str(time)]} #saving the input string to eliminate rounding issues on LB

	def savePlayers(self):
		pickle.dump(self.players, open("saves/players.pickle", "wb"))

#	def save

	@commands.command()
	@ChannelCheck.in_toilbot_or_cubing_channel()
	async def scramble(self, ctx, puzzle):
		match puzzle:
			case "2" | "2x2":
				await ctx.send(scrambler222.get_WCA_scramble())
			case "3" | "3x3":
				await ctx.send(scrambler333.get_WCA_scramble())
			case "4" | "4x4":
				await ctx.send(scrambler444.get_WCA_scramble())
			case "5" | "5x5":
				await ctx.send(scrambler555.get_WCA_scramble())
			case _:
				await ctx.send("List of supported scrambles: 2x2, 3x3, 4x4, 5x5")

	@commands.command()
	@ChannelCheck.in_toilbot_or_cubing_channel()
	async def dailyscramble(self, ctx, puzzle):
		if isinstance(ctx.channel, discord.Thread): #This actually shouldnt happen because of the channel check but i'll leave it just in case
			await ctx.send("You can't do that in a thread.")
			return
		match puzzle: #i should see if i can shorten this since it'll get even bigger if i add more scrambles
			case "2" | "2x2": 
				if self.lastDay["2x2"] < datetime.datetime.today().day:
					await self.createDailyThread(ctx, scrambler222.get_WCA_scramble(), "2x2")
					self.lastDay["2x2"] = datetime.datetime.today().day
				else:
					await ctx.send("A 2x2 scramble has already been rolled today.")
			case "3" | "3x3":
				if self.lastDay["3x3"] < datetime.datetime.today().day:
					await self.createDailyThread(ctx, scrambler333.get_WCA_scramble(), "3x3")
					self.lastDay["3x3"] = datetime.datetime.today().day
				else:
					await ctx.send("A 3x3 scramble has already been rolled today.")
			case "4" | "4x4":
				if self.lastDay["4x4"] < datetime.datetime.today().day:
					await self.createDailyThread(ctx, scrambler444.get_WCA_scramble(), "4x4")
					self.lastDay["4x4"] = datetime.datetime.today().day
				else:
					await ctx.send("A 4x4 scramble has already been rolled today.")
			case "5" | "5x5":
				if self.lastDay["5x5"] < datetime.datetime.today().day:
					await self.createDailyThread(ctx, scrambler555.get_WCA_scramble(), "5x5")
					self.lastDay["5x5"] = datetime.datetime.today().day
				else:
					await ctx.send("A 5x5 scramble has already been rolled today.")
			case _:
				await ctx.send("List of supported scrambles: 2x2, 3x3, 4x4, 5x5")

	@scramble.error
	@dailyscramble.error
	async def scramble_error(self, ctx, error):
		if isinstance(error, commands.MissingRequiredArgument):
			await ctx.message.reply("Enter the cube you'd like a scramble for.")
		else:
			pass

	async def createDailyThread(self, ctx, scramble, cube):
		today = datetime.datetime.today().strftime("%Y-%m-%d")
		self.threads[cube] = await ctx.message.create_thread(name=f"{cube} Scramble - {today}")
		await self.threads[cube].send(scramble)
		output = t2a(
			header=["User", "Time"],
			style=PresetStyle.thin_compact,
			alignments=[Alignment.LEFT, Alignment.RIGHT]
		)
		self.lbMessages[cube] = await self.threads[cube].send(f"```\n{output}\n```")
		await self.threads[cube].send("Submit times with `.submit`")

	@commands.command()
	async def submit(self, ctx, time):
		cube = ""
		for c, thread in self.threads.items():
			if ctx.channel.id == thread.id:
				cube = c
				break
		if cube == "": #not in latest daily thread
			return
		if cube not in self.dailyScores.keys():
			self.dailyScores.update({cube : []})

		alreadySubmitted = False
		for user in self.dailyScores[cube]:
			if user[0].id == ctx.author.id:
				alreadySubmitted = True
		if alreadySubmitted:
			await ctx.message.reply("You've already submitted a time.")
			return

		if re.search("\d{1,2}:\d{2}\.\d{2}", time):
			timeArr = re.split("[:.]", time)
			solveTime = (60 * int(timeArr[0])) + int(timeArr[1]) + (.01 * int(timeArr[2]))
		elif re.search("\d{1,2}\.\d{2}", time):
			timeArr = re.split("[.]", time)
			solveTime = int(timeArr[0]) + (.01 * int(timeArr[1]))
		else:
			await ctx.message.reply("Invalid input. A valid time looks like `m:ss.ff` or `ss.ff`. For example: `15.79`")
			return

		bisect.insort_left(self.dailyScores[cube], (ctx.author, solveTime, time), key=lambda x: x[1]) #insert sorted by solve time
		await ctx.message.reply("Time recorded.")
		await self.updateLeaderboard(cube)
		

	async def updateLeaderboard(self, cube):
		scoresArr = []
		for user, timeNum, timeStr in self.dailyScores[cube]:
			scoresArr.append([user.name, timeStr])
		output = t2a(
			header=["User", "Time"],
			body=scoresArr,
			style=PresetStyle.thin_compact,
			alignments=[Alignment.LEFT, Alignment.RIGHT]
		)
		await self.lbMessages[cube].edit(f"```\n{output}\n```")
		
	@commands.command()
	@commands.is_owner()
	async def deltime(self, ctx, member: discord.Member):
		cube = ""
		for c, thread in self.threads.items():
			if ctx.channel.id == thread.id:
				cube = c
				break
		if cube == "": #not in latest daily thread
			return

		for i in range(len(self.dailyScores[cube])):
			if member == self.dailyScores[cube][i][0]:
				del self.dailyScores[cube][i]
				await self.updateLeaderboard(cube)
				await ctx.message.reply("Time deleted.")
				return
		#else member not found
		await ctx.message.reply("User hasn't submitted a time.")



def setup(bot):
	bot.add_cog(Cubing(bot))