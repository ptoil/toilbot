import discord
from discord.ext import commands

from .exceptions import *
import random
import asyncio
import io

from PIL import Image, ImageDraw, ImageFont

########## GLOBALS

emoji_first_place  = "🥇"
emoji_second_place = "🥈"
emoji_third_place  = "🥉"
emoji_medal        = "🏅"
emoji_check_mark   = "✅"
emoji_red_x        = "❌"

########## END GLOBALS

class Game():

	def __init__(self, thread, p1, p2):
		self.thread = thread
		self.players = (p1, p2)
		self.currentP = 0
		self.board = [[-1 for j in range(6)] for i in range(7)]
		self.color= {
			-1: (0, 0, 0),
			0: (255, 0, 0), #red
			1: (255, 255, 0) #yellow
		}
		self.gameImages = []

	async def startGame(self):
		await self.drawBoard()

	async def sendImage(self, image):
		with io.BytesIO() as image_bin:
			image.save(image_bin, "PNG")
			image_bin.seek(0)
			await self.thread.send(content=f"{self.players[self.currentP].mention}'s turn", file=discord.File(fp=image_bin, filename="image.png"))

	async def sendImageEnd(self, image):
		with io.BytesIO() as image_bin:
			image.save(image_bin, "PNG")
			image_bin.seek(0)
			await self.thread.send(file=discord.File(fp=image_bin, filename="image.png"))

	async def drawBoard(self):
		im = Image.new("RGBA", (350, 350), (0, 0, 0, 255))
		draw = ImageDraw.Draw(im)
		draw.rectangle([(0, 0), (350, 300)], fill=(0, 0, 255))
		font = ImageFont.truetype("fonts/Arial.ttf", 40)
		for i in range(7):
			draw.text(((i*50)+15, 300), f"{i+1}", font=font)
		for j in range(6):
			for i in range(7):
				draw.ellipse([((i*50)+5, (j*50)+5), (((i+1)*50)-5, ((j+1)*50)-5)], fill=self.color[self.board[i][j]])

		self.gameImages.append(im)
		await self.sendImage(im)

	async def checkForWin(self, i, j):
		win = False
		allWinningTiles = []
		winningTiles = [(i, j)]
		for x in range(1, 4): #left
			if i - x < 0 or self.board[i - x][j] == -1:
				break
			if self.board[i - x][j] == self.currentP:
				winningTiles.append((i - x, j))
			else:
				break
		for x in range(1, 4): #right
			if i + x > 6 or self.board[i + x][j] == -1:
				break
			if self.board[i + x][j] == self.currentP:
				winningTiles.append((i + x, j))
			else:
				break
		if len(winningTiles) >= 4:
			allWinningTiles.extend(winningTiles)
			win = True

		winningTiles = [(i, j)]
		for x in range(1, 4): #up
			if j - x < 0 or self.board[i][j - x] == -1:
				break
			if self.board[i][j - x] == self.currentP:
				winningTiles.append((i, j - x))
			else:
				break
		for x in range(1, 4): #down
			if j + x > 5 or self.board[i][j + x] == -1:
				break
			if self.board[i][j + x] == self.currentP:
				winningTiles.append((i, j + x))
			else:
				break
		if len(winningTiles) >= 4:
			allWinningTiles.extend(winningTiles)
			win = True

		winningTiles = [(i, j)]
		for x in range(1, 4): #TL
			if i - x < 0 or j - x < 0 or self.board[i - x][j - x] == -1:
				break
			if self.board[i - x][j - x] == self.currentP:
				winningTiles.append((i - x, j - x))
			else:
				break
		for x in range(1, 4): #BR
			if i + x > 6 or j + x > 5 or self.board[i + x][j + x] == -1:
				break
			if self.board[i + x][j + x] == self.currentP:
				winningTiles.append((i + x, j + x))
			else:
				break
		if len(winningTiles) >= 4:
			allWinningTiles.extend(winningTiles)
			win = True

		winningTiles = [(i, j)]
		for x in range(1, 4): #BL
			if i - x < 0 or j + x > 5 or self.board[i - x][j + x] == -1:
				break
			if self.board[i - x][j + x] == self.currentP:
				winningTiles.append((i - x, j + x))
			else:
				break
		for x in range(1, 4): #TR
			if i + x > 6 or j - x < 0 or self.board[i + x][j - x] == -1:
				break
			if self.board[i + x][j - x] == self.currentP:
				winningTiles.append((i + x, j - x))
			else:
				break
		if len(winningTiles) >= 4:
			allWinningTiles.extend(winningTiles)
			win = True

		if win:
			await self.winner(allWinningTiles)
			return True
		else:
			return False

	async def checkForTie(self):
		if self.board[0][0] != -1 and self.board[1][0] != -1 and self.board[2][0] != -1 and self.board[3][0] != -1 and self.board[4][0] != -1 and self.board[5][0] != -1 and self.board[6][0] != -1:
			await self.tie()
			return True
		else:
			return False

	async def drop(self, player, col):
		j = 0
		while self.board[col][j] == -1:
			if self.board[col][j+1] == -1:
				j += 1
				if (j >= 5): #no pieces in col yet
					self.board[col][j] = player
					if not await self.checkForWin(col, j) and not await self.checkForTie():
						self.currentP = (self.currentP + 1) % 2
						await self.drawBoard()
					else:
						return #so "column is full" doesnt print on a tie
			else:
				self.board[col][j] = player
				if not await self.checkForWin(col, j) and not await self.checkForTie():
					self.currentP = (self.currentP + 1) % 2
					await self.drawBoard()
					j += 1 #prevent tripping if below
				else:
					return #so "column is full" doesnt print on a tie

		if j == 0:
			await self.thread.send("That column is full, choose another.")

	async def drawBoardWin(self, winningTiles):
		im = Image.new("RGBA", (350, 300), (0, 0, 0, 255))
		draw = ImageDraw.Draw(im)
		draw.rectangle([(0, 0), (350, 300)], fill=(0, 0, 255))
		for j in range(6):
			for i in range(7):
				if (i, j) in winningTiles:
					draw.ellipse([((i*50)+5, (j*50)+5), (((i+1)*50)-5, ((j+1)*50)-5)], fill=self.color[self.board[i][j]], outline=(0, 255, 0), width=3) #fill transparent, outline gold
				else:
					draw.ellipse([((i*50)+5, (j*50)+5), (((i+1)*50)-5, ((j+1)*50)-5)], fill=self.color[self.board[i][j]])

		self.gameImages.append(im)
		await self.sendImageEnd(im)

	async def winner(self, winningTiles):
		await self.drawBoardWin(winningTiles)
		await self.thread.send(f"{self.players[self.currentP].mention} wins the game!")
		await self.createGameGif()
		await self.thread.send("This thread will auto archive in 5 minutes")
		await asyncio.sleep(300)
		self.thread = await self.thread.archive()

	async def tie(self):
		await self.drawBoardWin([]) #no winning tiles
		await self.thread.send("Its a tie! Nobody wins")
		await self.createGameGif()
		await self.thread.send("This thread will auto archive in 5 minutes")
		await asyncio.sleep(300)
		self.thread = await self.thread.archive()

	async def createGameGif(self):
		with io.BytesIO() as image_bin:
			durations = []
			i = 0
			while i < len(self.gameImages):
				if i < 8:
					durations.append(500)
				elif i == len(self.gameImages)-1:
					durations.append(5000)
				else:
					durations.append(1000)
				i += 1

			gif = self.gameImages.pop(0)
			gif.save(image_bin, format="GIF", save_all=True, append_images=self.gameImages, duration=durations, loop=0)
			image_bin.seek(0)
			await self.thread.send(content="GIF", file=discord.File(fp=image_bin, filename="image.gif"))

class Challenge():

	def __init__(self, msg, p1, p2):
		self.message = msg
		self.player1 = p1
		self.player2 = p2


class ConnectFour(commands.Cog):

	def __init__(self, bot):
		self.bot = bot
		self.games = {}
		self.challenge = None

	@commands.command(aliases=["c4"])
	@ChannelCheck.in_toilbot_channel()
	async def connectfour(self, ctx):
		self.cleanGames()
		if isinstance(ctx.channel, discord.Thread):
			await ctx.send("You can't start a challenge in a thread.")
		elif self.challenge is not None:
			await ctx.send("There is already a challenge in progress. Wait for the current challenge to time out or be answered.")
		elif len(ctx.message.mentions) < 1:
			await ctx.send("Please mention the user you would like to play against.")
		elif len(ctx.message.mentions) > 1:
			await ctx.send("You can only play against one user at a time.")
		elif ctx.message.mentions[0] == ctx.author:
			await ctx.send("You can't play against yourself.")
		elif ctx.message.mentions[0] == self.bot.user:
			await ctx.send("I don't want to play with you.")
		else:
			confirm = await ctx.send(f"{ctx.message.mentions[0].mention} {ctx.message.author.display_name} wants to play Connect Four. Do you accept the challenge?")
			self.challenge = Challenge(confirm, ctx.author, ctx.message.mentions[0])
			await confirm.add_reaction(emoji_check_mark)
			await confirm.add_reaction(emoji_red_x)

			challengeHash = hash(self.challenge) #prevent previous challenge from causing early timeout on current challenge if they happen within a minute of each other
			await asyncio.sleep(60)
			#wait for on_reaction_add to confirm

			if self.challenge is not None and hash(self.challenge) == challengeHash:
				self.challenge = None
				await ctx.send("Challenge timed out.")
			#else game is playing

	@commands.command()
	async def db(self, ctx):
		game = Game(ctx, ctx.author, self.bot)
		await game.drawBoard()

	@commands.Cog.listener()
	async def on_reaction_add(self, reaction, user):
		if self.challenge is not None:
			if reaction.message == self.challenge.message:
				if user == self.challenge.player2 and reaction.emoji == emoji_check_mark:
					thread = await self.challenge.message.create_thread(name=f"{self.challenge.player1.display_name} vs {self.challenge.player2.display_name}")
					game = Game(thread, self.challenge.player1, self.challenge.player2)
					self.games.update({thread.id : game})
					await game.startGame()
					self.challenge = None
				elif user == self.challenge.player2 and reaction.emoji == emoji_red_x:
					await reaction.message.channel.send(f"{self.challenge.player1.mention} {self.challenge.player2.display_name} has declined.")
					self.challenge = None

	@commands.command(aliases=["p"], brief="You can use .p1 through .p7 to play")
	async def play(self, ctx, num):
		if ctx.channel.id in self.games.keys():
			game = self.games[ctx.channel.id]
			if ctx.message.author == game.players[game.currentP]:
				try:
					col = int(num)
					if col < 1 or col > 7:
						await ctx.send("Number isn't in range")
					else:
						await game.drop(game.currentP, col-1)
				except ValueError:
					await ctx.send("Invalid input")

	@commands.command(hidden=True)
	async def p1(self, ctx):
		await self.play(ctx, 1)
	@commands.command(hidden=True)
	async def p2(self, ctx):
		await self.play(ctx, 2)
	@commands.command(hidden=True)
	async def p3(self, ctx):
		await self.play(ctx, 3)
	@commands.command(hidden=True)
	async def p4(self, ctx):
		await self.play(ctx, 4)
	@commands.command(hidden=True)
	async def p5(self, ctx):
		await self.play(ctx, 5)
	@commands.command(hidden=True)
	async def p6(self, ctx):
		await self.play(ctx, 6)
	@commands.command(hidden=True)
	async def p7(self, ctx):
		await self.play(ctx, 7)

	def cleanGames(self): #garbage collection, removes games from self.games if their thread is archived
		delThreads = []
		for game in self.games.values():
			if game.thread.archived:
				delThreads.append(game.thread.id)
		for threadID in delThreads:
			print(threadID)
			del self.games[threadID]

def setup(bot):
	bot.add_cog(ConnectFour(bot))