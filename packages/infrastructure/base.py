"""
File: packages/infrastructure/base.py
Layer: Infrastructure / Port-Adapter Abstraction
Purpose: Defines the universal contract for all infrastructure-specific adapters.
Problem: Prevents agent logic from being tightly coupled to specific cloud providers (AWS, GCP, K8s).
Interaction: Agents use these abstract classes to collect telemetry and execute remediation plans without knowing the underlying stack.
Dependencies: pydantic, abc
Inputs: ActionPlan objects from Brain/Fixer agents
Outputs: NormalizedTelemetry and VerificationResult objects
"""
from abc import ABC, abstractmethod
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class NormalizedTelemetry(BaseModel):
    """
    Standardized schema for system telemetry across all platforms.
    Enables the Brain agent to perform RCA using the same logic regardless of the provider.
    """
    service_name: str
    error_rate: float
    latency_p95: float
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    trace_id: str
    timestamp: str  # ISO Format
    status: str     # HEALTHY, DEGRADED, CRITICAL
    error_spans: List[Dict[str, Any]]
    logs: List[str]
    raw_telemetry: Optional[Any] = None

class ActionPlan(BaseModel):
    """
    Standardized remediation request sent to execution adapters.
    Contains the intent and target of the autonomous fix.
    """
    action_type: str
    description: str
    parameters: Dict[str, Any]
    target_resource: str
    incident_id: str

class VerificationResult(BaseModel):
    """
    Structured result of a post-remediation verification check.
    Calculates metric deltas to confirm the fix actually worked.
    """
    success: bool
    metric_delta: Dict[str, Any]  # e.g. {"latency": -500, "error_rate": -0.05}
    rollback_required: bool

class SensoryAdapter(ABC):
    """
    Abstract Base Class for stack-specific observability adapters.
    Solves the problem of heterogeneous monitoring platforms.
    """
    @abstractmethod
    def collect(self) -> NormalizedTelemetry:
        """
        Fetch and normalize telemetry from the infrastructure.
        
        Returns:
            NormalizedTelemetry: A provider-agnostic health snapshot.
        """
        pass

class RemediationAdapter(ABC):
    """
    Abstract Base Class for stack-specific execution adapters.
    Defines the 'Hands' of the SRE control plane.
    """
    @abstractmethod
    def execute(self, action_plan: ActionPlan) -> Dict[str, Any]:
        """
        Execute stack-specific actions (restarts, patches, etc.) through provider APIs.
        
        Args:
            action_plan (ActionPlan): The intent object from the Fixer agent.
        Returns:
            Dict[str, Any]: Audit trail containing command status and audit logs.
        """
        pass

    @abstractmethod
    def verify(self, expected_state: str) -> VerificationResult:
        """
        Analyze telemetry to verify if the remediation improved system health.
        
        Args:
            expected_state (str): The desired status (e.g. 'HEALTHY').
        Returns:
            VerificationResult: The outcome of the health check.
        """
        pass

    @abstractmethod
    def snapshot(self, resource_id: str) -> str:
        """
        Perform a safety snapshot of the resource (EBS, Disk, Config) before mutation.
        
        Args:
            resource_id (str): The identifier for the resource to protect.
        Returns:
            str: The identifier of the created snapshot.
        """
        pass

class MemoryAdapter(ABC):
    """
    Abstract Base Class for persistent incident memory (Vector DBs).
    Solves the problem of 'system amnesia' by pattern matching past incidents.
    """
    @abstractmethod
    def upsert_fix(self, incident_id: str, root_cause: str, remediation: str, stack_type: str, score: float, telemetry: Optional[NormalizedTelemetry] = None, is_simulation: bool = False) -> bool:
        """
        Store a verified fix in long-term memory.
        
        Args:
            incident_id (str): Tracker ID for the incident.
            root_cause (str): The identified cause.
            remediation (str): The applied fix.
            stack_type (str): EC2, EKS, etc.
            score (float): Confidence or success score.
            telemetry (NormalizedTelemetry): The health snapshot at time of incident.
        Returns:
            bool: True if storage was successful.
        """
        pass

    @abstractmethod
    def query_memory(self, query_text: str, stack_type: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Search historical incidents for similar patterns.
        
        Args:
            query_text (str): The error signature or description to match.
            stack_type (str): Filter results by infrastructure stack.
            top_k (int): Number of relevant incidents to return.
        Returns:
            List[Dict[str, Any]]: List of matching incident documents and metadata.
        """
        pass
