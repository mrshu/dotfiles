from dataclasses import dataclass
import shlex
from typing import Iterable, List, Optional
from pyinfra.operations import brew, dnf
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
    Package("alacritty"),
    Package("bat"),
    Package("direnv"),
    Package(None, dnf_package="fd-find", brew_package="fd"),
    Package("fish"),
    Package("flameshot"),
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
    Package("tmux"),
    Package("zellij"),
)


# Deprecated Homebrew taps that should be removed when possible.
DEPRECATED_BREW_TAPS = (
    "homebrew/cask-fonts",
    "homebrew/homebrew-cask-fonts",
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
    """Run `base_cmd` to get a path, optionally append `suffix`, and check writability.

    Returns False on any failure.
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
        f"test -w {quoted} && echo writable || echo not_writable",
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
        brew_casks = get_packages_for_platform(PACKAGES, "brew_cask_name")

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

        if brew_casks:
            if can_manage_brew_casks():
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

if __name__ == "__main__":
    main()
