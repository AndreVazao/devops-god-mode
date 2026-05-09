export default async function handler(req, res) {
    const token = req.headers.authorization;
    const SECURE_TOKEN = process.env.RELAY_TOKEN || "GODMODE_SECURE_TOKEN";

    if (token !== `Bearer ${SECURE_TOKEN}`) {
        return res.status(401).json({ error: "unauthorized" });
    }

    // WARNING: In a production serverless environment like Vercel,
    // a global variable like 'queue' will NOT persist reliably across requests.
    // This requires a database like Redis or Upstash for real persistence.
    // Keeping this logic for now as a baseline as per the requested architecture.
    if (!global.queue) {
        global.queue = [];
    }
    const queue = global.queue;

    if (req.method === "POST" && req.url.includes("push-task")) {
        const task = req.body;
        task.id = Date.now();
        task.status = "pending";
        queue.push(task);
        return res.json({ ok: true, id: task.id });
    }

    if (req.method === "GET" && req.url.includes("pull-tasks")) {
        const pending = queue.filter(t => t.status === "pending");
        pending.forEach(t => t.status = "processing");
        return res.json(pending);
    }

    if (req.method === "POST" && req.url.includes("push-result")) {
        const { id, result } = req.body;
        const task = queue.find(t => t.id === id);
        if (task) {
            task.status = "done";
            task.result = result;
        }
        return res.json({ ok: true });
    }

    res.status(404).end();
}
