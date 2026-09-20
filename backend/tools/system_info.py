import sys
import platform
import psutil
import datetime
from typing import Dict, Any
from backend.config import settings


def get_safe_system_info() -> Dict[str, Any]:
    """Safely inspect system metrics, hardware specs, OS, and runtime environment."""
    try:
        # OS info
        os_info = {
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "architecture": platform.machine(),
            "processor": platform.processor()
        }

        # CPU info
        cpu_info = {
            "physical_cores": psutil.cpu_count(logical=False),
            "total_cores": psutil.cpu_count(logical=True),
            "current_usage_percent": psutil.cpu_percent(interval=None)
        }

        # RAM info
        mem = psutil.virtual_memory()
        ram_info = {
            "total_gb": round(mem.total / (1024 ** 3), 2),
            "available_gb": round(mem.available / (1024 ** 3), 2),
            "used_gb": round(mem.used / (1024 ** 3), 2),
            "percent_used": mem.percent
        }

        # Storage info (Primary disk)
        disk = psutil.disk_usage(sys.executable[0] + ":\\" if platform.system() == "Windows" else "/")
        disk_info = {
            "total_gb": round(disk.total / (1024 ** 3), 2),
            "free_gb": round(disk.free / (1024 ** 3), 2),
            "used_gb": round(disk.used / (1024 ** 3), 2),
            "percent_used": disk.percent
        }

        return {
            "success": True,
            "application": {
                "name": settings.APP_NAME,
                "version": settings.APP_VERSION,
                "environment": "Development" if settings.DEBUG else "Production"
            },
            "runtime": {
                "python_version": sys.version.split()[0],
                "current_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            },
            "os": os_info,
            "cpu": cpu_info,
            "memory": ram_info,
            "storage": disk_info,
            "message": f"System diagnostics: OS {os_info['system']} {os_info['release']}, CPU {cpu_info['current_usage_percent']}%, RAM {ram_info['percent_used']}%."
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to retrieve system information: {str(e)}"
        }
