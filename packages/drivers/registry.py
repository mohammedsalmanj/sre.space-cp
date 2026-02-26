"""
File: packages/drivers/registry.py
Layer: Infrastructure / Governance
Purpose: Dynamically selects the appropriate memory driver based on environment and availability.
Problem Solved: Provides a robust failover mechanism between Cloud (Pinecone) and Local (Chroma) memory.
Interaction: Shared by SRE agents to interact with long-term memory.
Dependencies: os, packages.infrastructure.memory.*
"""
import os
import sys

# Standardized singleton for driver orchestration
class VectorDriverRegistry:
    """
    Registry for managing vector database drivers.
    Enforces the 'Cloud-First with Local Failover' policy for the SRE Control Plane.
    """
    _instance = None
    _driver = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(VectorDriverRegistry, cls).__new__(cls)
        return cls._instance

    def get_vector_driver(self):
        """
        Retrieves the active memory driver (Pinecone or Chroma).
        Initializes Pinecone if the API key is present, otherwise falls back to Chroma.
        """
        if self._driver:
            return self._driver

        # Importing here to prevent circular dependencies in the package structure
        from packages.infrastructure.memory.pinecone_adapter import PineconeMemoryDriver
        from packages.infrastructure.memory.chroma_adapter import LocalChromaDriver

        provider = os.getenv("VECTOR_DB_PROVIDER", "pinecone")
        api_key = os.getenv("PINECONE_API_KEY")

        if provider == "pinecone" and api_key:
            try:
                print("🌲 [MEMORY] Handshaking with Pinecone Cloud instance...")
                self._driver = PineconeMemoryDriver()
                return self._driver
            except Exception as e:
                # 🛡️ Safety Note: If Pinecone connection times out, gracefully degrade to local memory
                print(f"⚠️ [MEMORY] Pinecone connection failure: {e}. Degrading to Local Chroma persistence.")

        # Fallback to Local Chroma for local development or as a safety failover
        print("💾 [MEMORY] Mounting Local Chroma storage...")
        self._driver = LocalChromaDriver()
        return self._driver

# Global registry accessor
vector_registry = VectorDriverRegistry()

def get_vector_driver():
    """Helper function to retrieve the active MemoryAdapter."""
    return vector_registry.get_vector_driver()
