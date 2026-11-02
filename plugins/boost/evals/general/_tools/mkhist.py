"""Собирает минимальный транскрипт Claude Code (.jsonl) из JSON-списка ходов.
Вход: [{"role":"user"|"assistant","text":"..."}]. Выход: jsonl для context.history_file."""
import json, sys, uuid
turns = json.load(open(sys.argv[1]))
sid = str(uuid.uuid5(uuid.NAMESPACE_URL, sys.argv[1]))
out, parent = [], None
for i, t in enumerate(turns):
    u = str(uuid.uuid5(uuid.NAMESPACE_URL, f"{sys.argv[1]}#{i}"))
    ts = f"2026-11-01T10:{i:02d}:00.000Z"
    base = {"parentUuid": parent, "isSidechain": False, "userType": "external",
            "cwd": "/workspace", "sessionId": sid, "version": "2.1.316",
            "uuid": u, "timestamp": ts, "type": t["role"]}
    if t["role"] == "user":
        base["message"] = {"role": "user", "content": t["text"]}
    else:
        base["message"] = {"id": f"msg_hist_{i}", "type": "message", "role": "assistant",
                           "model": "claude-opus-5-5", "content": [{"type": "text", "text": t["text"]}],
                           "stop_reason": "end_turn", "stop_sequence": None,
                           "usage": {"input_tokens": 0, "output_tokens": 0}}
    out.append(json.dumps(base, ensure_ascii=False)); parent = u
open(sys.argv[2], "w").write("\n".join(out) + "\n")
