# The World in One Day — Friday 20 November 2026
# make.fun contest news-image-20261120 ($250, top 50 share the prize)
#
# A program that writes one image summing up the world's news of
# Friday 20 November 2026 to /output/entry.png. The image is a
# one-page broadsheet drawn in code (see ../render.py for the drawing
# script; the rendered PNG is bundled here so the program is fully
# deterministic and needs no network): Trump pushes the Iran war
# decision to 2027; Russian strikes damage the Dutch and Austrian
# embassies in Kyiv; the ICJ rules Myanmar committed genocide
# against the Rohingya; Houthi missiles hit Riyadh; Anthropic's
# value reportedly hits $1.5tn after its record IPO; GTA VI sales
# pass $1.80bn; plus Voyager 1, Cyclone Akvan, Gaza, Hayabusa2,
# South Korea and North Korea.
#
# Python 3.13, standard library only. Outside the grader's container,
# MAKEFUN_OUTPUT_DIR stands in for /output:
#   mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py

import os
import shutil
import struct
import sys
import zlib
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))

EXPECTED_WIDTH = 1024
EXPECTED_HEIGHT = 1024
MAX_BYTES = 1_048_576  # contest cap: entry.png must fit in 1 MiB
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def fail(message):
    print(f"error: {message}", file=sys.stderr)
    raise SystemExit(1)


def validate_png(path):
    """Check the written file is a real, complete 1024x1024 PNG within 1 MiB."""
    if not path.is_file():
        fail(f"output missing: {path}")
    data = path.read_bytes()
    if not data:
        fail(f"output is empty: {path}")
    if len(data) > MAX_BYTES:
        fail(f"output is {len(data)} bytes, over the 1 MiB cap: {path}")
    if data[:8] != PNG_SIGNATURE:
        fail(f"output is not a PNG file: {path}")
    if len(data) < 33 or data[12:16] != b"IHDR":
        fail(f"output has no PNG IHDR chunk: {path}")
    width, height = struct.unpack(">II", data[16:24])
    if (width, height) != (EXPECTED_WIDTH, EXPECTED_HEIGHT):
        fail(
            f"output is {width}x{height}, expected "
            f"{EXPECTED_WIDTH}x{EXPECTED_HEIGHT}: {path}"
        )
    if zlib.crc32(data[12:29]) & 0xFFFFFFFF != struct.unpack(">I", data[29:33])[0]:
        fail(f"output IHDR chunk is corrupt (bad CRC): {path}")
    # Decompress the image data to prove the file is complete, not truncated.
    offset = 8
    idat = bytearray()
    while offset + 8 <= len(data):
        length = struct.unpack(">I", data[offset : offset + 4])[0]
        chunk_type = data[offset + 4 : offset + 8]
        if chunk_type == b"IDAT":
            idat += data[offset + 8 : offset + 8 + length]
        offset += 12 + length
        if chunk_type == b"IEND":
            break
    if not idat:
        fail(f"output has no PNG image data (IDAT): {path}")
    try:
        zlib.decompress(bytes(idat))
    except zlib.error as exc:
        fail(f"output image data is corrupt or truncated: {exc}")
    return len(data)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    src = HERE / "entry.png"
    dst = OUT / "entry.png"
    shutil.copyfile(src, dst)
    size = validate_png(dst)
    print(f"wrote {dst} ({size} bytes, {EXPECTED_WIDTH}x{EXPECTED_HEIGHT} PNG)")


if __name__ == "__main__":
    main()
