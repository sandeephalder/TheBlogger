# TheBlogger
Creates Blogger

## Hindi Chat Agent

A LangGraph conversational agent that always answers in Hindi, backed by an OpenAI
reasoning model (`gpt-5.4-mini` by default).

### Setup

```bash
export OPENAI_API_KEY="your-api-key"   # or put it in .env
```

### CLI

```bash
uv run python chat.py                                  # interactive chat
uv run python chat.py --model gpt-5.4 --effort high    # more reasoning
uv run python chat.py --message "भारत की राजधानी क्या है?"   # one-shot
```

Available models: `gpt-5.4-mini`, `gpt-5.4`, `gpt-5.6`, `o4-mini`.
Reasoning effort: `low`, `medium`, `high`.

### HTTP API

```bash
uv run python app.py

curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "नमस्ते, आप कैसे हैं?", "thread_id": "user-42"}'
```

Conversation memory is scoped to `thread_id`. It uses LangGraph's in-memory
checkpointer, so history is lost when the process restarts — swap `MemorySaver`
in `blueprint/chat_flow.py` for a persistent checkpointer to keep it.

### Layout

| File | Purpose |
|------|---------|
| `blueprint/chat_flow.py` | Builds and compiles the chat graph |
| `blueprint/states/chatstate.py` | Message-list state |
| `agents/hindi_chat_node.py` | The chat node |
| `prompts/hindi_chat_prompt.py` | Hindi system prompt |
| `llms/openai_reasoning_llm.py` | OpenAI reasoning model wrapper |
