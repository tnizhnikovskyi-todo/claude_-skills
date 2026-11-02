import json, re, sys, uuid
src, dst = sys.argv[1], sys.argv[2]
parts = re.split(r'^===(USER|ASSISTANT)===\n', open(src).read(), flags=re.M)[1:]
turns = list(zip(parts[0::2], parts[1::2]))
while turns and turns[-1][0] == 'USER':
    turns.pop()  # история заканчивается ответом ассистента
sid = str(uuid.UUID(int=0x1C))
parent = None
out = []
for i, (role, text) in enumerate(turns):
    u = str(uuid.uuid5(uuid.NAMESPACE_URL, f'{src}#{i}'))
    ts = f'2026-11-01T10:{i:02d}:00.000Z'
    base = {"parentUuid": parent, "isSidechain": False, "userType": "external",
            "cwd": "/workspace", "sessionId": sid, "version": "2.1.316",
            "uuid": u, "timestamp": ts}
    if role == 'USER':
        base.update(type="user", message={"role": "user", "content": text.strip()})
    else:
        base.update(type="assistant", message={
            "id": f"msg_hist_{i}", "type": "message", "role": "assistant",
            "model": "claude-opus-5-5",
            "content": [{"type": "text", "text": text.strip()}],
            "stop_reason": "end_turn", "stop_sequence": None,
            "usage": {"input_tokens": 0, "output_tokens": 0}})
    out.append(json.dumps(base, ensure_ascii=False))
    parent = u
open(dst, 'w').write('\n'.join(out) + '\n')
print(dst, len(out), 'records')
