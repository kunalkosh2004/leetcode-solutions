"""Generate simple PNG icons for the Chrome extension.

Creates minimal valid PNG files using pure Python (no dependencies).
"""

import struct
import zlib
from pathlib import Path


def create_png(size: int) -> bytes:
    """Create a simple colored square PNG."""
    # Green pixel data (RGBA)
    pixels = b""
    center = size // 2
    radius = size // 3

    for y in range(size):
        row = b"\x00"  # Filter byte
        for x in range(size):
            # Check if pixel is in the circle
            dx = x - center
            dy = y - center
            dist = (dx * dx + dy * dy) ** 0.5

            if dist < radius:
                # Dark green inside circle
                row += struct.pack("BBBB", 22, 163, 74, 255)
            elif dist < radius + 1:
                # Green border
                row += struct.pack("BBBB", 34, 197, 94, 255)
            else:
                # Transparent background
                row += struct.pack("BBBB", 0, 0, 0, 0)
        pixels += row

    # PNG file structure
    def png_chunk(chunk_type: bytes, data: bytes) -> bytes:
        chunk = chunk_type + data
        return struct.pack(">I", len(data)) + chunk + struct.pack(">I", zlib.crc32(chunk) & 0xFFFFFFFF)

    # IHDR
    ihdr_data = struct.pack(">IIBBBBB", size, size, 8, 6, 0, 0, 0)
    ihdr = png_chunk(b"IHDR", ihdr_data)

    # IDAT
    compressed = zlib.compress(pixels)
    idat = png_chunk(b"IDAT", compressed)

    # IEND
    iend = png_chunk(b"IEND", b"")

    return b"\x89PNG\r\n\x1a\n" + ihdr + idat + iend


def main():
    icons_dir = Path(__file__).parent
    for size in [16, 48, 128]:
        png_data = create_png(size)
        (icons_dir / f"icon{size}.png").write_bytes(png_data)
        print(f"Generated icon{size}.png ({len(png_data)} bytes)")


if __name__ == "__main__":
    main()
