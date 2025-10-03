import discord
from discord import User, Role
from discord.ext import commands
from datetime import time
from typing import cast, Any
from DadBot.config_manager import set_user_override, set_role_override, clear_role_override, clear_user_override

def _is_valid_time(hour: int, minute: int) -> str | None:
    if hour > 23 or hour < 0:
        return "The hour must be between 0 and 23 inclusive."
    if minute > 59 or minute < 0:
        return "The minute must be between 0 and 59 inclusive."
    return None

class Override(commands.Cog):
    """Override quiet time for users/roles"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # @commands.group()
    # async def parental(self, ctx):
    #     """Parent group placeholder so override attaches"""
    #     pass
    #     # if ctx.invoked_subcommand is None:
    #     #     await ctx.send("Use subcommands like override")

    @commands.group(name='override', invoke_without_command=True)
    @commands.has_guild_permissions(manage_guild=True)
    async def override(self, ctx):
        """Base override command"""
        await ctx.send(
            "Override commands:\n"
            "• $parental override start <@User|@Role> <H> <M>\n"
            "• $parental override end <@User|@Role> <H> <M>\n"
            "• $parental override days <@User|@Role> <MTWRFSU>\n"
            "• $parental override grace <@User|@Role> <minutes>\n"
            "• $parental override clear <@User|@Role>"
        )

    @override.command(name="start")
    @commands.has_guild_permissions(manage_guild=True)
    async def o_start(self, ctx, target: User | Role, hour: int, minute: int = 0) -> None:
        guild_id = ctx.guild.id
        err = _is_valid_time(hour, minute)
        if err: return await ctx.send(err)
        new_start_time = time(hour, minute)
        if isinstance(target, User):
            set_user_override(guild_id, target.id, start_time=new_start_time)
        elif isinstance(target, Role):
            set_role_override(guild_id, target.id, start_time=new_start_time)
        await ctx.send(f"Quiet time start overriden to {new_start_time} for {target.name}")
    
    @override.command(name="end")
    @commands.has_guild_permissions(manage_guild=True) 
    async def o_end(self, ctx, target: User | Role, hour: int, minute: int = 0) -> None:
        guild_id = ctx.guild.id
        err = _is_valid_time(hour, minute)
        if err: return await ctx.send(err)
        new_end_time = time(hour, minute)
        if isinstance(target, User):
            set_user_override(guild_id, target.id, end_time=new_end_time)
        elif isinstance(target, Role):
            set_role_override(guild_id, target.id, end_time=new_end_time)
        await ctx.send(f"Quiet time end overriden to {new_end_time} for {target.name}")
    
    @override.command(name="grace")
    @commands.has_guild_permissions(manage_guild=True)
    async def o_grace(self, ctx, target: User | Role, minutes: int) -> None:
        guild_id = ctx.guild.id
        if minutes < 0 or minutes > 240:
            return await ctx.send("Grace period must be between 0 and 240 minutes.")
        new_grace_period = minutes
        if isinstance(target, User):
            set_user_override(guild_id, target.id, grace_period=new_grace_period)
        elif isinstance(target, Role):
            set_role_override(guild_id, target.id, grace_period=new_grace_period)
        await ctx.send(f"Grace period overriden to {new_grace_period} minutes for {target.name}")
    
    @override.command(name="days")
    @commands.has_guild_permissions(manage_guild=True)
    async def o_days(self, ctx, target: User | Role, days: str) -> None:
        guild_id = ctx.guild.id
        days = days.upper()
        valid = set("MTWRFSU")
        if not set(days).issubset(valid):
            return await ctx.send("Invalid days, use a string like 'MTWRFSU' or 'MTWRF'")
        if isinstance(target, User):
            set_user_override(guild_id, target.id, quiet_days=days)
        elif isinstance(target, Role):
            set_role_override(guild_id, target.id, quiet_days=days)
        await ctx.send(f"Quiet days overriden to {days} for {target.name}")
    
    @override.command(name="clear")
    @commands.has_guild_permissions(manage_guild=True)
    async def o_clear(self, ctx, target: User | Role) -> None:
        guild_id = ctx.guild.id
        if isinstance(target, User):
            clear_user_override(guild_id, target.id)
        elif isinstance(target, Role):
            clear_role_override(guild_id, target.id)
        await ctx.send(f"Overrides cleared for {target.name}")

async def setup(bot: commands.Bot):
    cog = Override(bot)
    await bot.add_cog(cog)

    parental_cmd = bot.get_command("parental")
    if isinstance(parental_cmd, commands.Group):
        parental_cmd.add_command(cast(commands.Command[Any, Any, Any], cog.override))
    else:
        @commands.group(name="parental", invoke_without_command=True)
        async def parental(ctx: commands.Context):
            await ctx.send("Use `$parental override`")
        bot.add_command(parental)

        parental.add_command(cast(commands.Command[Any, Any, Any], cog.override))