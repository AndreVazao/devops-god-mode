import { pushResult } from "./_store";

export default async function handler(req, res) {
  const token = req.headers.authorization;
  const SECURE_TOKEN = process.env.RELAY_TOKEN;

  if (SECURE_TOKEN && token !== `Bearer ${SECURE_TOKEN}`) {
    return res.status(401).json({ error: "unauthorized" });
  }

  if (req.method !== "POST") return res.status(405).end();

  await pushResult(req.body);
  res.status(200).json({ ok: true });
}
