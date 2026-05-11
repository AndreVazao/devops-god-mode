import { kv } from "@vercel/kv";

export default async function handler(req, res) {
  const { method, url } = req;
  const token = req.headers.authorization;
  const SECURE_TOKEN = process.env.RELAY_TOKEN || "GODMODE_SECURE_TOKEN";

  // Allow health check without auth if needed, or keep it strict
  if (url.includes("health")) {
    return res.json({ status: "ok", mode: "relay-kv" });
  }

  if (token !== `Bearer ${SECURE_TOKEN}`) {
    return res.status(401).json({ error: "unauthorized" });
  }

  try {
    // 1. MOBILE -> CLOUD (Push Task)
    if (method === "POST" && url.includes("push")) {
      const body = req.body;
      const task = {
        ...body,
        id: body.id || Date.now(),
        timestamp: Date.now()
      };
      await kv.lpush("godmode_tasks", JSON.stringify(task));
      return res.json({ ok: true, id: task.id });
    }

    // 2. PC -> CLOUD (Respond Result)
    if (method === "POST" && url.includes("respond")) {
      const response = req.body;
      await kv.lpush("godmode_responses", JSON.stringify(response));
      return res.json({ ok: true });
    }

    // 3. PC -> CLOUD (Pull Tasks) OR MOBILE -> CLOUD (Pull Responses)
    if (method === "GET") {
      if (url.includes("responses")) {
        // MOBILE pulling responses
        const responses = await kv.lrange("godmode_responses", 0, -1);
        if (responses.length > 0) {
            await kv.del("godmode_responses");
        }
        return res.json(responses.map(r => typeof r === 'string' ? JSON.parse(r) : r));
      } else {
        // PC pulling tasks
        const tasks = await kv.lrange("godmode_tasks", 0, -1);
        if (tasks.length > 0) {
            await kv.del("godmode_tasks");
        }
        return res.json({ items: tasks.map(t => typeof t === 'string' ? JSON.parse(t) : t) });
      }
    }

  } catch (error) {
    console.error("Relay error:", error);
    return res.status(500).json({ error: error.message });
  }

  res.status(405).end();
}
