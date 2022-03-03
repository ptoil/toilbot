import discord
from discord.ext import commands

from .exceptions import *
import pickle

class Roles(commands.Cog):

	def __init__(self, bot):
		self.bot = bot
		self.roles = []

	@commands.Cog.listener()
	async def on_connect(self):
		try:
			self.roles = pickle.load(open("saves/roles.pickle", "rb"))
		except FileNotFoundError:
			pickle.dump(self.roles, open("saves/roles.pickle", "wb"))

	def saveRoles(self):
		pickle.dump(self.roles, open("saves/roles.pickle", "wb"))
#		json.dump(self.players, open("saves/players.json", "w"))

	@commands.command()
	@ChannelCheck.in_toilbot_channel()
	async def setcolor(self, ctx, color, *, name=None):
		try:
			if color[0] == '#':
				color = color[1:]
			if name is None:
				name = "#" + color
			hexNum = int(color, 16)
			if hexNum > 0xffffff:
				await ctx.message.reply("Hex value too high! Enter a hex value between #000000 and #FFFFFF")
				return
			if len(name) > 100:
				await ctx.message.reply("Role name too long! Must be 100 characters or fewer in length.")
				return
		except ValueError:
			await ctx.message.reply("Please enter a hex value for your color. For example `.setcolor #ABC123 role name`")
			return

		for role in ctx.author.roles:
			if role.id in self.roles:
				self.roles.remove(role.id)
				await role.delete()

		newRole = await ctx.guild.create_role(name=name, color=discord.Color(hexNum))
		botMember = ctx.guild.get_member(self.bot.user.id)
		botRole = botMember.roles[-1] #will return the bots top role, which should be the integration role if no other higher roles were added
		botRoleIndex = ctx.guild.roles.index(botRole)
		await ctx.guild.edit_role_positions(positions={newRole : botRoleIndex-1}) #move the color role to below the bot role (should be higher than any other custom role and therefore is the displayed color)
		await ctx.author.add_roles(newRole)
		await ctx.message.reply("Role added")
		self.roles.append(newRole.id)
		self.saveRoles()

	@setcolor.error
	async def setcolor_error(self, ctx, error):
		if isinstance(error, commands.MissingRequiredArgument):
			await ctx.message.reply("Please enter a hex value for your color. For example `.setcolor #ABC123 role name`")
		else:
			pass

	@commands.command()
	@ChannelCheck.in_toilbot_channel()
	async def clearcolor(self, ctx):
		for role in ctx.author.roles:
			if role.id in self.roles:
				self.roles.remove(role.id)
				self.saveRoles()
				await role.delete()
				await ctx.send("Your role has been removed")
				return
		await ctx.send("You don't have a role to remove")

"""
	@commands.command()
	async def roletest(self, ctx):
		output = ""
		for role in ctx.guild.roles:
			output += f"{role.name}: {role.position}\n"
		await ctx.send(output)
"""
def setup(bot):
	bot.add_cog(Roles(bot))
