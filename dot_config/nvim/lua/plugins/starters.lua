return {
  ---- change trouble config
  {
    "folke/trouble.nvim",
    -- opts will be merged with the parent spec
    opts = { use_diagnostic_signs = true },
  },
  --
  ---- disable trouble
  --{ "folke/trouble.nvim", enabled = false },

  -- override nvim-cmp and add cmp-emoji
  --{
  --  "hrsh7th/nvim-cmp",
  --  dependencies = { "hrsh7th/cmp-emoji" },
  --  ---@param opts cmp.ConfigSchema
  --  opts = function(_, opts)
  --    table.insert(opts.sources, { name = "emoji" })
  --  end,
  --},

  -- Treesitter: keep a single source of truth for parsers
  {
    "nvim-treesitter/nvim-treesitter",
    opts = {
      ensure_installed = {
        "bash",
        "html",
        "javascript",
        "json",
        "lua",
        "markdown",
        "markdown_inline",
        "python",
        "query",
        "regex",
        "tsx",
        "typescript",
        "vim",
        "yaml",
      },
    },
  },

  -- Use <tab> for completion and snippets (supertab)
  -- first: disable default <tab> and <s-tab> behavior in LuaSnip
  {
    "L3MON4D3/LuaSnip",
    keys = function()
      return {}
    end,
  },
  -- then: setup supertab in cmp
  --{
  --  "hrsh7th/nvim-cmp",
  --  dependencies = {
  --    "hrsh7th/cmp-emoji",
  --  },
  --  ---@param opts cmp.ConfigSchema
  --  opts = function(_, opts)
  --    local has_words_before = function()
  --      unpack = unpack or table.unpack
  --      local line, col = unpack(vim.api.nvim_win_get_cursor(0))
  --      return col ~= 0 and vim.api.nvim_buf_get_lines(0, line - 1, line, true)[1]:sub(col, col):match("%s") == nil
  --    end
  --
  --    local luasnip = require("luasnip")
  --    local cmp = require("cmp")
  --
  --    opts.mapping = vim.tbl_extend("force", opts.mapping, {
  --      ["<Tab>"] = cmp.mapping(function(fallback)
  --        if cmp.visible() then
  --          cmp.select_next_item()
  --          -- You could replace the expand_or_jumpable() calls with expand_or_locally_jumpable()
  --          -- this way you will only jump inside the snippet region
  --        elseif luasnip.expand_or_jumpable() then
  --          luasnip.expand_or_jump()
  --        elseif has_words_before() then
  --          cmp.complete()
  --        else
  --          fallback()
  --        end
  --      end, { "i", "s" }),
  --      ["<S-Tab>"] = cmp.mapping(function(fallback)
  --        if cmp.visible() then
  --          cmp.select_prev_item()
  --        elseif luasnip.jumpable(-1) then
  --          luasnip.jump(-1)
  --        else
  --          fallback()
  --        end
  --      end, { "i", "s" }),
  --    })
  --  end,
  --},

  -- Automatically put the cursor on the Exporer tab
  -- and close the picker when a file is selected.
  -- https://www.reddit.com/r/neovim/comments/1ifv5go/help_with_snacks_explorer_config_i_have_read_the/
  {
    "folke/snacks.nvim",
    opts = {
      picker = {
        sources = {
          explorer = {
            focus = "input",
            auto_close = true,
          },
        },
      },
    },
  },

  -- Toggle a git-status tree that only lists changed files.
  {
    "nvim-neo-tree/neo-tree.nvim",
    keys = {
      {
        "<leader>gs",
        function()
          require("neo-tree.command").execute({
            source = "git_status",
            position = "left",
            toggle = true,
          })
        end,
        desc = "Neo-tree: changed files",
      },
    },
    opts = function(_, opts)
      local function default_git_base()
        local head = vim.fn.systemlist({
          "git",
          "symbolic-ref",
          "--quiet",
          "--short",
          "refs/remotes/origin/HEAD",
        })
        if vim.v.shell_error == 0 and head[1] and head[1] ~= "" then
          return head[1]
        end
      end

      opts.git_status = opts.git_status or {}
      opts.git_status.git_base = opts.git_status.git_base or default_git_base()
    end,
  },

  -- Inline git hunks with easy navigation and inline previews.
  {
    "lewis6991/gitsigns.nvim",
    opts = function(_, opts)
      local old_attach = opts.on_attach

      opts.current_line_blame = true

      opts.on_attach = function(bufnr)
        if old_attach then
          old_attach(bufnr)
        end

        local gs = package.loaded.gitsigns
        local function map(mode, lhs, rhs, desc)
          vim.keymap.set(mode, lhs, rhs, { buffer = bufnr, desc = desc, silent = true })
        end

        map("n", "]c", function()
          if vim.wo.diff then
            vim.cmd.normal({ "]c", bang = true })
          else
            gs.nav_hunk("next")
          end
        end, "Next Hunk")

        map("n", "[c", function()
          if vim.wo.diff then
            vim.cmd.normal({ "[c", bang = true })
          else
            gs.nav_hunk("prev")
          end
        end, "Prev Hunk")

        map("n", "<leader>hp", gs.preview_hunk_inline, "Preview Hunk Inline")
      end
    end,
  },
}
