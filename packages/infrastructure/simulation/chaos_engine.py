"""
File: packages/infrastructure/simulation/chaos_engine.py
Layer: Infrastructure / Simulation
Purpose: Manages synthetic fault profiles for validating the OODA loop without real downtime.
Problem Solved: Enables safe E2E testing of agents across heterogeneous stacks.
Interaction: Scout Agent pulls data from here when SIMULATION_MODE is active.
"""
import os
from datetime import datetime
from typing import Dict, Any, Optional
from ..base import NormalizedTelemetry

class ChaosEngine:
    """
    Registry of structured fault profiles for various infrastructure stacks.
    Acts as a 'Shadow Telemetry' source for the Scout Agent.
    """
    
    FAULTS = {
        "AWS_EC2_DISK_FULL": {
            "service_name": "policy-service-ec2",
            "status": "CRITICAL",
            "disk_usage": 99.8,
            "error_rate": 0.05,
            "latency_p95": 120.5,
            "cpu_usage": 15.0,
            "memory_usage": 40.0,
            "error_spans": [{"exception.message": "IOError: No space left on device /dev/xvda1", "category": "Storage", "severity": 10}],
            "logs": [
                "Feb 26 19:44:01 ip-10-0-1-45 kernel: [8421.12] EXT4-fs error (device xvda1): ext4_add_entry:3233: inode #2: block 12: comm python: System is low on disk space",
                "Feb 26 19:44:02 policy-service [ERROR] Failed to write session log: No space left on device",
                "Feb 26 19:44:02 cloudwatch-agent [WARN] High disk usage detected on vol-0abcd1234efgh5678"
            ]
        },
        "K8S_POD_CRASH": {
            "service_name": "quote-service-k8s",
            "status": "CRITICAL",
            "error_rate": 1.0,
            "latency_p95": 0.0,
            "cpu_usage": 0.0,
            "memory_usage": 0.0,
            "disk_usage": 10.0,
            "error_spans": [{"exception.message": "CrashLoopBackOff: back-off 5m0s restarting failed container", "category": "Orchestration", "severity": 10}],
            "logs": [
                "Events: 25m (x12 over 45m) Back-off restarting failed container",
                "kubelet, ip-10-2-45-12.ec2.internal  Liveness probe failed: Get http://10.2.45.8:8080/health: dial tcp 10.2.45.8:8080: connect: connection refused",
                "State: Waiting, Reason: CrashLoopBackOff"
            ]
        },
        "GCE_CPU_BURN": {
            "service_name": "auth-service-gce",
            "status": "DEGRADED",
            "cpu_usage": 99.2,
            "error_rate": 0.12,
            "latency_p95": 2500.0,
            "memory_usage": 60.0,
            "disk_usage": 20.0,
            "error_spans": [{"exception.message": "CPU Throttling detected on instance-1", "category": "Compute", "severity": 7}],
            "logs": [
                "Feb 26 19:44:05 instance-1 kernel: [452.88] Watchdog: BUG: soft lockup - CPU#0 stuck for 22s! [stress-ng:4523]",
                "Feb 26 19:44:06 google-fluentd [INFO] High CPU load detected: 99.8%",
                "Feb 26 19:44:06 stackdriver-agent [ERROR] Latency threshold breached: 2500ms"
            ]
        }
    }

    def __init__(self):
        self.active_fault: Optional[str] = None

    def trigger_fault(self, fault_name: str):
        """Activates a specific fault profile."""
        if fault_name in self.FAULTS:
            self.active_fault = fault_name
            print(f"🔥 [CHAOS-ENGINE] Fault Triggered: {fault_name}")
        else:
            print(f"⚠️ [CHAOS-ENGINE] Unknown fault: {fault_name}")

    def clear_faults(self):
        """Restores healthy state."""
        self.active_fault = None
        print("✅ [CHAOS-ENGINE] All faults cleared.")

    def get_shadow_telemetry(self, stack_type: str) -> Optional[NormalizedTelemetry]:
        """
        Returns a NormalizedTelemetry object based on the active fault.
        Ensures the fault matches the target STACK_TYPE to prevent cross-stack confusion.
        """
        if not self.active_fault:
            return None
            
        fault_data = self.FAULTS.get(self.active_fault)
        
        # Check if fault is appropriate for stack
        if "EC2" in self.active_fault and stack_type != "ec2": return None
        if "K8S" in self.active_fault and stack_type != "kubernetes": return None
        if "GCE" in self.active_fault and stack_type != "gce": return None
        
        return NormalizedTelemetry(
            service_name=fault_data["service_name"],
            error_rate=fault_data["error_rate"],
            latency_p95=fault_data["latency_p95"],
            cpu_usage=fault_data["cpu_usage"],
            memory_usage=fault_data["memory_usage"],
            disk_usage=fault_data["disk_usage"],
            trace_id=f"sim-{datetime.now().strftime('%M%S')}",
            timestamp=datetime.now().isoformat(),
            status=fault_data["status"],
            error_spans=fault_data["error_spans"],
            logs=fault_data["logs"]
        )

# Global singleton
chaos_engine = ChaosEngine()
