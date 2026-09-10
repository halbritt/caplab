import { createHash } from "node:crypto";
import { createServer } from "node:http";
import { mkdir, readFile, readlink } from "node:fs/promises";
import { performance } from "node:perf_hooks";

const condition = process.argv[2];
if (!["ordinary", "delayed-body", "cancel-body", "pre-aborted"].includes(condition)) {
  throw new Error("unknown witness condition");
}
const { runDeepSeekMemberTurn } = await import("/source/src/v3/deepseek-runtime.ts");
const events: Array<{ event: string; ms: number }> = [];
const started = performance.now();
const record = (event: string) => events.push({ event, ms: performance.now() - started });
const controller = new AbortController();
const timers = new Set<ReturnType<typeof setTimeout>>();
let requests = 0;
const later = (callback: () => void, delay: number) => {
  const timer = setTimeout(() => { timers.delete(timer); callback(); }, delay);
  timers.add(timer);
};
const payload = JSON.stringify({
  model: "deepseek-chat",
  choices: [{ index: 0, finish_reason: "stop", message: { role: "assistant", content: "ordinary reply" } }],
  usage: { prompt_tokens: 10, completion_tokens: 3, total_tokens: 13 },
});
const server = createServer((request, response) => {
  requests++;
  record("request-arrived");
  request.resume();
  request.on("end", () => {
    response.writeHead(200, { "content-type": "application/json" });
    response.flushHeaders();
    record("headers-flushed");
    response.on("close", () => record("response-closed"));
    if (condition === "ordinary" || condition === "pre-aborted") {
      response.end(payload);
      record("body-ended");
      return;
    }
    response.write(payload.slice(0, 16));
    record("body-prefix-sent");
    if (condition === "cancel-body") {
      later(() => { record("service-aborted"); controller.abort(); }, 100);
    }
    later(() => {
      if (!response.destroyed) {
        response.end(payload.slice(16));
        record("body-ended");
      }
    }, 2000);
  });
});
await new Promise<void>((resolve, reject) => {
  server.once("error", reject);
  server.listen(0, "127.0.0.1", resolve);
});
const address = server.address();
if (address === null || typeof address === "string") throw new Error("no loopback port");
const sessionDirectory = "/tmp/council/topics/witness/sessions/deepseek";
await mkdir(sessionDirectory, { recursive: true });
const messageId = "msg_00000000-0000-4000-8000-000000000001";
const message = {
  schema: "council-message/1", id: messageId, topic: "witness", sequence: 1, revision: 1,
  kind: "operator", author: "operator", model: null, created_at: "2026-09-10T00:00:00.000Z",
  content: "Return an ordinary reply.", in_reply_to: null,
  addressing: { mode: "directed", members: ["deepseek"] }, sealed: false, seal_id: null, attachments: [],
};
if (condition === "pre-aborted") { record("service-aborted"); controller.abort(); }
record("turn-invoked");
let result;
try {
  result = await runDeepSeekMemberTurn({
    session: { schema: "council-session-ref/1", generation: 1, mode: "create", handle: "witness_session" },
    turn: { schema: "council-member-turn/1", turn_id: "turn_00000000-0000-4000-8000-000000000001",
      target_message_id: messageId, target_sequence: 1, input_cut: 1,
      delta: [{ message, attachment_paths: [] }], roots: [] },
    rootMappings: [], attachmentMappings: [], endpoint: `http://127.0.0.1:${address.port}/chat/completions`,
    apiKey: "synthetic-witness-credential", model: "deepseek-chat",
    timeoutMs: condition === "cancel-body" ? 5000 : 300,
    limits: { requestBytes: 2 * 1024 * 1024, responseBytes: 2 * 1024 * 1024, answerBytes: 256 * 1024 },
    councilHome: "/tmp/council", sessionDirectory, signal: controller.signal,
  });
  record("turn-returned");
} finally {
  for (const timer of timers) clearTimeout(timer);
  server.closeAllConnections();
  await new Promise<void>((resolve, reject) => server.close(error => error ? reject(error) : resolve()));
}
const source = await readFile("/source/src/v3/deepseek-runtime.ts");
process.stdout.write(JSON.stringify({
  schema: "caplab.council-provider-lifetime-observation/v1", condition,
  source_sha256: createHash("sha256").update(source).digest("hex"),
  node_version: process.version, net_namespace: await readlink("/proc/self/ns/net"),
  requests, events, result: {
    status: result.status, code: result.code ?? null, phase: result.phase ?? null,
    dispatched: result.dispatched, reply: result.reply ?? null,
  },
}) + "\n");
