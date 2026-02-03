local opt = vim.opt

local uv = vim.uv or vim.loop
local function cleanup_stale_markdown_parsers()
  local data = vim.fn.stdpath("data")
  local site_dir = data .. "/site/parser"
  local lazy_dir = data .. "/lazy/nvim-treesitter/parser"
  local backup_dir = data .. "/site/parser.bak"

  local function maybe_move(lang)
    local site_path = site_dir .. "/" .. lang .. ".so"
    local lazy_path = lazy_dir .. "/" .. lang .. ".so"
    local site_stat = uv.fs_stat(site_path)
    if not site_stat then
      return
    end
    if not uv.fs_stat(lazy_path) then
      return
    end
    local lazy_stat = uv.fs_stat(lazy_path)
    if lazy_stat and site_stat.mtime.sec <= lazy_stat.mtime.sec then
      if not uv.fs_stat(backup_dir) then
        pcall(uv.fs_mkdir, backup_dir, 493)
      end
      pcall(uv.fs_rename, site_path, backup_dir .. "/" .. lang .. ".so")
    end
  end

  maybe_move("markdown")
  maybe_move("markdown_inline")
end

cleanup_stale_markdown_parsers()

-- Numbers & columns
opt.number = true
opt.relativenumber = true
opt.signcolumn = "auto:1-2"
opt.statuscolumn = "%s %=%{v:relnum == 0 ? v:lnum : v:relnum} | "
opt.numberwidth = 2
opt.cursorline = true
opt.colorcolumn = "100"

-- Search & completion
opt.ignorecase = true
opt.smartcase = true
opt.completeopt = { "menuone", "noselect" }

-- Windows & scrolling
opt.splitright = true
opt.splitbelow = true
opt.scrolloff = 6
opt.sidescrolloff = 8

-- Visual whitespace to make indentation consistent everywhere
opt.list = true
opt.listchars = {
  tab = ">>",
  trail = "~",
  extends = ">",
  precedes = "<",
  nbsp = "+",
}
