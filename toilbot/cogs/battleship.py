import discord
from discord.ext import commands

import random
import asyncio

########## GLOBALS

BOT_OWNER = 205908835435544577
GUMIES_ID = 569942936939134988

emoji_first_place  = "🥇"
emoji_second_place = "🥈"
emoji_third_place  = "🥉"
emoji_medal        = "🏅"
emoji_check_mark   = "✅"

########## END GLOBALS


class Battleship(commands.Cog):

	def __init__(self, bot):
		self.bot = bot

	@commands.command()
	async def dm(self, ctx, user: discord.Member = None):
		if user is None:
			await ctx.send("ping recipient")
		else:
			await user.send("yaeyo")
	

def setup(bot):
		bot.add_cog(Battleship(bot))