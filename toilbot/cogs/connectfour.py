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
			await self.ctx.send(file=discord.File(fp=image_bin, filename="image.png"))

	async def drawBoard(self):
		im = Image.new("RGBA", (400, 350), (0, 0, 0, 255))
		draw = ImageDraw.Draw(im)
		draw.rectangle([(25, 25), (375, 325)], fill=(0, 0, 255))
		for j in range(6):
			for i in range(7):
				draw.ellipse([(25+(i*50)+5, 25+(j*50)+5), (25+((i+1)*50)-5, 25+((j+1)*50)-5)], fill=self.color[self.board[i][j]])

		await self.sendImage(im)

	async def checkForWin(self, i, j):
		matching = 0
		for x in range(1, 4): #left
			if i - x < 0 or self.board[i - x][j] == -1:
				break
			if self.board[i - x][j] == self.currentP:
				matching += 1
		for x in range(1, 4): #right
			if i + x > 6 or self.board[i + x][j] == -1:
				break
			if self.board[i + x][j] == self.currentP:
				matching += 1
		if matching >= 3:
			await self.ctx.send(f"Winner! LR")
			return True

		matching = 0
		for x in range(1, 4): #up
			if j - x < 0 or self.board[i][j - x] == -1:
				break
			if self.board[i][j - x] == self.currentP:
				matching += 1
		for x in range(1, 4): #down
			if j + x > 5 or self.board[i][j + x] == -1:
				break
			if self.board[i][j + x] == self.currentP:
				matching += 1
		if matching >= 3:
			await self.ctx.send(f"Winner! UD")
			return True

		matching = 0
		for x in range(1, 4): #TL
			if i - x < 0 or j - x < 0 or self.board[i - x][j - x] == -1:
				break
			if self.board[i - x][j - x] == self.currentP:
				matching += 1
		for x in range(1, 4): #BR
			if i + x > 6 or j + x > 5 or self.board[i + x][j + x] == -1:
				break
			if self.board[i + x][j + x] == self.currentP:
				matching += 1
		if matching >= 3:
			await self.ctx.send(f"Winner! TLBR")
			return True

		matching = 0
		for x in range(1, 4): #BL
			if i - x < 0 or j + x > 5 or self.board[i - x][j + x] == -1:
				break
			if self.board[i - x][j + x] == self.currentP:
				matching += 1
		for x in range(1, 4): #TR
			if i + x > 6 or j - x < 0 or self.board[i + x][j - x] == -1:
				break
			if self.board[i + x][j - x] == self.currentP:
				matching += 1
		if matching >= 3:
			await self.ctx.send(f"Winner! BLTR")
			return True


	async def drop(self, player, col):
		j = 0
		while self.board[col][j] == -1:
			if self.board[col][j+1] == -1:
				j += 1
				if (j >= 5): #no pieces in col yet
					self.board[col][j] = player
					await self.drawBoard()
					if await self.checkForWin(col, j):
						await self.ctx.send("winner spotted")
					self.currentP = (self.currentP + 1) % 2
			else:
				self.board[col][j] = player
				await self.drawBoard()
				if await self.checkForWin(col, j):
					await self.ctx.send("winner spotted")
				self.currentP = (self.currentP + 1) % 2
				j += 1 #prevent tripping if below

		if j == 0:
			await self.ctx.send("col is full")


class ConnectFour(commands.Cog):

	def __init__(self, bot):
		self.bot = bot

	@commands.Cog.listener()
	async def on_message(self, message):
		if message.author == self.bot.user:
			return
		
#		global game
#		if game is not None and message.channel == game.ctx.channel:
			

#		await self.bot.process_commands(message)

	@commands.command(aliases=["c4"])
	async def connectfour(self, ctx):
		if len(ctx.message.mentions) < 1:
			await ctx.send("Please mention the user you would like to play against.")
		elif len(ctx.message.mentions) > 1:
			await ctx.send("You can only play against one user at a time")
		else:
			confirm = await ctx.send(f"{ctx.message.mentions[0].mention} you wanna play?")
			await confirm.add_reaction(emoji_check_mark)
			global game
			game = Game(ctx, confirm)
			#wait for on_reaction_add to confirm

	@commands.Cog.listener()
	async def on_reaction_add(self, reaction, user):
		global game
		if game is not None:
			if reaction.message == game.confirm:
				if user == game.players[1]:
					await game.confirmGame()

	@commands.command(aliases=["p"])
	async def play(self, ctx, num):
		if ctx.message.author == game.players[game.currentP] and game.confirmed:
			try:
				col = int(num)
				if col < 1 or col > 7:
					await ctx.send("Number isn't in range")
				else:
					await game.drop(game.currentP, col-1)
			except ValueError:
				await ctx.send("Invalid input")

	@commands.command()
	async def p1(self, ctx):
		await self.play(ctx, 1)
	@commands.command()
	async def p2(self, ctx):
		await self.play(ctx, 2)
	@commands.command()
	async def p3(self, ctx):
		await self.play(ctx, 3)
	@commands.command()
	async def p4(self, ctx):
		await self.play(ctx, 4)
	@commands.command()
	async def p5(self, ctx):
		await self.play(ctx, 5)
	@commands.command()
	async def p6(self, ctx):
		await self.play(ctx, 6)
	@commands.command()
	async def p7(self, ctx):
		await self.play(ctx, 7)

def setup(bot):
		bot.add_cog(ConnectFour(bot))