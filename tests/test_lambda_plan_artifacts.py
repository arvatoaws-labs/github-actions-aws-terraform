"""Exercise embedded workflow scripts without AWS or OpenTofu execution."""
import contextlib
import hashlib
import io
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import zipfile

import yaml


WORKFLOWS = Path(__file__).resolve().parents[1] / '.github/workflows'


def script(filename, step_name):
    workflow = yaml.safe_load((WORKFLOWS / filename).read_text())
    steps = workflow['jobs']['tofu']['steps']
    run = next(step['run'] for step in steps if step.get('name') == step_name)
    return run.split("python3 - <<'PY'\n", 1)[1].split('\nPY', 1)[0]


SAVE = script('githubaction-comment-plan.yml', 'Upload ${{ inputs.stack }} Plan to S3')
RESTORE = script('githubaction-comment-apply.yml', 'Restore Lambda packages from plan')


class LambdaArtifactsTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.previous = Path.cwd()
        os.chdir(self.temp.name)
        self.addCleanup(self.temp.cleanup)
        self.addCleanup(os.chdir, self.previous)
        Path('tfplan').write_bytes(b'test saved plan')
        self.files = {
            '.terraform/modules/contao/update.zip': b'original update archive',
            '.terraform/modules/another/lambda.zip': b'original legacy archive',
        }
        for name, data in self.files.items():
            path = Path(name)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
        self.plan = {'resource_changes': [
            {'mode': 'managed', 'type': 'aws_lambda_function', 'address': name,
             'change': {'actions': ['update'], 'after': {'filename': name}}}
            for name in self.files
        ]}
        self.plan['resource_changes'].append({
            'mode': 'managed', 'type': 'aws_lambda_function', 'address': 'image_lambda',
            'change': {'actions': ['create'], 'after': {'image_uri': 'test:latest'}},
        })

    def execute(self, source):
        with contextlib.redirect_stdout(io.StringIO()):
            exec(compile(source, '<workflow>', 'exec'), {})

    def save(self):
        with patch('subprocess.check_output', return_value=json.dumps(self.plan).encode()) as command:
            self.execute(SAVE)
            command.assert_called_once_with(['tofu', 'show', '-json', 'tfplan'])

    def test_exact_packages_restore_after_deletion_and_rebuild(self):
        self.save()
        for name in self.files:
            Path(name).unlink()
        Path('.terraform/modules/another/lambda.zip').write_bytes(b'incorrect rebuilt bytes')
        self.execute(RESTORE)
        for name, data in self.files.items():
            self.assertEqual(Path(name).read_bytes(), data)

    def test_changed_plan_fails(self):
        self.save()
        Path('tfplan').write_bytes(b'different plan')
        with self.assertRaisesRegex(SystemExit, 'do not match'):
            self.execute(RESTORE)

    def test_missing_planned_package_fails(self):
        Path(next(iter(self.files))).unlink()
        with self.assertRaisesRegex(SystemExit, 'Missing or out-of-stack'):
            self.save()

    def test_empty_bundle_is_supported(self):
        self.plan = {'resource_changes': []}
        self.save()
        self.execute(RESTORE)

    def invalid_bundle(self, name, expected_hash):
        manifest = {
            'plan_sha256': hashlib.sha256(Path('tfplan').read_bytes()).hexdigest(),
            'files': {name: expected_hash},
        }
        with zipfile.ZipFile('lambda-plan-artifacts.zip', 'w') as bundle:
            bundle.writestr('manifest.json', json.dumps(manifest))
            bundle.writestr(name, b'bad archive')

    def test_traversal_fails(self):
        self.invalid_bundle('../outside.zip', 'unused')
        with self.assertRaisesRegex(SystemExit, 'Unsafe'):
            self.execute(RESTORE)

    def test_checksum_mismatch_fails_without_overwriting(self):
        name = next(iter(self.files))
        self.invalid_bundle(name, 'incorrect hash')
        with self.assertRaisesRegex(SystemExit, 'checksum mismatch'):
            self.execute(RESTORE)
        self.assertEqual(Path(name).read_bytes(), self.files[name])


if __name__ == '__main__':
    unittest.main()
