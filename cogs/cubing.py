import discord
from discord.ext import commands

from pyTwistyScrambler import scrambler333, scrambler222, scrambler444, scrambler555
import datetime
from zoneinfo import ZoneInfo
import pickle
import re
import bisect
from table2ascii import table2ascii as t2a, PresetStyle, Alignment

class Cubing(commands.Cog):

	def __init__(self, bot):
		self.bot = bot

		self.lastDay = { #last day a daily scramble was created
			"2x2" : "",
			"3x3" : "",
			"4x4" : "",
			"5x5" : "",
		}
		self.threads = {} #threads for different cubes {"3x3", discord.Thread}
		self.lbMessages = {} #the message in each thread that displays the leaderboard {cube, discord.Message}
		self.dailyScores = {} #dict holding sorted lists holding tuples {cube, [(user, float(time)]}
#		self.scrambleQueue = []
#		self.queueEnjoyers = {}

#	queue = commands.Group("Queue")
	"""
	@commands.group("queue")
	async def addtoqueue(self, ctx, count):
		if int(count) > 30:
			await ctx.send("brother seek help <:Starege:944414670830325830>")
			return
		for i in range(int(count)):
			self.scrambleQueue.append(scrambler333.get_WCA_scramble())
		await ctx.send('\n'.join(self.scrambleQueue))

	@addtoqueue.error
	async def give_error(self, ctx, error):
		if isinstance(error, commands.MemberNotFound):
			await ctx.send("That user was not found")
		else:
			pass

	@commands.command()
	async def scram(self, ctx):
		await ctx.send(self.scrambleQueue.pop(0))
		self.queueEnjoyers = dict.fromkeys(self.queueEnjoyers, 0)

	@commands.command()
	async def joinqueue(self, ctx):
		self.queueEnjoyers.update({ctx.author.id : 0})
		await ctx.send("welcome to the queue <:Squidtoil:1144317094964506624>")
		print(self.queueEnjoyers)

	@commands.Cog.listener()
	async def on_message(self, message):
		if message.author == self.bot.user:
			return

		if message.author.id in self.queueEnjoyers.keys() and '.' in message.content:
			self.queueEnjoyers[message.author.id] = 1
			if all(enjoyer == 1 for enjoyer in self.queueEnjoyers.values()):
				await message.channel.send(self.scrambleQueue.pop(0))
				self.queueEnjoyers = dict.fromkeys(self.queueEnjoyers, 0) #reset all enjoyers back to 0
	"""




	def generateScramble(self, puzzle):
		match puzzle:
			case "2" | "2x2":
				return scrambler222.get_WCA_scramble()
			case "3" | "3x3":
				return scrambler333.get_WCA_scramble()
			case "4" | "4x4":
				return scrambler444.get_WCA_scramble()
			case "5" | "5x5":
				return scrambler555.get_WCA_scramble()
			case _:
				return None


	@commands.command()
	async def scramble(self, ctx, puzzle):
		scramble = self.generateScramble(puzzle)
		if scramble:
			await ctx.send(scramble)
		else:
			await ctx.send("List of supported scrambles: 2x2, 3x3, 4x4, 5x5")


	@commands.command()
	async def dailyscramble(self, ctx, puzzle):
		if isinstance(ctx.channel, discord.Thread):
			await ctx.send("You can't do that in a thread.")
			return

		currentDay = datetime.datetime.now(ZoneInfo("America/Chicago")).strftime("%Y-%m-%d")
		if 'x' not in puzzle:
			puzzle = puzzle + 'x' + puzzle

		if puzzle not in self.lastDay.keys():
			await ctx.send("List of supported scrambles: 2x2, 3x3, 4x4, 5x5")
			return

		if self.lastDay[puzzle] < currentDay:
			await self.createDailyThread(ctx, self.generateScramble(puzzle), puzzle)
		else:
			await ctx.send(f"A {puzzle} scramble has already been rolled today.")


	@scramble.error
	@dailyscramble.error
	async def scramble_error(self, ctx, error):
		if isinstance(error, commands.MissingRequiredArgument):
			await ctx.message.reply("Enter the cube you'd like a scramble for.")
		else:
			pass


	async def createDailyThread(self, ctx, scramble, cube):
		if cube in self.threads.keys():
			await self.threads[cube].archive()
			self.dailyScores[cube].clear()

		today = datetime.datetime.now(ZoneInfo("America/Chicago")).strftime("%Y-%m-%d")
		self.lastDay[cube] = today
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

		for user in self.dailyScores[cube]:
			if user[0].id == ctx.author.id:
				await ctx.message.reply("You've already submitted a time.")
				return		

		timeMatch = re.findall(r"(?:(\d{1,2}):)?(\d{2})\.(\d{1,3})", time)[0]
		if timeMatch:
			solveTime = (int(timeMatch[0] or 0) * 60) + int(timeMatch[1]) + float("0." + timeMatch[2])
		else:
			await ctx.message.reply("Invalid input. A valid time looks like `m:ss.ff` or `ss.ff`. For example: `15.79`")
			return

		bisect.insort_left(self.dailyScores[cube], (ctx.author, solveTime), key=lambda x: x[1]) #insert sorted by solve time
		await ctx.message.reply("Time recorded.")
		await self.updateLeaderboard(cube)
		

	async def updateLeaderboard(self, cube):
		scoresArr = []
		for user, time in self.dailyScores[cube]:
			minutes      = int(time // 60)
			seconds      = int(time % 60)
			milliseconds = int(time % 1 * 1000)
			if minutes:
				timeStr = f"{minutes}:{seconds}.{milliseconds}"
			else:
				timeStr = f"{seconds}.{milliseconds}"
			scoresArr.append([user.name, timeStr])
		output = t2a(
			header=["User", "Time"],
			body=scoresArr,
			style=PresetStyle.thin_compact,
			alignments=[Alignment.LEFT, Alignment.RIGHT]
		)
		await self.lbMessages[cube].edit(f"```\n{output}\n```")
		

	@commands.command(hidden=True)
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