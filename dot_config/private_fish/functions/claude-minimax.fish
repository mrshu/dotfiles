# MiniMax M2.7 via Anthropic-compatible API
# See: https://platform.minimax.io/docs/guides/text-ai-coding-tools
function claude-minimax --wraps='claude' --description 'Run Claude Code against MiniMax M2.7 API'
    ANTHROPIC_BASE_URL="https://api.minimax.io/anthropic" \
        ANTHROPIC_AUTH_TOKEN=(keepassxc-proxy-getpw "https://api.minimax.io" --filter name="MiniMax API Key") \
        ANTHROPIC_MODEL="MiniMax-M2.7" \
        ANTHROPIC_SMALL_FAST_MODEL="MiniMax-M2.7" \
        ANTHROPIC_DEFAULT_SONNET_MODEL="MiniMax-M2.7" \
        ANTHROPIC_DEFAULT_OPUS_MODEL="MiniMax-M2.7" \
        ANTHROPIC_DEFAULT_HAIKU_MODEL="MiniMax-M2.7" \
        API_TIMEOUT_MS="3000000" \
        CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC="1" \
        claude --strict-mcp-config --mcp-config ~/.claude/minimax.mcp.json $argv
end
