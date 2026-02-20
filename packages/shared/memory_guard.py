import psutil
import logging
from apps.control_plane.runtime_config import MEMORY_THRESHOLD_MB, update_degraded_mode

logger = logging.getLogger(__name__)

def check_memory_health():
    """
    Checks the system's memory usage and triggers DEGRADED_MODE if necessary.
    This is critical for Render environments (450MB limit).
    """
    mem = psutil.virtual_memory()
    used_mb = mem.used / (1024 * 1024)
    
    # Check both percentage and absolute used memory
    if used_mb > MEMORY_THRESHOLD_MB or mem.percent > 85:
        logger.warning(f"MEMORY ALERT: {used_mb:.2f}MB used. Entering DEGRADED_MODE.")
        update_degraded_mode(True)
        return True
    
    # Check if we have less than 100MB remaining
    free_mb = mem.available / (1024 * 1024)
    if free_mb < 100:
        logger.warning(f"LOW MEMORY: only {free_mb:.2f}MB available. Entering DEGRADED_MODE.")
        update_degraded_mode(True)
        return True

    # If we are in degraded mode but memory has recovered
    from apps.control_plane.runtime_config import DEGRADED_MODE
    if DEGRADED_MODE and mem.percent < 60:
        logger.info("Memory usage normalized. Resuming Normal Mode.")
        update_degraded_mode(False)
        return False
        
    return DEGRADED_MODE

def get_system_stats():
    mem = psutil.virtual_memory()
    return {
        "memory_percent": mem.percent,
        "memory_available_mb": round(mem.available / (1024 * 1024), 2),
        "memory_used_mb": round(mem.used / (1024 * 1024), 2),
        "cpu_percent": psutil.cpu_percent(),
        "degraded": check_memory_health()
    }
