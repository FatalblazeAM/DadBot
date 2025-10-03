import discord
from discord.ext import commands
from datetime import time, date
from DadBot.config_manager import get_server_config, set_server_config

def _is_valid_time(hour: int, minute: int) -> str | None:
    if hour > 23 or hour < 0:
        return "The hour must be between 0 and 23 inclusive."
    if minute > 59 or minute < 0:
        return "The minute must be between 0 and 59 inclusive."
    return None

class Parental(commands.Cog):
    """Server-wide quiet-time configuration"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.group(name='parental', invoke_without_command=True)
    @commands.has_guild_permissions(manage_guild=True)
    async def parental(self, ctx):
        """Base parental command"""
        guild_id = ctx.guild.id
        server_config = get_server_config(guild_id)
        await ctx.send("Use subcommands: start, end, days, grace, reset, override")
        await ctx.send(
            f"Current server quiet config:\n"
            f"• start: {server_config.start_time}\n"
            f"• end: {server_config.end_time}\n"
            f"• days: {server_config.quiet_days}\n"
            f"• grace: {server_config.grace_period} minutes"
        )

    @parental.command(name='start')
    @commands.has_guild_permissions(manage_guild=True)
    async def set_start(self, ctx, hour: int | None = None, minute: int = 0):
        """Sets quiet time start"""

        guild_id = ctx.guild.id

        if hour is None:
            start_time = get_server_config(guild_id).start_time
            return await ctx.send(f"Quiet time start time is {start_time}")

        err = _is_valid_time(hour, minute)
        if err: return await ctx.send(err)
       
        new_start_time = time(hour, minute)
        set_server_config(guild_id, start_time=new_start_time)
        await ctx.send(f"Quiet time start set to {new_start_time}")

    
    @parental.command(name='end')
    @commands.has_guild_permissions(manage_guild=True)
    async def set_end(self, ctx, hour: int | None = None, minute: int = 0):
        """Sets quiet time end"""

        guild_id = ctx.guild.id

        if hour is None:
            end_time = get_server_config(guild_id).end_time
            return await ctx.send(f"Quiet time end time is {end_time}")

        err = _is_valid_time(hour, minute)
        if err: return await ctx.send(err)
        
        new_end_time = time(hour, minute)
        set_server_config(guild_id, end_time=new_end_time)
        await ctx.send(f"Quiet time end set to {new_end_time}")

    @parental.command(name='grace')
    @commands.has_guild_permissions(manage_guild=True)
    async def set_grace_period(self, ctx, minutes: int | None = None):
        """Set grace period"""

        guild_id = ctx.guild.id

        if minutes is None:
            grace_period = get_server_config(guild_id).grace_period
            return await ctx.send(f"Grace period is {grace_period} minutes.")
        if minutes < 0 or minutes > 240:
            return await ctx.send("Grace period must be between 0 and 240 minutes.")
        new_grace_period = minutes
        set_server_config(guild_id, grace_period=new_grace_period)
        await ctx.send(f"Grace period set to {new_grace_period} minutes.")

    @parental.command(name='days')
    @commands.has_guild_permissions(manage_guild=True)
    async def set_quiet_days(self, ctx, days: str | None = None):
        """Set quiet days. Day format should be a string like 'MTWRFSU' or 'MTWRF'"""

        guild_id = ctx.guild.id

        if days is None:
            quiet_days = get_server_config(guild_id).quiet_days
            return await ctx.send(quiet_days)

        days = days.upper()
        valid = set("MTWRFSU")
        if not set(days).issubset(valid):
            return await ctx.send("Invalid days, use a string like 'MTWRFSU' or 'MTWRF'")
        
        new_quiet_days = days
        set_server_config(guild_id, quiet_days=new_quiet_days)
        await ctx.send(f"Quiet days set to {new_quiet_days}")

    @parental.command(name='reset')
    @commands.has_guild_permissions(manage_guild=True)
    async def reset(self, ctx):
        """Reset quiet time config"""
        guild_id = ctx.guild.id
        set_server_config(guild_id=guild_id, 
            start_time = time(0,30), 
            end_time = time(7,0), 
            quiet_days = 'MTWRF',
            grace_period = 30
        )
        await ctx.send("Reset quiet time config to defaults.")

    @parental.command(name='holiday')
    @commands.has_guild_permissions(manage_guild=True)
    async def holiday(self, ctx, month: int | None = None, day: int | None = None):
        guild_id = ctx.guild.id
        holidays = get_server_config(guild_id).holidays
        if month is None and day is None:
            return await ctx.send(holidays)
        if month is None or day is None:
            return await ctx.send("Must specify a month and date.")
        if month > 12 or month < 1:
            return await ctx.send("Month must be between 1 and 12.")
        if day > 31 or day < 1: 
            return await ctx.send("Day must be between 1 and 31.")
        if holidays is None:
            holidays = []
        holidays.append((month, day))
        set_server_config(guild_id, holidays=holidays)
        raise NotImplementedError


async def setup(bot: commands.Bot):
    await bot.add_cog(Parental(bot))