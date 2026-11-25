"""Core radix-prefix request coalescer for GPU KV-cache reuse."""
from typing import Any, Dict, List, Tuple


class KVPrefixCoalescer:
    """Reorders queued LLM requests to cluster shared token prefixes into contiguous batches."""

    def __init__(self, block_size: int = 16):
        if block_size < 1:
            raise ValueError("block_size must be >= 1")
        self.block_size = block_size

    def _prefix_blocks(self, tokens: List[str]) -> Tuple[Tuple[str, ...], ...]:
        full_blocks = len(tokens) // self.block_size
        return tuple(tuple(tokens[i * self.block_size:(i + 1) * self.block_size]) for i in range(full_blocks))

    def schedule(self, requests: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not requests:
            return {"schedule": [], "estimated_cache_hit_ratio": 0.0, "saved_tokens": 0}

        enriched = []
        for idx, req in enumerate(requests):
            toks = list(req["tokens"])
            blocks = self._prefix_blocks(toks)
            enriched.append((blocks, idx, req))

        enriched.sort(key=lambda item: (item[0], item[1]))
        ordered = [item[2] for item in enriched]

        prev_blocks: Tuple[Tuple[str, ...], ...] = ()
        total_tokens = 0
        reused_tokens = 0
        for blocks, _, req in enriched:
            tok_len = len(req["tokens"])
            total_tokens += tok_len
            shared = 0
            for b1, b2 in zip(prev_blocks, blocks):
                if b1 == b2:
                    shared += self.block_size
                else:
                    break
            reused_tokens += shared
            prev_blocks = blocks

        ratio = round(reused_tokens / max(1, total_tokens), 4)
        return {
            "schedule": ordered,
            "estimated_cache_hit_ratio": ratio,
            "saved_tokens": reused_tokens,
        }
