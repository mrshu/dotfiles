--[[
lvim is the global options object

Linters should be
filled in as strings with either
a global executable or a path to
an executable
]]
-- THESE ARE EXAMPLE CONFIGS FEEL FREE TO CHANGE TO WHATEVER YOU WANT

-- general
lvim.log.level = "warn"
lvim.format_on_save.enabled = false
lvim.colorscheme = "onedarker"
-- to disable icons and use a minimalist setup, uncomment the following
-- lvim.use_icons = false

-- keymappings [view all the defaults by pressing <leader>Lk]
lvim.leader = "space"
-- add your own keymapping
lvim.keys.normal_mode["<C-s>"] = ":w<cr>"
lvim.keys.normal_mode["<S-l>"] = ":BufferLineCycleNext<CR>"
lvim.keys.normal_mode["<S-h>"] = ":BufferLineCyclePrev<CR>"
-- unmap a default keymapping
-- vim.keymap.del("n", "<C-Up>")
-- override a default keymapping
-- lvim.keys.normal_mode["<C-q>"] = ":q<cr>" -- or vim.keymap.set("n", "<C-q>", ":q<cr>" )

vim.api.nvim_set_keymap('i', 'jk', '<Esc>', { noremap = true })

-- Change Telescope navigation to use j and k for navigation and n and p for history in both input and normal mode.
-- we use protected-mode (pcall) just in case the plugin wasn't loaded yet.
-- local _, actions = pcall(require, "telescope.actions")
-- lvim.builtin.telescope.defaults.mappings = {
--   -- for input mode
--   i = {
--     ["<C-j>"] = actions.move_selection_next,
--     ["<C-k>"] = actions.move_selection_previous,
--     ["<C-n>"] = actions.cycle_history_next,
--     ["<C-p>"] = actions.cycle_history_prev,
--   },
--   -- for normal mode
--   n = {
--     ["<C-j>"] = actions.move_selection_next,
--     ["<C-k>"] = actions.move_selection_previous,
--   },
-- }

-- Change theme settings
-- lvim.builtin.theme.options.dim_inactive = true
-- lvim.builtin.theme.options.style = "storm"

-- Use which-key to add extra bindings with the leader-key prefix
-- lvim.builtin.which_key.mappings["P"] = { "<cmd>Telescope projects<CR>", "Projects" }
-- lvim.builtin.which_key.mappings["t"] = {
--   name = "+Trouble",
--   r = { "<cmd>Trouble lsp_references<cr>", "References" },
--   f = { "<cmd>Trouble lsp_definitions<cr>", "Definitions" },
--   d = { "<cmd>Trouble document_diagnostics<cr>", "Diagnostics" },
--   q = { "<cmd>Trouble quickfix<cr>", "QuickFix" },
--   l = { "<cmd>Trouble loclist<cr>", "LocationList" },
--   w = { "<cmd>Trouble workspace_diagnostics<cr>", "Workspace Diagnostics" },
-- }

-- TODO: User Config for predefined plugins
-- After changing plugin config exit and reopen LunarVim, Run :PackerInstall :PackerCompile
lvim.builtin.alpha.active = true
lvim.builtin.alpha.mode = "dashboard"
lvim.builtin.terminal.active = true
lvim.builtin.nvimtree.setup.view.side = "left"
lvim.builtin.nvimtree.setup.renderer.icons.show.git = false

-- if you don't want all the parsers change this to a table of the ones you want
lvim.builtin.treesitter.ensure_installed = {
  "bash",
  "c",
  "javascript",
  "json",
  "lua",
  "python",
  "typescript",
  "tsx",
  "css",
  "rust",
  "java",
  "yaml",
}

lvim.builtin.treesitter.ignore_install = { "haskell" }
lvim.builtin.treesitter.highlight.enable = true

-- generic LSP settings

-- -- make sure server will always be installed even if the server is in skipped_servers list
-- lvim.lsp.installer.setup.ensure_installed = {
--     "sumneko_lua",
--     "jsonls",
-- }
-- -- change UI setting of `LspInstallInfo`
-- -- see <https://github.com/williamboman/nvim-lsp-installer#default-configuration>
-- lvim.lsp.installer.setup.ui.check_outdated_servers_on_open = false
-- lvim.lsp.installer.setup.ui.border = "rounded"
-- lvim.lsp.installer.setup.ui.keymaps = {
--     uninstall_server = "d",
--     toggle_server_expand = "o",
-- }

-- ---@usage disable automatic installation of servers
-- lvim.lsp.installer.setup.automatic_installation = false

-- ---configure a server manually. !!Requires `:LvimCacheReset` to take effect!!
-- ---see the full default list `:lua print(vim.inspect(lvim.lsp.automatic_configuration.skipped_servers))`
-- vim.list_extend(lvim.lsp.automatic_configuration.skipped_servers, { "pyright" })
-- local opts = {} -- check the lspconfig documentation for a list of all possible options
-- require("lvim.lsp.manager").setup("pyright", opts)

-- ---remove a server from the skipped list, e.g. eslint, or emmet_ls. !!Requires `:LvimCacheReset` to take effect!!
-- ---`:LvimInfo` lists which server(s) are skipped for the current filetype
-- lvim.lsp.automatic_configuration.skipped_servers = vim.tbl_filter(function(server)
--   return server ~= "emmet_ls"
-- end, lvim.lsp.automatic_configuration.skipped_servers)

-- -- you can set a custom on_attach function that will be used for all the language servers
-- -- See <https://github.com/neovim/nvim-lspconfig#keybindings-and-completion>
-- lvim.lsp.on_attach_callback = function(client, bufnr)
--   local function buf_set_option(...)
--     vim.api.nvim_buf_set_option(bufnr, ...)
--   end
--   --Enable completion triggered by <c-x><c-o>
--   buf_set_option("omnifunc", "v:lua.vim.lsp.omnifunc")
-- end

-- -- set a formatter, this will override the language server formatting capabilities (if it exists)
-- local formatters = require "lvim.lsp.null-ls.formatters"
-- formatters.setup {
--   { command = "black", filetypes = { "python" } },
--   { command = "isort", filetypes = { "python" } },
--   {
--     -- each formatter accepts a list of options identical to https://github.com/jose-elias-alvarez/null-ls.nvim/blob/main/doc/BUILTINS.md#Configuration
--     command = "prettier",
--     ---@usage arguments to pass to the formatter
--     -- these cannot contain whitespaces, options such as `--line-width 80` become either `{'--line-width', '80'}` or `{'--line-width=80'}`
--     extra_args = { "--print-with", "100" },
--     ---@usage specify which filetypes to enable. By default a providers will attach to all the filetypes it supports.
--     filetypes = { "typescript", "typescriptreact" },
--   },
-- }

-- -- set additional linters
-- local linters = require "lvim.lsp.null-ls.linters"
-- linters.setup {
--   { command = "flake8", filetypes = { "python" } },
--   {
--     -- each linter accepts a list of options identical to https://github.com/jose-elias-alvarez/null-ls.nvim/blob/main/doc/BUILTINS.md#Configuration
--     command = "shellcheck",
--     ---@usage arguments to pass to the formatter
--     -- these cannot contain whitespaces, options such as `--line-width 80` become either `{'--line-width', '80'}` or `{'--line-width=80'}`
--     extra_args = { "--severity", "warning" },
--   },
--   {
--     command = "codespell",
--     ---@usage specify which filetypes to enable. By default a providers will attach to all the filetypes it supports.
--     filetypes = { "javascript", "python" },
--   },
-- }

-- Additional Plugins
lvim.plugins = {
      {
        "folke/trouble.nvim",
        cmd = "TroubleToggle",
      },
      { "tpope/vim-surround" },
      { "tpope/vim-fugitive" },
      { "averms/black-nvim" },
      { "renerocksai/calendar-vim" },
      { "renerocksai/telekasten.nvim",
        dependencies = {
          { "nvim-telescope/telescope.nvim" },
          { "nvim-telescope/telescope-media-files.nvim" }
        },
      },
}

local telekasten_home_dir = vim.fn.expand("~/Nextcloud/zettelkasten")
local telekasten_templates_dir = telekasten_home_dir .. "/templates"
require('telekasten').setup({
  home = telekasten_home_dir, -- Put the name of your notes directory here
	dailies = telekasten_home_dir .. "/" .. "daily",
	weeklies = telekasten_home_dir .. "/" .. "weekly",
	templates = telekasten_templates_dir ,

  -- Image subdir for pasting
    -- subdir name
    -- or nil if pasted images shouldn't go into a special subdir
  image_subdir = "img",

  -- File extension for note files
  extension    = ".md",

	-- template for new notes (new_note, follow_link)
	template_new_note = telekasten_templates_dir .. "/new_note.md",

	-- template for newly created daily notes (goto_today)
	template_new_daily = telekasten_templates_dir .. "/daily.md",

	-- template for newly created weekly notes (goto_thisweek)
	template_new_weekly = telekasten_templates_dir .. "/weekly.md",

	image_link_style = "markdown",

	-- default sort option: 'filename', 'modified'
	sort = "modified",

    -- Generate note filenames. One of:
    -- "title" (default) - Use title if supplied, uuid otherwise
    -- "uuid" - Use uuid
    -- "uuid-title" - Prefix title by uuid
    -- "title-uuid" - Suffix title with uuid
  new_note_filename = "uuid-title",
  -- file uuid type ("rand" or input for os.date such as "%Y%m%d%H%M")
  uuid_type = "%Y%m%d-%H%M",
  -- UUID separator
  uuid_sep = "-",

  -- Tag notation: '#tag', '@tag', ':tag:', 'yaml-bare'
  tag_notation = "#tag",

  -- When linking to a note in subdir/, create a [[subdir/title]] link
  -- instead of a [[title only]] link
  subdirs_in_links = true,

  -- Command palette theme: dropdown (window) or ivy (bottom panel)
  command_palette_theme = "ivy",

  -- Tag list theme:
    -- get_cursor (small tag list at cursor)
    -- dropdown (window)
    -- ivy (bottom panel)
  show_tags_theme = "dropdown",

  -- telescope actions behavior
  close_after_yanking = false,
  insert_after_inserting = true,

  -- Previewer for media files (images mostly)
    -- "telescope-media-files" if you have telescope-media-files.nvim installed
    -- "catimg-previewer" if you have catimg installed
    -- "viu-previewer" if you have viu installed
  media_previewer = "telescope-media-files",

})

vim.api.nvim_set_keymap('n', '<Leader>zf', [[<Cmd>lua require('telekasten').find_notes()<CR>]], { noremap = true, silent = true })
vim.api.nvim_set_keymap('n', '<Leader>zd', [[<Cmd>lua require('telekasten').find_daily_notes()<CR>]], { noremap = true, silent = true })
vim.api.nvim_set_keymap('n', '<Leader>zg', [[<Cmd>lua require('telekasten').search_notes()<CR>]], { noremap = true, silent = true })
vim.api.nvim_set_keymap('n', '<Leader>zz', [[<Cmd>lua require('telekasten').follow_link()<CR>]], { noremap = true, silent = true })
vim.api.nvim_set_keymap('n', '<Leader>zT', [[<Cmd>lua require('telekasten').goto_today()<CR>]], { noremap = true, silent = true })
vim.api.nvim_set_keymap('n', '<Leader>zW', [[<Cmd>lua require('telekasten').goto_thisweek()<CR>]], { noremap = true, silent = true })
vim.api.nvim_set_keymap('n', '<Leader>zw', [[<Cmd>lua require('telekasten').find_weekly_notes()<CR>]], { noremap = true, silent = true })
vim.api.nvim_set_keymap('n', '<Leader>zn', [[<Cmd>lua require('telekasten').new_note()<CR>]], { noremap = true, silent = true })
vim.api.nvim_set_keymap('n', '<Leader>zN', [[<Cmd>lua require('telekasten').new_templated_note()<CR>]], { noremap = true, silent = true })
vim.api.nvim_set_keymap('n', '<Leader>zy', [[<Cmd>lua require('telekasten').yank_notelink()<CR>]], { noremap = true, silent = true })
vim.api.nvim_set_keymap('n', '<Leader>zc', [[<Cmd>lua require('telekasten').show_calendar()<CR>]], { noremap = true, silent = true })
vim.api.nvim_set_keymap('n', '<Leader>zC', [[<Cmd>CalendarT<CR>]], { noremap = true, silent = true })
vim.api.nvim_set_keymap('n', '<Leader>zi', [[<Cmd>lua require('telekasten').paste_img_and_link()<CR>]], { noremap = true, silent = true })
vim.api.nvim_set_keymap('n', '<Leader>zt', [[<Cmd>lua require('telekasten').toggle_todo()<CR>]], { noremap = true, silent = true })
vim.api.nvim_set_keymap('n', '<Leader>zb', [[<Cmd>lua require('telekasten').show_backlinks()<CR>]], { noremap = true, silent = true })
vim.api.nvim_set_keymap('n', '<Leader>zF', [[<Cmd>lua require('telekasten').find_friends()<CR>]], { noremap = true, silent = true })
vim.api.nvim_set_keymap('n', '<Leader>zI', [[<Cmd>lua require('telekasten').insert_img_link({ i=true })<CR>]], { noremap = true, silent = true })
vim.api.nvim_set_keymap('n', '<Leader>zp', [[<Cmd>lua require('telekasten').preview_img()<CR>]], { noremap = true, silent = true })
vim.api.nvim_set_keymap('n', '<Leader>zm', [[<Cmd>lua require('telekasten').browse_media()<CR>]], { noremap = true, silent = true })
vim.api.nvim_set_keymap('n', '<Leader>za', [[<Cmd>lua require('telekasten').show_tags()<CR>]], { noremap = true, silent = true })
vim.api.nvim_set_keymap('n', '<Leader>#', [[<Cmd>lua require('telekasten').show_tags()<CR>]], { noremap = true, silent = true })
vim.api.nvim_set_keymap('n', '<Leader>zr', [[<Cmd>lua require('telekasten').rename_note()<CR>]], { noremap = true, silent = true })
vim.api.nvim_set_keymap('n', '<Leader>z', [[<Cmd>lua require('telekasten').panel()<CR>]], { noremap = true, silent = true })


vim.api.nvim_create_autocmd("FileType", {
  pattern = "markdown",
  callback = function()
    vim.api.nvim_set_keymap('i', '[[', [[<Cmd>lua require('telekasten').insert_link({ i = true })<CR>]], { noremap = true, silent = true })
    vim.api.nvim_set_keymap('i', '#', [[<Cmd>lua require('telekasten').show_tags({ i = true })<CR>]], { noremap = true, silent = true })
  end,
})

-- Autocommands (https://neovim.io/doc/user/autocmd.html)
-- vim.api.nvim_create_autocmd("BufEnter", {
--   pattern = { "*.json", "*.jsonc" },
--   -- enable wrap mode for json files only
--   command = "setlocal wrap",
-- })
-- vim.api.nvim_create_autocmd("FileType", {
--   pattern = "zsh",
--   callback = function()
--     -- let treesitter use bash highlight for zsh files as well
--     require("nvim-treesitter.highlight").attach(0, "bash")
--   end,
-- })
