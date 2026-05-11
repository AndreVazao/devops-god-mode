import { kv } from '@vercel/kv';

export default async function handler(req, res) {
  if (req.method === "POST") {
    const { cost } = req.body;
    const spent = await kv.hincrbyfloat('godmode_budget', 'spent', cost || 0);
    const limit = await kv.hget('godmode_budget', 'daily_limit') || 5.0;

    return res.json({ ok: true, spent, remaining: limit - spent });
  }

  if (req.method === "GET") {
    const spent = await kv.hget('godmode_budget', 'spent') || 0;
    const limit = await kv.hget('godmode_budget', 'daily_limit') || 5.0;
    return res.json({ spent, limit, remaining: limit - spent });
  }

  res.status(405).end();
}
