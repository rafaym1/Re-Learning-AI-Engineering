"""Assemble a self-contained, deployable bundle for the Hugging Face Space.

HF Spaces need a flat repo with app.py at the root and the packages it imports alongside it.
Rather than hand-maintaining a second copy of fdi/, this script copies the current source of
truth (fdi/, the pre-built vector index, and the space/ config files) into space/dist/ -- a
disposable build artifact, not something to edit directly or commit.

Run from the "Financial Document Intelligence" directory: python space/build_space.py
"""

import shutil
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
SPACE_DIR = ROOT / "space"
DIST_DIR = SPACE_DIR / "dist"

FDI_MODULES = [
    "vector_store.py",
    "embeddings.py",
    "reranker.py",
    "verification.py",
    "numbers.py",
    "rate_limit.py",
    "__init__.py",
]


def main():
    if DIST_DIR.exists():
        shutil.rmtree(DIST_DIR)
    DIST_DIR.mkdir(parents=True)

    fdi_dist = DIST_DIR / "fdi"
    fdi_dist.mkdir()
    for name in FDI_MODULES:
        shutil.copy2(ROOT / "fdi" / name, fdi_dist / name)

    index_dist = DIST_DIR / "data" / "vector_index"
    index_dist.mkdir(parents=True)
    for path in (ROOT / "data" / "vector_index").iterdir():
        if path.name == "embeddings.npy":
            # Stored as float64, far more precision than cosine similarity needs -- float16
            # keeps retrieval quality (confirmed: identical top-10 rankings) while cutting the
            # file to a quarter of its size, which matters for browser-based upload limits.
            embeddings = np.load(path).astype(np.float16)
            np.save(index_dist / path.name, embeddings)
        else:
            shutil.copy2(path, index_dist / path.name)

    for name in ("app.py", "llm.py", "requirements.txt", "README.md"):
        shutil.copy2(SPACE_DIR / name, DIST_DIR / name)

    print(f"Bundle assembled at {DIST_DIR}")
    print("Next: cd into it, git init (or add as a remote), and push to your Hugging Face Space.")


if __name__ == "__main__":
    main()
