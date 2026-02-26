"""
File: packages/infrastructure/memory/pinecone_adapter.py
Layer: Infrastructure / Memory Adapter
Purpose: Cloud-native persistent incident memory using Pinecone.
Problem Solved: Enables cross-stack learning and pattern matching for globally distributed SRE squads.
Interaction: Used by Brain (search) and Curator (storage).
Dependencies: pinecone-client, packages.infrastructure.base
"""
import os
import time
from typing import List, Dict, Any, Optional
from pinecone import Pinecone, ServerlessSpec
from ..base import MemoryAdapter, NormalizedTelemetry

class PineconeMemoryDriver(MemoryAdapter):
    """
    Implementation of incident memory using the Pinecone Vector Database.
    Targeted for production-grade, distributed SRE control planes.
    """
    def __init__(self):
        """
        Initializes the Pinecone connection and ensures the target index exists.
        Uses the official Pinecone v6.0.0+ SDK patterns.
        """
        self.api_key = os.getenv("PINECONE_API_KEY")
        self.index_name = os.getenv("PINECONE_INDEX_NAME", "sre-incident-memory")
        
        if not self.api_key:
            raise ConnectionError("PINECONE_API_KEY is missing. Cannot initialize cloud memory.")

        # 1. Initialization using the latest Pinecone SDK specification
        self.pc = Pinecone(api_key=self.api_key)
        
        # 2. Index Management: Dynamic creation of the serverless index if not present
        existing_indexes = [idx.name for idx in self.pc.list_indexes()]
        if self.index_name not in existing_indexes:
            print(f"🌲 [PINECONE] Creating serverless index: {self.index_name}")
            self.pc.create_index(
                name=self.index_name,
                dimension=1536, # Calibrated for standard OpenAI text-embedding models
                metric="cosine",
                spec=ServerlessSpec(cloud='aws', region='us-east-1')
            )
            # Polling for index readiness to prevent immediate upsert failure
            while not self.pc.describe_index(self.index_name).status['ready']:
                time.sleep(1)

        self.index = self.pc.Index(self.index_name)
        
        # 3. Dimension Discovery: Dynamic detection to ensure compatibility with pre-existing indexes
        try:
            desc = self.pc.describe_index(self.index_name)
            self.dimension = desc.dimension
            print(f"🌲 [PINECONE] Index '{self.index_name}' detected. Dimension: {self.dimension}")
        except Exception:
            self.dimension = 1536 # Fallback to OpenAI standard

    def upsert_fix(self, incident_id: str, root_cause: str, remediation: str, stack_type: str, score: float, telemetry: Optional[NormalizedTelemetry] = None, is_simulation: bool = False) -> bool:
        """
        Stores a verified remediation strategy in the cloud vector store with full metadata context.
        
        Args:
            incident_id (str): Unique incident identifier for tracking.
            root_cause (str): The identified root cause of the failure.
            remediation (str): The specific fix or patch applied.
            stack_type (str): The target infrastructure stack (EC2, EKS, GCE, etc.).
            score (float): The success or confidence score of the operation.
            telemetry (NormalizedTelemetry, optional): Standardized system health data.
            is_simulation (bool): Flag indicating if this is a synthetic incident.
        Returns:
            bool: Success status of the upsert operation.
        """
        # Metadata construction enforcing mandatory security and context requirements
        metadata = {
            "incident_id": incident_id,
            "root_cause": root_cause,
            "remediation": remediation,
            "stack_type": stack_type,
            "remediation_success_score": score,
            "confidence_gate": 0.85, # Production safety standard threshold
            "timestamp": time.time(),
            "is_simulation": is_simulation
        }

        # Embed NormalizedTelemetry into metadata to facilitate deep diagnostic filtering
        if telemetry:
            telemetry_data = telemetry.model_dump()
            for k, v in telemetry_data.items():
                # Enforce flat metadata structure for cross-provider compatibility
                if isinstance(v, (dict, list)):
                    metadata[f"tel_{k}"] = str(v)
                else:
                    metadata[f"tel_{k}"] = v

        # Vector generation placeholder
        # In production, this would call an Embedding Service (OpenAI/HuggingFace)
        vector = [0.1] * self.dimension 
        
        try:
            self.index.upsert(vectors=[{"id": incident_id, "values": vector, "metadata": metadata}])
            return True
        except Exception as e:
            print(f"⚠️ Pinecone Cloud Upsert Failed: {e}")
            return False

    def query_memory(self, query_text: str, stack_type: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Searches historical incidents across the cloud memory, filtered by infrastructure stack.
        
        Args:
            query_text (str): The error signature string to perform RAG search against.
            stack_type (str): Filters results effectively to the current infrastructure type.
            top_k (int): Number of most relevant historical contexts to retrieve.
        Returns:
            List[Dict[str, Any]]: Metadata collection for matching historical events.
        """
        # Search vector generation placeholder
        query_vector = [0.1] * self.dimension
        
        try:
            results = self.index.query(
                vector=query_vector,
                top_k=top_k,
                filter={"stack_type": {"$eq": stack_type}},
                include_metadata=True
            )
            return [match.metadata for match in results.matches]
        except Exception as e:
            print(f"⚠️ Pinecone Cloud Query Failed: {e}")
            return []
