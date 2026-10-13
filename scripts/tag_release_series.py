#!/usr/bin/env python3
"""Tag verified release-boundary commits; refuse existing tags pointing elsewhere."""
import argparse
import json
import re
import subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def git(*args):
    return subprocess.run(['git',*args],cwd=ROOT,check=True,capture_output=True,text=True).stdout.strip()


def plan():
    series=json.loads((ROOT/'docs/release-series.json').read_text())
    base=series['base_commit'];git('merge-base','--is-ancestor',base,'HEAD')
    commits=[line.split('\t',1) for line in git('log','--format=%H%x09%s',base+'..HEAD').splitlines()]
    tags=[]
    for release in series['releases']:
        version=release['version']
        if not re.fullmatch(r'\d+\.\d+\.\d+(?:-rc\.\d+)?',version):raise ValueError('Invalid release version')
        matches=[sha for sha,message in commits if message==release['boundary_commit_message']]
        if len(matches)!=1:raise ValueError('Release boundary must have exactly one matching commit')
        sha=matches[0]
        plugin=json.loads(git('show',sha+':plugins/security-audit/.claude-plugin/plugin.json'))
        marketplace=json.loads(git('show',sha+':.claude-plugin/marketplace.json'))
        if plugin['version']!=version or marketplace['plugins'][0]['version']!=version:raise ValueError('Boundary manifest version mismatch')
        tag='v'+version
        existing=subprocess.run(['git','rev-parse','--verify','refs/tags/'+tag+'^{commit}'],cwd=ROOT,capture_output=True,text=True)
        if existing.returncode==0 and existing.stdout.strip()!=sha:raise ValueError('Refusing to move existing tag '+tag)
        tags.append({'tag':tag,'sha':sha,'exists':existing.returncode==0})
    return tags


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--publish',action='store_true');args=parser.parse_args()
    try:
        tags=plan()
        for row in tags:
            if args.publish and not row['exists']:git('tag',row['tag'],row['sha'])
        if args.publish:git('push','origin',*('refs/tags/'+row['tag'] for row in tags))
        print(json.dumps(tags,indent=2))
    except (OSError,ValueError,subprocess.CalledProcessError) as exc:parser.exit(2,'Release tags blocked: '+str(exc)+'\n')

if __name__=='__main__':main()
