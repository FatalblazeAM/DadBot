import discord
import sqlite3
from discord.ext import commands

class Money(commands.Cog):
    """Allowance"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name='allowance')
    async def allowance(self, ctx):
        #give allowance amount
        pass

    @commands.command(name='balance')
    async def balance(self, ctx):
        #check balance
        pass

async def setup(bot: commands.Bot):
    await bot.add_cog(Money(bot))
