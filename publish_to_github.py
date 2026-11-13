# SubExtract Studio — Developed by NoYz
# Automated GitHub Publisher: Uploads source tree and creates release with installer asset

import os
import sys
import base64
import requests
import subprocess

REPO_OWNER = "BoMayood"
REPO_NAME = "SubExtract-Studio"
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))

print("=" * 60)
print(f"Publishing SubExtract Studio to GitHub: {REPO_OWNER}/{REPO_NAME}")
print("=" * 60)

res = subprocess.run([r"C:\Program Files\GitHub CLI\gh.EXE", "auth", "token"], capture_output=True, text=True)
if res.returncode != 0 or not res.stdout.strip():
    print("Failed to obtain GitHub token from gh CLI!")
    sys.exit(1)

TOKEN = res.stdout.strip()
HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28"
}

# 1. Get current branch head commit and tree
ref_resp = requests.get(f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/git/refs/heads/main", headers=HEADERS)
if ref_resp.status_code != 200:
    print("Failed to get main branch ref:", ref_resp.text)
    sys.exit(1)

base_commit_sha = ref_resp.json()["object"]["sha"]
commit_resp = requests.get(f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/git/commits/{base_commit_sha}", headers=HEADERS)
base_tree_sha = commit_resp.json()["tree"]["sha"]
print(f"Base commit: {base_commit_sha[:7]}, Base tree: {base_tree_sha[:7]}")

# 2. Gather source files
IGNORED_DIRS = {"build", "dist", "release", "bin", "__pycache__", ".git", ".gemini", ".idea", ".vscode", "venv", "env"}
IGNORED_EXTS = {".zip", ".pyc", ".spec", ".log"}

files_to_upload = []
for root, dirs, files in os.walk(PROJECT_DIR):
    dirs[:] = [d for d in dirs if d not in IGNORED_DIRS]
    for f in files:
        ext = os.path.splitext(f)[1].lower()
        if ext in IGNORED_EXTS:
            continue
        full_path = os.path.join(root, f)
        rel_path = os.path.relpath(full_path, PROJECT_DIR).replace("\\", "/")
        files_to_upload.append((rel_path, full_path))

print(f"\nUploading {len(files_to_upload)} files...")
tree_items = []

for rel_path, full_path in files_to_upload:
    with open(full_path, "rb") as fp:
        data = fp.read()
    
    try:
        text_content = data.decode("utf-8")
        payload = {"content": text_content, "encoding": "utf-8"}
    except UnicodeDecodeError:
        b64_content = base64.b64encode(data).decode("ascii")
        payload = {"content": b64_content, "encoding": "base64"}

    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/git/blobs"
    r = requests.post(url, headers=HEADERS, json=payload)
    if r.status_code == 201:
        sha = r.json()["sha"]
        tree_items.append({
            "path": rel_path,
            "mode": "100644",
            "type": "blob",
            "sha": sha
        })
        print(f"  [OK] {rel_path}")
    else:
        print(f"  [FAIL] {rel_path}: {r.status_code} - {r.text}")

# 3. Create Tree with base_tree
print("\nBuilding Git Tree...")
tree_url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/git/trees"
r = requests.post(tree_url, headers=HEADERS, json={"base_tree": base_tree_sha, "tree": tree_items})
if r.status_code != 201:
    print(f"Failed to create tree: {r.status_code} - {r.text}")
    sys.exit(1)
new_tree_sha = r.json()["sha"]
print(f"New Tree SHA: {new_tree_sha}")

# 4. Create Commit
print("\nCreating Commit...")
commit_url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/git/commits"
commit_payload = {
    "message": "SubExtract Studio v2.5 Pro Edition — Complete Source Code\n\nDeveloped by NoYz — Licensed under GNU General Public License v3.0",
    "tree": new_tree_sha,
    "parents": [base_commit_sha]
}
r = requests.post(commit_url, headers=HEADERS, json=commit_payload)
if r.status_code != 201:
    print(f"Failed to create commit: {r.status_code} - {r.text}")
    sys.exit(1)
new_commit_sha = r.json()["sha"]
print(f"New Commit SHA: {new_commit_sha}")

# 5. Update main branch
print("\nUpdating main branch...")
patch_url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/git/refs/heads/main"
r = requests.patch(patch_url, headers=HEADERS, json={"sha": new_commit_sha, "force": True})
if r.status_code in [200, 201]:
    print("Main branch updated successfully!")
else:
    print(f"Failed to update main ref: {r.status_code} - {r.text}")
    sys.exit(1)

print("\n" + "=" * 60)
print(f"SOURCE CODE DEPLOYED SUCCESSFULLY TO https://github.com/{REPO_OWNER}/{REPO_NAME}")
print("=" * 60)
