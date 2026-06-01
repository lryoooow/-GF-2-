from __future__ import annotations

import argparse


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Landsat atmospheric correction entrypoint.")
    parser.add_argument("--input-dir", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.parse_args(argv)
    raise NotImplementedError(
        "Landsat processing is not yet available in this module."
    )
