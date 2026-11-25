"""CLI for KV Prefix Cache Coalescer."""
import argparse
import json
from .core import KVPrefixCoalescer


def main():
    parser = argparse.ArgumentParser(description="KV Prefix Cache Coalescer CLI")
    parser.add_argument("--block-size", type=int, default=4, help="KV cache block size")
    args = parser.parse_args()

    c = KVPrefixCoalescer(block_size=args.block_size)
    reqs = [
        {"id": "req-1", "tokens": ["SYS", "RULE", "MCP", "A", "hello"]},
        {"id": "req-2", "tokens": ["OTHER", "SYS", "X", "Y", "bye"]},
        {"id": "req-3", "tokens": ["SYS", "RULE", "MCP", "A", "world"]},
    ]
    res = c.schedule(reqs)
    print(json.dumps({"order": [r["id"] for r in res["schedule"]], "saved_tokens": res["saved_tokens"]}, indent=2))


if __name__ == "__main__":
    main()
