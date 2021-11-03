import discord
from discord.ext import commands

import asyncio
import io
import random
import pickle

from PIL import Image, ImageDraw

########## GLOBALS

emoji_first_place  = "🥇"
emoji_second_place = "🥈"
emoji_third_place  = "🥉"
emoji_medal        = "🏅"
emoji_check_mark   = "✅"

########## END GLOBALS

class Card():

	def __init__(self, s, r):
		self.suit = s
		self.rank = r

	def score():
		if self.rank == 1:
			return 11
		elif rank > 10:
			return 10
		else:
			return rank

	def __str__(self):
		if self.rank >= 2 and self.rank <= 10:
			return str(self.rank) + " of " + self.suit
		else:
			match self.rank:
				case 1:  return "Ace of " + self.suit
				case 11: return "Jack of " + self.suit
				case 12: return "Queen of " + self.suit
				case 13: return "King of " + self.suit
				case _:  return "Not a Card"
			
class Deck():

	def __init__(self):
		self.deck = []
		self.top = 0

		suits = ["Diamonds", "Hearts", "Clubs", "Spades"]
		for s in suits:
			for r in range(1, 14):
				self.deck.append(Card(s, r))

	def drawCard(self):
		c = deck[top]
		top += 1
		return c

	def shuffle(self):
		for x in range(2): #shuffle loops
			for i in range(len(self.deck)):
				r = random.randint(0, len(self.deck)-1)
				c = self.deck[i]
				self.deck[i] = self.deck[r]
				self.deck[r] = c

	def __str__(self):
		out = ""
		for c in self.deck:
			out += str(c) + "\n"
		return out

class Dealer():

	def __init__(self):
		self.aceCount = 0
		self.score = 0
		self.cards = []

	def addCard(self, card):
		self.cards.append(card)

	def calcScore(self):
		aceCount = 0
		self.score = 0

		for card in self.cards:
			if card.rank == 1:
				aceCount += 1

			self.score += card.score()
			if self.score > 21 and aceCount > 0:
				aceCount -= 1
				self.score -= 10

class Player(Dealer):
	def __init__(self):
		super().__init__()
		self.money = 0


class Game():

	def __init__(self, ctx, p):
		self.ctx = ctx
		self.player = p
		self.dealer = Dealer()
		self.deck = Deck()
		self.deck.shuffle()
		
	async def start(self, bet):
		if bet > self.player.money:
			return False
		


class Blackjack(commands.Cog):

	def __init__(self, bot):
		self.bot = bot
		self.players = {}

	@commands.Cog.listener()
	async def on_ready(self):
		try:
			self.players = pickle.load(open("saves/players.pickle", "rb"))
		except FileNotFoundError:
			pickle.dump(self.players, open("saves/players.pickle", "wb"))

	def savePlayers(self):
		pickle.dump(self.players, open("saves/players.pickle", "wb"))

	@commands.command()
	async def blackjack(self, ctx, bet):
		if ctx.author.id not in self.players.keys():
			self.players.update({ctx.author.id : Player()})
		game = Game(ctx, self.players[ctx.author.id])
		if not await game.start(bet):
			await ctx.send(f"You only have ${self.players[ctx.author.id].money}. You can't bet that much.")
		self.savePlayers()
		
	@commands.command()
	async def daily(self, ctx):
		if ctx.author.id not in self.players.keys():
			self.players.update({ctx.author.id : Player()})
		self.players[ctx.author.id].money += 5
		await ctx.send(f"You have ${self.players[ctx.author.id].money}")
		self.savePlayers()

	@commands.command()
	async def money(self, ctx):
		if ctx.author.id not in self.players.keys():
			self.players.update({ctx.author.id : Player()})
		await ctx.send(f"You have ${self.players[ctx.author.id].money}")

	@commands.command()
	async def h(self, ctx):
		d = Deck()
		d.shuffle()
		await ctx.send(d)
	

def setup(bot):
		bot.add_cog(Blackjack(bot))