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

	def __init__(self, ctx):
		self.ctx = ctx
		self.board = [[0 for j in range(6)] for i in range(7)]
		self.color= {
			0: (0, 0, 0),
			1: (255, 0, 0), #red
			2: (255, 255, 0) #yellow
		}

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

	async def drop(self, player, col):
		j = 0
		while self.board[col][j] == 0:
			if self.board[col][j+1] == 0:
				j += 1
				if (j >= 5): #no pieces in col yet
					self.board[col][j] = player
					await self.drawBoard()
			else:
				self.board[col][j] = player
				await self.drawBoard()
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
		
		global game
		if game is not None and message.channel == game.ctx.channel:
			pass

#		await self.bot.process_commands(message)

	@commands.command(aliases=["c4"])
	async def connectfour(self, ctx):
		if len(ctx.message.mentions) < 1:
			await ctx.send("Please mention the user you would like to play against.")
		elif len(ctx.message.mentions) > 1:
			await ctx.send("You can only play against one user at a time")
		else:
			global game
			game = Game(ctx)
			await game.drawBoard()


	@commands.command()
	async def t1(self, ctx):
		global game
		await game.drop(1, 3);

	@commands.command()
	async def t2(self, ctx):
		global game
		await game.drop(2, 5);

	@commands.command()
	async def t3(self, ctx):
		global game
		await game.drop(1, 5);

def setup(bot):
		bot.add_cog(ConnectFour(bot))