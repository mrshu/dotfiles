import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

import install


class PackageInstallationTests(unittest.TestCase):
    def test_fresh_homebrew_can_create_missing_tap_directories(self):
        with tempfile.TemporaryDirectory(prefix="brew path ") as directory:
            def get_fact(fact, command):
                if command == "brew --repository":
                    return directory
                return subprocess.check_output(command, shell=True, text=True).strip()

            with patch.object(install, "host") as host:
                host.get_fact.side_effect = get_fact
                self.assertTrue(install.can_manage_brew_taps())
                self.assertFalse((Path(directory) / "Library/Taps").exists())

    def test_existing_file_is_not_a_writable_directory(self):
        with tempfile.NamedTemporaryFile() as file:
            def get_fact(fact, command):
                if command == "brew --caskroom":
                    return file.name
                return subprocess.check_output(command, shell=True, text=True).strip()

            with patch.object(install, "host") as host:
                host.get_fact.side_effect = get_fact
                self.assertFalse(install.can_manage_brew_casks())

    def test_disabled_casks_are_not_installed_as_brew_packages(self):
        packages = install.get_packages_for_platform(install.PACKAGES, "brew")
        self.assertNotIn("alacritty", packages)
        self.assertNotIn("flameshot", packages)
        linux = install.get_packages_for_platform(install.PACKAGES, "dnf")
        self.assertIn("alacritty", linux)
        self.assertIn("flameshot", linux)

    def test_migration_fetches_before_uninstalling_without_zapping_settings(self):
        for cask, previous in install.BREW_CASK_REPLACEMENTS.items():
            with self.subTest(cask=cask), patch.object(install, "host") as host:
                host.get_fact.side_effect = [{previous: ["old"]}, previous]
                self.assertEqual(
                    list(install.install_tap_cask._inner(cask, previous)),
                    [
                        f"brew fetch --cask {cask}",
                        f"brew uninstall --cask {previous}",
                        f"brew install --cask {cask}",
                    ],
                )

    def test_fresh_install_does_not_uninstall_anything(self):
        with patch.object(install, "host") as host:
            host.get_fact.return_value = {}
            self.assertEqual(
                list(install.install_tap_cask._inner("owner/tap/app", "old-app")),
                ["brew fetch --cask owner/tap/app", "brew install --cask owner/tap/app"],
            )

    def test_migrated_installation_is_a_noop(self):
        with patch.object(install, "host") as host:
            host.get_fact.side_effect = [{"app": ["1.0"]}, "owner/tap/app"]
            self.assertEqual(
                list(install.install_tap_cask._inner("owner/tap/app", "old-app")), []
            )

    def test_trust_is_limited_to_missing_casks(self):
        with patch.object(install, "host") as host:
            host.get_fact.side_effect = [
                "install\ntrust\nupgrade",
                json.dumps({"taps": ["first/tap"], "casks": ["second/tap/app"]}),
            ]
            self.assertEqual(
                list(install.trust_brew_casks._inner([
                    "first/tap/app", "second/tap/app", "third/tap/app"
                ])),
                ["brew trust --cask third/tap/app"],
            )

    def test_older_homebrew_does_not_run_trust(self):
        with patch.object(install, "host") as host:
            host.get_fact.return_value = "install\nupgrade"
            self.assertEqual(list(install.trust_brew_casks._inner(["owner/tap/app"])), [])
            self.assertEqual(host.get_fact.call_count, 1)

    def test_older_macos_keeps_existing_flameshot(self):
        with (
            patch.object(install, "host") as host,
            patch.object(install.brew, "tap") as tap,
            patch.object(install, "trust_brew_casks") as trust,
            patch.object(install, "install_tap_cask") as install_cask,
        ):
            host.get_fact.return_value = "14.7"
            install.install_tapped_brew_casks()
            tap.assert_not_called()
            self.assertEqual(trust.call_args.kwargs["casks"], [])
            install_cask.assert_not_called()

    def test_readonly_taps_skip_replacements_but_keep_regular_casks(self):
        with (
            patch.object(install, "get_os_platform", return_value="darwin"),
            patch.object(install, "can_update_brew", return_value=False),
            patch.object(install, "can_manage_brew_taps", return_value=False),
            patch.object(install, "can_manage_brew_casks", return_value=True),
            patch.object(install, "install_tapped_brew_casks") as custom,
            patch.object(install, "brew") as brew,
            patch.object(install, "server") as server,
        ):
            install.main()
            custom.assert_not_called()
            brew.tap.assert_not_called()
            casks = brew.casks.call_args.kwargs["casks"]
            self.assertIn("keepassxc", casks)
            self.assertTrue(set(install.BREW_CASK_REPLACEMENTS).isdisjoint(casks))
            server.script.assert_called_once()
            self.assertTrue(server.script.call_args.kwargs["src"].endswith("scripts/install_alacritty.py"))

    def test_linux_uses_dnf_without_homebrew_setup(self):
        with (
            patch.object(install, "get_os_platform", return_value="linux"),
            patch.object(install, "dnf") as dnf,
            patch.object(install, "brew") as brew,
            patch.object(install, "install_tapped_brew_casks") as custom,
            patch.object(install, "server") as server,
        ):
            install.main()
            custom.assert_not_called()
            self.assertEqual(brew.mock_calls, [])
            server.script.assert_not_called()
            packages = dnf.packages.call_args.kwargs["packages"]
            self.assertIn("alacritty", packages)
            self.assertIn("flameshot", packages)


if __name__ == "__main__":
    unittest.main()
