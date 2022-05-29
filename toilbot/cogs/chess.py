import discord
from discord.ext import commands

import asyncio
import io
from PIL import Image, ImageDraw
from bidict import bidict

########## GLOBALS

emoji_first_place  = "🥇"
emoji_second_place = "🥈"
emoji_third_place  = "🥉"
emoji_medal        = "🏅"
emoji_check_mark   = "✅"

letters_to_numbers = bidict({"a":0, "b":1, "c":2, "d":3, "e":4, "f":5, "g":6, "h":7})

########## END GLOBALS

class Game():

	def __init__(self, thread, p1, p2):
		self.thread = thread
		self.players = (p1, p2)
		self.currentP = 0
		self.board = [
		["WR", "WP", "--", "--", "--", "--", "BP", "BR"],
		["WN", "WP", "--", "--", "--", "--", "BP", "BN"],
		["WB", "WP", "--", "WQ", "--", "WQ", "BP", "BB"],
		["WQ", "WP", "--", "--", "--", "--", "BP", "BQ"],
		["WK", "WP", "--", "WQ", "--", "--", "BP", "BK"],
		["WB", "WP", "--", "--", "--", "--", "BP", "BB"],
		["WN", "WP", "--", "--", "--", "--", "BP", "BN"],
		["WR", "WP", "--", "--", "--", "--", "BP", "BR"]
		]
		# self.board = [
		# ["WR", "WP", "--", "--", "--", "--", "--", "--"],
		# ["WN", "WP", "--", "--", "--", "--", "--", "--"],
		# ["WB", "WP", "--", "--", "--", "--", "--", "--"],
		# ["WQ", "WP", "--", "--", "--", "--", "--", "--"],
		# ["WK", "WP", "--", "--", "--", "--", "--", "--"],
		# ["WB", "WP", "--", "--", "--", "--", "--", "--"],
		# ["WN", "WP", "--", "--", "--", "--", "--", "--"],
		# ["WR", "WP", "--", "--", "--", "--", "--", "--"]
		# ]
		self.gameMoves = []
		self.gameImages = []

	async def startGame(self):
		await self.drawBoard()

	async def sendImage(self, image):
		with io.BytesIO() as image_bin:
			image.save(image_bin, "PNG")
			image_bin.seek(0)
			await self.thread.send(file=discord.File(fp=image_bin, filename="image.png"))

	async def drawBoard(self):
		im = Image.open("cogs/chess/board.png")
		for i in range(8):
			for j in range(8):
				if self.board[i][j] != "--":
					pieceIm = Image.open(f"cogs/chess/{self.board[i][j]}.png", 'r')
					im.paste(pieceIm, ((i*100)+5, 800-((j+1)*100)+5), pieceIm)

		await self.sendImage(im)

	async def submitMove(self, moveL): #[startX, startY, endX, endY]
		if self.isMoveValid(moveL):
			self.gameMoves.append(self.toNotation(moveL))
			self.movePiece(moveL)
			await self.drawBoard()
		else:
			await self.thread.send("Invalid move")

	def toNotation(self, moveL):
		startPiece = self.board[moveL[0]][moveL[1]]
		endPiece = self.board[moveL[2]][moveL[3]]
		output = ""
		notatedDest = letters_to_numbers.inverse[moveL[2]] + str(moveL[3]+1)

		def disambiguateMove(moveL):
			out = ""
			otherPieces = []
			for i in range(8):
				for j in range(8):
					if self.board[i][j] == startPiece and (i, j) != (moveL[0], moveL[1]):
						otherPieces.append((i, j))

			fileUsed = False
			rankUsed = False
			for piece in otherPieces:
				if self.isMoveValid([piece[0], piece[1], moveL[2], moveL[3]]):
					if piece[0] == moveL[0] and not fileUsed:
						out = str(moveL[1]+1)
						fileUsed = True
					elif piece[1] == moveL[1] and not rankUsed:
						if fileUsed == True:
							out = letters_to_numbers.inverse[moveL[0]] + str(moveL[1]+1)
						else:
							out = letters_to_numbers.inverse[moveL[0]]
						rankUsed = True
					else:
						out = letters_to_numbers.inverse[moveL[0]]
						fileUsed = True
			return out

		if startPiece[1] == 'P':
			output += letters_to_numbers.inverse[moveL[0]]
			if moveL[0] == moveL[2]:
				output += str(moveL[3]+1)
			else:
				output += disambiguateMove(moveL)
				output += 'x' + notatedDest
				#TODO En passant
		else:
			output += startPiece[1]
			output += disambiguateMove(moveL)
			if endPiece == "--":
				output += notatedDest
			else:
				output += 'x' + notatedDest

		return output



	def isMoveValid(self, moveL): #[startX, startY, endX, endY] #TODO make this not async once done testing and prints no longer needed
		startPiece = self.board[moveL[0]][moveL[1]]
		endPiece = self.board[moveL[2]][moveL[3]]
		if startPiece == "--":
			return

		def rookCheck():
			if moveL[0] == moveL[2]: #vertical
				if moveL[1] < moveL[3]:
					r = range(moveL[1]+1, moveL[3])
				elif moveL[1] > moveL[3]:
					r = range(moveL[1]-1, moveL[3], -1)
				else:
					return False #start == end
				for i in r:                            #check spaces between start and end
					if self.board[moveL[0]][i] != "--":
						return False
				return endPiece[0] != startPiece[0]    #end is empty or opposite color

			elif moveL[1] == moveL[3]: #horizontal
				if moveL[0] < moveL[2]:
					r = range(moveL[0]+1, moveL[2])
				elif moveL[0] > moveL[2]:
					r = range(moveL[0]-1, moveL[2], -1)
				else:
					return False #start == end
				for i in r:                            #check spaces between start and end
					if self.board[i][moveL[1]] != "--":
						return False
				return endPiece[0] != startPiece[0]    #end is empty or opposite color

			else: #horizontal and vertical
				return False

		def bishopCheck():
			try:
				if abs(moveL[0] - moveL[2]) / abs(moveL[1] - moveL[3]) == 1: #throws ZeroDivisionError if row is same
					if moveL[0] < moveL[2]:
						x_range = range(moveL[0]+1, moveL[2])
					elif moveL[0] > moveL[2]:
						x_range = range(moveL[0]-1, moveL[2], -1)
					if moveL[1] < moveL[3]:
						y_range = range(moveL[1]+1, moveL[3])
					elif moveL[1] > moveL[3]:
						y_range = range(moveL[1]-1, moveL[3], -1)
					for x, y in zip(x_range, y_range):
						if self.board[x][y] != "--":
							return False
					return endPiece[0] != startPiece[0]
				else:
					return False
			except ZeroDivisionError:
				return False
		
		#TODO check that start piece is actually the right color and exists
		if startPiece[1] == 'R':
			return rookCheck()
		elif startPiece[1] == 'B':
			return bishopCheck()
		elif startPiece[1] == 'Q':
			return bishopCheck() or rookCheck()
		elif startPiece[1] == 'N':
			return (
				(
					(abs(moveL[2] - moveL[0]) == 2 and abs(moveL[3] - moveL[1]) == 1)
					or 
					(abs(moveL[2] - moveL[0]) == 1 and abs(moveL[3] - moveL[1]) == 2)
				)
				and endPiece[0] != startPiece[0]
			)
		elif startPiece[1] == 'K':
			x_dist = abs(moveL[0] - moveL[2])
			y_dist = abs(moveL[1] - moveL[3])
			return (x_dist <= 1 and y_dist <= 1 and (x_dist > 0 or y_dist > 0) and endPiece[0] != startPiece[0])
		elif startPiece == "WP":
			return (
				(moveL[2] == moveL[0] and moveL[3] == moveL[1]+1 and endPiece == "--") #move forward 1
				or
				(moveL[2] == moveL[0] and moveL[3] == moveL[1]+2 and moveL[1] == 1 and endPiece == "--" and self.board[moveL[2]][moveL[3]-1] == "--") #move forward 2
				or
				((moveL[2] == moveL[0]-1 or moveL[2] == moveL[0]+1) and moveL[3] == moveL[1]+1 and endPiece[0] == 'B') #diagonal take
			)
		elif startPiece == "BP":
			return (
				(moveL[2] == moveL[0] and moveL[3] == moveL[1]-1 and endPiece == "--") #move forward 1
				or
				(moveL[2] == moveL[0] and moveL[3] == moveL[1]-2 and moveL[1] == 6 and endPiece == "--" and self.board[moveL[2]][moveL[3]+1] == "--") #move forward 2
				or
				((moveL[2] == moveL[0]-1 or moveL[2] == moveL[0]+1) and moveL[3] == moveL[1]-1 and endPiece[0] == 'W') #diagonal take
			)
		else: #startPiece == "--"
			return False

	def movePiece(self, moveL): #[startX, startY, endX, endY]
		self.board[moveL[2]][moveL[3]] = self.board[moveL[0]][moveL[1]]
		self.board[moveL[0]][moveL[1]] = "--"


class Challenge():

	def __init__(self, msg, p1, p2):
		self.message = msg
		self.player1 = p1
		self.player2 = p2

class Chess(commands.Cog):

	def __init__(self, bot):
		self.bot = bot
		self.games = {}
		self.challenge = None
		self.tempGame = None

	@commands.command(aliases=["ch"])
	async def chess(self, ctx):
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
		else:
			confirm = await ctx.send(f"{ctx.message.mentions[0].mention} {ctx.message.author.display_name} wants to play Chess. Do you accept their challenge?")
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

	@commands.Cog.listener()
	async def on_reaction_add(self, reaction, user):
		if self.challenge is not None:
			if reaction.message == self.challenge.message:
				if user == self.challenge.player2 and reaction.emoji == emoji_check_mark:
					thread = await self.challenge.message.create_thread(name=f"Chess: {self.challenge.player1.display_name} vs {self.challenge.player2.display_name}")
					game = Game(thread, self.challenge.player1, self.challenge.player2)
					self.games.update({thread.id : game})
					await game.startGame()
					self.challenge = None
				elif user == self.challenge.player2 and reaction.emoji == emoji_red_x:
					await reaction.message.channel.send(f"{self.challenge.player1.mention} {self.challenge.player2.display_name} has declined.")
					self.challenge = None

	@commands.command(aliases=["sc"])
	async def startchess(self, ctx):
		self.tempGame = Game(ctx, "p1", "p2")
		await self.tempGame.drawBoard()

	@commands.command(aliases=["cm"])
	async def moves(self, ctx):
		await ctx.send(self.tempGame.gameMoves)

	@commands.command(aliases=["m"])
	async def move(self, ctx, move): #expecting origin/destination in form of b1c3
#		if ctx.channel.id in self.games.keys():
#			game = self.games[ctx.channel.id]
#			if ctx.message.author == game.players[game.currentP]:
				try:
					moveL = [char for char in move]
					moveL[0] = letters_to_numbers[moveL[0].lower()]
					moveL[1] = int(moveL[1])-1
					moveL[2] = letters_to_numbers[moveL[2].lower()]
					moveL[3] = int(moveL[3])-1
					if len(moveL) != 4 or moveL[1] < 0 or moveL[1] > 7 or moveL[3] < 0 or moveL[3] > 7:
						await ctx.send("Invalid input")
					else:
						await self.tempGame.submitMove(moveL)
				except (ValueError, IndexError, KeyError):
					await ctx.send("Invalid input")

	@commands.command()
	async def t(self, ctx):
		move = "h1a3"
		moveL = [char for char in move]
		moveL[0] = letters_to_numbers[moveL[0].lower()]
		moveL[1] = int(moveL[1])-1
		moveL[2] = letters_to_numbers[moveL[2].lower()]
		moveL[3] = int(moveL[3])-1
		x = self.tempGame.isMoveValid(moveL)
		await ctx.send(x)

	def cleanGames(self): #garbage collection, removes games from self.games if their thread is archived
		delThreads = []
		for game in self.games.values():
			print(f"name: {game.thread.name}, id: {game.thread.id}, archived: {game.thread.archived}")
			if game.thread.archived:
				delThreads.append(game.thread.id)
		for threadID in delThreads:
			print(threadID)
			del self.games[threadID]
	
def setup(bot):
	bot.add_cog(Chess(bot))