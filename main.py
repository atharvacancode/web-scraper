"""
main.py — CLI entry point for the web scraper
"""

import argparse
import json
import sys
from scraper import run_once, run_scheduled


def load_jobs_file(path: str) -> list:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"[ERROR] Could not load jobs file '{path}': {e}")
        sys.exit(1)


def build_job_from_args(args) -> list:
    selectors = {}
    for pair in args.select:
        if "=" not in pair:
            print(f"[ERROR] Invalid selector format '{pair}'. Use field=selector")
            sys.exit(1)
        field, selector = pair.split("=", 1)
        selectors[field.strip()] = selector.strip()
    if not selectors:
        print("[ERROR] Provide at least one --select field=css_selector")
        sys.exit(1)
    return [{"url": args.url, "selectors": selectors}]


def main():
    parser = argparse.ArgumentParser(prog="scraper", description="General-purpose web scraper.")
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument("--url", type=str, help="Single URL to scrape")
    input_group.add_argument("--jobs", type=str, help="Path to jobs JSON config file")
    parser.add_argument("--select", metavar="field=selector", action="append", default=[])
    parser.add_argument("--interval", type=int, default=0, metavar="SECONDS")
    parser.add_argument("--output", type=str, default="output")

    args = parser.parse_args()

    if args.jobs:
        jobs = load_jobs_file(args.jobs)
    else:
        jobs = build_job_from_args(args)

    print(f"\n  Web Scraper — @thragg-codes")
    print(f"  Jobs: {len(jobs)} | Output: {args.output} | Interval: {args.interval or 'once'}\n")

    if args.interval > 0:
        run_scheduled(jobs, args.interval, args.output)
    else:
        run_once(jobs, args.output)
        print("\n  [DONE]")


if __name__ == "__main__":
    main()
