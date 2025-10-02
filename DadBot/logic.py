from datetime import datetime, time, timedelta
from discord import Member
import calendar
from .config_manager import get_server_config, load_root
from .config_models import QuietConfig


def _is_day_enabled(quiet_days: str, dt: datetime) -> bool:
    day = calendar.day_name[dt.weekday()]
    code = {"Monday":"M","Tuesday":"T","Wednesday":"W","Thursday":"R","Friday":"F","Saturday":"S","Sunday":"U"}[day]
    return code in (quiet_days or "") 

def _between(target: time, start: time, end: time) -> bool:
    """Checks if the target time is located between the start and end times"""
    if start <= end:
        return (start <= target <= end)
    else:
        return (target >= start or target <= end)
    
def resolve_config_for_member(guild_id: int, *, member: Member = None) -> QuietConfig:
    root = load_root()
    guild_config = root.ensure_guild(guild_id)
    server_config = guild_config.server_config

    if member is None:
        return server_config
    
    return_config = QuietConfig(
        start_time=server_config.start_time,
        end_time=server_config.end_time,
        quiet_days=server_config.quiet_days,
        grace_period=server_config.grace_period
    )

    overrides = guild_config.overrides

    # Apply role overrides
    for role in member.roles:
        if role.id in overrides.roles:
            role_config = overrides.roles[role.id]
            if role_config.start_time is not None:
                return_config.start_time = role_config.start_time
            if role_config.end_time is not None:
                return_config.end_time = role_config.end_time
            if role_config.grace_period is not None:
                return_config.grace_period = role_config.grace_period
            if role_config.quiet_days is not None:
                return_config.quiet_days = role_config.quiet_days

    # Apply user overrides
    if member.id in overrides.users:
        member_config = overrides.users[member.id]
        if member_config.start_time is not None:
            return_config.start_time = member_config.start_time
        if member_config.end_time is not None:
            return_config.end_time = member_config.end_time
        if member_config.grace_period is not None:
            return_config.grace_period = member_config.grace_period
        if member_config.quiet_days is not None:
            return_config.quiet_days = member_config.quiet_days

    return return_config

def is_quiet_time(guild_id: int, *, member: Member = None, now: datetime | None = None):
    config = resolve_config_for_member(guild_id, member=member)
    now = now or datetime.now()
    if not _is_day_enabled(config.quiet_days, now):
        return False
    return _between(now.time(), config.start_time, config.end_time)

def is_dc_time(guild_id: int, *, member: Member = None, now: datetime | None = None):
    config = resolve_config_for_member(guild_id, member=member)
    now = now or datetime.now()
    if not _is_day_enabled(config.quiet_days, now):
        return False
    dc_time = (datetime.combine(now.date(), config.start_time) + timedelta(minutes=config.grace_period)).time()
    return _between(now.time(), dc_time, config.end_time)