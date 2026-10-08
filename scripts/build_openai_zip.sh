#!/bin/sh
# Rebuild dist/clawmaven-openai-<version>.zip and the listing icon from openai/.
# Runs the packaging tests first, then audits the ZIP that will be uploaded.
set -eu
cd "$(dirname "$0")/.."
python3 -m unittest discover -s scripts -p 'test_*.py'
python3 scripts/package_openai.py --replace
cp openai/assets/logo.png dist/clawmaven-openai-icon.png
PYTHONPATH=scripts python3 -m unittest -v test_package_openai.SubmissionAuditTests.test_submission_zip_in_dist_is_clean
