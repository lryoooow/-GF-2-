from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

from atmcorr.common.raster import GDAL_DTYPES
from atmcorr.common.sixs import SixSOptions

from .calibration import load_calibration_config
from .processor import GFProcessOptions, process_input


def parse_args(argv: list[str] | None = None):
    parser = argparse.ArgumentParser(description="Atmospheric correction for GF MSS imagery.")
    parser.add_argument("--input-dir", "--Input_dir", required=True, help="GF scene directory or parent directory")
    parser.add_argument("--output-dir", "--Output_dir", required=True, help="Output directory")
    parser.add_argument("--fallback-year", "--Fallback_year", default="2019")
    parser.add_argument("--aot550", type=float, default=0.14497)
    parser.add_argument("--ground-reflectance", type=float, default=0.36)
    parser.add_argument("--aerosol-profile", default="Continental")
    parser.add_argument("--block-size", type=int, default=2048)
    parser.add_argument("--output-dtype", choices=sorted(GDAL_DTYPES), default="int16")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    start = time.time()
    args = parse_args(sys.argv[1:] if argv is None else argv)

    config = load_calibration_config()
    options = GFProcessOptions(
        fallback_year=args.fallback_year,
        block_size=args.block_size,
        output_dtype=args.output_dtype,
        sixs=SixSOptions(
            aot550=args.aot550,
            ground_reflectance=args.ground_reflectance,
            aerosol_profile=args.aerosol_profile,
        ),
    )

    outputs = process_input(Path(args.input_dir), Path(args.output_dir), config, options)
    print(f"Finished {len(outputs)} scene(s) in {time.time() - start:.1f}s")
    for output in outputs:
        print(f"Output: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
