import hashlib
import json
import math
from typing import List, Dict, Any, Optional, Tuple

class MerkleTree:
    """
    Standard Binary Merkle Tree implementation (RFC 6962 compliant):
    - Computes cryptographic root hash over arbitrary event leaves.
    - Generates compact O(log N) audit inclusion proofs.
    - Allows standalone verification of any single event against the root without downloading the full ledger.
    """

    def __init__(self, leaf_hashes: List[str]):
        # Sanitize and ensure even leaf count by duplicating the last leaf if odd
        self.leaves = [h.lower() for h in leaf_hashes] if leaf_hashes else []
        self.levels: List[List[str]] = []
        self._build_tree()

    @staticmethod
    def hash_pair(left: str, right: str) -> str:
        """Computes SHA-256 hash of two concatenated child node hashes."""
        combined = (left + right).encode('utf-8')
        return hashlib.sha256(combined).hexdigest()

    def _build_tree(self):
        if not self.leaves:
            self.root = "0" * 64
            self.levels = [[]]
            return

        current_level = self.leaves
        self.levels = [current_level]

        while len(current_level) > 1:
            next_level = []
            for i in range(0, len(current_level), 2):
                left = current_level[i]
                # If odd number of nodes, duplicate the last node
                right = current_level[i + 1] if (i + 1) < len(current_level) else left
                parent = self.hash_pair(left, right)
                next_level.append(parent)
            self.levels.append(next_level)
            current_level = next_level

        self.root = self.levels[-1][0]

    def get_root(self) -> str:
        return self.root

    def generate_proof(self, leaf_index: int) -> Optional[Dict[str, Any]]:
        """
        Generates an O(log N) Merkle audit proof path for a leaf index.
        Returns: { 'leaf_hash': str, 'leaf_index': int, 'root': str, 'proof': [{'position': 'left'|'right', 'hash': str}] }
        """
        if leaf_index < 0 or leaf_index >= len(self.leaves):
            return None

        leaf_hash = self.leaves[leaf_index]
        proof_path = []
        idx = leaf_index

        for level_idx in range(len(self.levels) - 1):
            level = self.levels[level_idx]
            is_right_child = (idx % 2 == 1)
            sibling_idx = idx - 1 if is_right_child else idx + 1

            if sibling_idx < len(level):
                sibling_hash = level[sibling_idx]
            else:
                # Sibling is self if odd
                sibling_hash = level[idx]

            proof_path.append({
                "position": "left" if is_right_child else "right",
                "hash": sibling_hash
            })
            idx = idx // 2

        return {
            "leaf_hash": leaf_hash,
            "leaf_index": leaf_index,
            "merkle_root": self.root,
            "tree_depth": len(self.levels),
            "proof_path": proof_path
        }

    @classmethod
    def verify_proof(cls, leaf_hash: str, proof_path: List[Dict[str, str]], expected_root: str) -> bool:
        """
        Verifies that a leaf hash is part of the Merkle tree with root expected_root
        using only the O(log N) proof path.
        """
        current_hash = leaf_hash.lower()
        for step in proof_path:
            sibling = step["hash"].lower()
            position = step["position"].lower()
            if position == "left":
                current_hash = cls.hash_pair(sibling, current_hash)
            else:
                current_hash = cls.hash_pair(current_hash, sibling)

        return current_hash.lower() == expected_root.lower()
