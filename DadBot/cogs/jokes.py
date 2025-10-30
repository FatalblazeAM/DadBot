import re
import discord
from discord.ext import commands
import random

class Jokes(commands.Cog):
    """Dad jokes"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.group(name='jokes', invoke_without_command=False)
    @commands.has_guild_permissions(manage_guild=True)
    async def jokes(self, ctx):
        """Base jokes command"""
        pass

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or message.author == self.bot.user or message.guild is None:
            return
        
        message_template = re.compile(
            r"""(?ix)
            \b
            i \s* (?: (?:['’]?\s*m) |a \s* m)
            \s+
            (?P<who> .+? )
            [\s\.\!\?]* $
            """
        )
        m = message_template.search(message.content or "")
        if m:
            who = m.group("who").strip()

            if len(who) > 60:
                who = who[:60] + "..."

            allowed = discord.AllowedMentions.none()
            num_words = len(who.split())
            if num_words <= 1:
                await message.channel.send(f"Hi {who}, I'm DadBot.", allowed_mentions=allowed)
            elif num_words <= 2 and random.random() < 0.5: 
                await message.channel.send(f"Hi {who}, I'm DadBot.", allowed_mentions=allowed)
            elif num_words <= 3 and random.random() < 0.33:
                await message.channel.send(f"Hi {who}, I'm DadBot.", allowed_mentions=allowed)

        await self.bot.process_commands(message)

async def setup(bot: commands.Bot):
    await bot.add_cog(Jokes(bot))