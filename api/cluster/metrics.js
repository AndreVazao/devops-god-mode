import { kv } from '@vercel/kv';

export default async function handler(req, res) {
  const token = req.headers.authorization;
  const SECURE_TOKEN = process.env.RELAY_TOKEN || "GODMODE_SECURE_TOKEN";

  if (token !== `Bearer ${SECURE_TOKEN}`) {
    return res.status(401).json({ error: "unauthorized" });
  }

  try {
    if (req.method === "POST") {
      const { latency, cost, ok } = req.body;
      try {
        await kv.hincrby('godmode_metrics', 'completed', ok ? 1 : 0);
        await kv.hincrby('godmode_metrics', 'failed', ok ? 0 : 1);
        await kv.hincrbyfloat('godmode_metrics', 'total_cost', cost || 0);
        await kv.lpush('godmode_latency_list', latency);
        await kv.ltrim('godmode_latency_list', 0, 99);
      } catch (e) {
        console.warn("KV write failed", e);
      }
      return res.json({ ok: true });
    }

    if (req.method === "GET") {
      let metrics = {};
      let latencies = [];
      try {
        metrics = await kv.hgetall('godmode_metrics') || {};
        latencies = await kv.lrange('godmode_latency_list', 0, -1);
      } catch (e) {
        console.warn("KV fetch failed", e);
      }

      const avg = latencies.length
        ? Math.round(latencies.reduce((a, b) => a + (typeof b === 'number' ? b : parseInt(b)), 0) / latencies.length)
        : 0;

      return res.json({
        completed: parseInt(metrics.completed || 0),
        failed: parseInt(metrics.failed || 0),
        total_cost: parseFloat(metrics.total_cost || 0),
        avg_latency: avg
      });
    }
  } catch (error) {
    return res.status(500).json({ error: error.message });
  }

  res.status(405).end();
}
