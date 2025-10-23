import discord
from discord.ext import commands

import cogs.database as db

import asyncio
import re
import time
import decimal
import random
from table2ascii import table2ascii as t2a, PresetStyle, Alignment

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

	def file_name(self):
		output = ""
		match self.rank:
			case 1: output += "A"
			case 11: output += "J"
			case 12: output += "Q"
			case 13: output += "K"
			case _: output += str(self.rank)
		match self.suit:
			case "Diamonds": output += "D"
			case "Hearts": output += "H"
			case "Clubs": output += "C"
			case "Spades": output += "S"
		output += ".png"
		return output

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


class Player():

	def __init__(self):
		self.score = 0
		self.cards = []
		self.softScore = ""

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

		if aceCount > 0:
			soft = self.score - (aceCount * 10)
			self.softScore = f"{soft}/{self.score}"
		else:
			self.softScore = str(self.score)


class HitStay(discord.ui.View):
	def __init__(self, g):
		super().__init__()
		self.timeout = None
		self.game = g

	@discord.ui.button(label="Hit", style=discord.ButtonStyle.blurple)
	async def hit(self, button: discord.ui.Button, interaction: discord.Interaction):
#		print(f"1: {time.time()}")
		if interaction.user.id == self.game.playerID:
			await self.game.hit(interaction)
#		print(f"2: {time.time()}\n")

	@discord.ui.button(label="Stay", style=discord.ButtonStyle.blurple)
	async def stay(self, button: discord.ui.Button, interaction: discord.Interaction):
		if interaction.user.id == self.game.playerID:
			await self.game.stay()
			self.stop()


def formatMoney(money):
	with decimal.localcontext() as ctx:
		d = decimal.Decimal(money)
		ctx.rounding = decimal.ROUND_HALF_UP
		return "${:,.2f}".format(round(d, 2))


class Game():

	def __init__(self, ctx, b):
		self.ctx = ctx
		self.playerID = ctx.author.id
		self.playerName = ctx.author.display_name
		self.bet = b
		self.player = Player()
		self.dealer = Player()
		self.playerEmbed = None
		self.playerMsg = None
		self.dealerEmbed = None
		self.dealerMsg = None
		self.deck = Deck()
		self.deck.shuffle()


	def dealCards(self):
		self.player.addCard(self.deck.drawCard())	
		self.dealer.addCard(self.deck.drawCard())
		self.player.addCard(self.deck.drawCard())
		self.dealer.addCard(self.deck.drawCard())

	async def start(self):
		db.setBlackjackMoney(self.playerID, db.getBlackjackMoney(self.playerID) - self.bet)

		self.dealCards()

		if self.player.score == 21 and self.dealer.score == 21:
			await self.postDealerMsgBlackjack()
			await self.postPlayerMsgBlackjack()
			db.increaseBlackjackMoney(self.playerID, self.bet)
			await self.ctx.message.reply(f"It's a tie! Your bet has been returned to you. You have {formatMoney(db.getBlackjackMoney(self.playerID))}")
		elif self.player.score == 21:
			await self.postDealerMsgLoseToBlackjack()
			await self.postPlayerMsgBlackjack()
			db.increaseBlackjackMoney(self.playerID, self.bet * 2.5)
			await self.ctx.message.reply(f"Blackjack!!! You win {formatMoney(self.bet * 1.5)}! You now have {formatMoney(db.getBlackjackMoney(self.playerID))}")
		elif self.dealer.score == 21:
			await self.postDealerMsgBlackjack()
			await self.postPlayerMsgLoseToBlackjack()
			await self.ctx.message.reply(f"The Dealer got a blackjack! You lose! You now have {formatMoney(db.getBlackjackMoney(self.playerID))}")
		else:
			await self.postDealerMsg()
			await self.postPlayerMsg()
			await self.hitStay.wait()

	async def sendImages(self, dealerIm, playerIm):
		with io.BytesIO() as dealerBin, io.BytesIO() as playerBin:
			dealerIm.save(dealerBin, "PNG")
			playerIm.save(playerBin, "PNG")
			dealerBin.seek(0)
			playerBin.seek(0)
			if self.msg is None:
				self.hitStay = HitStay(self)
				self.msg = await self.ctx.send(
					files=[
					discord.File(fp=dealerBin, filename="dealer.png"),
					discord.File(fp=playerBin, filename="player.png")],
					view=self.hitStay
				)
			else:
				await self.msg.edit(
					files=[
					discord.File(fp=dealerBin, filename="dealer.png"),
					discord.File(fp=playerBin, filename="player.png")],
				)
			

	async def postCards(self):
		dealerIm = Image.new("RGBA", (750, 475), (53, 101, 77, 255))
		playerIm = Image.new("RGBA", (397, 475), (53, 101, 77, 255))

		for i in range(len(self.dealer.cards)):
			cardIm = Image.open(f"cogs/cards/{self.dealer.cards[i].file_name()}", 'r')
			dealerIm.paste(cardIm, (20 + (i * 45), 20), cardIm)
		for i in range(len(self.player.cards)):
			cardIm = Image.open(f"cogs/cards/{self.player.cards[i].file_name()}", 'r')
			playerIm.paste(cardIm, (20 + (i * 45), 20), cardIm)
		
		draw = ImageDraw.Draw(dealerIm)
		draw.text((400, 10), "yo mr white", font=ImageFont.truetype("fonts/arial.ttf", 30))

		await self.sendImages(dealerIm, playerIm)


	async def postDealerMsg(self):
		self.dealerEmbed = discord.Embed(title="Dealer", description="Dealer is waiting for you to finish your turn")
		self.dealerEmbed.add_field(name="Card 1", value="HIDDEN CARD",        inline=True)
		self.dealerEmbed.add_field(name="Score",  value="_",                  inline=True)
		self.dealerEmbed.add_field(name="Card 2", value=self.dealer.cards[1], inline=False)
		self.dealerMsg = await self.ctx.message.reply(embed=self.dealerEmbed)

	async def postDealerMsgBlackjack(self):
		self.dealerEmbed = discord.Embed(title="Dealer", description="Blackjack!", colour=discord.Colour.gold())
		self.dealerEmbed.add_field(name="Card 1", value=self.dealer.cards[0], inline=True)
		self.dealerEmbed.add_field(name="Score",  value=self.dealer.score,    inline=True)
		self.dealerEmbed.add_field(name="Card 2", value=self.dealer.cards[1], inline=False)
		self.dealerMsg = await self.ctx.message.reply(embed=self.dealerEmbed)

	async def postDealerMsgLoseToBlackjack(self):
		self.dealerEmbed = discord.Embed(title="Dealer", description="", colour=discord.Colour.red())
		self.dealerEmbed.add_field(name="Card 1", value="HIDDEN CARD",        inline=True)
		self.dealerEmbed.add_field(name="Score",  value="_",                  inline=True)
		self.dealerEmbed.add_field(name="Card 2", value=self.dealer.cards[1], inline=False)
		self.dealerMsg = await self.ctx.message.reply(embed=self.dealerEmbed)

	async def postPlayerMsg(self):
		self.playerEmbed = discord.Embed(title=self.playerName, description="Would you like to hit or stay?")
		self.playerEmbed.add_field(name="Card 1", value=self.player.cards[0],  inline=True)
		self.playerEmbed.add_field(name="Score",  value=self.player.softScore, inline=True)
		self.playerEmbed.add_field(name="Card 2", value=self.player.cards[1],  inline=False)
		self.hitStay = HitStay(self)
		self.playerMsg = await self.ctx.message.reply(embed=self.playerEmbed, view=self.hitStay)

	async def postPlayerMsgBlackjack(self):
		self.playerEmbed = discord.Embed(title=self.playerName, description="Blackjack!", colour=discord.Colour.gold())
		self.playerEmbed.add_field(name="Card 1", value=self.player.cards[0], inline=True)
		self.playerEmbed.add_field(name="Score",  value=self.player.score,    inline=True)
		self.playerEmbed.add_field(name="Card 2", value=self.player.cards[1], inline=False)
		self.playerMsg = await self.ctx.message.reply(embed=self.playerEmbed)

	async def postPlayerMsgLoseToBlackjack(self):
		self.playerEmbed = discord.Embed(title=self.playerName, description="Dealer got a blackjack!", colour=discord.Colour.red())
		self.playerEmbed.add_field(name="Card 1", value=self.player.cards[0],  inline=True)
		self.playerEmbed.add_field(name="Score",  value=self.player.score, inline=True)
		self.playerEmbed.add_field(name="Card 2", value=self.player.cards[1],  inline=False)
		self.playerMsg = await self.ctx.message.reply(embed=self.playerEmbed)

	async def hit(self, interaction):
		self.player.addCard(self.deck.drawCard())
		self.playerEmbed.add_field(name=f"Card {len(self.player.cards)}", value=self.player.cards[-1], inline="False")
		self.playerEmbed.set_field_at(1, name="Score", value=self.player.softScore, inline="True")
		if self.player.score > 21:
#			self.playerEmbed.description = "You busted!"
#			self.playerEmbed.colour = discord.Colour.red()
#			self.dealerEmbed.description = "The dealer takes your bet"
#			self.dealerEmbed.colour = discord.Colour.green()
#			await self.dealerMsg.edit(embed=self.dealerEmbed)
			self.hitStay.stop()
			await self.playerMsg.edit(embed=self.playerEmbed, view=None)
			await self.ctx.message.reply(f"You busted! The Dealer takes your bet. You now have {formatMoney(db.getBlackjackMoney(self.playerID))}")
		else:
#			await self.playerMsg.edit(embed=self.playerEmbed) #using this instead of the below causes "This interaction failed"
			await interaction.response.edit_message(embed=self.playerEmbed) 

	async def stay(self):
		self.playerEmbed.description = "You have finished your turn."
		await self.playerMsg.edit(embed=self.playerEmbed, view=None)
		await self.dealerTurn()

	async def dealerTurn(self):
		self.dealerEmbed.description = "Dealer is taking their turn"
		self.dealerEmbed.set_field_at(0, name="Card 1", value=self.dealer.cards[0], inline=True)
		self.dealerEmbed.set_field_at(1, name="Score", value=self.dealer.softScore, inline=True)
		await self.dealerMsg.edit(embed=self.dealerEmbed)
		while (self.dealer.score < 17):
			await asyncio.sleep(1)
			self.dealer.addCard(self.deck.drawCard())
			self.dealerEmbed.add_field(name=f"Card {len(self.dealer.cards)}", value=self.dealer.cards[-1], inline=False)
			self.dealerEmbed.set_field_at(1, name="Score", value=self.dealer.softScore, inline=True)
			await self.dealerMsg.edit(embed=self.dealerEmbed)
		await asyncio.sleep(1)
		if self.dealer.score > 21:
			self.dealerEmbed.description = "Dealer has busted!"
			self.dealerEmbed.colour = discord.Colour.red()
			self.playerEmbed.colour = discord.Colour.green()
			await self.dealerMsg.edit(embed=self.dealerEmbed)			
			await self.playerMsg.edit(embed=self.playerEmbed)
			db.increaseBlackjackMoney(self.playerID, self.bet * 2)
			await self.ctx.message.reply(f"You win! You now have {formatMoney(db.getBlackjackMoney(self.playerID))}")
		else:
			self.dealerEmbed.description = "Dealer has finished taking their turn"
			if self.player.score > self.dealer.score:
				self.dealerEmbed.colour = discord.Colour.red()
				self.playerEmbed.colour = discord.Colour.green()
				await self.dealerMsg.edit(embed=self.dealerEmbed)			
				await self.playerMsg.edit(embed=self.playerEmbed)
				db.increaseBlackjackMoney(self.playerID, self.bet * 2)
				await self.ctx.message.reply(f"You win! You now have {formatMoney(db.getBlackjackMoney(self.playerID))}")
			elif self.player.score < self.dealer.score:
				self.dealerEmbed.colour = discord.Colour.green()
				self.playerEmbed.colour = discord.Colour.red()
				await self.dealerMsg.edit(embed=self.dealerEmbed)			
				await self.playerMsg.edit(embed=self.playerEmbed)
				await self.ctx.message.reply(f"You lose! You now have {formatMoney(db.getBlackjackMoney(self.playerID))}")
			else: # ==
				db.increaseBlackjackMoney(self.playerID, self.bet)
				await self.ctx.message.reply(f"It's a tie! Your bet has been returned to you. You have {formatMoney(db.getBlackjackMoney(self.playerID))}")


class Blackjack(commands.Cog):

	def __init__(self, bot):
		self.bot = bot

	@commands.command(aliases=["bj"])
	async def blackjack(self, ctx, *, bet):
		UserID = ctx.author.id
		db.addBlackjackUser(UserID)

		allin = False
		if re.search("(^| )all", bet):
			bet = db.getBlackjackMoney(UserID)
			allin = True
		else:
			try:
				bet = float(bet)
			except ValueError:
				await ctx.message.reply("Please enter a number for your bet. For example `.blackjack 5`")
				return

		if bet > db.getBlackjackMoney(UserID):
			await ctx.message.reply(f"You only have {formatMoney(db.getBlackjackMoney(UserID))}. You can't bet that much.")
			return

		if bet >= .01:
			roundedBet = round(bet, 2)
			if bet != roundedBet and not allin:
				await ctx.message.reply(f"Bet has been rounded to {formatMoney(roundedBet)}")
			elif allin:
				if roundedBet > bet: #cant go allin with more money than you have
					roundedBet = bet
				await ctx.message.reply(f"You've gone all in with {formatMoney(roundedBet)}")
			game = Game(ctx, roundedBet)
			await game.start()
		else:
			await ctx.message.reply("The minimum bet is $0.01")
	"""
	@blackjack.error
	async def blackjack_error(self, ctx, error):
		if isinstance(error, commands.MissingRequiredArgument):
			await ctx.message.reply("Please enter a bet amount. For example `.blackjack 5`")
		else:
			pass

	@commands.command(aliases=["fm"], brief="Collect $10 every hour")
	async def freemoney(self, ctx):
		UserID = ctx.author.id
		db.addBlackjackUser(UserID)

		if db.getBlackjackMoney(UserID) >= 100:
			await ctx.message.reply("You can only use this command if you have less than $100")
		elif db.getBlackjackCooldown(UserID) >= time.time():
			secondsLeft = int(db.getBlackjackCooldown(UserID) - time.time())
			m, s = divmod(secondsLeft, 60)
			await ctx.message.reply(f"{m}m{s}s left until you can use this command again.")
		else:
			db.increaseBlackjackMoney(UserID, 10)
			db.setBlackjackCooldown(UserID, time.time() + 3600)
			await ctx.message.reply(f"You now have {formatMoney(db.getBlackjackMoney(UserID))}")

	@commands.command(hidden=True)
	@commands.is_owner()
	async def resetcooldowns(self, ctx):
		resetted = "\n".join([f"<@{id}>" for id in db.getAllBlackjackActiveCooldowns()])
		db.resetBlackjackCooldowns()
		await ctx.send(f"Cooldowns have been reset for the following users:\n{resetted}")


	@commands.command()
	async def money(self, ctx, *, member: discord.Member=None):
		if member is None:
			member = ctx.author
		db.addBlackjackUser(member.id)

		if member == ctx.author:
			await ctx.message.reply(f"You have {formatMoney(db.getBlackjackMoney(member.id))}")
		else:
			await ctx.message.reply(f"{member.display_name} has {formatMoney(db.getBlackjackMoney(member.id))}")

	@commands.command(brief="Give your money to someone else")
	async def donate(self, ctx, member: discord.Member, *, amount):
		db.addBlackjackUser(ctx.author.id)
		db.addBlackjackUser(member.id)

		allin = False
		if re.search("(^| )all", amount):
			amount = db.getBlackjackMoney(ctx.author.id)
			allin = True
		else:
			try:
				amount = float(amount)
			except ValueError:
				await ctx.message.reply("Please enter a number for your donation. For example `.donate @toilbot 5`")
				return

		if amount > db.getBlackjackMoney(ctx.author.id):
			await ctx.message.reply("You can't donate money you don't have.")
		else:
			if amount >= .01:
				roundedAmount = round(amount, 2)
			else:
				await ctx.message.reply("The minimum amount to donate is $0.01")
				return
			output = ""
			if amount != roundedAmount:
				output += f"Donation has been rounded to {roundedAmount}\n"
			db.decreaseBlackjackMoney(ctx.author.id, roundedAmount)
			db.increaseBlackjackMoney(member.id, roundedAmount)
			output += f"{ctx.author.mention} now has {formatMoney(db.getBlackjackMoney(ctx.author.id))}\n{member.mention} now has {formatMoney(db.getBlackjackMoney(member.id))}"
			await ctx.send(output)

	@donate.error
	async def donate_error(self, ctx, error):
		if isinstance(error, commands.MissingRequiredArgument):
			await ctx.message.reply("Please ping the desired user and enter a donation amount. For example `.donate @toilbot 5`")
		elif isinstance(error, commands.MemberNotFound):
			await ctx.message.reply("Please ping the user you want to donate to. For example `.donate @toilbot 5`")
		else:
			pass

	@commands.command(aliases=["lb"])
	async def leaderboard(self, ctx):
		guildPlayers = []
		for userID, money in db.getAllBlackjackMoney():
			user = ctx.guild.get_member(userID)
			if user is not None and money > 0:
				guildPlayers.append([user.display_name, formatMoney(money)])
			#else player is from another server, so dont print

		output = t2a(
			header=["Player", "Money"],
			body=guildPlayers,
			style=PresetStyle.thin_compact,
			alignments=[Alignment.LEFT, Alignment.RIGHT]
		)
		await ctx.send(f"```\n{output}\n```")

	@commands.command(aliases=["glb"])
	async def globalleaderboard(self, ctx):
		players = []
		for userID, money in db.getAllBlackjackMoney():
			user = self.bot.get_user(userID)
			if money > 0:
				try:
					players.append([user.name, formatMoney(money)])
				except:
					await ctx.send(f"<@205908835435544577> {userID}") #TEMP investigating bug

		output = t2a(
			header=["Player", "Money"],
			body=players,
			style=PresetStyle.thin_compact,
			alignments=[Alignment.LEFT, Alignment.RIGHT]
		)
		await ctx.send(f"```\n{output}\n```")

	@commands.command(hidden=True)
	@commands.is_owner()
	async def givemoney(self, ctx, member: discord.Member, amount):
		db.addBlackjackUser(member.id)
		try:
			amount = float(amount)
		except ValueError:
			await ctx.send("Number required")
			return
		db.increaseBlackjackMoney(member.id, amount)
		await ctx.send(f"{member.mention} now has {formatMoney(db.getBlackjackMoney(member.id))}")

	@commands.command(hidden=True)
	@commands.is_owner()
	async def setmoney(self, ctx, member: discord.Member, amount):
		db.addBlackjackUser(member.id)
		try:
			amount = float(amount)
		except ValueError:
			await ctx.send("Number required")
			return
		db.setBlackjackMoney(member.id, amount)
		await ctx.send(f"{member.mention} now has {formatMoney(db.getBlackjackMoney(member.id))}")
	
	@resetcooldowns.error
	@givemoney.error
	@setmoney.error
	@money.error
	async def give_error(self, ctx, error):
		if isinstance(error, commands.MemberNotFound):
			await ctx.send("That user was not found")
		else:
			pass


def setup(bot):
	bot.add_cog(Blackjack(bot))