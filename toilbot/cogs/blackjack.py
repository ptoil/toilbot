import discord
from discord.ext import commands

import asyncio
import io
import random
import pickle
import time

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

	def score(self):
		if self.rank == 1:
			return 11
		elif self.rank > 10:
			return 10
		else:
			return self.rank

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
		c = self.deck[self.top]
		self.top += 1
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
		self.score = 0
		self.cards = []

	def addCard(self, card):
		self.cards.append(card)
		self.calcScore()

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

class Player(Dealer): #player is same as dealer but has money
	def __init__(self, i):
		super().__init__()
		self.money = 0
		self.id = i
		self.cooldown = 0

	def freeMoney(self):
		if self.cooldown < time.time():
			self.money += 10
			self.cooldown = time.time() + 3600
			return True
		else:
			return False

	def removeCards(self):
		self.cards.clear()

class HitStay(discord.ui.View):

	def __init__(self, g):
		super().__init__()
		self.game = g

	@discord.ui.button(label="Hit", style=discord.ButtonStyle.blurple)
	async def hit(self, button: discord.ui.Button, interaction: discord.Interaction):
		if interaction.user.id == self.game.player.id:
			await self.game.hit()

	@discord.ui.button(label="Stay", style=discord.ButtonStyle.blurple)
	async def stay(self, button: discord.ui.Button, interaction: discord.Interaction):
		if interaction.user.id == self.game.player.id:
			await self.game.stay()
			self.stop()

class Game():

	def __init__(self, ctx, p, b):
		self.ctx = ctx
		self.bet = b
		self.player = p
		self.playerName = ctx.author.display_name
		self.playerMsg = None
		self.playerEmbed = None
		self.playerCardCount = 2
		self.hitStay = None
		self.dealerMsg = None
		self.dealerEmbed = None
		self.dealer = Dealer()
		self.deck = Deck()
		self.deck.shuffle()
		
	async def start(self):
		self.player.removeCards()
		if self.bet > self.player.money:
			return False

		self.player.money -= self.bet
		self.player.money = round(self.player.money, 2)

		self.dealCards()
#		self.dealBJ()
		if self.player.score == 21 and self.dealer.score == 21:
			await self.postDealerMsgBlackjack()
			await self.postPlayerMsgBlackjack()
			self.player.money += self.bet
			await self.ctx.message.reply(f"It's a tie! Your bet has been returned to you. You have ${self.player.money}")
		elif self.player.score == 21:
			await self.postDealerMsg()
			await self.postPlayerMsgBlackjack()
			self.dealerEmbed.description = ""
			await self.dealerMsg.edit(embed=self.dealerEmbed)
			self.player.money += round(self.bet * 2.5, 2)
			await self.ctx.message.reply(f"Blackjack!!! You win ${round(self.bet * 1.5, 2)}! You now have ${self.player.money}")
		elif self.dealer.score == 21:
			await self.postDealerMsgBlackjack()
			await self.postPlayerMsgLoseToBlackjack()
			await self.ctx.message.reply(f"The Dealer got a blackjack! You lose! You now have ${self.player.money}")
		else:
			await self.postDealerMsg()
			await self.postPlayerMsg()

			#wait for hit/stay
		
		return True #returns false if not enough money

	def dealCards(self):
		self.player.addCard(self.deck.drawCard())	
		self.dealer.addCard(self.deck.drawCard())
		self.player.addCard(self.deck.drawCard())
		self.dealer.addCard(self.deck.drawCard())

	def dealBJ(self):
		self.dealer.addCard(Card("Diamonds", 1))
		self.dealer.addCard(Card("Diamonds", 10))
		self.player.addCard(self.deck.drawCard())
		self.player.addCard(self.deck.drawCard())

	async def postDealerMsg(self):
		self.dealerEmbed = discord.Embed(title="Dealer", description="Dealer is waiting for you to finish your turn")
		self.dealerEmbed.add_field(name="Card 1", value="HIDDEN CARD", inline=True)
		self.dealerEmbed.add_field(name="Score",  value="_",    inline=True)
		self.dealerEmbed.add_field(name="Card 2", value=self.dealer.cards[1], inline=False)
		self.dealerMsg = await self.ctx.message.reply(embed=self.dealerEmbed, mention_author=False)

	async def postPlayerMsg(self):
		self.playerEmbed = discord.Embed(title=self.playerName, description="Would you like to hit or stay?")
		self.playerEmbed.add_field(name="Card 1", value=self.player.cards[0], inline=True)
		self.playerEmbed.add_field(name="Score",  value=self.player.score,    inline=True)
		self.playerEmbed.add_field(name="Card 2", value=self.player.cards[1], inline=False)
		self.hitStay = HitStay(self)
		self.playerMsg = await self.ctx.message.reply(embed=self.playerEmbed, view=self.hitStay, mention_author=False)

	async def postDealerMsgBlackjack(self):
		self.dealerEmbed = discord.Embed(title="Dealer", description="Blackjack!", colour=discord.Colour.gold())
		self.dealerEmbed.add_field(name="Card 1", value=self.dealer.cards[0], inline=True)
		self.dealerEmbed.add_field(name="Score",  value=self.dealer.score,    inline=True)
		self.dealerEmbed.add_field(name="Card 2", value=self.dealer.cards[1], inline=False)
		self.dealerMsg = await self.ctx.message.reply(embed=self.dealerEmbed, mention_author=False)

	async def postPlayerMsgBlackjack(self):
		self.playerEmbed = discord.Embed(title=self.playerName, description="Blackjack!", colour=discord.Colour.gold())
		self.playerEmbed.add_field(name="Card 1", value=self.player.cards[0], inline=True)
		self.playerEmbed.add_field(name="Score",  value=self.player.score,    inline=True)
		self.playerEmbed.add_field(name="Card 2", value=self.player.cards[1], inline=False)
		self.playerMsg = await self.ctx.message.reply(embed=self.playerEmbed, mention_author=False)

	async def postPlayerMsgLoseToBlackjack(self):
		self.playerEmbed = discord.Embed(title=self.playerName, description="Dealer got a blackjack!", colour=discord.Colour.red())
		self.playerEmbed.add_field(name="Card 1", value=self.player.cards[0], inline=True)
		self.playerEmbed.add_field(name="Score",  value=self.player.score,    inline=True)
		self.playerEmbed.add_field(name="Card 2", value=self.player.cards[1], inline=False)
		self.playerMsg = await self.ctx.message.reply(embed=self.playerEmbed, mention_author=False)
		
	async def hit(self):
		self.player.addCard(self.deck.drawCard())
		self.playerCardCount += 1
		self.playerEmbed.add_field(name=f"Card {self.playerCardCount}", value=self.player.cards[self.playerCardCount-1], inline="False")
		self.playerEmbed.set_field_at(1, name="Score", value=self.player.score, inline="True")
		if self.player.score > 21:
			self.playerEmbed.description = "You busted!"
			self.playerEmbed.colour = discord.Colour.red()
			self.dealerEmbed.description = "The dealer takes your bet"
			self.dealerEmbed.colour = discord.Colour.green()
			await self.dealerMsg.edit(embed=self.dealerEmbed)
			self.hitStay.stop()
			await self.playerMsg.edit(embed=self.playerEmbed, view=None)
			await self.ctx.message.reply(f"You busted! The Dealer takes your bet. You now have ${self.player.money}")
		else:
			await self.playerMsg.edit(embed=self.playerEmbed)

	async def stay(self):
		self.playerEmbed.description = "You have finished your turn."
		self.hitStay.stop()
		await self.playerMsg.edit(view=None)
		await self.dealerTurn()

	async def dealerTurn(self):
		self.dealerEmbed.description = "Dealer is taking their turn"
		self.dealerEmbed.set_field_at(0, name="Card 1", value=self.dealer.cards[0], inline=True)
		self.dealerEmbed.set_field_at(1, name="Score", value=self.dealer.score, inline=True)
		await self.dealerMsg.edit(embed=self.dealerEmbed)
		await asyncio.sleep(1)
		i = 2
		while (self.dealer.score < 17):
			if i != 2: #theres already a wait before the first turn
				await asyncio.sleep(2)
			self.dealer.addCard(self.deck.drawCard())
			self.dealerEmbed.add_field(name=f"Card {i+1}", value=self.dealer.cards[i], inline=False)
			self.dealerEmbed.set_field_at(1, name="Score", value=self.dealer.score, inline=True)
			await self.dealerMsg.edit(embed=self.dealerEmbed)
			i += 1
		await asyncio.sleep(1)
		if self.dealer.score > 21:
			self.dealerEmbed.description = "Dealer has busted!"
			self.dealerEmbed.colour = discord.Colour.red()
			self.playerEmbed.colour = discord.Colour.green()
			await self.dealerMsg.edit(embed=self.dealerEmbed)			
			await self.playerMsg.edit(embed=self.playerEmbed)
			self.player.money += round(self.bet * 2, 2)
			await self.ctx.message.reply(f"You win! You now have ${self.player.money}")
		else:
			self.dealerEmbed.description = "Dealer has finished taking their turn"
			if self.player.score > self.dealer.score:
				self.dealerEmbed.colour = discord.Colour.red()
				self.playerEmbed.colour = discord.Colour.green()
				await self.dealerMsg.edit(embed=self.dealerEmbed)			
				await self.playerMsg.edit(embed=self.playerEmbed)
				self.player.money += round(self.bet * 2, 2)
				await self.ctx.message.reply(f"You win! You now have ${self.player.money}")
			elif self.player.score < self.dealer.score:
				self.dealerEmbed.colour = discord.Colour.green()
				self.playerEmbed.colour = discord.Colour.red()
				await self.dealerMsg.edit(embed=self.dealerEmbed)			
				await self.playerMsg.edit(embed=self.playerEmbed)
				await self.ctx.message.reply(f"You lose! You now have ${self.player.money}")
			else: # ==
				self.player.money += self.bet
				await self.ctx.message.reply(f"It's a tie! Your bet has been returned to you. You have ${self.player.money}")

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

	@commands.command(aliases=["bj"])
	async def blackjack(self, ctx, bet):
		if ctx.author.id not in self.players.keys():
			self.players.update({ctx.author.id : Player(ctx.author.id)})
		try:
			bet = float(bet)
		except ValueError:
			await ctx.message.reply("Please enter a number for your bet. For example `.blackjack 5`")
			return
		if bet > .01:
			roundedBet = round(bet, 2)
			if bet != roundedBet:
				await ctx.message.reply(f"Bet has been rounded to {roundedBet}", mention_author=False)
			game = Game(ctx, self.players[ctx.author.id], roundedBet)
			if not await game.start():
				await ctx.message.reply(f"You only have ${self.players[ctx.author.id].money}. You can't bet that much.")
			self.savePlayers()
		else:
			await ctx.message.reply("The minimum bet is $0.01")

	@blackjack.error
	async def blackjack_error(self, ctx, error):
		if isinstance(error, commands.MissingRequiredArgument):
			await ctx.message.reply("Please enter a bet amount. For example `.blackjack 5`")
		else:
			await ctx.send(f"{type(error)}: {error}")
		
	@commands.command(brief="Give your money to someone else")
	async def donate(self, ctx, member: discord.Member, amount):
		if member.id not in self.players.keys():
			self.players.update({member.id : Player(member.id)})
		try:
			amountF = float(amount)
		except ValueError:
				await ctx.message.reply("Please enter a number for your donation. For example `.donate @toilbot 5`")
				return
		if amountF > self.players[ctx.author.id].money:
			await ctx.message.reply("You can't donate money you don't have.")
		else:
			if amountF > .01:
				roundedAmount = round(amountF, 2)
			output = ""
			if amountF != roundedAmount:
				output += f"Donation has been rounded to {roundedAmount}\n"
			self.players[ctx.author.id].money -= roundedAmount
			self.players[member.id].money += roundedAmount
			self.players[ctx.author.id].money = round(self.players[ctx.author.id].money, 2)
			self.players[member.id].money = round(self.players[member.id].money, 2)
			output += f"{ctx.author.mention} now has ${self.players[ctx.author.id].money}\n{member.mention} now has ${self.players[member.id].money}"
			await ctx.send(output)
			self.savePlayers()

	@donate.error
	async def donate_error(self, ctx, error):
		if isinstance(error, commands.MissingRequiredArgument):
			await ctx.message.reply("Please ping the desired user and enter a donation amount. For example `.donate @toilbot 5`")
		elif isinstance(error, commands.MemberNotFound):
			await ctx.message.reply("Please ping the user you want to donate to. For example `.donate @toilbot 5`")
		else:
			await ctx.send(f"{type(error)}: {error}")

	@commands.command(brief="Collect $10 every hour")
	async def freemoney(self, ctx):
		if ctx.author.id not in self.players.keys():
			self.players.update({ctx.author.id : Player(ctx.author.id)})
		if self.players[ctx.author.id].freeMoney():
			await ctx.send(f"You now have ${self.players[ctx.author.id].money}")
			self.savePlayers()
		else:
			secondsLeft = int(self.players[ctx.author.id].cooldown - time.time())
			m, s = divmod(secondsLeft, 60)
			h, m = divmod(m, 60)
			await ctx.send(f"{h}hr{m}m{s}s left until you can use this command again.")

	@commands.command(hidden=True)
	@commands.is_owner()
	async def resetcooldowns(self, ctx):
		resetted = ""
		for player in self.players.values():
			if player.cooldown > time.time():
				player.cooldown = time.time()
				resetted += f"<@{player.id}>\n"
		await ctx.send(f"Cooldowns have been reset for the following users:\n{resetted}")

	@commands.command(hidden=True)
	@commands.is_owner()
	async def givemoney(self, ctx, member: discord.Member, amount):
		if member.id not in self.players.keys():
			self.players.update({member.id : Player(member.id)})
		try:
			self.players[member.id].money += float(amount)
		except ValueError:
			await ctx.send("Number required")
		await ctx.send(f"{member.mention} now has ${self.players[member.id].money}")
		self.savePlayers()

	@commands.command(hidden=True)
	@commands.is_owner()
	async def setmoney(self, ctx, member: discord.Member, amount):
		if member.id not in self.players.keys():
			self.players.update({member.id : Player(member.id)})
		try:
			self.players[member.id].money = float(amount)
		except ValueError:
			await ctx.send("Number required")
		await ctx.send(f"{member.mention} now has ${self.players[member.id].money}")
		self.savePlayers()

	@resetcooldowns.error
	@givemoney.error
	@setmoney.error
	async def give_error(self, ctx, error):
		if isinstance(error, commands.NotOwner):
			await ctx.send("only ptoil can use that command FUNgineer")
		else:
			await ctx.send(f"{type(error)}: {error}")

	@commands.command()
	async def money(self, ctx):
		if ctx.author.id not in self.players.keys():
			self.players.update({ctx.author.id : Player(ctx.author.id)})
		await ctx.send(f"You have ${self.players[ctx.author.id].money}")
	

def setup(bot):
		bot.add_cog(Blackjack(bot))