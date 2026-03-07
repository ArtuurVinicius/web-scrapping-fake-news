#!/usr/bin/env python3
"""Remove the `scraped_at` column from a CSV while preserving other fields.

Usage:
  python remove-scrapped-at.py --input corpus-pt.csv --output corpus-pt.no-scraped.csv
  python remove-scrapped-at.py --input corpus-pt.csv --inplace
"""
from __future__ import annotations
import argparse
import sys
from pathlib import Path
import pandas as pd


def main(argv: list[str] | None = None) -> int:
	argv = argv if argv is not None else sys.argv[1:]
	p = argparse.ArgumentParser(description='Remove scraped_at column from CSV')
	p.add_argument('-i', '--input', default='corpus-pt.csv', help='input CSV path')
	p.add_argument('-o', '--output', default=None, help='output CSV path (default: <input>.no-scraped.csv)')
	p.add_argument('--inplace', action='store_true', help='overwrite the input file')
	args = p.parse_args(argv)

	input_path = Path(args.input)
	if not input_path.exists():
		print(f"Input file not found: {input_path}")
		return 2

	df = pd.read_csv(input_path, encoding='utf-8')
	col = 'scraped_at'
	if col not in df.columns:
		print(f"Column '{col}' not found in {input_path}. Nothing to remove.")
		# still allow writing a copy if requested
		if args.output:
			out = Path(args.output)
			df.to_csv(out, index=False, encoding='utf-8')
			print(f"Wrote unchanged file to {out}")
		return 0

	non_null = int(df[col].notna().sum())
	total = int(len(df))
	print(f"Found column '{col}' with {non_null}/{total} non-empty values. Removing column...")

	df = df.drop(columns=[col])

	if args.inplace:
		out_path = input_path
	else:
		out_path = Path(args.output) if args.output else input_path.with_name(input_path.stem + '.no-scraped.csv')

	df.to_csv(out_path, index=False, encoding='utf-8')
	print(f"Saved {len(df)} rows x {len(df.columns)} cols to {out_path}")
	return 0


if __name__ == '__main__':
	raise SystemExit(main())

