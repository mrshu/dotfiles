from dataclasses import dataclass
import json
from pathlib import Path
import shlex
from typing import Iterable, List, Optional
import pyinfra
from pyinfra.api import operation
from pyinfra.operations import brew, dnf, server
from pyinfra import facts
from pyinfra import host


@dataclass
class Package:
    name: Optional[str] = None
    brew_package: Optional[str] = None
    brew_cask: Optional[str] = None
    dnf_package: Optional[str] = None

    @property
    def brew(self) -> Optional[str]:
        if self.brew_cask:
            return None
        return self.brew_package if self.brew_package else self.name

    @property
    def dnf(self) -> Optional[str]:
        return self.dnf_package if self.dnf_package else self.name

    @property
    def brew_cask_name(self) -> Optional[str]:
        return self.brew_cask if self.brew_cask else None


# Package catalog. Use per-manager overrides when names differ.
PACKAGES = (
    # macOS Alacritty is installed directly from its official releases below.
    Package(None, dnf_package="alacritty"),
    Package("bat"),
    Package(None, brew_cask="codexbar"),
    Package("direnv"),
    Package(None, dnf_package="fd-find", brew_package="fd"),
    Package("fish"),
    Package("flameshot", brew_cask="flameshot-org/flameshot/flameshot-org-flameshot"),
    Package("fzf"),
    Package("gh"),
    Package(None, dnf_package="gnome-pomodoro"),
    # https://fedora.pkgs.org/37/terra/hack-nerd-fonts-0:2.3.3-2.fc37.noarch.rpm.html
    # dnf config-manager --add-repo https://terra.fyralabs.com/terra.repo
    Package(
        None,
        dnf_package="hack-nerd-fonts",
        brew_cask="font-hack-nerd-font",
    ),
    Package("htop"),
    Package("jq"),
    Package("keepassxc", brew_cask="keepassxc"),
    # https://copr.fedorainfracloud.org/coprs/atim/lazygit/
    # dnf copr enable atim/lazygit -y
    Package("lazygit"),
    Package("ncdu"),
    Package("neovim"),
    Package("nextcloud", brew_cask="nextcloud"),
    Package("ripgrep"),
    Package(None, brew_cask="rectangle"),
    # https://copr.fedorainfracloud.org/coprs/atim/starship/
    # dnf copr enable atim/starship
    Package("starship"),
    Package("task"),
    Package(None, brew_cask="thaw"),
    Package("tmux"),
    Package("zellij"),
)


# Deprecated Homebrew taps that should be removed when possible.
DEPRECATED_BREW_TAPS = (
    "homebrew/cask-fonts",
    "homebrew/homebrew-cask-fonts",
)

# This cask replaces the disabled homebrew/cask entry on macOS only.
BREW_CASK_REPLACEMENTS = {
    "flameshot-org/flameshot/flameshot-org-flameshot": "flameshot",
}


@operation()
def trust_brew_casks(casks: List[str]):
    """Trust only the selected casks on Homebrew versions with tap trust."""
    commands = host.get_fact(facts.server.Command, "brew commands --quiet") or ""
    if "trust" not in commands.split():
        host.noop("This Homebrew version does not require tap trust")
        return

    trusted = json.loads(host.get_fact(facts.server.Command, "brew trust --json=v1"))
    pending = [
        cask for cask in casks
        if cask not in trusted.get("casks", [])
        and cask.rsplit("/", 1)[0] not in trusted.get("taps", [])
    ]
    if pending:
        yield "brew trust --cask " + " ".join(shlex.quote(cask) for cask in pending)
    else:
        host.noop("The selected Homebrew casks are already trusted")


@operation()
def install_tap_cask(cask: str, replaces: str):
    """Install a tapped cask, fetching before removing its old package."""
    installed = host.get_fact(facts.brew.BrewCasks)
    token = cask.rsplit("/", 1)[-1]
    if token in installed:
        installed_names = host.get_fact(
            facts.server.Command, "brew list --cask --full-name"
        ) or ""
        if cask in installed_names.split():
            host.noop(f"Cask {cask} is already installed")
            return

    # pyinfra's cask facts use bare tokens, so handle qualified names here.
    # Check the download and checksum before removing the old app.
    yield f"brew fetch --cask {shlex.quote(cask)}"
    if replaces in installed:
        yield f"brew uninstall --cask {shlex.quote(replaces)}"
    yield f"brew install --cask {shlex.quote(cask)}"


def install_tapped_brew_casks() -> None:
    """Add Flameshot's upstream tap when the current release supports macOS."""
    replacements = dict(BREW_CASK_REPLACEMENTS)
    macos_version = host.get_fact(facts.server.Command, "sw_vers -productVersion")
    if int(macos_version.strip().split(".")[0]) < 15:
        del replacements["flameshot-org/flameshot/flameshot-org-flameshot"]
        print("Skipping Flameshot: its current macOS release requires macOS 15 or newer.")

    for tap in dict.fromkeys(cask.rsplit("/", 1)[0] for cask in replacements):
        brew.tap(name=f"Add tap {tap}", src=tap)
    trust_brew_casks(
        name="Trust Flameshot's upstream cask",
        casks=list(replacements),
    )
    for cask, replaces in replacements.items():
        install_tap_cask(
            name=f"Install {cask}, replacing {replaces} when needed",
            cask=cask,
            replaces=replaces,
        )


def get_os_platform() -> str:
    """
    Returns `uname` result, `strip`ped and `lower`ed.
    e.g.
        "darwin"
    """
    uname = host.get_fact(facts.server.Command, "uname")
    if not uname:
        return ""
    return uname.lower().strip()


def get_packages_for_platform(packages: Iterable[Package], package_manager: str) -> List[str]:
    """Return non-empty package names for a given manager key.

    Example: package_manager in {"brew", "brew_cask_name", "dnf"}.
    """
    names: List[str] = []
    for pkg in packages:
        value = getattr(pkg, package_manager)
        if value:
            names.append(value)
    return names


def _is_path_writable_from_cmd(base_cmd: str, suffix: Optional[str] = None) -> bool:
    """Check writability of a directory or its nearest existing ancestor.

    Missing Homebrew directories can be created when their parent is writable.
    Returns False if the path cannot be resolved.
    """
    resolved = host.get_fact(facts.server.Command, base_cmd)
    if not resolved:
        return False

    base = resolved.strip()
    if not base:
        return False

    path = base if not suffix else f"{base.rstrip('/')}/{suffix}"
    quoted = shlex.quote(path)
    check = host.get_fact(
        facts.server.Command,
        f"brew_check_path={quoted}; "
        'while test ! -e "$brew_check_path"; do '
        'brew_check_path=$(dirname "$brew_check_path"); done; '
        'test -d "$brew_check_path" && test -w "$brew_check_path" '
        "&& echo writable || echo not_writable",
    )
    return bool(check) and check.strip() == "writable"


def can_update_brew() -> bool:
    # Homebrew updates need write access to prefix/Cellar
    return _is_path_writable_from_cmd("brew --prefix", suffix="Cellar")


def can_manage_brew_casks() -> bool:
    return _is_path_writable_from_cmd("brew --caskroom")


def can_manage_brew_taps() -> bool:
    return _is_path_writable_from_cmd("brew --repository", suffix="Library/Taps")


def main() -> None:
    platform = get_os_platform()

    if platform == "darwin":
        brew_packages = get_packages_for_platform(PACKAGES, "brew")
        brew_casks = [
            cask for cask in get_packages_for_platform(PACKAGES, "brew_cask_name")
            if cask not in BREW_CASK_REPLACEMENTS
        ]

        can_update = can_update_brew()
        can_manage_taps = can_manage_brew_taps()

        if can_manage_taps:
            for tap in DEPRECATED_BREW_TAPS:
                brew.tap(
                    name=f"Remove deprecated tap {tap}",
                    src=tap,
                    present=False,
                )
        else:
            print(
                "Skipping removal of deprecated brew taps: unable to write to the "
                "Homebrew taps directory."
            )

        if brew_packages:
            brew.packages(
                name=f"Install packages {', '.join(brew_packages)}",
                packages=brew_packages,
                update=can_update,
            )

        server.script(
            name="Install or update Alacritty from its official release",
            src=str(Path(__file__).resolve().parent / "scripts/install_alacritty.py"),
        )

        if can_manage_brew_casks():
            if can_manage_taps:
                install_tapped_brew_casks()
            else:
                print(
                    "Skipping Flameshot setup: unable to write to the "
                    "Homebrew taps directory."
                )
            if brew_casks:
                brew.casks(
                    name=f"Install casks {', '.join(brew_casks)}",
                    casks=brew_casks,
                )
        else:
            print(
                "Skipping brew cask installs: unable to write to the cask "
                "directory."
            )

    elif platform == "linux":
        packages = get_packages_for_platform(PACKAGES, "dnf")
        if packages:
            dnf.packages(
                name=f"Install packages {', '.join(packages)}",
                packages=packages,
                latest=True,
                _sudo=True,
            )
    else:
        print(f"Unsupported platform '{platform}'. Nothing to do.")

if __name__ == "__main__" or pyinfra.is_cli:
    main()
