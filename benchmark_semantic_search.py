import argparse
import os
import time
from pathlib import Path

import aeronavx
from aeronavx.core.loader import load_airports
from aeronavx.hf.semantic_search import SemanticAirportSearch


def _load_airport_sample(sample_size: int):
    airports = load_airports()
    if sample_size and sample_size > 0:
        return airports[:sample_size]
    return airports


def main():
    parser = argparse.ArgumentParser(description="Benchmark AeroNavX semantic search")
    parser.add_argument("--query", default="Istanbul international airport")
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--sample-size", type=int, default=2000)
    parser.add_argument("--cache-dir", default=os.getenv("AERONAVX_CACHE", "~/.aeronavx"))
    parser.add_argument("--model", default=os.getenv("AERONAVX_EMBED_MODEL", "sentence-transformers/all-MiniLM-L6-v2"))
    args = parser.parse_args()

    cache_dir = Path(args.cache_dir).expanduser()
    token = os.getenv("HF_TOKEN") or os.getenv("HF_API_TOKEN") or os.getenv("HUGGINGFACE_HUB_TOKEN")
    local_only = os.getenv("AERONAVX_OFFLINE", "0") == "1"

    airports = _load_airport_sample(args.sample_size)

    t0 = time.perf_counter()
    searcher = SemanticAirportSearch(
        airports,
        model_name=args.model,
        cache_dir=cache_dir,
        token=token,
        local_only=local_only,
    )
    t1 = time.perf_counter()

    cold_init = t1 - t0

    t2 = time.perf_counter()
    results = searcher.search(args.query, top_k=args.top_k, return_format="list")
    t3 = time.perf_counter()

    cold_search = t3 - t2

    t4 = time.perf_counter()
    results_warm = searcher.search(args.query, top_k=args.top_k, return_format="list")
    t5 = time.perf_counter()

    warm_search = t5 - t4

    t6 = time.perf_counter()
    cached_searcher = SemanticAirportSearch(
        airports,
        model_name=args.model,
        model=searcher.model,
        cache_dir=cache_dir,
    )
    t7 = time.perf_counter()

    cached_init = t7 - t6

    print("Semantic Search Benchmark")
    print(f"Sample size: {len(airports)}")
    print(f"Query: {args.query}")
    print(f"Cold init: {cold_init:.3f}s")
    print(f"Cold search: {cold_search:.3f}s")
    print(f"Warm search: {warm_search:.3f}s")
    print(f"Cached init (reuse model): {cached_init:.3f}s")
    print("Top results:")
    for row in results[: args.top_k]:
        print(f"  {row.get('iata') or '---'}: {row.get('name')} (score={row.get('score'):.3f})")

    if results != results_warm:
        print("Warning: warm search results differ from cold search.")

    aeronavx.clear_semantic_search_cache()


if __name__ == "__main__":
    main()
