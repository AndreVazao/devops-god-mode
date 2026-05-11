import { kv } from "@vercel/kv";

export default async function handler(req, res) {
  const { method, url } = req;
  const token = req.headers.authorization;
  const SECURE_TOKEN = process.env.RELAY_TOKEN || "GODMODE_SECURE_TOKEN";

  if (url.includes("health")) {
    return res.json({
        status: "ok",
        mode: "relay-kv-v2",
        endpoints: ["/api/state", "/api/relay", "/api/cluster/metrics", "/api/cluster/budget"]
    });
  }

  if (token !== `Bearer ${SECURE_TOKEN}`) {
    return res.status(401).json({ error: "unauthorized" });
  }

  const TASKS_KEY = "godmode_tasks";
  const PENDING_KEY = "godmode_pending_tasks";

  try {
    if (method === "POST") {
      const task = {
        ...req.body,
        id: req.body.id || Date.now().toString(),
        timestamp: Date.now()
      };

      if (task.type === "run_code" || task.action === "run_code") {
        try {
            await kv.lpush(PENDING_KEY, JSON.stringify(task));
        } catch (e) {
            console.warn("KV lpush failed", e);
        }
        return res.json({ requiresApproval: true, task });
      }

      try {
        await kv.lpush(TASKS_KEY, JSON.stringify(task));
      } catch (e) {
        console.warn("KV lpush failed", e);
      }
      return res.json({ ok: true, id: task.id });
    }

    if (method === "GET") {
      let tasks = [];
      try {
        tasks = await kv.lrange(TASKS_KEY, 0, -1);
        if (tasks.length > 0) {
            await kv.del(TASKS_KEY);
        }
      } catch (e) {
        console.warn("KV lrange/del failed", e);
      }
      return res.json({ items: tasks.map(t => typeof t === 'string' ? JSON.parse(t) : t) });
    }

    if (method === "PUT") {
      const { approve } = req.body;
      try {
          if (approve) {
            const pending = await kv.lrange(PENDING_KEY, 0, -1);
            if (pending.length > 0) {
              for (const item of pending) {
                await kv.rpush(TASKS_KEY, typeof item === 'string' ? item : JSON.stringify(item));
              }
              await kv.del(PENDING_KEY);
            }
          } else {
            await kv.del(PENDING_KEY);
          }
      } catch (e) {
        console.warn("KV PUT ops failed", e);
      }
      return res.json({ ok: true });
    }
  } catch (error) {
    console.error("Relay API Error:", error);
    return res.status(500).json({ error: error.message });
  }

  res.status(405).end();
}
