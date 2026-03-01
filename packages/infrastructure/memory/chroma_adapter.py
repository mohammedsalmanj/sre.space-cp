"""
File: packages/infrastructure/memory/chroma_adapter.py
Layer: Infrastructure / Memory Adapter
Purpose: Local incident memory using ChromaDB for sub-second retrieval.
Problem Solved: Provides a persistent historical record for local-only development and serves as a failover for cloud memory.
Interaction: Used by Brain (querying) and Curator (archiving).
Dependencies: chromadb, packages.infrastructure.base
"""
import chromadb
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from ..base import MemoryAdapter, NormalizedTelemetry

class LocalChromaDriver(MemoryAdapter):
    """
    Implementation of the MemoryAdapter using ChromaDB.
    Optimized for local persistence and low-latency pattern matching.
    """
    def __init__(self):
        """Initializes the Chroma HTTP client and retrieves the incident collection."""
        host = os.getenv('CHROMA_DB_HOST', 'localhost')
        port = int(os.getenv('CHROMA_DB_PORT', 8000))
        try:
            self.client = chromadb.HttpClient(host=host, port=port)
            self.collection = self.client.get_or_create_collection(name="sre_incident_memory")
        except Exception:
            self.collection = None

    def upsert_fix(self, incident_id: str, root_cause: str, remediation: str, stack_type: str, score: float, telemetry: Optional[NormalizedTelemetry] = None, is_simulation: bool = False) -> bool:
        """
        Persists a verified remediation plan to local storage.
        
        Args:
            incident_id (str): Unique identifier for the incident.
            root_cause (str): Analyzed cause of the failure.
            remediation (str): The applied fix.
            stack_type (str): Infrastructure provider (ec2, eks, etc.).
            score (float): Confidence score of the diagnosis.
            telemetry (NormalizedTelemetry, optional): Standardized system metrics.
            is_simulation (bool): Flag indicating if this is a synthetic incident.
        Returns:
            bool: Success status of the storage operation.
        """
        if not self.collection: return False
        try:
            doc_id = f"PM-{incident_id or datetime.now().strftime('%S%M')}"
            metadata = {
                "solution": remediation,
                "stack_type": stack_type,
                "remediation_success_score": score,
                "incident_id": incident_id,
                "confidence_gate": 0.85,
                "is_simulation": is_simulation
            }
            
            # Map telemetry fields into metadata for future rich filtering
            if telemetry:
                metadata.update({f"tel_{k}": str(v) if isinstance(v, (dict, list)) else v 
                               for k, v in telemetry.model_dump().items()})
            
            self.collection.add(
                documents=[f"RCA: {root_cause} | Mitigation: {remediation}"],
                metadatas=[metadata],
                ids=[doc_id]
            )
            return True
        except Exception as e:
            print(f"⚠️ Chroma Storage Warning: {e}")
            return False

    def query_memory(self, query_text: str, stack_type: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Queries local memory for incidents related to the current error trace.
        
        Args:
            query_text (str): The error signature to match.
            stack_type (str): Filters results to the current infrastructure stack.
            top_k (int): Maximum number of results to return.
        Returns:
            List[Dict[str, Any]]: Historical metadata for relevant incidents.
        """
        if not self.collection: return []
        try:
            results = self.collection.query(
                query_texts=[query_text], 
                n_results=top_k,
                where={"stack_type": stack_type}
            )
            if results and results['metadatas']:
                return results['metadatas'][0]
            return []
        except Exception as e:
            print(f"⚠️ Chroma Query Warning: {e}")
            return []
