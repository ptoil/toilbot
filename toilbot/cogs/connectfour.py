import discord
from discord.ext import commands

import random
import asyncio
import io

from PIL import Image, ImageDraw

########## GLOBALS

game = None

emoji_first_place  = "🥇"
emoji_second_place = "🥈"
emoji_third_place  = "🥉"
emoji_medal        = "🏅"
emoji_check_mark   = "✅"
emoji_red_x        = "❌"

########## END GLOBALS

class Game():

	def __init__(self, ctx, cf):
		self.ctx = ctx
		self.confirm = cf
		self.confirmed = False
		self.players = (ctx.message.author, ctx.message.mentions[0])
		self.currentP = 0
		self.board = [[-1 for j in range(6)] for i in range(7)]
		self.color= {
			-1: (0, 0, 0),
			0: (255, 0, 0), #red
			1: (255, 255, 0) #yellow
		}

	async def confirmGame(self):
		self.confirmed = True
		await self.drawBoard()

	async def sendImage(self, image):
		with io.BytesIO() as image_bin:
			image.save(image_bin, "PNG")
			image_bin.seek(0)
			await self.ctx.send(content=f"{self.players[self.currentP].mention}'s turn", file=discord.File(fp=image_bin, filename="image.png"))

	async def sendImageEnd(self, image):
		with io.BytesIO() as image_bin:
			image.save(image_bin, "PNG")
			image_bin.seek(0)
			await self.ctx.send(file=discord.File(fp=image_bin, filename="image.png"))

	async def drawBoard(self):
		im = Image.new("RGBA", (350, 300), (0, 0, 0, 255))
		draw = ImageDraw.Draw(im)
		draw.rectangle([(0, 0), (350, 300)], fill=(0, 0, 255))
		for j in range(6):
			for i in range(7):
				draw.ellipse([((i*50)+5, (j*50)+5), (((i+1)*50)-5, ((j+1)*50)-5)], fill=self.color[self.board[i][j]])

		await self.sendImage(im)

	async def checkForWin(self, i, j):
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
			await self.winner(winningTiles)
			return True

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
			await self.winner(winningTiles)
			return True

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
			await self.winner(winningTiles)
			return True

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
			await self.winner(winningTiles)
			return True

		return False #default if no win found

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
			await self.ctx.send("That column is full, choose another.")

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

		await self.sendImageEnd(im)

	async def winner(self, winningTiles):
		await self.drawBoardWin(winningTiles)
		await self.ctx.send(f"{self.players[self.currentP].mention} wins the game!")
		global game
		game = None

	async def tie(self):
		await self.drawBoardWin([]) #no winning tiles
		await self.ctx.send("Its a tie! Nobody wins")
		global game
		game = None


class ConnectFour(commands.Cog):

	def __init__(self, bot):
		self.bot = bot
		self.games = {}

	@commands.command(aliases=["c4"])
	async def connectfour(self, ctx):
		global game
		if game is not None:
			await ctx.send("There is already a game in progress.")
		elif len(ctx.message.mentions) < 1:
			await ctx.send("Please mention the user you would like to play against.")
		elif len(ctx.message.mentions) > 1:
			await ctx.send("You can only play against one user at a time.")
		elif ctx.message.mentions[0] == ctx.author:
			await ctx.send("You can't play against yourself.")
		else:
			confirm = await ctx.send(f"{ctx.message.mentions[0].mention} {ctx.message.author.display_name} wants to play Connect Four. Do you accept the challenge?")
			await confirm.add_reaction(emoji_check_mark)
			await confirm.add_reaction(emoji_red_x)
			game = Game(ctx, confirm)
			await asyncio.sleep(60)
			#wait for on_reaction_add to confirm

			if game is not None:
				if game.confirmed is False:
					await ctx.send("Challenge timed out.")
					game = None
				#else game is playing

	@commands.Cog.listener()
	async def on_reaction_add(self, reaction, user):
		global game
		if game is not None:
			if reaction.message == game.confirm:
				if user == game.players[1] and reaction.emoji == emoji_check_mark:
					await game.confirmGame()
				elif user == game.players[1] and reaction.emoji == emoji_red_x:
					await game.ctx.send(f"{game.players[0].mention} {game.players[1].display_name} has declined.")
					game = None

	@commands.command(aliases=["p"])
	async def play(self, ctx, num):
		global game
		if game is not None:
			if ctx.message.author == game.players[game.currentP] and game.confirmed:
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

def setup(bot):
		bot.add_cog(ConnectFour(bot))