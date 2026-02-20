from datetime import datetime
from packages.shared.localization import localize

def add_agent_log(state, agent_name, message):
    """
    Appends a formatted and localized log entry to the state's logs.
    """
    logs = state.get("logs", [])
    lang = state.get("language", "en")
    
    # Localize the core message
    localized_msg = localize(message, lang)
    
    # Format: [HH:MM:SS] [AGENT_NAME] Localized Message
    timestamp = datetime.now().strftime('%H:%M:%S')
    log_entry = f"[{timestamp}] [{agent_name.upper()}] {localized_msg}"
    
    logs.append(log_entry)
    state["logs"] = logs
