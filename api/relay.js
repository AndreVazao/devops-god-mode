import { kv } from "@vercel/kv";

export default async function handler(req, res) {
  const { method, url } = req;
  const token = req.headers.authorization;
  const SECURE_TOKEN = process.env.RELAY_TOKEN || "GODMODE_SECURE_TOKEN";

  if (url.includes("health")) {
    return res.json({ status: "ok", mode: "relay-kv-simple" });
  }

  if (token !== `Bearer ${SECURE_TOKEN}`) {
    return res.status(401).json({ error: "unauthorized" });
  }

  const TASKS_KEY = "godmode_tasks";

  try {
    if (method === "POST") {
      const body = req.body;
      const task = {
        ...body,
        id: body.id || Date.now().toString(),
        timestamp: Date.now()
      };
      await kv.lpush(TASKS_KEY, JSON.stringify(task));
      return res.json({ ok: true, id: task.id });
    }

    if (method === "GET") {
      const tasks = await kv.lrange(TASKS_KEY, 0, -1);
      if (tasks.length > 0) {
        await kv.del(TASKS_KEY);
      }
      return res.json({ items: tasks.map(t => typeof t === 'string' ? JSON.parse(t) : t) });
    }
  } catch (error) {
    console.error("Relay API Error:", error);
    return res.status(500).json({ error: error.message });
  }

  res.status(405).end();
}
