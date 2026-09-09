from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from typing import Dict, Any, List
from pydantic import BaseModel

from app.core.database import get_db
from app.models.all import AuditEvent
from app.services.audit.audit_chain import AuditChain
from app.services.audit.merkle import MerkleTree
from app.services.audit.compliance import ClinicalComplianceService

router = APIRouter()

class VerifyProofRequest(BaseModel):
    leaf_hash: str
    proof_path: List[Dict[str, str]]
    expected_root: str

class SimulateTamperRequest(BaseModel):
    target_index: int = 0

@router.get("/")
def get_audit_history(db: Session = Depends(get_db)):
    """Fetches full historical immutable audit chain ordered chronologically."""
    events = db.query(AuditEvent).order_by(AuditEvent.timestamp.asc()).all()
    return [{
        "id": e.id,
        "timestamp": e.timestamp,
        "event_type": e.event_type,
        "entity_type": e.entity_type,
        "entity_id": e.entity_id,
        "actor": e.actor,
        "payload": e.payload,
        "previous_hash": e.previous_hash,
        "hash": e.hash
    } for e in events]

@router.post("/verify")
def verify_audit_chain(db: Session = Depends(get_db)):
    """Executes dual-layer linear SHA-256 and Merkle verification across the entire database ledger."""
    events = db.query(AuditEvent).order_by(AuditEvent.timestamp.asc()).all()
    result = AuditChain.verify_chain(events)
    return result

@router.get("/merkle-root")
def get_merkle_root(db: Session = Depends(get_db)):
    """Computes and returns the RFC 6962 Binary Merkle Root for all ledger records."""
    events = db.query(AuditEvent).order_by(AuditEvent.timestamp.asc()).all()
    tree = AuditChain.build_merkle_tree(events)
    return {
        "merkle_root": tree.get_root(),
        "total_leaves": len(tree.leaves),
        "tree_depth": len(tree.levels),
        "genesis_hash": AuditChain.GENESIS_HASH
    }

@router.get("/merkle-proof/{event_id}")
def get_merkle_proof(event_id: str, db: Session = Depends(get_db)):
    """
    Generates a compact O(log N) Merkle audit proof path for a given audit event.
    Permits instant standalone client-side verification without pulling the complete ledger.
    """
    events = db.query(AuditEvent).order_by(AuditEvent.timestamp.asc()).all()
    leaf_hashes = [e.hash for e in events]
    try:
        leaf_index = next(i for i, e in enumerate(events) if e.id == event_id)
    except StopIteration:
        raise HTTPException(status_code=404, detail=f"Event ID '{event_id}' not found in audit chain")

    tree = MerkleTree(leaf_hashes)
    proof = tree.generate_proof(leaf_index)
    if not proof:
        raise HTTPException(status_code=500, detail="Failed to generate Merkle proof")

    proof["event_id"] = event_id
    proof["actor"] = events[leaf_index].actor
    proof["event_type"] = events[leaf_index].event_type
    return proof

@router.post("/verify-proof")
def verify_merkle_proof(req: VerifyProofRequest):
    """
    Validates an O(log N) Merkle proof path against the target Merkle root.
    Returns boolean validity status.
    """
    is_valid = MerkleTree.verify_proof(req.leaf_hash, req.proof_path, req.expected_root)
    return {
        "valid": is_valid,
        "leaf_hash": req.leaf_hash,
        "expected_root": req.expected_root,
        "status": "VALID_INCLUSION_PROOF" if is_valid else "INVALID_PROOF_PATH"
    }

@router.post("/simulate-tamper")
def simulate_tamper_attack(req: SimulateTamperRequest, db: Session = Depends(get_db)):
    """
    Simulates an adversarial database attack (bit-flip/unauthorized edit) on a copy of the ledger,
    demonstrating the cryptographic chain's instant rejection and pinpointing the exact modified record.
    """
    events = db.query(AuditEvent).order_by(AuditEvent.timestamp.asc()).all()
    result = AuditChain.simulate_tamper(events, target_index=req.target_index)
    return result

@router.get("/certificate/{shipment_id}")
def generate_regulatory_certificate(shipment_id: str, actor: str = "Chief_Regulatory_Officer", db: Session = Depends(get_db)):
    """
    Generates CDSCO Schedule M / WHO-PQS E006 Digital Batch Release Certificate with cryptographic Merkle seal.
    """
    cert = ClinicalComplianceService.generate_batch_certificate(db, shipment_id=shipment_id, actor=actor)
    if "error" in cert:
        raise HTTPException(status_code=404, detail=cert["error"])
    return cert

@router.get("/certificate/{shipment_id}/html", response_class=HTMLResponse)
def get_regulatory_certificate_html(shipment_id: str, actor: str = "Chief_Regulatory_Officer", db: Session = Depends(get_db)):
    """
    Returns the printable, official clinical release HTML dossier.
    """
    cert = ClinicalComplianceService.generate_batch_certificate(db, shipment_id=shipment_id, actor=actor)
    if "error" in cert:
        raise HTTPException(status_code=404, detail=cert["error"])
    return HTMLResponse(content=cert["html_document"], status_code=200)
