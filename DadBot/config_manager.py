import json
from datetime import time

CONFIG_FILE = "config.json"
def load_config():
    try:
        with open(CONFIG_FILE, "r") as f:
            data = json.load(f)
            for i, server in enumerate(data):
                server["server_config"]["start_time"] = _parse_time(server.get("server_config").get("start_time", "00:30"))
                server["server_config"]["end_time"] = _parse_time(server.get("server_config").get("end_time", "07:00"))
                pass
            return data
    except FileNotFoundError:
        # Defaults if config file doesn’t exist
        return {
            "start_time": time(0, 30),
            "end_time": time(7, 0),
            "quiet_days": "MTWRF",
            "grace_period": 30
        }

def save_config(server_id, start_time, end_time, quiet_days, grace_period):
    new_data = {
        "server_id": server_id,
        "server_config": {
            "start_time": start_time.strftime("%H:%M"),
            "end_time": end_time.strftime("%H:%M"),
            "quiet_days": quiet_days,
            "grace_period": grace_period
        }
    }
    old_data = ''
    with open(CONFIG_FILE, 'r') as f:
        old_data = json.load(f) 
    server_config_not_found = True
    for i, server in enumerate(old_data):
        if server["server_id"] == server_id:
            server_config_not_found = False
            old_data[i] = new_data
            break
    if server_config_not_found:
        old_data.append(new_data)
    with open(CONFIG_FILE, "w") as f:
        json.dump(old_data, f, indent=4)

def _parse_time(tstr: str) -> time:
    hour, minute = map(int, tstr.split(":"))
    return time(hour, minute)
