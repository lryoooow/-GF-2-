from __future__ import annotations

import argparse
import tarfile
from multiprocessing import Pool
from pathlib import Path

from atmcorr.common.sixs import SixSOptions

from .calibration import load_calibration_config
from .processor import GFProcessOptions, process_scene


def extract_archive(archive_path: Path, extract_root: Path) -> Path:
    scene_dir = extract_root / archive_path.name.removesuffix(".tar.gz")
    scene_dir.mkdir(parents=True, exist_ok=True)
    with tarfile.open(archive_path) as archive:
        archive.extractall(scene_dir)
    return scene_dir


def _process_archive(args):
    archive_path, extract_root, output_dir, fallback_year = args
    config = load_calibration_config()
    scene_dir = extract_archive(Path(archive_path), Path(extract_root))
    options = GFProcessOptions(fallback_year=fallback_year, sixs=SixSOptions())
    return process_scene(scene_dir, output_dir, config, options)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Batch atmospheric correction for GF tar.gz scenes.")
    parser.add_argument("--input-dir", required=True, help="Directory containing GF .tar.gz files")
    parser.add_argument("--work-dir", required=True, help="Directory used for extraction")
    parser.add_argument("--output-dir", required=True, help="Output directory")
    parser.add_argument("--fallback-year", default="2019")
    parser.add_argument("--workers", type=int, default=3)
    args = parser.parse_args(argv)

    archives = sorted(Path(args.input_dir).glob("*.tar.gz"))
    with Pool(args.workers) as pool:
        for output in pool.imap_unordered(
            _process_archive,
            [(archive, args.work_dir, args.output_dir, args.fallback_year) for archive in archives],
        ):
            print(f"Output: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
