#!/usr/bin/env python3
"""Install the latest official Alacritty macOS release, retaining quarantine."""

import argparse
from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path
import plistlib
import re
import shutil
import subprocess
import sys
import tempfile
import time
from urllib.request import Request, urlopen


RELEASE_API = "https://api.github.com/repos/alacritty/alacritty/releases/latest"
APP = Path("/Applications/Alacritty.app")
RECEIPT = Path.home() / "Library/Application Support/dotfiles/alacritty.json"
BREW_CASKS = {"alacritty", "mrshu-alacritty"}


def read_url(url):
    request = Request(url, headers={"User-Agent": "mrshu-dotfiles"})
    return urlopen(request, timeout=60)


def latest_release():
    with read_url(RELEASE_API) as response:
        release = json.load(response)
    tag = release.get("tag_name", "")
    if release.get("draft") or release.get("prerelease") or not re.fullmatch(r"v\d+\.\d+\.\d+", tag):
        raise ValueError("The latest Alacritty release is not a stable version")
    filename = f"Alacritty-{tag}.dmg"
    asset = next((item for item in release.get("assets", []) if item["name"] == filename), None)
    if asset is None:
        raise ValueError(f"No official macOS disk image found for {tag}")
    url = f"https://github.com/alacritty/alacritty/releases/download/{tag}/{filename}"
    if asset.get("browser_download_url") != url:
        raise ValueError("The disk image URL does not match the official release")
    digest = asset.get("digest") or ""
    if not re.fullmatch(r"sha256:[0-9a-f]{64}", digest):
        raise ValueError("The official release has no SHA256 digest; refusing to install")
    return {"version": tag[1:], "url": url, "sha256": digest.split(":", 1)[1]}


def download(release, destination):
    digest = hashlib.sha256()
    with read_url(release["url"]) as response, destination.open("wb") as output:
        while True:
            chunk = response.read(1024 * 1024)
            if not chunk:
                break
            digest.update(chunk)
            output.write(chunk)
    if digest.hexdigest() != release["sha256"]:
        raise ValueError("Alacritty download failed SHA256 verification")


def app_version(app):
    plist = app / "Contents/Info.plist"
    if not plist.is_file():
        return None
    with plist.open("rb") as stream:
        info = plistlib.load(stream)
    if info.get("CFBundleIdentifier") != "org.alacritty":
        raise ValueError(f"Unexpected application at {app}")
    return info.get("CFBundleShortVersionString")


@contextmanager
def mounted_image(dmg, mountpoint):
    subprocess.run([
        "hdiutil", "attach", "-readonly", "-nobrowse", "-mountpoint", str(mountpoint), str(dmg)
    ], check=True, stdout=subprocess.DEVNULL)
    try:
        yield mountpoint / "Alacritty.app"
    finally:
        subprocess.run(["hdiutil", "detach", str(mountpoint)], check=True, stdout=subprocess.DEVNULL)


def integrations(app, prefix):
    resources = app / "Contents/Resources"
    links = [(app / "Contents/MacOS/alacritty", prefix / "bin/alacritty")]
    terminfo = Path(os.environ.get("TERMINFO", str(Path.home() / ".terminfo"))).expanduser()
    for name in ("alacritty", "alacritty-direct"):
        links.append((resources / "61" / name, terminfo / "61" / name))
    for source in sorted(resources.glob("*.gz")):
        section = source.name.rsplit(".", 2)[-2]
        if section.isdigit():
            links.append((source, prefix / "share/man" / f"man{section}" / source.name))
    for source, destination in (
        ("alacritty.bash", "etc/bash_completion.d/alacritty"),
        ("_alacritty", "share/zsh/site-functions/_alacritty"),
        ("alacritty.fish", "share/fish/vendor_completions.d/alacritty.fish"),
    ):
        links.append((resources / "completions" / source, prefix / destination))
    return links


def check_links(links, staged, app):
    for source, destination in links:
        if not (staged / source.relative_to(app)).is_file():
            raise ValueError(f"The release is missing {source.relative_to(app)}")
        if destination.is_symlink():
            existing = destination.resolve()
            if existing != source.resolve():
                raise ValueError(f"Refusing to replace unrelated symlink {destination}")
        elif destination.exists():
            raise ValueError(f"Refusing to replace existing file {destination}")
        ancestor = destination.parent
        while not ancestor.exists():
            ancestor = ancestor.parent
        if not ancestor.is_dir() or not os.access(ancestor, os.W_OK):
            raise PermissionError(f"Cannot create {destination}")


def install_release(release, app, receipt, prefix, brew_casks):
    if subprocess.run(["pgrep", "-x", "alacritty"], stdout=subprocess.DEVNULL).returncode == 0:
        raise RuntimeError("Quit Alacritty before updating, and run this from another terminal")
    app.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".alacritty-", dir=app.parent) as directory:
        work = Path(directory)
        dmg, staged, backup = work / "Alacritty.dmg", work / "Alacritty.app", work / "previous.app"
        download(release, dmg)
        with mounted_image(dmg, work / "mount") as source:
            if app_version(source) != release["version"]:
                raise ValueError("The app version does not match the official release")
            subprocess.run(["ditto", str(source), str(staged)], check=True)
        # urllib downloads do not acquire quarantine automatically. Add it explicitly.
        quarantine = f"0083;{int(time.time()):x};dotfiles;"
        subprocess.run(["xattr", "-w", "com.apple.quarantine", quarantine, str(staged)], check=True)
        links = [
            (app / source.relative_to(staged), destination)
            for source, destination in integrations(staged, prefix)
        ]
        check_links(links, staged, app)
        original_links = {destination: os.readlink(destination) for _, destination in links if destination.is_symlink()}
        if app.exists():
            subprocess.run(["ditto", str(app), str(backup)], check=True)
        changed_links = []
        try:
            # Unregister old casks only after the new app and integrations are checked.
            for cask in sorted(brew_casks):
                subprocess.run(["brew", "uninstall", "--cask", cask], check=True)
            if app.exists():
                shutil.rmtree(app)
            staged.rename(app)
            for source, destination in links:
                destination.parent.mkdir(parents=True, exist_ok=True)
                if destination.is_symlink():
                    continue  # Already points at this app, as checked above.
                destination.symlink_to(source)
                changed_links.append(destination)
            receipt.parent.mkdir(parents=True, exist_ok=True)
            temporary_receipt = receipt.with_suffix(".tmp")
            temporary_receipt.write_text(json.dumps(release, indent=2) + "\n")
            temporary_receipt.replace(receipt)
        except Exception:
            for destination in reversed(changed_links):
                destination.unlink(missing_ok=True)
            if app.exists():
                shutil.rmtree(app)
            if backup.exists():
                backup.rename(app)
            for destination, target in original_links.items():
                if not destination.exists() and not destination.is_symlink():
                    destination.symlink_to(target)
            raise
    print(f"Installed Alacritty {release['version']} from its official release.")
    print("On first launch, approve it in System Settings > Privacy & Security > Open Anyway.")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Show update status without changing files")
    args = parser.parse_args(argv)
    if sys.platform != "darwin":
        parser.error("This installer is for macOS; use the system package manager on Linux")
    release = latest_release()
    installed = app_version(APP)
    listed = subprocess.check_output(["brew", "list", "--cask", "--versions"], text=True)
    casks = {line.split()[0] for line in listed.splitlines() if line.strip()} & BREW_CASKS
    previous = json.loads(RECEIPT.read_text()) if RECEIPT.exists() else {}
    current = installed == release["version"] and previous.get("sha256") == release["sha256"] and not casks
    print(f"Alacritty: installed {installed or 'none'}, latest {release['version']}.")
    if current:
        print("The official release is already installed.")
    elif args.check:
        print("The next install will download, verify and install the official release.")
    else:
        prefix = Path(subprocess.check_output(["brew", "--prefix"], text=True).strip())
        install_release(release, APP, RECEIPT, prefix, casks)


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, RuntimeError, subprocess.CalledProcessError) as error:
        print(f"Alacritty installation failed: {error}", file=sys.stderr)
        sys.exit(1)
