#!/usr/bin/env python3
"""Create missing symlinks for CodeLlama model"""

import os
import json
from pathlib import Path

# Paths
cache_dir = Path.home() / ".cache/huggingface/hub/models--codellama--CodeLlama-7b-hf"
snapshot_dir = cache_dir / "snapshots/6c284d1468fe6c413cf56183e69b194dcfa27fe6"
blobs_dir = cache_dir / "blobs"

# Read index to find what files we need
index_link = snapshot_dir / "model.safetensors.index.json"
with open(os.readlink(index_link) if index_link.is_symlink() else index_link) as f:
    # Need to read from blob
    index_path = blobs_dir / os.readlink(index_link).replace("../../blobs/", "")
    with open(index_path) as f2:
        index_data = json.load(f2)

# Find required safetensor files
required_files = set(index_data["weight_map"].values())
print(f"Required files: {required_files}")

# Find blobs
blobs = list(blobs_dir.glob("*"))
print(f"\nTotal blobs: {len(blobs)}")

# Map by size
large_blobs = [(b, b.stat().st_size) for b in blobs if b.stat().st_size > 1_000_000_000]
large_blobs.sort(key=lambda x: x[1], reverse=True)

print("\nLarge blobs (>1GB):")
for blob, size in large_blobs[:5]:
    print(f"  {blob.name}: {size / 1024**3:.2f} GB")

# Create symlinks
if len(large_blobs) >= 2:
    # Largest should be model-00001
    link1 = snapshot_dir / "model-00001-of-00002.safetensors"
    link2 = snapshot_dir / "model-00002-of-00002.safetensors"
    
    if not link1.exists():
        os.symlink(f"../../blobs/{large_blobs[0][0].name}", link1)
        print(f"\nCreated: {link1.name} -> {large_blobs[0][0].name}")
    
    if not link2.exists():
        os.symlink(f"../../blobs/{large_blobs[1][0].name}", link2)
        print(f"Created: {link2.name} -> {large_blobs[1][0].name}")
    
    print("\nSymlinks created successfully!")
else:
    print("\nERROR: Not enough large blobs found!")
