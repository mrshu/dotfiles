if status is-interactive
    # Commands to run in interactive sessions can go here
end

if test -d "$HOME/micromamba"
    # >>> mamba initialize >>>
    # !! Contents within this block are managed by 'mamba init' !!
    set -gx MAMBA_EXE "$HOME/.local/bin/micromamba"
    set -gx MAMBA_ROOT_PREFIX "$HOME/micromamba"
    $MAMBA_EXE shell hook --shell fish --prefix $MAMBA_ROOT_PREFIX | source
    # <<< mamba initialize <<<
end

# editors
set -gx VISUAL nvim
set -gx EDITOR nvim
# use neovim to read man pages
set -gx MANPAGER "nvim +Man!"
set -gx MANWIDTH 80

starship init fish | source
direnv hook fish | source
fzf --fish | source

fish_vi_key_bindings
