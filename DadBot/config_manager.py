import json
from datetime import time
from pathlib import Path
from .config_models import RootConfig, QuietConfig

CONFIG_FILE = "config.json"
CONFIG_PATH = Path(__file__).resolve().parent.parent / CONFIG_FILE

def load_root() -> RootConfig:
    if CONFIG_PATH.exists():
        with CONFIG_PATH.open("r", encoding="utf-8") as file:
            return RootConfig.from_dict(json.load(file))
    return RootConfig()

def save_root(root: RootConfig) -> None:
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with CONFIG_PATH.open("w", encoding="utf-8") as file:
        json.dump(root.to_dict(), file, indent=2)

def get_server_config(guild_id: int) -> QuietConfig:
    root = load_root()
    return root.ensure_guild(guild_id).server_config

def set_server_config(guild_id: int, **kwargs) -> None:
    root = load_root()
    guild = root.ensure_guild(guild_id)
    for k, v in kwargs.items():
        setattr(guild.server_config, k, v)
    save_root(root)

def set_user_override(guild_id: int, user_id: int, **kwargs) -> None:
    root = load_root()
    guild = root.ensure_guild(guild_id)
    q = guild.overrides.users.get(user_id) or QuietConfig(start_time=None, end_time=None, grace_period=None, quiet_days=None)
    for k, v in kwargs.items():
        setattr(q, k, v)
    guild.overrides.users[user_id] = q
    save_root(root)

def set_role_override(guild_id: int, role_id: int, **kwargs) -> None:
    root = load_root()
    guild = root.ensure_guild(guild_id)
    q = guild.overrides.roles.get(role_id) or QuietConfig(start_time=None, end_time=None, grace_period=None, quiet_days=None)
    for k, v in kwargs.items():
        setattr(q, k, v)
    guild.overrides.roles[role_id] = q
    save_root(root)

def clear_user_override(guild_id: int, user_id: int) -> None:
    root = load_root()
    guild = root.ensure_guild(guild_id)
    guild.overrides.users.pop(user_id, None)
    save_root(root)

def clear_role_override(guild_id: int, role_id: int) -> None:
    root = load_root()
    guild = root.ensure_guild(guild_id)
    guild.overrides.roles.pop(role_id, None)
    save_root(root)