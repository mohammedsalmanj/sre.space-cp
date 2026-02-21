class SimulationState:
    """
    Singleton manager for the synthetic ground-truth state.
    Ensures that the Control Plane backend and the SRE Agents are
    looking at the same 'Real' system reality.
    """
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SimulationState, cls).__new__(cls)
            cls._instance.is_anomaly = False
            cls._instance.failure_type = None
            cls._instance.active_incidents = []
        return cls._instance

    def inject_failure(self, failure_type):
        self.is_anomaly = True
        self.failure_type = failure_type
        print(f"🔥 [SIM-STATE] Failure Injected: {failure_type}")

    def resolve_fix(self):
        self.is_anomaly = False
        self.failure_type = None
        print(f"✅ [SIM-STATE] System Restored to Stable.")

    def get_state(self):
        return {
            "is_anomaly": self.is_anomaly,
            "failure_type": self.failure_type
        }

# Global singleton for the process
sim_state = SimulationState()
