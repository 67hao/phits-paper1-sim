#!/usr/bin/env python3
"""
Script trich xuat cot Flux (cot so 4 - 'n') tu cac file .out cua PHITS.

Quy tac:
- File "water" (ten file co chua 'water'): bat dau lay tu dong co num = 24
- Cac file nguyen to khac (b, ca, la, o, si, ...): bat dau lay tu dong co num = 34
- Chi lay gia tri cot 4 (flux) khi cot 5 (r.err) < THRESHOLD
- Ngay khi gap dong co r.err >= THRESHOLD thi DUNG lai (khong lay cac dong sau do nua)

Output: 1 file CSV dang COT DOC - moi nguyen to (file) la 1 cot, chi chua flux (n),
khong co r.err.

Cach dung:
    python3 extract_flux.py <thu_muc_chua_file_out> [file_output.csv] [threshold]

Vi du:
    python3 extract_flux.py .                     # threshold mac dinh = 0.2
    python3 extract_flux.py . ket_qua.csv 0.3     # doi threshold thanh 0.3

Neu khong truyen thu muc, script se dung thu muc hien tai.
"""

import os
import re
import sys
import csv
from itertools import zip_longest

# ==== CHINH THRESHOLD O DAY NEU MUON (hoac truyen qua tham so dong lenh) ====
THRESHOLD = 0.1 
# =============================================================================

START_NUM_ELEMENT = 11 
START_NUM_WATER = 1 


def parse_out_file(filepath, start_num, threshold):
    """
    Doc file .out, tra ve list cac gia tri flux (cot 4)
    bat dau tu dong co so thu tu (cot 1 - num) = start_num,
    va dung ngay khi gap r.err >= threshold.
    """
    fluxes = []
    data_line_re = re.compile(
        r'^\s*(\d+)\s+(\d+)\s+([\d.Ee+-]+)\s+([\d.Ee+-]+)\s+([\d.Ee+-]+)\s*$'
    )

    with open(filepath, 'r', errors='ignore') as f:
        for line in f:
            m = data_line_re.match(line)
            if not m:
                continue

            num = int(m.group(1))
            flux = float(m.group(4))
            rerr = float(m.group(5))

            if num < start_num:
                continue

            if rerr >= threshold:
                # Gap gia tri r.err vuot nguong -> dung lai, khong lay nua
                break

            fluxes.append(flux)

    return fluxes


def main():
    folder = sys.argv[1] if len(sys.argv) > 1 else '.'
    output_csv = sys.argv[2] if len(sys.argv) > 2 else 'flux_extracted.csv'
    threshold = float(sys.argv[3]) if len(sys.argv) > 3 else THRESHOLD

    out_files = [
        f for f in sorted(os.listdir(folder))
        if f.lower().endswith('.out')
    ]

    if not out_files:
        print(f"Khong tim thay file .out nao trong thu muc: {folder}")
        return

    print(f"Dang dung threshold r.err < {threshold}\n")

    columns = {}  # ten_cot (khong duoi .out) -> list flux

    for fname in out_files:
        filepath = os.path.join(folder, fname)
        is_water = 'water' in fname.lower()
        start_num = START_NUM_WATER if is_water else START_NUM_ELEMENT

        fluxes = parse_out_file(filepath, start_num, threshold)

        col_name = os.path.splitext(fname)[0]
        columns[col_name] = fluxes

        print(f"--- {fname} (start_num={start_num}) -> lay duoc {len(fluxes)} gia tri ---")

    # Ghi ra file CSV dang cot doc, moi nguyen to 1 cot
    out_path = os.path.join(folder, output_csv)
    col_names = list(columns.keys())
    rows = zip_longest(*[columns[c] for c in col_names], fillvalue='')

    with open(out_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(col_names)
        for row in rows:
            writer.writerow(row)

    print(f"\nDa ghi ket qua (dang cot) vao: {out_path}")


if __name__ == '__main__':
    main()
