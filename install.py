from dataclasses import dataclass
from typing import Optional
from pyinfra.operations import (brew, dnf)
from pyinfra import facts
from pyinfra import host


@dataclass
class Package:
    name: Optional[str] = None
    brew_package: Optional[str] = None
    dnf_package: Optional[str] = None

    @property
    def brew(self) -> Optional[str]:
        return self.brew_package if self.brew_package else self.name

    @property
    def dnf(self) -> Optional[str]:
        return self.dnf_package if self.dnf_package else self.name


PACKAGES = (
    Package('alacritty'),
    Package('bat'),
    Package('fish'),
    Package('gh'),
    Package(None, dnf_package='gnome-pomodoro'),
    Package(None, brew_package='homebrew/cask-fonts/font-iosevka-nerd-font'),
    Package('jq'),
    Package('neovim'),
    Package('ncdu'),
    Package('ripgrep'),
    Package(None, brew_package='rectangle'),
    Package('tmux'),
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


def get_packages_for_platform(packages: tuple, package_manager: str) -> list:
    result = []
    for pkg in packages:
        result.append(getattr(pkg, package_manager))

    # Cleanup the results of Nones and return
    return [r for r in result if r is not None]


def main():
    platform = get_os_platform()

    if platform == 'darwin':
        packages = get_packages_for_platform(PACKAGES, 'brew')
        brew.packages(
            name=f"Install packages {', '.join(packages)}",
            packages=packages,
            update=True
        )

    elif platform == 'linux':
        packages = get_packages_for_platform(PACKAGES, 'dnf')
        dnf.packages(
            name=f"Install packages {', '.join(packages)}",
            packages=packages,
            latest=True,
            _sudo=True
        )


main()
