import { kv } from '@vercel/kv';

function hash(s) {
  let h = 0;
  for (let i = 0; i < s.length; i++) h = ((h << 5) - h) + s.charCodeAt(i) | 0;
  return h.toString();
}

export default async function handler(req, res) {
  const { method } = req;

  if (method === "POST") {
    const t = req.body;
    const id = t.id || `${Date.now()}-${Math.random()}`;
    const key = hash((t.role || "") + (t.content || ""));

    // Dedupe check
    const existing = await kv.get(`godmode_task_dedupe_${key}`);
    if (existing) {
      return res.json({ ok: true, deduped: true });
    }

    const task = {
      id, key,
      role: t.role || "dev",
      content: t.content || "",
      priority: t.priority ?? 5,
      attempts: 0,
      created_at: Date.now(),
      chatId: t.chatId || "global"
    };

    await kv.zadd('godmode_cluster_queue', { score: task.priority, member: JSON.stringify(task) });
    await kv.set(`godmode_task_dedupe_${key}`, id, { ex: 300 }); // 5 min dedupe

    return res.json({ ok: true, id });
  }

  if (method === "GET") {
    const { role, node_id } = req.query;

    // Simplificado: pega todos e filtra por role. Em prod usaríamos filas separadas.
    const allTasks = await kv.zrange('godmode_cluster_queue', 0, -1);
    let taskToReturn = null;

    for (const tStr of allTasks) {
      const t = typeof tStr === 'string' ? JSON.parse(tStr) : tStr;
      if (t.role === role) {
        taskToReturn = t;
        await kv.zrem('godmode_cluster_queue', JSON.stringify(t));
        await kv.hset('godmode_cluster_inflight', { [t.id]: JSON.stringify({ ...t, node_id, taken_at: Date.now() }) });
        break;
      }
    }

    return res.json({ task: taskToReturn });
  }

  if (method === "PUT") {
    const { task_id, ok, task } = req.body;
    await kv.hdel('godmode_cluster_inflight', task_id);

    if (!ok && task) {
      task.attempts = (task.attempts || 0) + 1;
      if (task.attempts < 3) {
        // Requeue with lower priority (higher score)
        task.priority += 1;
        await kv.zadd('godmode_cluster_queue', { score: task.priority, member: JSON.stringify(task) });
      }
    }
    return res.json({ ok: true });
  }

  res.status(405).end();
}
