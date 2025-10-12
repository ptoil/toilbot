import discord
from discord.ext import commands
import cogs.database as db

class Roles(commands.Cog):

	def __init__(self, bot):
		self.bot = bot

	@commands.command()
	@commands.bot_has_permissions(manage_roles=True)
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
			if hexNum < 0x0:
				await ctx.message.reply("Hex value too low! Enter a hex value between #000000 and #FFFFFF")
				return
			if len(name) > 100:
				await ctx.message.reply("Role name too long! Must be 100 characters or fewer in length.")
				return
		except ValueError:
			await ctx.message.reply("Please enter a hex value for your color. For example `.setcolor #ABC123 role name`")
			return

		for role in ctx.author.roles:
			if role.id in db.getAllRoles():
				db.deleteRole(role.id)
				await role.delete()

		newRole = await ctx.guild.create_role(name=name, color=discord.Color(hexNum))
		botMember = ctx.guild.get_member(self.bot.user.id)
		botRole = botMember.roles[-1] #will return the bots top role, which should be the integration role if no other higher roles were added
		botRoleIndex = ctx.guild.roles.index(botRole)
#		usersHighestRole = ctx.guild.roles.index(ctx.author.roles[-1])
#		print(f"usersHighestRole index: {usersHighestRole}, botRole index: {botRoleIndex}")
		await ctx.guild.edit_role_positions(positions={newRole : botRoleIndex-1}) #move the color role to below the bot role (should be higher than any other custom role and therefore is the displayed color)
		await ctx.author.add_roles(newRole)
		await ctx.message.reply("Role added")
		db.addRole(newRole.id)

	@setcolor.error
	async def setcolor_error(self, ctx, error):
		if isinstance(error, commands.errors.MissingRequiredArgument):
			await ctx.message.reply("Please enter a hex value for your color. For example `.setcolor #ABC123 role name`")
		else:
			pass

	@commands.command()
	@commands.bot_has_permissions(manage_roles=True)
	async def clearcolor(self, ctx):
		for role in ctx.author.roles:
			if role.id in db.getAllRoles():
				db.deleteRole(role.id)
				await role.delete()
				await ctx.send("Your role has been removed")
				return
		await ctx.send("You don't have a role to remove")


	@commands.command()
	@commands.bot_has_permissions(manage_roles=True)
	async def roletest(self, ctx):
		output = ""
		for role in ctx.guild.roles:
			output += f"{role.name}: {role.position}\n"
		await ctx.send(output)

def setup(bot):
	bot.add_cog(Roles(bot))
