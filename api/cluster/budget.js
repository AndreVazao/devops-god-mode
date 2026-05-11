import { kv } from '@vercel/kv';

export default async function handler(req, res) {
  const token = req.headers.authorization;
  const SECURE_TOKEN = process.env.RELAY_TOKEN || "GODMODE_SECURE_TOKEN";

  if (token !== `Bearer ${SECURE_TOKEN}`) {
    return res.status(401).json({ error: "unauthorized" });
  }

  try {
    if (req.method === "POST") {
      const { cost } = req.body;
      let spent = 0;
      let limit = 5.0;
      try {
        spent = await kv.hincrbyfloat('godmode_budget', 'spent', cost || 0);
        limit = await kv.hget('godmode_budget', 'daily_limit') || 5.0;
      } catch (e) {
        console.warn("KV write failed", e);
      }
      return res.json({ ok: true, spent, remaining: limit - spent });
    }

    if (req.method === "GET") {
      let spent = 0;
      let limit = 5.0;
      try {
        spent = await kv.hget('godmode_budget', 'spent') || 0;
        limit = await kv.hget('godmode_budget', 'daily_limit') || 5.0;
      } catch (e) {
        console.warn("KV read failed", e);
      }
      return res.json({ spent, limit, remaining: limit - spent });
    }
  } catch (error) {
    return res.status(500).json({ error: error.message });
  }

  res.status(405).end();
}
