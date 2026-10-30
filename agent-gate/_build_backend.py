"""Minimal standard-library build backend for this pure-Python package."""

import base64
import csv
import hashlib
import io
from pathlib import Path
import tarfile
import tomllib
import zipfile


ROOT = Path(__file__).parent
PROJECT = tomllib.loads((ROOT / "pyproject.toml").read_text())["project"]
STEM = f"agent_gate-{PROJECT['version']}"
METADATA = (
    f"Metadata-Version: 2.1\nName: {PROJECT['name']}\n"
    f"Version: {PROJECT['version']}\nSummary: {PROJECT['description']}\n"
    f"Requires-Python: {PROJECT['requires-python']}\n\n"
).encode()


def build_wheel(wheel_directory, config_settings=None, metadata_directory=None):
    filename = f"{STEM}-py3-none-any.whl"
    info = f"{STEM}.dist-info"
    files = {
        str(path.relative_to(ROOT / "src")): path.read_bytes()
        for path in sorted((ROOT / "src" / "agent_gate").glob("*.py"))
    }
    files[f"{info}/METADATA"] = METADATA
    files[f"{info}/WHEEL"] = (
        "Wheel-Version: 1.0\nGenerator: agent-gate\n"
        "Root-Is-Purelib: true\nTag: py3-none-any\n"
    ).encode()
    files[f"{info}/entry_points.txt"] = (
        "[console_scripts]\n"
        + "".join(f"{name} = {entry}\n" for name, entry in PROJECT["scripts"].items())
    ).encode()
    record = io.StringIO(newline="")
    writer = csv.writer(record)
    for name, content in files.items():
        digest = base64.urlsafe_b64encode(hashlib.sha256(content).digest()).rstrip(b"=")
        writer.writerow([name, f"sha256={digest.decode()}", len(content)])
    writer.writerow([f"{info}/RECORD", "", ""])
    files[f"{info}/RECORD"] = record.getvalue().encode()
    with zipfile.ZipFile(Path(wheel_directory) / filename, "w", zipfile.ZIP_DEFLATED) as wheel:
        for name, content in files.items():
            wheel.writestr(name, content)
    return filename


def build_sdist(sdist_directory, config_settings=None):
    filename = f"{STEM}.tar.gz"
    paths = [ROOT / name for name in ("pyproject.toml", "_build_backend.py", "README.md")]
    for directory in ("src", "tests", "examples", ".github"):
        paths.extend(
            path for path in (ROOT / directory).rglob("*")
            if path.is_file() and "__pycache__" not in path.parts
        )
    with tarfile.open(Path(sdist_directory) / filename, "w:gz") as archive:
        for path in sorted(paths):
            archive.add(path, arcname=f"{STEM}/{path.relative_to(ROOT)}")
        metadata = tarfile.TarInfo(f"{STEM}/PKG-INFO")
        metadata.size = len(METADATA)
        archive.addfile(metadata, io.BytesIO(METADATA))
    return filename
