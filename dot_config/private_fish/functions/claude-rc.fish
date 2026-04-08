# Run claude with ~/.claude-rc config directory
function claude-rc --wraps='claude' --description 'Run claude with ~/.claude-rc config'
    CLAUDE_CONFIG_DIR=~/.claude-rc claude $argv
end
