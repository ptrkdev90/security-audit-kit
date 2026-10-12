#!/usr/bin/env python3
"""Migrate into a new directory using explicit manually reviewed replacement records."""
import argparse
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from validate_audit import validate, schema_errors, SCHEMAS

REPLACEMENTS={'findings':'findings.json','evidence':'evidence.json','audit-plan':'audit-plan.json','architecture':'architecture.json','report-source':'report-source.json','report-metadata':'report-metadata.json'}


def migrate(source,output,review):
    source=Path(source).resolve(strict=True);output=Path(output).resolve()
    if not source.is_dir() or output==source or output.is_relative_to(source):raise ValueError('Choose a new directory outside the source audit')
    if output.exists():raise FileExistsError('Migration output exists')
    if not isinstance(review,dict) or set(review)!={'reviewed_by','reason',*REPLACEMENTS}:raise ValueError('Explicit complete review contract required')
    if not isinstance(review['reviewed_by'],str) or not review['reviewed_by'].strip() or not isinstance(review['reason'],str) or not review['reason'].strip():raise ValueError('Reviewer identity and migration reason required')
    for name in REPLACEMENTS:
        schema=json.loads((SCHEMAS/(name+'.schema.json')).read_text())
        if schema_errors(review[name],schema,name):raise ValueError('Invalid reviewed '+name)
    if review['findings']['schema_version']!='1.2':raise ValueError('Reviewed findings must use 1.2')
    if review['report-metadata']['signature']['status']!='unsigned':raise ValueError('Migrated report must be unsigned; re-sign only through an authorized workflow')
    original=json.loads((source/'findings.json').read_text(encoding='utf-8'))
    before=[r['id'] for r in original['items']];after=[r['id'] for r in review['findings']['items']]
    if len(before)!=len(set(before)) or len(after)!=len(set(after)) or set(before)!=set(after):raise ValueError('Preserve original finding IDs; document new findings in a separate audit revision')
    previous_meta=source/'report-metadata.json'
    if previous_meta.exists():
        if previous_meta.is_symlink():raise ValueError('Symlink source metadata')
        metadata=json.loads(previous_meta.read_text())
        if metadata.get('report_id') and metadata['report_id']!=review['report-metadata']['report_id']:raise ValueError('Preserve report identity')
        if metadata.get('report_version')==review['report-metadata']['report_version']:raise ValueError('Increment report version for migration')
    files=[]
    for path in source.rglob('*'):
        if path.is_symlink():raise ValueError('Symlinks cannot be migrated')
        if path.is_file():files.append(path)
        elif not path.is_dir():raise ValueError('Only regular source artifacts can be migrated')
    source_hashes={p.relative_to(source).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
    output.mkdir(parents=True,exist_ok=False)
    # Preserve originals verbatim in a dedicated provenance directory.
    original_output=output/'previous-version';shutil.copytree(source,original_output)
    for name in ('inventory.json','scope.md','threat-model.md','report.md','checkpoint.md','coverage.json','tool-runs.json','compliance-matrix.csv'):
        path=source/name
        if path.is_file():shutil.copyfile(path,output/name)
    for key,filename in REPLACEMENTS.items():
        (output/filename).write_text(json.dumps(review[key],indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    record={'schema_version':'1.0','migrated_at':datetime.now(timezone.utc).isoformat(),'reviewed_by':review['reviewed_by'],'reason':review['reason'],'source_sha256':source_hashes,'limits':['Manual replacement records, not automated classification or factual verification','Old signatures/approvals do not apply to the migrated document']}
    (output/'migration.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
    errors=validate(output,final=True)
    if errors:raise ValueError('Migrated draft retained for review; validation failed: '+'; '.join(errors))
    return output


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('source');parser.add_argument('--output',required=True);parser.add_argument('--review-file',required=True);args=parser.parse_args()
    try:print(migrate(args.source,args.output,json.loads(Path(args.review_file).read_text(encoding='utf-8'))))
    except (OSError,ValueError,KeyError,TypeError) as exc:parser.exit(2,'Migration failed: '+str(exc)+'\n')

if __name__=='__main__':main()
