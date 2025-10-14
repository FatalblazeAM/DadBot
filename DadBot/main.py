import discord
from discord.ext import commands, tasks
import os
from dotenv import load_dotenv
import logging
from pathlib import Path
from DadBot.logic import is_dc_time, is_quiet_time

def make_bot() -> commands.Bot:
    intents = discord.Intents.default()
    intents.message_content = True
    intents.members = True
    bot: commands.Bot = commands.Bot(command_prefix='$', description='Go to bed NOW.', intents=intents)
    return bot

async def load_cogs(bot: commands.Bot):
    await bot.load_extension("DadBot.cogs.parental")
    await bot.load_extension("DadBot.cogs.override")
    await bot.load_extension("DadBot.cogs.jokes")

def main():
    load_dotenv(Path(__file__).resolve().parent.parent / ".env")
    TOKEN = os.getenv("DISCORD_TOKEN")
    if TOKEN is None:
        print("ERROR: No authentication token")
        return
    bot = make_bot()
    
    @tasks.loop(minutes=1)
    async def end_call():
        for guild in bot.guilds:
            for vc in guild.voice_channels:
                for member in vc.members:
                    if (is_dc_time(guild.id, member=member)):
                        print(f"Kicking {member} from the #{vc} voice channel in {guild}")
                        await member.move_to(None)

    @bot.event
    async def on_ready():
        print(f'We have logged in as {bot.user}')
        await load_cogs(bot)
        end_call.start()

    @bot.event
    async def on_voice_state_update(member, before, after):
        if after.channel is not None and before.channel != after.channel:
            print(f"{member} joined {after.channel.name}")
            if is_quiet_time(after.channel.guild.id, member=member):
                await member.move_to(None, reason="Quiet Time!")

    bot.run(TOKEN)

if __name__ == '__main__':
    main()