import { kv } from '@vercel/kv';

export default async function handler(req, res) {
  if (req.method === "POST") {
    const { latency, cost, ok } = req.body;

    await kv.hincrby('godmode_metrics', 'completed', ok ? 1 : 0);
    await kv.hincrby('godmode_metrics', 'failed', ok ? 0 : 1);
    await kv.hincrbyfloat('godmode_metrics', 'total_cost', cost || 0);

    // Store latency in a list to calculate average
    await kv.lpush('godmode_latency_list', latency);
    await kv.ltrim('godmode_latency_list', 0, 99); // Keep last 100

    return res.json({ ok: true });
  }

  if (req.method === "GET") {
    const metrics = await kv.hgetall('godmode_metrics') || {};
    const latencies = await kv.lrange('godmode_latency_list', 0, -1);

    const avg = latencies.length
      ? Math.round(latencies.reduce((a, b) => a + b, 0) / latencies.length)
      : 0;

    return res.json({
      completed: parseInt(metrics.completed || 0),
      failed: parseInt(metrics.failed || 0),
      total_cost: parseFloat(metrics.total_cost || 0),
      avg_latency: avg
    });
  }

  res.status(405).end();
}
