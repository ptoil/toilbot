from twitchio.ext import commands
import os
from dotenv import load_dotenv
from cobe.brain import Brain
import asyncio

class Bot(commands.Bot):

	def __init__(self):
		load_dotenv()
		super().__init__(token=os.getenv('TWITCH_TOKEN'), prefix='!', initial_channels=['ptoil', 'Oatsngoats'])
		self.brain = Brain("cobe/temp.brain")
		self.botAccounts = ["cynanbot", "oathybot", "funtoon"]

	async def event_ready(self):
		print(f"Logged in as | {self.nick}")
		print(f"User id is | {self.user_id}")
	
	async def event_message(self, message):
		if message.author and message.author.name.lower() != self.nick.lower(): 
			if message.content[0] != "!" and message.author.name not in self.botAccounts:
				self.brain.learn(message.content)
				print(f"{message.author.name}: {message.content}")
			await self.handle_commands(message)
	"""
	@commands.command()
	async def reply(self, ctx, *, msg=""):
		await ctx.send(self.brain.reply(msg))
	"""

bot = Bot()
bot.run()
