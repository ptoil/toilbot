import discord
from discord.ext import commands

import random
import asyncio

########## GLOBALS

teaGame = None #will hold the Tea object
teaExecute = None #for mixtea
teaPrompts = {
	"long":  "Type the **longest** word containing: ",
	"quick": "**Quickly** type a word containing: ",
	"many":  "Type as **many** words as possible containing: "
}
moons = [":full_moon:", ":waxing_gibbous_moon:", ":first_quarter_moon:", ":waxing_crescent_moon:", ":new_moon:", 
		 ":waning_crescent_moon:", ":last_quarter_moon:", ":waning_gibbous_moon:", ":full_moon:"]
freq_thresh = 500

emoji_first_place  = "🥇"
emoji_second_place = "🥈"
emoji_third_place  = "🥉"
emoji_medal        = "🏅"
emoji_check_mark   = "✅"

########## END GLOBALS

class Score:

	def __init__(self):
		self.score = 0
		self.words = []
		self.words.append("")


class Tea:

	scores = {}
	usedPhrases = []

	def __init__(self, ctx, bot):
		self.ctx = ctx
		self.bot = bot
		self.rawWords = open("collins_scrabble.txt", "r").read()
		self.wordsList = self.rawWords.split("\n")
		self.phrase = ""
		self.randWord = ""
		self.timeCounter = 0
		self.roundOver = 0
		self.usedWords = []
		self.roundScores = {} #{discord.Member, Score[score, word]}
		self.teaMode = ""
		self.active = True

	async def startGame(self):
		self.generateWord()
		self.timer()
		await asyncio.sleep(10)

		self.roundOver = 1
		self.active = False
		if self.timeCounter == 10:
			return #game was quit

		sortedScores = sorted(self.roundScores.items(), key = lambda kv:(kv[1].score, kv[0].display_name), reverse=True)
#			removeScores = []
#			for i in sortedScores:
#				if i[1] == 0:
#					removeScores.append(i)
#			for i in removeScores:
#				sortedScores.remove(i)

		for i in self.roundScores:
			if i not in self.scores:
				self.scores[i] = 0
			self.scores[i] += self.roundScores[i].score

		if len(sortedScores) == 0:
			await self.ctx.send(f"Nobody wins the round. A word that would've been accepted is **{self.randWord}**.")
		else:
			winOutput = ""
			i = 0
			for score in sortedScores:
				if i == 0:
					winOutput += ":first_place: "
				elif i == 1:
					winOutput += ":second_place: "
				elif i == 2:
					winOutput += ":third_place: "
				else:
					winOutput += ":medal "
				if not isinstance(self, ManyTea):
					if score[1].score > 1:
						winOutput += score[0].mention + " wins **" + str(score[1].score) + "** points with the word **" + score[1].words[0].upper() + "**. (" + str(self.scores[score[0]]) + ")\n"
					elif score[1].score == 1:
						winOutput += score[0].mention + " wins **" + str(score[1].score) + "** point with the word **" + score[1].words[0].upper() + "**. (" + str(self.scores[score[0]]) + ")\n"
					elif score[1].score == 0:
						winOutput += score[0].mention + " wins **" + str(score[1].score) + "** points. (" + str(self.scores[score[0]]) + ")\n"
					else:
						print("error: negative score")
				else:
					if score[1].score > 1:
						winOutput += score[0].mention + " wins **" + str(score[1].score) + "** points with the word **" + score[1].words[0].upper() + "**. (" + str(self.scores[score[0]]) + ")\n"
					elif score[1].score == 1:
						winOutput += score[0].mention + " wins **" + str(score[1].score) + "** point with the word **" + score[1].words[0].upper() + "**. (" + str(self.scores[score[0]]) + ")\n"
					elif score[1].score == 0:
						winOutput += score[0].mention + " wins **" + str(score[1].score) + "** points. (" + str(self.scores[score[0]]) + ")\n"
					else:
						print("error: negative score")
				i += 1

			await self.ctx.send(winOutput)

#	def submitWord(self, word, user): #overridden by subclasses

	def generateWord(self):
		belowThreshold = 1
		while belowThreshold == 1:
			randWord = self.wordsList[random.randint(0, len(self.wordsList)-1)]
			randIndex = random.randint(0, len(randWord)-3)
			phrase = randWord[randIndex:randIndex+3]
			frequency = self.rawWords.count(phrase)
			if (frequency > freq_thresh and phrase not in self.usedPhrases): #make sure phrase appears enough times
				self.phrase = phrase
				self.randWord = randWord
				self.usedPhrases.append(phrase)
				belowThreshold = 0
#			print(f"word: {randWord}\nindex: {randIndex}\nphrase: {phrase}\nfrequency: {frequency}")

	def timer(self):
		async def background_counter(ctx):
			await self.bot.wait_until_ready()
			counterMessage = None
			global moons
			while not self.bot.is_closed():
				if self.timeCounter >= 10: #game was quit
					return
				elif self.timeCounter == 9: #timer is done
					return
				elif self.timeCounter == 0: #start timer
					await ctx.send(teaPrompts[self.teaMode] + "**" + self.phrase + "**")
					counterMessage = await ctx.send(moons[self.timeCounter])
				else: #update timer
					await counterMessage.edit(content=moons[self.timeCounter])
				self.timeCounter += 1
				await asyncio.sleep(1)				
		self.bot.loop.create_task(background_counter(self.ctx))

	def isActive(self):
		return self.active

	def stop(self):
		self.timeCounter = 10


class LongTea(Tea):

	def __init__(self, ctx, bot):
		super().__init__(ctx, bot)
		self.teaMode = "long"
		self.longestWord = ""

	def submitWord(self, word, user):
		if user not in self.roundScores:
			self.roundScores[user] = Score()
		if self.phrase.lower() in word.lower() and word.lower() not in self.usedWords and len(word) > self.roundScores[user].score:
			if word.upper() in self.wordsList: 
				self.usedWords.append(word.lower())
				self.roundScores[user].words[0] = word.lower()
				if len(word) == 4:
					self.roundScores[user].score = 1
				elif len(word) == 5:
					self.roundScores[user].score = 2
				elif len(word) == 6:
					self.roundScores[user].score = 3
				elif len(word) == 7 or len(word) == 8:
					self.roundScores[user].score = 4
				elif len(word) == 9 or len(word) == 10:
					self.roundScores[user].score = 5
				elif len(word) == 11 or len(word) == 12:
					self.roundScores[user].score = 6
				elif len(word) >= 13:
					self.roundScores[user].score = 7
				else:
					print("score calculation error")
				longestUser = max(self.roundScores, key=lambda x: self.roundScores[x].score)
				if longestUser == user:
					self.longestWord = word.upper()
					return 1 #longest word for all #first_place
				else:
					return 5 #longest word for user #check_mark
			else:
				return None #invalid word


class QuickTea(Tea):
	
	def __init__(self, ctx, bot):
		super().__init__(ctx, bot)
		self.teaMode = "quick"
		self.placing = 0

	def submitWord(self, word, user):
		if user not in self.roundScores:
			self.roundScores[user] = Score()
		if self.phrase.lower() in word.lower() and word.lower() not in self.usedWords and self.roundScores[user].score == 0:
			if word.upper() in self.wordsList: 
				self.usedWords.append(word.lower())
				self.roundScores[user].words[0] = word.lower()
				if self.placing < 4:
					self.placing += 1
				if self.placing == 1:
					self.roundScores[user].score = 5
				elif self.placing == 2:
					self.roundScores[user].score = 3
				elif self.placing == 3:
					self.roundScores[user].score = 2
				elif self.placing > 3:
					self.roundScores[user].score = 1
				else:
					print("score calculation error")
				return self.placing #1 for 1st, 2 for 2nd, 3 for 3rd, 4 for medals
			else:
				return None #invalid word


class ManyTea(Tea):
	
	def __init__(self, ctx, bot):
		super().__init__(ctx, bot)
		self.teaMode = "many"

	def submitWord(self, word, user):
		if user not in self.roundScores:
			self.roundScores[user] = Score()
		if self.phrase.lower() in word.lower() and word.lower() not in self.usedWords:
			if word.upper() in self.wordsList:
				self.usedWords.append(word.lower())
				if self.roundScores[user].words[0] == "":
					self.roundScores[user].words[0] = word.lower()
				else:
					self.roundScores[user].words.append(word.lower())
				if self.roundScores[user].score >= 6:
					self.roundScores[user].score += 1
				elif self.roundScores[user].score < 6:
					self.roundScores[user].score += 2
				else:
					print("score calculation error")
				return 5 #check_mark
			else:
				return None #invalid word

class TeaExecuter:

	def __init__(self, ctx, bot):
		self.ctx = ctx
		self.bot = bot
		self.gamesArray = []
		for i in range(5):
			self.gamesArray.append("long")
		for i in range(5):
			self.gamesArray.append("quick")
		for i in range(3):
			self.gamesArray.append("many")
		self.gameExited = 0

	async def startGame(self):
		global teaGame
		for i in range(len(self.gamesArray)):
			teaMode = self.gamesArray.pop(random.randint(0, len(self.gamesArray)-1))
			if teaMode == "long":
				teaGame = LongTea(self.ctx, self.bot)
			elif teaMode == "quick":
				teaGame = QuickTea(self.ctx, self.bot)
			elif teaMode == "many":
				teaGame = ManyTea(self.ctx, self.bot)
			else:
				await self.ctx.send("error: h")
			await teaGame.startGame()
			await asyncio.sleep(5)
			if self.gameExited == 1:
				return

		await asyncio.sleep(1)

		sortedScores = sorted(teaGame.scores.items(), key = lambda kv:(kv[1], kv[0].display_name), reverse=True)
#			removeScores = []
#			for i in sortedScores:
#				if i[1] == 0:
#					removeScores.append(i)
#			for i in removeScores:
#				sortedScores.remove(i)

		if len(sortedScores) == 0:
			await self.ctx.send("Nobody wins! HAHAHA! Fuck you!")
		else:
			winOutput = "Standings:\n"
			i = 0
			for score in sortedScores:
				if i == 0:
					winOutput += ":first_place: "
				elif i == 1:
					winOutput += ":second_place: "
				elif i == 2:
					winOutput += ":third_place: "
				else:
					winOutput += ":medal "
				winOutput += score[0].mention + ": " + str(score[1]) + " points.\n" #TODO point scaling
				i += 1

			await self.ctx.send(winOutput)

	def stop(self):
		self.gameExited = 1

class MixTea(commands.Cog):

	def __init__(self, bot):
		self.bot = bot

	@commands.Cog.listener()
	async def on_message(self, message):
		if message.author == self.bot.user:
			return
		
		global teaGame
		if teaGame is not None and teaGame.isActive() and message.channel == teaGame.ctx.channel:
			wordStatus = teaGame.submitWord(message.content, message.author)
			teaMode = teaGame.teaMode
			if teaMode == "long":
				if wordStatus == 1:
					await message.add_reaction(emoji_first_place)
				elif wordStatus == 2:
					await message.add_reaction(emoji_check_mark)
			elif teaMode == "quick":
				if wordStatus == 1:
					await message.add_reaction(emoji_first_place)
				elif wordStatus == 2:
					await message.add_reaction(emoji_second_place)
				elif wordStatus == 3:
					await message.add_reaction(emoji_third_place)
				elif wordStatus == 4:
					await message.add_reaction(emoji_medal)
			elif teaMode == "many":
				pass
			else:
				await message.channel.send("error: w")


			if wordStatus == 1:
				await message.add_reaction(emoji_first_place)
			elif wordStatus == 2:
				await message.add_reaction(emoji_second_place)
			elif wordStatus == 3:
				await message.add_reaction(emoji_third_place)
			elif wordStatus == 4:
				await message.add_reaction(emoji_medal)
			elif wordStatus == 5:
				await message.add_reaction(emoji_check_mark)
		
#		await self.bot.process_commands(message)

	@commands.command()
	async def longtea(self, ctx):
		global teaGame
		if teaGame is not None:
			await ctx.send("There is already a game in progress.")
			return
		teaGame = LongTea(ctx, self.bot)
		await teaGame.startGame()
		teaGame = None

	@commands.command()
	async def quicktea(self, ctx):
		global teaGame
		if teaGame is not None:
			await ctx.send("There is already a game in progress.")
			return
		teaGame = QuickTea(ctx, self.bot)
		await teaGame.startGame()
		teaGame = None

	@commands.command()
	async def manytea(self, ctx):
		global teaGame
		if teaGame is not None:
			await ctx.send("There is already a game in progress.")
			return
		teaGame = ManyTea(ctx, self.bot)
		await teaGame.startGame()
		teaGame = None

	@commands.command()
	async def mixtea(self, ctx):
		global teaExecute
		global teaGame
		if teaGame is not None:
			await ctx.send("There is already a game in progress")
			return
		teaExecute = TeaExecuter(ctx, self.bot)
		await teaExecute.startGame()
		teaExecute = None




	@commands.command()
	async def scores(self, ctx):
		global teaGame
		if teaGame is None:
			await ctx.send("No active tea game.")
			return
		output = ""
		sortedScores = sorted(teaGame.scores.items(), key = lambda kv:(kv[1], kv[0].display_name), reverse=True)
		for score in sortedScores:
			output += score[0].mention + ": " + str(score[1]) + "\n"
		await ctx.send(output)
#		await ctx.send(teaGame.scores)

	@commands.command()
	async def exitgame(self, ctx):
		global teaGame
		global teaExecute
		if teaGame is None:
			await ctx.send("No active tea game.")
			return
		teaGame.stop()
		teaGame = None
		await ctx.send("Game was quit.")
		if teaExecute is None:
			return
		teaExecute.stop()
		teaExecute = None

def setup(bot):
		bot.add_cog(MixTea(bot))