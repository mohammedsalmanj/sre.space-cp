from .factory import get_event_bus
import asyncio

async def emit_agent_thought(agent_name: str, thought: str, state: dict = None):
    """Emits an agent's internal reasoning to the event bus."""
    bus = get_event_bus()
    payload = {
        "agent": agent_name,
        "thought": thought,
        "service": state.get("service") if state else "unknown",
        "incident_id": state.get("incident_number") if state else None
    }
    await bus.emit("agent_thoughts", payload)

async def emit_incident_update(state: dict, status: str):
    """Emits a status update for a tracked incident."""
    bus = get_event_bus()
    payload = {
        "incident_id": state.get("incident_number"),
        "status": status,
        "remediation": state.get("remediation"),
        "confidence": state.get("confidence_score")
    }
    await bus.emit("incident_updates", payload)
