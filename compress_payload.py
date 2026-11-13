# SubExtract Studio — Developed by NoYz
# Compresses the compiled application directory into installer_payload.zip

import os
import zipfile
import time

SRC_DIR = r"C:\Users\NoYz\.gemini\antigravity\scratch\subextract_studio\dist\SubExtract Studio"
OUTPUT_ZIP = r"C:\Users\NoYz\.gemini\antigravity\scratch\subextract_studio\installer_payload.zip"

print("Compressing SubExtract Studio into installer payload...")
start_time = time.time()

total_files = sum(len(files) for _, _, files in os.walk(SRC_DIR))
processed = 0

with zipfile.ZipFile(OUTPUT_ZIP, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
    for root, dirs, files in os.walk(SRC_DIR):
        for f in files:
            full_path = os.path.join(root, f)
            arcname = os.path.relpath(full_path, SRC_DIR)
            zf.write(full_path, arcname)
            processed += 1
            if processed % 10 == 0 or processed == total_files:
                print(f"[{processed}/{total_files}] Packed: {arcname}")

elapsed = time.time() - start_time
zip_size_mb = os.path.getsize(OUTPUT_ZIP) / (1024 * 1024)
print(f"\nCompression complete in {elapsed:.1f}s!")
print(f"Payload created: {OUTPUT_ZIP} ({zip_size_mb:.2f} MB)")
