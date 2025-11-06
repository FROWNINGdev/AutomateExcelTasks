#!/usr/bin/env python3
"""
Compare UID lists between POCHTA, Telecom and ASBT for a given month directory.

Directory structure (example):
  Comparer/
    AUGUST/
      ASBT/
        ASBT_AVGUST.csv
      POCHTA/
        POCHTA_AVGUST_1.txt
        POCHTA_AVGUST_2.txt
      Telecom/
        TL_AVGUST_KSUBDD.xlsx
        TL_AVGUST_MAB.xlsx

Rules:
- POCHTA TXT files: one UID per line. First line may be a header like "Uid". Ignore blank lines.
- ASBT CSV: semicolon-separated, quoted; UID in column TV_SERIALNUMBER.
- Telecom XLSX: UID in column doc_num.
- Merge files within the same subdirectory (treat as a single combined list for that source).

Outputs two blocks:
1) Pochta vs Telecom
2) Pochta vs ASBT

Usage:
  python compare_month.py --base-dir "c:/Users/User/CascadeProjects/QOIDA_Buzar/Comparer/AUGUST" --month "Avgust" --export

"""
from __future__ import annotations
import argparse
import os
import sys
from typing import Iterable, Set, List

# We use pandas for CSV/XLSX reading due to varied encodings and Excel support
try:
    import pandas as pd  # type: ignore
except Exception as e:
    pd = None

# Optional progress bars via tqdm
try:
    from tqdm import tqdm  # type: ignore
    _TQDM_AVAILABLE = True
except Exception:
    tqdm = None  # type: ignore
    _TQDM_AVAILABLE = False


def _normalize_uid(value) -> str | None:
    if value is None:
        return None
    s = str(value)
    # Remove BOM if present and surrounding quotes/whitespace
    s = s.lstrip('\ufeff').strip().strip('"').strip("'")
    if not s:
        return None
    return s


def _write_uids_txt(file_path: str, uids: Set[str]) -> None:
    """Write a TXT file with header 'Uid' and each UID on new line.
    The file will be encoded as UTF-8.
    """
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w', encoding='utf-8', newline='') as f:
        f.write('Uid\n')
        for uid in sorted(uids):
            f.write(f"{uid}\n")


def read_pochta_txts(dir_path: str, use_tqdm: bool = True) -> Set[str]:
    """Read all .txt files, return set of UIDs.
    First line may be a header (e.g., 'Uid'); ignore if so.
    """
    uids: Set[str] = set()
    if not os.path.isdir(dir_path):
        return uids
    txt_files = [os.path.join(dir_path, f) for f in os.listdir(dir_path) if f.lower().endswith('.txt')]
    files_iter = sorted(txt_files)
    if use_tqdm and _TQDM_AVAILABLE:
        files_iter = tqdm(files_iter, desc='POCHTA TXT files', unit='file')  # type: ignore
    for fp in files_iter:  # type: ignore
        try:
            # Try UTF-8 first, then fallback to cp1251/latin1
            tried_encodings = ['utf-8', 'utf-8-sig', 'cp1251', 'latin1']
            success = False
            for enc in tried_encodings:
                try:
                    with open(fp, 'r', encoding=enc, errors='ignore') as f:
                        first = True
                        for line in f:
                            s = _normalize_uid(line)
                            if s is None:
                                continue
                            header_tokens = {'uid', 'id', 'doc_num', 'docnum'}
                            if first and s.lower() in header_tokens:
                                first = False
                                continue
                            first = False
                            # Also guard against stray header tokens mid-file
                            if s.lower() in header_tokens:
                                continue
                            uids.add(s)
                    success = True
                    break
                except Exception:
                    continue
            if not success:
                print(f"Warning: Failed to read {fp}")
        except Exception as e:
            print(f"Warning: Error reading {fp}: {e}")
    return uids


def read_asbt_csv(dir_path: str, use_tqdm: bool = True) -> Set[str]:
    """Read ASBT CSV file(s), extract TV_SERIALNUMBER as UID set.
    Handles semicolon separator and varied encodings.
    """
    uids: Set[str] = set()
    if not os.path.isdir(dir_path):
        return uids
    csv_files = [os.path.join(dir_path, f) for f in os.listdir(dir_path) if f.lower().endswith('.csv')]
    files_iter = sorted(csv_files)
    if use_tqdm and _TQDM_AVAILABLE:
        files_iter = tqdm(files_iter, desc='ASBT CSV files', unit='file')  # type: ignore
    for fp in files_iter:  # type: ignore
        if pd is None:
            print("Error: pandas not installed. Please install dependencies from requirements.txt")
            sys.exit(1)
        # Try common encodings
        for enc in ['utf-8', 'utf-8-sig', 'cp1251', 'latin1']:
            try:
                df = pd.read_csv(fp, sep=';', quotechar='"', engine='python', encoding=enc, dtype=str, on_bad_lines='skip')
                break
            except Exception:
                df = None  # type: ignore
                continue
        if df is None:
            print(f"Warning: Could not read CSV {fp}")
            continue
        # Accept common variants of the column name
        possible_cols = ['TV_SERIALNUMBER', 'Tv_SerialNumber', 'tv_serialnumber', 'TV_SERIALNUMBER\ufeff']
        col = None
        for c in df.columns:
            if c in possible_cols or c.strip().upper() == 'TV_SERIALNUMBER':
                col = c
                break
        if col is None:
            print(f"Warning: Column TV_SERIALNUMBER not found in {fp}. Available columns: {list(df.columns)}")
            continue
        series = df[col].astype(str)
        for v in series:
            s = _normalize_uid(v)
            if s:
                uids.add(s)
    return uids


def read_telecom_excels(dir_path: str, use_tqdm: bool = True) -> Set[str]:
    """Read Telecom Excel files, extract doc_num as UID set."""
    uids: Set[str] = set()
    if not os.path.isdir(dir_path):
        return uids
    xlsx_files = [os.path.join(dir_path, f) for f in os.listdir(dir_path) if f.lower().endswith(('.xlsx', '.xls'))]
    files_iter = sorted(xlsx_files)
    if use_tqdm and _TQDM_AVAILABLE:
        files_iter = tqdm(files_iter, desc='Telecom Excel files', unit='file')  # type: ignore
    for fp in files_iter:  # type: ignore
        if pd is None:
            print("Error: pandas not installed. Please install dependencies from requirements.txt")
            sys.exit(1)
        try:
            # Read only the necessary column to reduce memory if possible
            df = pd.read_excel(fp, dtype=str, engine=None)  # engine auto-select; openpyxl for xlsx
        except Exception as e:
            print(f"Warning: Could not read Excel {fp}: {e}")
            continue
        # Try to locate 'doc_num' with case-insensitive matching
        col = None
        for c in df.columns:
            if c.strip().lower() == 'doc_num':
                col = c
                break
        if col is None:
            print(f"Warning: Column doc_num not found in {fp}. Available columns: {list(df.columns)}")
            continue
        series = df[col].astype(str)
        for v in series:
            s = _normalize_uid(v)
            if s:
                uids.add(s)
    return uids


def print_stats(month_display: str, po: Set[str], tl: Set[str], asbt: Set[str]) -> None:
    # Pochta vs Telecom
    both_pt = po & tl
    only_po_vs_tl = po - tl
    only_tl_vs_po = tl - po

    print("-" * 10)
    print(f"{month_display} uchun statistika (Pochta-Telecom)")
    print("-" * 44)
    print(f"Pochta bergan faylda jami: {len(po):,}".replace(',', ' '))
    print(f"Telecom bergan faylda jami: {len(tl):,}".replace(',', ' '))
    print("-" * 44)
    print(f"Ikkalasida ham mavjud bo'lganlar soni: {len(both_pt):,}".replace(',', ' '))
    print(f"Pochta bergan faylda mavjud, Telecom bergan faylda yo'q soni: {len(only_po_vs_tl):,}".replace(',', ' '))
    print(f"Telecom bergan faylda mavjud, Pochta bergan faylda yo'q soni: {len(only_tl_vs_po):,}".replace(',', ' '))
    print()

    # Pochta vs ASBT
    both_pa = po & asbt
    only_po_vs_asbt = po - asbt
    only_asbt_vs_po = asbt - po

    print("-" * 12)
    print(f"{month_display} uchun solishtirma statistika (Pochta - ASBT):")
    print("-" * 50)
    print(f"TXT (Pochta) fayldagi jami: {len(po):,}".replace(',', ' '))
    print(f"CSV (ASBT) fayldagi jami: {len(asbt):,}".replace(',', ' '))
    print("-" * 50)
    print(f"Ikkalasida ham mavjud bo'lganlar soni: {len(both_pa):,}".replace(',', ' '))
    print(f"Faqat TXT (Pochta) faylda mavjud bo'lganlar soni: {len(only_po_vs_asbt):,}".replace(',', ' '))
    print(f"Faqat CSV (ASBT) faylda mavjud bo'lganlar soni: {len(only_asbt_vs_po):,}".replace(',', ' '))


def main():
    parser = argparse.ArgumentParser(description='Compare UID lists between POCHTA, Telecom and ASBT for a month directory.')
    parser.add_argument('--base-dir', type=str, default=os.path.join('Comparer', 'AUGUST'), help='Path to month directory containing ASBT/ POCHTA/ Telecom/')
    parser.add_argument('--month', type=str, default='Avgust', help='Month display name for report headers (e.g., Avgust, Iyul)')
    parser.add_argument('--no-progress', action='store_true', help='Disable tqdm progress bars')
    parser.add_argument('--export', action='store_true', help='Export UID differences to TXT files')
    parser.add_argument('--export-dir', type=str, default=None, help='Directory to save exported TXT files (defaults to <base-dir>/output)')
    args = parser.parse_args()

    base_dir = args.base_dir
    asbt_dir = os.path.join(base_dir, 'ASBT')
    pochta_dir = os.path.join(base_dir, 'POCHTA')
    telecom_dir = os.path.join(base_dir, 'Telecom')

    # Read sources
    use_tqdm = not args.no_progress
    pochta_uids = read_pochta_txts(pochta_dir, use_tqdm=use_tqdm)
    asbt_uids = read_asbt_csv(asbt_dir, use_tqdm=use_tqdm)
    telecom_uids = read_telecom_excels(telecom_dir, use_tqdm=use_tqdm)

    # Print stats
    print_stats(args.month, pochta_uids, telecom_uids, asbt_uids)

    # Optionally export differences
    if args.export:
        export_base = args.export_dir or os.path.join(base_dir, 'output')
        # Pochta vs Telecom differences
        only_po_vs_tl = pochta_uids - telecom_uids
        only_tl_vs_po = telecom_uids - pochta_uids
        _write_uids_txt(os.path.join(export_base, 'pochta_minus_telecom.txt'), only_po_vs_tl)
        _write_uids_txt(os.path.join(export_base, 'telecom_minus_pochta.txt'), only_tl_vs_po)

        # Pochta vs ASBT differences
        only_po_vs_asbt = pochta_uids - asbt_uids
        only_asbt_vs_po = asbt_uids - pochta_uids
        _write_uids_txt(os.path.join(export_base, 'pochta_minus_asbt.txt'), only_po_vs_asbt)
        _write_uids_txt(os.path.join(export_base, 'asbt_minus_pochta.txt'), only_asbt_vs_po)


if __name__ == '__main__':
    main()
