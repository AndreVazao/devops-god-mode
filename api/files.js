import fs from "fs";
import path from "path";

export default function handler(req, res) {
  const token = req.headers.authorization;
  const SECURE_TOKEN = process.env.RELAY_TOKEN || "GODMODE_SECURE_TOKEN";

  if (token !== `Bearer ${SECURE_TOKEN}`) {
    return res.status(401).json({ error: "unauthorized" });
  }

  const dir = path.join(process.cwd(), "repos");
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }

  if (req.method === "GET") {
    if (req.query.name) {
      const filePath = path.join(dir, req.query.name);
      if (fs.existsSync(filePath)) {
        return res.send(fs.readFileSync(filePath, "utf8"));
      } else {
        return res.status(404).send("File not found");
      }
    }

    return res.json(fs.readdirSync(dir));
  }

  if (req.method === "POST") {
    const { name, content } = req.body;
    const filePath = path.join(dir, name);
    fs.writeFileSync(filePath, content);
    return res.json({ ok: true });
  }

  res.status(405).end();
}
