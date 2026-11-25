"""Tests for KV Prefix Cache Coalescer."""
import unittest
from kv_prefix_cache_coalescer.core import KVPrefixCoalescer


class TestKVPrefixCoalescer(unittest.TestCase):
    def test_clusters_shared_prefix_blocks(self):
        c = KVPrefixCoalescer(block_size=2)
        res = c.schedule([
            {"id": "a1", "tokens": ["s1", "s2", "p1", "p2", "x"]},
            {"id": "b1", "tokens": ["z1", "z2", "q1", "q2", "y"]},
            {"id": "a2", "tokens": ["s1", "s2", "p1", "p2", "w"]},
        ])
        ids = [r["id"] for r in res["schedule"]]
        self.assertEqual(abs(ids.index("a1") - ids.index("a2")), 1)
        self.assertEqual(res["saved_tokens"], 4)

    def test_empty_queue(self):
        res = KVPrefixCoalescer().schedule([])
        self.assertEqual(res["saved_tokens"], 0)
