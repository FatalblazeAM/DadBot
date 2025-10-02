from dataclasses import dataclass, field
from datetime import time


def _str_to_time(tstr: str) -> time:
    hh, mm = map(int, tstr.split(":"))
    return time(int(hh), int(mm))

def _time_to_str(t: time | None) -> str | None:
    if t is None: return None
    return f"{t.hour:02d}:{t.minute:02d}"

@dataclass
class QuietConfig:
    """Dataclass for holding data regarding the quiet time configuration."""
    start_time: time | None = time(0,30)
    end_time: time | None = time(7, 0)
    quiet_days: str | None = "MTWRF"
    grace_period: int | None = 30

    def to_dict(self) -> dict:
        return {
            "start_time": _time_to_str(self.start_time),
            "end_time": _time_to_str(self.end_time),
            "quiet_days": self.quiet_days if self.quiet_days is not None else None,
            "grace_period": self.grace_period if self.grace_period is not None else None,
        }
    
    @classmethod
    def from_dict(cls, d: dict) -> "QuietConfig":
        if not d:
            return cls()
        
        def present(key):
            return key in d
        
        start_time_raw = d.get("start_time") if present("start_time") else "00:30"
        end_time_raw = d.get("end_time") if present("end_time") else "07:00"
        
        start_time = None if start_time_raw is None else _str_to_time(start_time_raw)
        end_time = None if end_time_raw is None else _str_to_time(end_time_raw)

        quiet_days = d.get("quiet_days") if present("quiet_days") else "MTWRF"
        grace_period = d.get("grace_period") if present("grace_period") else 30

        return cls(
            start_time=start_time,
            end_time=end_time,
            quiet_days=quiet_days,
            grace_period=grace_period,
        )

@dataclass
class Overrides:
    """Dataclass for holding data regarding user and role-specific overrides for quiet time configuration"""
    users: dict[int, QuietConfig] = field(default_factory=dict)
    roles: dict[int, QuietConfig] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "users": {str(user_id): config.to_dict() for user_id, config in self.users.items()},
            "roles": {str(role_id): config.to_dict() for role_id, config in self.roles.items()},
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Overrides":
        d = d or {}
        users = {int(user_id): QuietConfig.from_dict(config) for user_id, config in d.get("users", {}).items()}
        roles = {int(role_id): QuietConfig.from_dict(config) for role_id, config in d.get("roles", {}).items()}
        return cls(users=users, roles=roles)

@dataclass
class GuildConfig:
    """Dataclass for holding data regarding all configurations for a server"""
    server_id: int
    server_config: QuietConfig = field(default_factory=QuietConfig)
    overrides: Overrides = field(default_factory=Overrides)

    def to_dict(self) -> dict:
        return {
            "server_id": self.server_id,
            "server_config": self.server_config.to_dict(),
            "overrides": self.overrides.to_dict(),
        }

    @classmethod
    def from_dict(cls, d: dict) -> "GuildConfig":
        return cls(
            server_id=int(d["server_id"]),
            server_config=QuietConfig.from_dict(d.get("server_config", {})),
            overrides=Overrides.from_dict(d.get("overrides", {})),
        )

@dataclass
class RootConfig:
    """Dataclass for holding data of all servers"""
    servers: list[GuildConfig] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {"servers": [s.to_dict() for s in self.servers]}

    @classmethod
    def from_dict(cls, d: dict) -> "RootConfig":
        servers = [GuildConfig.from_dict(s) for s in d.get("servers", [])]
        return cls(servers=servers)

    def ensure_guild(self, guild_id: int) -> GuildConfig:
        for server in self.servers:
            if server.server_id == guild_id:
                return server
        g = GuildConfig(server_id=guild_id)
        self.servers.append(g)
        return g