#!/usr/bin/env python3
"""Fingerprint explicitly allowed files and conservatively plan audit resumption."""
import argparse
import hashlib
import json
import os
import stat
from datetime import datetime, timezone, timedelta
from pathlib import Path, PurePosixPath
from inventory import git_metadata


def digest_file(root, relative):
    rel = PurePosixPath(relative)
    if not relative or rel.is_absolute() or any(p in {'', '.', '..', '.git'} for p in rel.parts) or '\\' in relative or ':' in relative:
        raise ValueError('Expected a safe relative path')
    if any(p.startswith('.env') or p.lower().endswith(('.pem', '.key', '.pfx', '.p12')) for p in rel.parts):
        raise ValueError('Credential file excluded from fingerprinting')
    path = root.joinpath(*rel.parts)
    for part in (path, *path.parents):
        if part == root: break
        if part.is_symlink(): raise ValueError('Symlink paths cannot be fingerprinted')
    if not path.exists(): return None
    # Directory-relative no-follow opens also reject a parent swap during traversal.
    if os.open in os.supports_dir_fd and hasattr(os, 'O_NOFOLLOW'):
        fd = os.open(root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        try:
            for component in rel.parts[:-1]:
                child = os.open(component, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
                os.close(fd); fd = child
            file_fd = os.open(rel.parts[-1], os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=fd)
        finally:
            os.close(fd)
    else:
        file_fd = os.open(path, os.O_RDONLY | getattr(os, 'O_NOFOLLOW', 0) | getattr(os, 'O_NONBLOCK', 0))
    try:
        if not stat.S_ISREG(os.fstat(file_fd).st_mode): raise ValueError('Only regular files can be fingerprinted')
        digest = hashlib.sha256()
        while True:
            block = os.read(file_fd, 1024 * 1024)
            if not block: break
            digest.update(block)
        return digest.hexdigest()
    finally:
        os.close(file_fd)


def capture(root, paths, context):
    root = Path(root).resolve(strict=True)
    if not root.is_dir() or not paths: raise ValueError('Root and nonempty explicit allowlist required')
    if len(paths) != len(set(paths)): raise ValueError('Duplicate allowlist paths')
    serialized = json.dumps(context, sort_keys=True, separators=(',', ':'), ensure_ascii=False)
    return {'schema_version': '1.0', 'captured_at': datetime.now(timezone.utc).isoformat(),
            'root': str(root), 'git': git_metadata(root),
            'context_sha256': hashlib.sha256(serialized.encode()).hexdigest(),
            'helper_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'files': {p: digest_file(root, p) for p in sorted(paths)},
            'limitations': ['Allowlisted content only; omitted files and external state are unverified.',
                            'Hashes identify content; they do not validate security or secrets.',
                            'Platforms without directory-relative no-follow opens require a stable isolated target.']}


def compare(previous, current, max_age_hours=24):
    if max_age_hours <= 0: raise ValueError('Positive maximum age required')
    changes = sorted(p for p in set(previous['files']) | set(current['files']) if previous['files'].get(p) != current['files'].get(p))
    reasons = []
    for key in ('root', 'git', 'context_sha256', 'helper_sha256'):
        if previous.get(key) != current.get(key): reasons.append(key + ' changed')
    try:
        captured = datetime.fromisoformat(previous['captured_at'].replace('Z', '+00:00'))
        now = datetime.fromisoformat(current['captured_at'].replace('Z', '+00:00'))
        if captured.tzinfo is None or now.tzinfo is None: raise ValueError()
        if now < captured or now - captured > timedelta(hours=max_age_hours): reasons.append('Baseline time invalid or expired')
    except (ValueError, TypeError, KeyError): reasons.append('Unknown baseline age')
    missing = sorted(p for p, digest in current['files'].items() if digest is None)
    if missing: reasons.append('Allowlisted files missing')
    if changes: reasons.append('Content changed; inspect callers, shared defenses and dependent flows')
    return {'schema_version': '1.0', 'changed_paths': changes, 'missing_paths': missing,
            'requires_review': bool(reasons), 'reasons': reasons,
            'reuse_decision': 'invalidated' if reasons else 'eligible-for-manual-review',
            'limitations': ['No automatic coverage promotion. External deployment and feeds must be rechecked.']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', required=True); parser.add_argument('--allowlist', required=True)
    parser.add_argument('--context', required=True); parser.add_argument('--output', required=True)
    parser.add_argument('--previous'); parser.add_argument('--max-age-hours', type=float, default=24)
    args = parser.parse_args()
    try:
        paths = json.loads(Path(args.allowlist).read_text(encoding='utf-8'))
        if not isinstance(paths, list) or not all(isinstance(p, str) for p in paths): raise ValueError('Allowlist must be a string array')
        context = json.loads(Path(args.context).read_text(encoding='utf-8'))
        current = capture(args.root, paths, context)
        result = {'snapshot': current, 'resume': compare(json.loads(Path(args.previous).read_text(encoding='utf-8'))['snapshot'], current, args.max_age_hours) if args.previous else None}
        with Path(args.output).open('x', encoding='utf-8') as out: json.dump(result, out, indent=2); out.write('\n')
    except (OSError, ValueError, KeyError, TypeError) as exc:
        parser.exit(2, 'Checkpoint failed: ' + type(exc).__name__ + '\n')

if __name__ == '__main__': main()
