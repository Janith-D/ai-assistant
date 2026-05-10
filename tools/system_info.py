"""
System Info Tools - CPU, RAM, IP, Disk usage
"""

import socket
import psutil
from langchain_core.tools import tool


@tool
def get_system_info(query: str = "all") -> str:
    """Get system information including IP address, RAM, CPU, and disk usage.
    Query can be: 'ip', 'ram', 'cpu', 'disk', or 'all'
    Example: get_system_info('ip') or get_system_info('all')"""
    try:
        info = {}

        # IP Address
        hostname = socket.gethostname()
        try:
            ip = socket.gethostbyname(hostname)
        except:
            ip = "Unable to retrieve"
        info["hostname"] = hostname
        info["ip_address"] = ip

        # CPU
        info["cpu_percent"] = f"{psutil.cpu_percent(interval=1)}%"
        info["cpu_cores"] = psutil.cpu_count(logical=True)

        # RAM
        ram = psutil.virtual_memory()
        info["ram_total"] = f"{round(ram.total / 1e9, 2)} GB"
        info["ram_used"] = f"{round(ram.used / 1e9, 2)} GB"
        info["ram_free"] = f"{round(ram.available / 1e9, 2)} GB"
        info["ram_percent"] = f"{ram.percent}%"

        # Disk
        disk = psutil.disk_usage("C:\\")
        info["disk_total"] = f"{round(disk.total / 1e9, 2)} GB"
        info["disk_used"] = f"{round(disk.used / 1e9, 2)} GB"
        info["disk_free"] = f"{round(disk.free / 1e9, 2)} GB"
        info["disk_percent"] = f"{disk.percent}%"

        # Battery (if laptop)
        battery = psutil.sensors_battery()
        if battery:
            info["battery"] = f"{round(battery.percent)}% {'(Charging)' if battery.power_plugged else '(On Battery)'}"

        # Filter by query
        query_lower = query.lower()
        if query_lower == "ip":
            return f"🌐 IP Address: {info['ip_address']}\n📛 Hostname: {info['hostname']}"
        elif query_lower == "ram":
            return (f"💾 RAM Info:\n"
                    f"  Total: {info['ram_total']}\n"
                    f"  Used:  {info['ram_used']}\n"
                    f"  Free:  {info['ram_free']}\n"
                    f"  Usage: {info['ram_percent']}")
        elif query_lower == "cpu":
            return f"🖥️ CPU Usage: {info['cpu_percent']} | Cores: {info['cpu_cores']}"
        elif query_lower == "disk":
            return (f"💽 Disk (C:) Info:\n"
                    f"  Total: {info['disk_total']}\n"
                    f"  Used:  {info['disk_used']}\n"
                    f"  Free:  {info['disk_free']}\n"
                    f"  Usage: {info['disk_percent']}")
        else:
            # Return all info
            lines = ["📊 System Information:"]
            lines.append(f"  🌐 IP Address : {info['ip_address']}")
            lines.append(f"  📛 Hostname   : {info['hostname']}")
            lines.append(f"  🖥️ CPU Usage  : {info['cpu_percent']} ({info['cpu_cores']} cores)")
            lines.append(f"  💾 RAM        : {info['ram_used']} / {info['ram_total']} ({info['ram_percent']})")
            lines.append(f"  💽 Disk (C:)  : {info['disk_used']} / {info['disk_total']} ({info['disk_percent']})")
            if "battery" in info:
                lines.append(f"  🔋 Battery    : {info['battery']}")
            return "\n".join(lines)

    except Exception as e:
        return f"❌ Error getting system info: {e}"
