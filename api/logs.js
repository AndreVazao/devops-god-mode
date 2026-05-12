let logs = [];

export default function handler(req, res) {
  const token = req.headers.authorization;
  const SECURE_TOKEN = process.env.RELAY_TOKEN || "GODMODE_SECURE_TOKEN";

  if (token !== `Bearer ${SECURE_TOKEN}`) {
    return res.status(401).json({ error: "unauthorized" });
  }

  if (req.method === "GET") {
    return res.json(logs);
  }

  if (req.method === "POST") {
    const { text } = req.body;
    logs.push(`[${new Date().toISOString()}] ${text}`);
    if (logs.length > 100) logs.shift(); // Keep last 100 logs
    return res.json({ ok: true });
  }

  res.status(405).end();
}
