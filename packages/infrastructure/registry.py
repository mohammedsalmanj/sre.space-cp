"""
File: packages/infrastructure/registry.py
Layer: Infrastructure / Registry
Purpose: Dynamically selects and loads the appropriate infrastructure adapter at runtime.
Problem Solved: Enables the "One Brain, Many Hands" architecture by abstracting away the specifics of the active tech stack.
Interaction: Scout and Fixer agents use this registry to get the correct adapter for the current 'STACK_TYPE'.
Dependencies: os, .aws_ec2_adapter, .kubernetes_adapter, .beanstalk_adapter, .gce_adapter
Inputs: STACK_TYPE environment variable
Outputs: Concrete instance of SensoryAdapter/RemediationAdapter
"""
import os
from .aws_ec2_adapter import AWSEC2Adapter
from .kubernetes_adapter import KubernetesAdapter
from .beanstalk_adapter import BeanstalkAdapter
from .gce_adapter import GCEAdapter

class AdapterRegistry:
    """
    Singleton registry for managing and retrieving infrastructure-specific adapters.
    Acts as a central dispatch for the control plane.
    """
    _instance = None
    _adapters = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AdapterRegistry, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """
        Registers the mapping of the 'STACK_TYPE' environment variable 
        to concrete adapter implementation classes.
        """
        self._adapters = {
            "ec2": AWSEC2Adapter,
            "eks": KubernetesAdapter,
            "gke": KubernetesAdapter,
            "aks": KubernetesAdapter,
            "kops": KubernetesAdapter,
            "beanstalk": BeanstalkAdapter,
            "gce": GCEAdapter
        }

    def get_adapter(self):
        """
        Retrieves the concrete adapter instance for the current operational environment.
        
        Returns:
            SensoryAdapter/RemediationAdapter: The active stack adapter.
        """
        stack_type = os.getenv("STACK_TYPE", "ec2").lower()
        adapter_cls = self._adapters.get(stack_type)
        if not adapter_cls:
            # Default to EC2 for safe fallback
            return AWSEC2Adapter()
        return adapter_cls()

# Global Singleton instance for effortless agent-layer access
registry = AdapterRegistry()
