return {
  {
    "stevearc/conform.nvim",
    opts = function(_, opts)
      local function remove(list, value)
        if type(list) ~= "table" then
          return
        end
        for i = #list, 1, -1 do
          if list[i] == value then
            table.remove(list, i)
          end
        end
      end

      opts.formatters_by_ft = opts.formatters_by_ft or {}
      remove(opts.formatters_by_ft.markdown, "markdownlint-cli2")
      remove(opts.formatters_by_ft["markdown.mdx"], "markdownlint-cli2")
    end,
  },
  {
    "nvimtools/none-ls.nvim",
    optional = true,
    opts = function(_, opts)
      if type(opts.sources) ~= "table" then
        return
      end
      opts.sources = vim.tbl_filter(function(source)
        return source.name ~= "markdownlint" and source.name ~= "markdownlint_cli2"
      end, opts.sources)
    end,
  },
  {
    "mfussenegger/nvim-lint",
    optional = true,
    opts = function(_, opts)
      opts.linters_by_ft = opts.linters_by_ft or {}
      opts.linters_by_ft.markdown = {}
    end,
  },
  {
    "mason-org/mason.nvim",
    opts = function(_, opts)
      local function remove(list, value)
        if type(list) ~= "table" then
          return
        end
        for i = #list, 1, -1 do
          if list[i] == value then
            table.remove(list, i)
          end
        end
      end

      opts.ensure_installed = opts.ensure_installed or {}
      remove(opts.ensure_installed, "markdownlint-cli2")
    end,
  },
}
