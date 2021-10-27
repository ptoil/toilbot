import discord
from discord.ext import commands

import random
import asyncio
import math
import io

from PIL import Image, ImageDraw

########## GLOBALS

BOT_OWNER = 205908835435544577
GUMIES_ID = 569942936939134988

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
		im = Image.new("RGBA", (1000, 1000), (0, 0, 0, 255))
		draw = ImageDraw.Draw(im)
#		draw.rectangle([(25, 25), (375, 325)], fill=(0, 0, 255))
#		for j in range(1):
#			for i in range(15):
		for i in range(8):
			draw.line(list(self.hexagon_generator(30, offset=(25+(0*(2*math.sqrt(3)/2)*30), 200+(i*(2*math.sqrt(3)/2)*30)))), fill=(0, 0, 255), width=10)
		for i in range(9):
			draw.line(list(self.hexagon_generator(30, offset=(25+(1*(2*math.sqrt(3)/2)*30), 175+(i*(2*math.sqrt(3)/2)*30)))), fill=(0, 0, 255), width=10)
		for i in range(10):
			draw.line(list(self.hexagon_generator(30, offset=(25+(2*(2*math.sqrt(3)/2)*30), 150+(i*(2*math.sqrt(3)/2)*30)))), fill=(0, 0, 255), width=10)
		for i in range(11):
			draw.line(list(self.hexagon_generator(30, offset=(25+(3*(2*math.sqrt(3)/2)*30), 125+(i*(2*math.sqrt(3)/2)*30)))), fill=(0, 0, 255), width=10)
		for i in range(12):
			draw.line(list(self.hexagon_generator(30, offset=(25+(4*(2*math.sqrt(3)/2)*30), 100+(i*(2*math.sqrt(3)/2)*30)))), fill=(0, 0, 255), width=10)
		for i in range(13):
			draw.line(list(self.hexagon_generator(30, offset=(25+(5*(2*math.sqrt(3)/2)*30), 75+(i*(2*math.sqrt(3)/2)*30)))), fill=(0, 0, 255), width=10)
		for i in range(14):
			draw.line(list(self.hexagon_generator(30, offset=(25+(6*(2*math.sqrt(3)/2)*30), 50+(i*(2*math.sqrt(3)/2)*30)))), fill=(0, 0, 255), width=10)
		for i in range(14):
			draw.line(list(self.hexagon_generator(30, offset=(25+(7*(2*math.sqrt(3)/2)*30), 25+(i*(2*math.sqrt(3)/2)*30)))), fill=(0, 0, 255), width=10)
		for i in range(14):
			draw.line(list(self.hexagon_generator(30, offset=(25+(8*(2*math.sqrt(3)/2)*30), 50+(i*(2*math.sqrt(3)/2)*30)))), fill=(0, 0, 255), width=10)
		for i in range(13):
			draw.line(list(self.hexagon_generator(30, offset=(25+(9*(2*math.sqrt(3)/2)*30), 75+(i*(2*math.sqrt(3)/2)*30)))), fill=(0, 0, 255), width=10)
		for i in range(12):
			draw.line(list(self.hexagon_generator(30, offset=(25+(10*(2*math.sqrt(3)/2)*30), 100+(i*(2*math.sqrt(3)/2)*30)))), fill=(0, 0, 255), width=10)
		for i in range(11):
			draw.line(list(self.hexagon_generator(30, offset=(25+(11*(2*math.sqrt(3)/2)*30), 125+(i*(2*math.sqrt(3)/2)*30)))), fill=(0, 0, 255), width=10)
		for i in range(10):
			draw.line(list(self.hexagon_generator(30, offset=(25+(12*(2*math.sqrt(3)/2)*30), 150+(i*(2*math.sqrt(3)/2)*30)))), fill=(0, 0, 255), width=10)
		for i in range(9):
			draw.line(list(self.hexagon_generator(30, offset=(25+(13*(2*math.sqrt(3)/2)*30), 175+(i*(2*math.sqrt(3)/2)*30)))), fill=(0, 0, 255), width=10)
		for i in range(8):
			draw.line(list(self.hexagon_generator(30, offset=(25+(14*(2*math.sqrt(3)/2)*30), 200+(i*(2*math.sqrt(3)/2)*30)))), fill=(0, 0, 255), width=10)

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