return {
  {
    "MeanderingProgrammer/render-markdown.nvim",
    opts = {
      pipe_table = {
        enabled = true,
      },
    },
    config = function(_, opts)
      require("render-markdown").setup(opts)

      local ok, tbl = pcall(require, "render-markdown.render.markdown.table")
      if not ok or tbl._safe_layout then
        return
      end

      tbl._safe_layout = true
      local str = require("render-markdown.lib.str")

      -- Avoid crashing on odd pipe table layouts.
      tbl.parse_row = function(self, node, num_cols)
        local pipes, cells = self:parse_cells(node, "pipe_table_cell")
        if not pipes or not cells or #cells ~= num_cols then
          return nil
        end

        local cols = {}
        for i, cell in ipairs(cells) do
          local start_col, end_col = pipes[i].end_col, pipes[i + 1].start_col
          local width = (end_col - start_col)
            - (cell.end_col - cell.start_col)
            + self.context:width(cell)
            + self.config.cell_offset({ node = cell:get() })

          if width < 0 then
            width = 0
          end

          cols[#cols + 1] = {
            row = cell.start_row,
            start_col = cell.start_col,
            end_col = cell.end_col,
            width = width,
            space = {
              left = math.max(cell.start_col - start_col, 0),
              right = math.max(str.spaces("end", cell.text), 0),
            },
          }
        end

        return { node = node, pipes = pipes, cols = cols }
      end
    end,
  },
}
