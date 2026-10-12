#!/usr/bin/env python3
"""Inventory file metadata only; do not follow symlinks or run target code."""
import argparse
import json
import os
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_EXCLUDES = {".git", "node_modules", ".venv", "venv", "__pycache__", "bin", "obj", ".audit", "audit-output"}
TOOLS = ("git", "semgrep", "gitleaks", "trivy", "codeql", "dotnet", "npm", "pip-audit")

def git_metadata(root):
    result = {}
    for key, args in (("commit", ["rev-parse", "HEAD"]), ("working_tree", ["status", "--porcelain", "--untracked-files=normal"]), ("shallow", ["rev-parse", "--is-shallow-repository"])):
        try:
            proc = subprocess.run(["git", "--no-optional-locks", "-c", "core.fsmonitor=false", "-C", str(root), *args], capture_output=True, text=True, timeout=15)
            # Never emit stderr: Git configuration/remote URLs may contain credentials.
            result[key] = proc.stdout.strip() if proc.returncode == 0 else None
        except (OSError, subprocess.TimeoutExpired):
            result[key] = None
    return result

def collect(root, excludes=None, output=None):
    root = Path(root).expanduser().resolve()
    if not root.is_dir():
        raise ValueError("Target root must be an existing directory")
    excluded_names = DEFAULT_EXCLUDES | set(excludes or [])
    output = Path(output).resolve() if output else None
    files, skipped, errors = [], [], []
    indicators = set()
    def error(exc):
        errors.append({"path": str(exc.filename), "error": type(exc).__name__})
    for current, dirs, names in os.walk(root, followlinks=False, onerror=error):
        base = Path(current)
        kept = []
        for name in sorted(dirs):
            path = base / name
            reason = "symlink" if path.is_symlink() else ("excluded-directory" if name in excluded_names else None)
            if reason:
                skipped.append({"path": path.relative_to(root).as_posix(), "reason": reason})
            else:
                kept.append(name)
        dirs[:] = kept
        for name in sorted(names):
            path = base / name
            rel = path.relative_to(root).as_posix()
            if path.is_symlink():
                skipped.append({"path": rel, "reason": "symlink"}); continue
            if output and path == output:
                skipped.append({"path": rel, "reason": "inventory-output"}); continue
            try:
                stat = path.stat(follow_symlinks=False)
                import stat as stat_module
                if not stat_module.S_ISREG(stat.st_mode):
                    skipped.append({"path": rel, "reason": "non-regular-file"}); continue
                files.append({"path": rel, "size_bytes": stat.st_size})
            except OSError as exc:
                error(exc); continue
            if path.suffix in {".csproj", ".sln", ".fsproj"}: indicators.add("dotnet")
            if name in {"package.json", "package-lock.json", "pnpm-lock.yaml", "yarn.lock"}: indicators.add("javascript-typescript")
            if name in {"pyproject.toml", "requirements.txt", "Pipfile.lock", "uv.lock"}: indicators.add("python")
            if name == "go.mod": indicators.add("go")
            if name == "Cargo.toml": indicators.add("rust")
            if name in {"pom.xml", "build.gradle", "build.gradle.kts"}: indicators.add("jvm")
            if name == "Dockerfile" or path.suffix in {".tf", ".bicep"}: indicators.add("infrastructure")
    return {"schema_version": "1.0", "utc_time": datetime.now(timezone.utc).isoformat(), "root": str(root), "git": git_metadata(root), "stack_indicators": sorted(indicators), "tools_available": {name: shutil.which(name) is not None for name in TOOLS}, "excluded_directory_names": sorted(excluded_names), "files": files, "skipped": skipped, "errors": errors, "limitations": ["Metadata inventory only; no source review or vulnerability detection.", "Excluded and symlink paths need separate scope decisions.", "No detection of Git LFS availability or effective deployed configuration."]}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--exclude-dir", action="append", default=[])
    args = parser.parse_args()
    try:
        output = Path(args.output).expanduser().resolve()
        if output.exists():
            raise ValueError("Output already exists; choose a new inventory filename")
        data = collect(args.root, args.exclude_dir, output)
        output.parent.mkdir(parents=True, exist_ok=True)
        with output.open("x", encoding="utf-8") as stream:
            json.dump(data, stream, indent=2); stream.write("\n")
        print(f"Inventoried {len(data['files'])} files; skipped {len(data['skipped'])}; errors {len(data['errors'])}")
    except (OSError, ValueError) as exc:
        parser.exit(2, "Inventory failed: " + str(exc) + "\n")

if __name__ == "__main__":
    main()
