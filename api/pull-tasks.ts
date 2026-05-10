import { pullTasks } from "./_store";

export default async function handler(req, res) {
  const token = req.headers.authorization;
  const SECURE_TOKEN = process.env.RELAY_TOKEN;

  if (SECURE_TOKEN && token !== `Bearer ${SECURE_TOKEN}`) {
    return res.status(401).json({ error: "unauthorized" });
  }

  const tasks = await pullTasks();
  res.status(200).json({ tasks });
}
