import discord
from discord.ext import commands

import random
import asyncio
import math
import io

from PIL import Image, ImageDraw

########## GLOBALS

emoji_first_place  = "🥇"
emoji_second_place = "🥈"
emoji_third_place  = "🥉"
emoji_medal        = "🏅"
emoji_check_mark   = "✅"

########## END GLOBALS

class Board():

	def __init__(self):
		pass

class Game():

	def __init__(self, ctx):
		self.board = Board

class Battleship(commands.Cog):

	def __init__(self, bot):
		self.bot = bot

	@commands.command()
	async def dm(self, ctx, user: discord.Member = None):
		if user is None:
			await ctx.send("ping recipient")
		else:
			await user.send("yaeyo")

	async def sendImage(self, image, ctx):
		with io.BytesIO() as image_bin:
			image.save(image_bin, "PNG")
			image_bin.seek(0)
			await ctx.send(file=discord.File(fp=image_bin, filename="image.png"))

	@commands.command()
	async def drawBoard(self, ctx):
		im = Image.new("RGBA", (712, 800), (0, 0, 0, 255))
		draw = ImageDraw.Draw(im)
#		draw.rectangle([(25, 25), (375, 325)], fill=(0, 0, 255))
#		for j in range(1):
#			for i in range(15):
		"""width  of hexagon is side*2, each is offset by 3/4 the width, therefore multiply by 3/2"""
		"""height of hexagon is side*sqrt(3)"""
		lightblue = (111, 223, 225)
		darkblue = ()
		lightgreen = (185, 222, 106)
		darkgreen = ()
		for i in range(4):
			draw.line(list(self.hexagon_generator(30, offset=(25+(0*(3/2)*30), 200+(i*(math.sqrt(3))*30)))), fill=lightgreen, width=4)
		for i in range(4):
			draw.line(list(self.hexagon_generator(30, offset=(25+(0*(3/2)*30), (200+(math.sqrt(3)*30)*4)+(i*(math.sqrt(3))*30)))), fill=lightblue, width=4)

		for i in range(9):
			draw.line(list(self.hexagon_generator(30, offset=(25+(1*(3/2)*30), 175+(i*(math.sqrt(3))*30)))), fill=(0, 0, 255), width=4)
		for i in range(10):
			draw.line(list(self.hexagon_generator(30, offset=(25+(2*(3/2)*30), 150+(i*(math.sqrt(3))*30)))), fill=(0, 0, 255), width=4)
		for i in range(11):
			draw.line(list(self.hexagon_generator(30, offset=(25+(3*(3/2)*30), 125+(i*(math.sqrt(3))*30)))), fill=(0, 0, 255), width=4)
		for i in range(12):
			draw.line(list(self.hexagon_generator(30, offset=(25+(4*(3/2)*30), 100+(i*(math.sqrt(3))*30)))), fill=(0, 0, 255), width=4)
		for i in range(13):
			draw.line(list(self.hexagon_generator(30, offset=(25+(5*(3/2)*30), 75+(i*(math.sqrt(3))*30)))), fill=(0, 0, 255), width=4)
		for i in range(14):
			draw.line(list(self.hexagon_generator(30, offset=(25+(6*(3/2)*30), 50+(i*(math.sqrt(3))*30)))), fill=(0, 0, 255), width=4)
		for i in range(14):
			draw.line(list(self.hexagon_generator(30, offset=(25+(7*(3/2)*30), 25+(i*(math.sqrt(3))*30)))), fill=(0, 0, 255), width=4)
		for i in range(14):
			draw.line(list(self.hexagon_generator(30, offset=(25+(8*(3/2)*30), 50+(i*(math.sqrt(3))*30)))), fill=(0, 0, 255), width=4)
		for i in range(13):
			draw.line(list(self.hexagon_generator(30, offset=(25+(9*(3/2)*30), 75+(i*(math.sqrt(3))*30)))), fill=(0, 0, 255), width=4)
		for i in range(12):
			draw.line(list(self.hexagon_generator(30, offset=(25+(10*(3/2)*30), 100+(i*(math.sqrt(3))*30)))), fill=(0, 0, 255), width=4)
		for i in range(11):
			draw.line(list(self.hexagon_generator(30, offset=(25+(11*(3/2)*30), 125+(i*(math.sqrt(3))*30)))), fill=(0, 0, 255), width=4)
		for i in range(10):
			draw.line(list(self.hexagon_generator(30, offset=(25+(12*(3/2)*30), 150+(i*(math.sqrt(3))*30)))), fill=(0, 0, 255), width=4)
		for i in range(9):
			draw.line(list(self.hexagon_generator(30, offset=(25+(13*(3/2)*30), 175+(i*(math.sqrt(3))*30)))), fill=(0, 0, 255), width=4)
		for i in range(8):
			draw.line(list(self.hexagon_generator(30, offset=(25+(14*(3/2)*30), 200+(i*(math.sqrt(3))*30)))), fill=(0, 0, 255), width=4)

		await self.sendImage(im, ctx)
	
	def hexagon_generator(self, edge_length, offset):
		"""Generator for coordinates in a hexagon."""
		x, y = offset
		for angle in range(0, 420, 60):
			x += math.cos(math.radians(angle)) * edge_length
			y += math.sin(math.radians(angle)) * edge_length
			yield x, y

def setup(bot):
		bot.add_cog(Battleship(bot))