import discord
from discord.ext import commands, tasks
from datetime import time, datetime, timedelta
import calendar
import os
from dotenv import load_dotenv
from config_manager import load_config, save_config
import random
import logging

config = load_config()

def get_server_info(server_id) -> tuple[time, time, str, int]:
    for server in config:
        if server_id == server.get("server_id"):
            server_config = server.get("server_config")
            return (server_config.get("start_time"),
                    server_config.get("end_time"),
                    server_config.get("quiet_days"),
                    server_config.get("grace_period"))
    return (time(0,30), time(7,0), "MTWRF", 30)

def is_quiet_time(server_id) -> bool:
    """Determines whether or not it is currently quiet time"""
    start_time, end_time, quiet_days, _ = get_server_info(server_id)
    today = calendar.day_name[datetime.today().weekday()]
    match today:
        case 'Monday':
            if 'M' not in quiet_days:
                return False
        case 'Tuesday':
            if 'T' not in quiet_days:
                return False
        case 'Wednesday':
            if 'W' not in quiet_days:
                return False
        case 'Thursday':
            if 'R' not in quiet_days:
                return False
        case 'Friday':
            if 'F' not in quiet_days:
                return False
        case 'Saturday':
            if 'S' not in quiet_days:
                return False
        case 'Sunday':
            if 'U' not in quiet_days:
                return False

    target = datetime.now().time()
    if start_time <= end_time:
        return (start_time <= target <= end_time)
    else:
        return (target >= start_time or target <= end_time)

def is_end_time(server_id) -> bool:
    """Determines whether or not it is time to end the call"""
    start_time, end_time, quiet_days, grace_period = get_server_info(server_id)
    today = calendar.day_name[datetime.today().weekday()]
    dc_time = (datetime.combine(datetime.today(), start_time) + timedelta(minutes=grace_period)).time()
    match today:
        case 'Monday':
            if 'M' not in quiet_days:
                return False
        case 'Tuesday':
            if 'T' not in quiet_days:
                return False
        case 'Wednesday':
            if 'W' not in quiet_days:
                return False
        case 'Thursday':
            if 'R' not in quiet_days:
                return False
        case 'Friday':
            if 'F' not in quiet_days:
                return False
        case 'Saturday':
            if 'S' not in quiet_days:
                return False
        case 'Sunday':
            if 'U' not in quiet_days:
                return False

    target = datetime.now().time()
    if dc_time <= end_time:
        return (dc_time <= target <= end_time)
    else:
        return (target >= dc_time or target <= end_time)

def main():
    load_dotenv("../.env")
    TOKEN = os.getenv("DISCORD_TOKEN")

    intents = discord.Intents.default()
    intents.message_content = True

    bot = commands.Bot(command_prefix='$', description='Go to bed NOW.', intents=intents)

    @tasks.loop(minutes=1)
    async def end_call():
        for guild in bot.guilds:
            if (is_end_time(guild.id)):
                for vc in guild.voice_channels:
                    for member in vc.members:
                        print(f"Kicking {member} from the #{vc} voice channel in {guild}")
                        await member.move_to(None)
            
    @bot.command(name='start')
    async def start(ctx, hour: int = None, minute: int = None):
        """Sets quiet time start"""

        start_time, end_time, quiet_days, grace_period = get_server_info(ctx.guild.id)

        if hour is None and minute is None:
            await ctx.send(f"Quiet time start time is {start_time}")
            return
        elif minute is None:
            minute = 0

        if hour > 23 or hour < 0:
            await ctx.send(f"The hour must be between 0 and 23 inclusive.")
        elif minute > 59 or minute < 0:
            await ctx.send(f"The minute must be between 0 and 59 inclusive.")
        else:
            start_time = time(hour, minute)
            save_config(ctx.guild.id, start_time, end_time, quiet_days, grace_period)
            await ctx.send(f"Quiet time start set to {start_time}")

    @bot.command(name='end')
    async def end(ctx, hour: int = None, minute: int = None):
        """Sets quiet time end"""

        start_time, end_time, quiet_days, grace_period = get_server_info(ctx.guild.id)

        if hour is None and minute is None:
            await ctx.send(f"Quiet time end time is {end_time}")
            return
        elif minute is None:
            minute = 0

        if hour > 23 or hour < 0:
            await ctx.send(f"The hour must be between 0 and 23 inclusive.")
        elif minute > 59 or minute < 0:
            await ctx.send(f"The minute must be between 0 and 59 inclusive.")
        else:
            end_time = time(hour, minute)
            save_config(ctx.guild.id, start_time, end_time, quiet_days, grace_period)
            await ctx.send(f"Quiet time end set to {end_time}")

    @bot.command(name='days')
    async def days(ctx, days: str = None):
        """Set which days for quiet time to be enabled. Day format should be a string like 'MTWRFSU' or 'MTWRF'"""
        start_time, end_time, quiet_days, grace_period = get_server_info(ctx.guild.id)
        days = days.upper()

        if days is None:
            await ctx.send(quiet_days)
            return

        valid = set("MTWRFSU")
        if not set(days.issubset(valid)):
            await ctx.send("Invalid days, use a string like 'MTWRFSU' or 'MTWRF'")
            return
        quiet_days = days
        await ctx.send(f"Quiet days set to {quiet_days}")
        save_config(ctx.guild.id, start_time, end_time, quiet_days, grace_period)

    @bot.command(name='reset')
    async def reset(ctx):
        """Reset quiet time config"""
        start_time, end_time, quiet_days, grace_period = get_server_info(ctx.guild.id)
        start_time = time(0,30) 
        end_time = time(7,0) 
        quiet_days = 'MTWRF'
        grace_period = 30
        save_config(ctx.guild.id, start_time, end_time, quiet_days, grace_period)
        await ctx.send("Reset quiet time config")

    @bot.command(name='holiday')
    async def holiday(ctx, date: str = None):
        await ctx.send("Not yet implemented")

    @bot.command(name='override')
    async def override(ctx, user, hour: int, minute: int):
        await ctx.send("Not yet implemented")

    @bot.command(name='grace')
    async def grace(ctx, minute: int = None):
        start_time, end_time, quiet_days, grace_period = get_server_info(ctx.guild.id)
        if minute is None:
            await ctx.send(f"Grace period is {grace_period} minutes")
            return
        
        grace_period = minute
        await ctx.send(f"Updated grace period to {grace_period} minutes.")
        save_config(ctx.guild.id, start_time, end_time, quiet_days, grace_period)

    @bot.event
    async def on_typing(channel, user, when):
        if is_quiet_time(channel.guild.id):
            await user.send(f"{user}, Don't even think about it")

    @bot.event
    async def on_ready():
        print(f'We have logged in as {bot.user}')
        end_call.start()

    @bot.event
    async def on_message(message):
        if message.author == bot.user:
            return
        
        ctx = await bot.get_context(message)

        if is_quiet_time(ctx.guild.id) and not ctx.valid:
            try:
                await message.delete()
                pass
            except discord.Forbidden:
                print("No permission to delete messages")
                ctx.send("No permission to delete messages")

        print(f'Message in {message.guild}, #{message.channel} from {message.author}: {message.content}')
        await bot.process_commands(message)

    @bot.event
    async def on_voice_state_update(member, before, after):
        if after.channel is not None and before.channel != after.channel:
            print(f"{member} joined {after.channel.name}")
            if is_quiet_time(after.channel.guild.id):
                await member.move_to(None, reason="Quiet Time!")

    bot.run(TOKEN)

if __name__ == '__main__':
    main()