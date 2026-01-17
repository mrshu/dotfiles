local opt = vim.opt

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
