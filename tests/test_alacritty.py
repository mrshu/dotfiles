import contextlib
import copy
import hashlib
import io
import json
from pathlib import Path
import plistlib
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from scripts import install_alacritty as alacritty


def make_app(path, version="0.17.0", identifier="org.alacritty"):
    (path / "Contents/MacOS").mkdir(parents=True)
    (path / "Contents/MacOS/alacritty").write_text(version)
    with (path / "Contents/Info.plist").open("wb") as stream:
        plistlib.dump({
            "CFBundleIdentifier": identifier,
            "CFBundleShortVersionString": version,
        }, stream)
    return path


class ReleaseValidationTests(unittest.TestCase):
    def setUp(self):
        self.asset_url = (
            "https://github.com/alacritty/alacritty/releases/download/"
            "v0.17.0/Alacritty-v0.17.0.dmg"
        )
        self.metadata = {
            "tag_name": "v0.17.0", "draft": False, "prerelease": False,
            "assets": [{
                "name": "Alacritty-v0.17.0.dmg",
                "browser_download_url": self.asset_url,
                "digest": "sha256:" + "a" * 64,
            }],
        }

    def latest(self, metadata):
        with patch.object(alacritty, "read_url", return_value=io.BytesIO(
            json.dumps(metadata).encode()
        )) as read_url:
            result = alacritty.latest_release()
        read_url.assert_called_once_with(alacritty.RELEASE_API)
        return result

    def test_official_metadata_provides_version_url_and_digest(self):
        self.assertEqual(self.latest(self.metadata), {
            "version": "0.17.0", "url": self.asset_url, "sha256": "a" * 64,
        })

    def test_changed_download_origin_or_missing_digest_is_rejected(self):
        for key, value in (
            ("browser_download_url", "https://example.org/Alacritty.dmg"),
            ("browser_download_url", self.asset_url.replace("alacritty/alacritty", "other/alacritty")),
            ("digest", None),
            ("digest", "sha256:" + "a" * 63),
            ("digest", "sha512:" + "a" * 64),
        ):
            with self.subTest(key=key, value=value):
                metadata = copy.deepcopy(self.metadata)
                metadata["assets"][0][key] = value
                with self.assertRaises(ValueError):
                    self.latest(metadata)

    def test_unstable_or_missing_macos_releases_are_rejected(self):
        for changes in (
            {"draft": True}, {"prerelease": True}, {"tag_name": "v0.17.0-rc1"},
            {"assets": []},
        ):
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                self.latest(dict(self.metadata, **changes))

    def test_download_requires_matching_checksum(self):
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory) / "release.dmg"
            payload = b"official disk image content"
            release = {"url": self.asset_url, "sha256": hashlib.sha256(payload).hexdigest()}
            with patch.object(alacritty, "read_url", return_value=io.BytesIO(payload)):
                alacritty.download(release, destination)
            self.assertEqual(destination.read_bytes(), payload)
            with (
                patch.object(alacritty, "read_url", return_value=io.BytesIO(b"modified")),
                self.assertRaisesRegex(ValueError, "SHA256"),
            ):
                alacritty.download(release, destination)


class InstallationSafetyTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.app = make_app(self.root / "Applications/Alacritty.app", "0.16.0")
        self.source = make_app(self.root / "release/Alacritty.app")
        self.prefix = self.root / "prefix"
        self.receipt = self.root / "state/alacritty.json"
        self.receipt.parent.mkdir()
        self.receipt.write_text('{"old": true}\n')
        self.release = {"version": "0.17.0", "url": "https://example.invalid/release", "sha256": "a" * 64}
        self.calls = []
        self.failure_command = None
        self.fail_after_uninstall = False
        self.destination = self.prefix / "bin/alacritty"

        @contextlib.contextmanager
        def mounted_image(*args):
            yield self.source

        def run(command, **kwargs):
            self.calls.append(command)
            if command[0] == self.failure_command:
                raise subprocess.CalledProcessError(1, command)
            if command[0] == "ditto":
                shutil.copytree(command[1], command[2])
            elif command[:3] == ["brew", "uninstall", "--cask"]:
                if self.app.exists():
                    shutil.rmtree(self.app)
                if self.fail_after_uninstall:
                    raise subprocess.CalledProcessError(1, command)
            return subprocess.CompletedProcess(command, 1 if command[0] == "pgrep" else 0)

        def integrations(app, prefix):
            return [(app / "Contents/MacOS/alacritty", self.destination)]

        self.stack = contextlib.ExitStack()
        self.addCleanup(self.stack.close)
        self.stack.enter_context(patch.object(alacritty, "mounted_image", mounted_image))
        self.stack.enter_context(patch.object(alacritty, "download"))
        self.stack.enter_context(patch.object(alacritty.subprocess, "run", side_effect=run))
        self.stack.enter_context(patch.object(alacritty, "integrations", side_effect=integrations))
        self.stack.enter_context(contextlib.redirect_stdout(io.StringIO()))

    def install(self, casks=frozenset({"alacritty"})):
        alacritty.install_release(self.release, self.app, self.receipt, self.prefix, casks)

    def assert_old_installation_preserved(self):
        self.assertEqual(alacritty.app_version(self.app), "0.16.0")
        self.assertEqual((self.app / "Contents/MacOS/alacritty").read_text(), "0.16.0")
        self.assertEqual(json.loads(self.receipt.read_text()), {"old": True})

    def assert_not_uninstalled(self):
        self.assertFalse(any(command[0] == "brew" for command in self.calls))
        self.assert_old_installation_preserved()

    def test_wrong_bundle_or_version_is_rejected_before_uninstall(self):
        for identifier, version in (("org.other", "0.17.0"), ("org.alacritty", "0.18.0")):
            with self.subTest(identifier=identifier, version=version):
                shutil.rmtree(self.source)
                make_app(self.source, version, identifier)
                with self.assertRaises(ValueError):
                    self.install()
                self.assert_not_uninstalled()

    def test_existing_integration_file_is_preserved_before_uninstall(self):
        self.destination.parent.mkdir(parents=True)
        self.destination.write_text("another terminal")
        with self.assertRaisesRegex(ValueError, "existing file"):
            self.install()
        self.assertEqual(self.destination.read_text(), "another terminal")
        self.assert_not_uninstalled()

    def test_unrelated_symlink_is_preserved_before_uninstall(self):
        self.destination.parent.mkdir(parents=True)
        target = self.root / "other-terminal"
        target.write_text("unrelated")
        self.destination.symlink_to(target)
        with self.assertRaisesRegex(ValueError, "unrelated symlink"):
            self.install()
        self.assertEqual(self.destination.readlink(), target)
        self.assert_not_uninstalled()

    def test_symlink_to_wrong_resource_in_same_app_is_rejected(self):
        self.destination.parent.mkdir(parents=True)
        target = self.app / "Contents/Info.plist"
        self.destination.symlink_to(target)
        with self.assertRaisesRegex(ValueError, "unrelated symlink"):
            self.install()
        self.assertEqual(self.destination.readlink(), target)
        self.assert_not_uninstalled()

    def test_missing_bundle_resource_is_rejected_before_uninstall(self):
        (self.source / "Contents/MacOS/alacritty").unlink()
        with self.assertRaisesRegex(ValueError, "missing"):
            self.install()
        self.assert_not_uninstalled()

    def test_quarantine_failure_leaves_previous_installation(self):
        self.failure_command = "xattr"
        with self.assertRaises(subprocess.CalledProcessError):
            self.install()
        self.assert_not_uninstalled()

    def test_brew_uninstall_failure_restores_previous_installation(self):
        self.failure_command = "brew"
        with self.assertRaises(subprocess.CalledProcessError):
            self.install()
        self.assert_old_installation_preserved()
        self.assertFalse(self.destination.exists())

    def test_partial_brew_uninstall_failure_restores_previous_installation(self):
        self.fail_after_uninstall = True
        with self.assertRaises(subprocess.CalledProcessError):
            self.install()
        self.assert_old_installation_preserved()

    def test_integration_failure_restores_previous_installation(self):
        with (
            patch.object(Path, "symlink_to", side_effect=OSError("integration failed")),
            self.assertRaisesRegex(OSError, "integration failed"),
        ):
            self.install()
        self.assert_old_installation_preserved()
        self.assertFalse(self.destination.exists())

    def test_receipt_failure_rolls_back_app_and_new_links(self):
        original_replace = Path.replace

        def replace(path, target):
            if target == self.receipt:
                raise OSError("receipt failed")
            return original_replace(path, target)

        with (
            patch.object(Path, "replace", replace),
            self.assertRaisesRegex(OSError, "receipt failed"),
        ):
            self.install()
        self.assert_old_installation_preserved()
        self.assertFalse(self.destination.is_symlink())

    def test_install_adds_quarantine_and_records_verified_release(self):
        self.install()
        self.assertEqual(alacritty.app_version(self.app), "0.17.0")
        self.assertEqual(self.destination.resolve(), (self.app / "Contents/MacOS/alacritty").resolve())
        self.assertEqual(json.loads(self.receipt.read_text()), self.release)
        commands = [command for command in self.calls if command[0] == "xattr"]
        self.assertEqual(len(commands), 1)
        self.assertEqual(commands[0][:3], ["xattr", "-w", "com.apple.quarantine"])
        self.assertTrue(commands[0][3].startswith("0083;"))

    def test_existing_link_to_app_is_accepted(self):
        self.destination.parent.mkdir(parents=True)
        self.destination.symlink_to(self.app / "Contents/MacOS/alacritty")
        self.install()
        self.assertEqual(self.destination.resolve().read_text(), "0.17.0")


class InstallerStatusTests(unittest.TestCase):
    def test_same_version_and_verified_receipt_are_a_noop(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            app = make_app(root / "Alacritty.app")
            release = {"version": "0.17.0", "sha256": "a" * 64}
            receipt = root / "receipt.json"
            receipt.write_text(json.dumps(release))
            with (
                patch.object(alacritty.sys, "platform", "darwin"),
                patch.object(alacritty, "APP", app),
                patch.object(alacritty, "RECEIPT", receipt),
                patch.object(alacritty, "latest_release", return_value=release),
                patch.object(alacritty.subprocess, "check_output", return_value="flameshot 14.0.0\n"),
                patch.object(alacritty, "install_release") as install,
                contextlib.redirect_stdout(io.StringIO()),
            ):
                alacritty.main([])
            install.assert_not_called()


if __name__ == "__main__":
    unittest.main()
