"""
File: packages/shared/sim_state.py
Layer: Shared / Simulation
Purpose: Manages the 'ground truth' of the simulated infrastructure for development and demonstration.
Problem Solved: Synchronization between chaos injection components and sensory agents in a synthetic environment.
Interaction: Used by Apps (to inject chaos via API) and Scout (to poll status in dev mode).
Dependencies: None
Inputs: Injection commands from the demo API
Outputs: Simulation state snapshots
"""

class SimulationState:
    """
    Singleton manager for the synthetic ground-truth state.
    Ensures that the Control Plane backend and the SRE Agents are
    looking at the same 'Real' system reality during simulations.
    """
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SimulationState, cls).__new__(cls)
            cls._instance.is_anomaly = False
            cls._instance.failure_type = None
            cls._instance.active_incidents = []
        return cls._instance

    def inject_failure(self, failure_type: str):
        """
        Triggers a simulated system failure to test autonomic response.
        
        Args:
            failure_type (str): The type of chaos to inject (e.g. 'db_pool_exhaustion').
        """
        self.is_anomaly = True
        self.failure_type = failure_type
        print(f"🔥 [SIM-STATE] Failure Injected: {failure_type}")

    def resolve_fix(self):
        """Restores the system to a healthy/stable state, ending the simulation."""
        self.is_anomaly = False
        self.failure_type = None
        print(f"✅ [SIM-STATE] System Restored to Stable.")

    def get_state(self) -> dict:
        """
        Returns the current simulated reality for agent sensory inspection.
        
        Returns:
            dict: The current simulation status indicators.
        """
        return {
            "is_anomaly": self.is_anomaly,
            "failure_type": self.failure_type
        }

# Global singleton instance for the control plane process lifetime
sim_state = SimulationState()
