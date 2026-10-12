#!/usr/bin/env python3
"""Opt-in install/update smoke check in a fresh CLAUDE_CONFIG_DIR; no model calls."""
import argparse
import json
import os
import shutil
import subprocess
import tempfile
from datetime import datetime,timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',required=True);args=parser.parse_args()
    executable=shutil.which('claude')
    if not executable:parser.exit(77,'Claude Code unavailable; host smoke test not performed.\n')
    output=Path(args.output)
    if output.exists():parser.exit(2,'Output exists; choose a new receipt path.\n')
    expected=json.loads((ROOT/'plugins/security-audit/.claude-plugin/plugin.json').read_text())['version']
    commands=[['--version'],['plugin','validate',str(ROOT)],['plugin','validate',str(ROOT/'plugins/security-audit')],['plugin','marketplace','add',str(ROOT)],['plugin','install','security-audit@security-audit-kit'],['plugin','marketplace','update','security-audit-kit'],['plugin','update','security-audit@security-audit-kit'],['plugin','list']]
    results=[]
    with tempfile.TemporaryDirectory(prefix='audit-plugin-smoke-') as config:
        env=dict(os.environ,CLAUDE_CONFIG_DIR=config,CI='true')
        # No credential/store reuse is needed for local plugin bookkeeping.
        for key in ('ANTHROPIC_API_KEY','ANTHROPIC_AUTH_TOKEN','CLAUDE_CODE_OAUTH_TOKEN'):
            env.pop(key,None)
        try:
            for command in commands:
                result=subprocess.run([executable,*command],cwd=ROOT,env=env,capture_output=True,text=True,timeout=120)
                # Isolated bookkeeping only; record outcomes without unrestricted logs.
                results.append({'command':['claude',*command],'exit_code':result.returncode})
                if result.returncode!=0:raise RuntimeError('Host command failed: '+' '.join(command))
                if command==['plugin','list'] and ('security-audit' not in result.stdout or expected not in result.stdout):raise RuntimeError('Installed plugin name/version not shown in listing')
        except (OSError,subprocess.TimeoutExpired,RuntimeError) as exc:
            receipt={'status':'failed','expected_version':expected,'commands':results,'limitation':str(exc)}
        else:receipt={'status':'passed','expected_version':expected,'commands':results,'limitations':['Local-path installation/update only; public GitHub transport and active-session reload need separate verification.','No model calls or real Claude audit behavior tested.']}
    receipt['checked_at']=datetime.now(timezone.utc).isoformat()
    with output.open('x',encoding='utf-8') as stream:json.dump(receipt,stream,indent=2);stream.write('\n')
    print('Claude smoke check: '+receipt['status'])
    raise SystemExit(0 if receipt['status']=='passed' else 1)

if __name__=='__main__':main()
