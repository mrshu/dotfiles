from dataclasses import dataclass
from typing import Optional
from pyinfra.operations import brew, dnf
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
    Package("alacritty"),
    Package("bat"),
    Package("direnv"),
    Package(None, dnf_package="fd-find", brew_package="fd"),
    Package("fish"),
    Package("flameshot"),
    Package("gh"),
    Package(None, dnf_package="gnome-pomodoro"),
    # https://fedora.pkgs.org/37/terra/hack-nerd-fonts-0:2.3.3-2.fc37.noarch.rpm.html
    # dnf config-manager --add-repo https://terra.fyralabs.com/terra.repo
    Package(
        None,
        dnf_package="hack-nerd-fonts",
        brew_package="homebrew/cask-fonts/font-hack-nerd-font",
    ),
    Package("htop"),
    Package("jq"),
    # https://copr.fedorainfracloud.org/coprs/atim/lazygit/
    # dnf copr enable atim/lazygit -y
    Package("lazygit"),
    Package("neovim"),
    Package("ncdu"),
    Package("ripgrep"),
    Package(None, brew_package="rectangle"),
    # https://copr.fedorainfracloud.org/coprs/atim/starship/
    # dnf copr enable atim/starship
    Package("starship"),
    Package("task"),
    Package("tmux"),
    Package("zellij"),
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

    if platform == "darwin":
        packages = get_packages_for_platform(PACKAGES, "brew")
        brew.packages(
            name=f"Install packages {', '.join(packages)}",
            packages=packages,
            update=True,
        )

    elif platform == "linux":
        packages = get_packages_for_platform(PACKAGES, "dnf")
        dnf.packages(
            name=f"Install packages {', '.join(packages)}",
            packages=packages,
            latest=True,
            _sudo=True,
        )


main()
