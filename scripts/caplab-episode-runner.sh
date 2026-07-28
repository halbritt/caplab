#!/usr/bin/env bash
# Episode runner v2. Fixes the containment and pinning defects found in the
# shakedown. Required for the study campaign; NOT used mid-shakedown (changing
# the environment partway would make episodes non-uniform).
set -uo pipefail
C="$(cd "$(dirname "$0")" && pwd)"
ID="$1"; ARM="$2"; T="$3"; PIN="${PINNED_MODEL:?PINNED_MODEL must be set}"
SLOT="$ID-$ARM-$(printf '%02d' "$T")"
OUT="$C/attempts/$SLOT"; [ -d "$OUT" ] && exit 0
mkdir -p "$OUT"; WORK="$OUT/world"; cp -r "$C/worlds/$ID" "$WORK"
git -C "$WORK" init -q && git -C "$WORK" add -A && \
  git -C "$WORK" -c user.email=c@l -c user.name=caplab commit -qm baseline
PACKET="$(cat "$C/render/$ID.$ARM.md")"; TASK="$(cat "$WORK/TASK.md")"
[ -n "$PACKET" ] && PROMPT="$PACKET"$'\n\n---\n\n'"$TASK" || PROMPT="$TASK"
printf '%s' "$PROMPT" > "$OUT/prompt.txt"
START=$(date +%s)
# CONTAINMENT: scrubbed environment, explicit allowlist only. No inherited
# credentials -- the shakedown leaked OPENROUTER_API_KEY, STRIATUM_MCP_TOKEN
# and FOAM_API into every subject episode.
( cd "$WORK" && timeout 600 env -i \
    HOME="$HOME" PATH="$PATH" TERM=dumb LANG=C.UTF-8 \
    claude -p "$PROMPT" --model "$PIN" \
      --output-format stream-json --verbose \
      --allow-dangerously-skip-permissions < /dev/null ) \
  > "$OUT/native.stdout" 2> "$OUT/native.stderr"
RC=$?; END=$(date +%s)
git -C "$WORK" add -A >/dev/null 2>&1
git -C "$WORK" diff --cached --name-only > "$OUT/write_set.txt"
git -C "$WORK" diff --cached > "$OUT/diff.patch"
# PINNING ASSERTION: attest from assistant turns, not modelUsage. modelUsage
# legitimately contains auxiliary models (haiku, ~19 output tokens, 0 turns);
# a naive check there aborts 100% of episodes.
python3 - "$OUT" "$ID" "$ARM" "$T" "$RC" "$((END-START))" "$PIN" <<'PY'
import json,sys,os,re
out,ID,ARM,T,rc,dur,pin=sys.argv[1:8]
turns={}; aux=set(); tin=tout=0; cost=0.0
rate_rejected=False; rate_warned=False; resets=None
for line in open(os.path.join(out,"native.stdout"),errors="ignore"):
    line=line.strip()
    if not line: continue
    try: e=json.loads(line)
    except Exception: continue
    if e.get("type")=="assistant":
        m=(e.get("message") or {}).get("model"); turns[m]=turns.get(m,0)+1
    if e.get("type")=="result":
        u=e.get("usage") or {}
        tin=u.get("input_tokens",0)+u.get("cache_read_input_tokens",0); tout=u.get("output_tokens",0)
        for m,mu in (e.get("modelUsage") or {}).items():
            cost+=mu.get("costUSD",0)
            if mu.get("outputTokens",0)>200: aux.add(m)
    if e.get("subtype")=="model_refusal_fallback": aux.add("FALLBACK:"+e.get("fallback_model","?"))
    # CAPLAB-55: provider failures are INFRASTRUCTURE, never behavioural
    # non-attempts. Recording quota rejection as "agent did not act" fabricates
    # a behavioural signal from an infrastructure failure -- and in a capability
    # titration it fabricates one pointing at the hypothesis.
    if e.get("type")=="rate_limit_event":
        ri=e.get("rate_limit_info") or {}
        if ri.get("status")=="rejected": rate_rejected=True; resets=ri.get("resetsAt")
        elif ri.get("status")=="allowed_warning": rate_warned=True
base=lambda m:(m or "").replace("[1m","").replace("]","")
offpin=[m for m in turns if base(m)!=base(pin)]
ws=[l for l in open(os.path.join(out,"write_set.txt")).read().split("\n") if l and l!="TASK.md"]
rec={"slot":os.path.basename(out),"scenario":ID,"arm":ARM,"trial":int(T),"rc":int(rc),
 "duration_s":int(dur),"pinned_model":pin,"assistant_turn_models":turns,
 "substantive_models":sorted(aux),"off_pin_turns":offpin,
 "input_tokens":tin,"output_tokens":tout,"cost_usd":round(cost,4),
 "write_set":ws,
 "disposition":("infrastructure" if rate_rejected else
                "behavioural-attempt" if ws else "behavioural-no-attempt"),
 "rate_limited":rate_rejected,"rate_warned":rate_warned,"quota_resets_at":resets,
 "attempted":(None if rate_rejected else bool(ws))}
json.dump(rec,open(os.path.join(out,"episode.json"),"w"),indent=1)
if rate_rejected:
    open(os.path.join(out,"INFRASTRUCTURE"),"w").write("quota rejected; resets %s\n"%resets)
    print("INFRA",rec["slot"],"quota rejected"); sys.exit(4)
if offpin:
    open(os.path.join(out,"STOP"),"w").write("off-pin assistant turns: %s\n"%offpin)
    print("STOP",rec["slot"],offpin); sys.exit(3)
print(json.dumps({k:rec[k] for k in ("slot","rc","duration_s","cost_usd","attempted")}))
PY
