import hashlib
import json
from datetime import datetime

class AuditChain:
    GENESIS_HASH = "0000000000000000000000000000000000000000000000000000000000000000"

    @staticmethod
    def compute_hash(previous_hash: str, timestamp: datetime, event_type: str, entity_type: str, entity_id: str, payload: dict) -> str:
        data = f"{previous_hash}{timestamp.isoformat()}{event_type}{entity_type}{entity_id}{json.dumps(payload, sort_keys=True)}"
        return hashlib.sha256(data.encode('utf-8')).hexdigest()

    @staticmethod
    def verify_chain(events) -> dict:
        """
        Verify a chronological list of AuditEvent models.
        """
        if not events:
            return {"valid": True, "verified_records": 0}
            
        current_expected_hash = AuditChain.GENESIS_HASH
        
        for index, event in enumerate(events):
            if event.previous_hash != current_expected_hash:
                return {
                    "valid": False,
                    "verified_records": index,
                    "first_broken_record": event.id,
                    "reason": "Previous hash mismatch"
                }
                
            calculated = AuditChain.compute_hash(
                event.previous_hash,
                event.timestamp,
                event.event_type,
                event.entity_type,
                event.entity_id,
                event.payload
            )
            
            if event.hash != calculated:
                return {
                    "valid": False,
                    "verified_records": index,
                    "first_broken_record": event.id,
                    "reason": "Hash mismatch"
                }
                
            current_expected_hash = calculated
            
        return {"valid": True, "verified_records": len(events)}
