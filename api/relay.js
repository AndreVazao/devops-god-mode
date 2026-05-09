import { kv } from "@vercel/kv";

export default async function handler(req, res) {
    const token = req.headers.authorization;
    const SECURE_TOKEN = process.env.RELAY_TOKEN || "GODMODE_SECURE_TOKEN";

    if (token !== `Bearer ${SECURE_TOKEN}`) {
        return res.status(401).json({ error: "unauthorized" });
    }

    if (req.method === "POST" && req.url.includes("push-task")) {
        const task = req.body;
        task.id = Date.now();
        task.status = "pending";
        // Push task to the 'tasks' list in KV
        await kv.lpush("tasks", JSON.stringify(task));
        return res.json({ ok: true, id: task.id });
    }

    if (req.method === "GET" && req.url.includes("pull-tasks")) {
        // Pull all tasks from the list (this is a simplified implementation for the demo)
        // In a real scenario, we might want to pop them or use a more sophisticated queue.
        const tasks = await kv.lrange("tasks", 0, -1);
        const parsedTasks = tasks.map(t => typeof t === 'string' ? JSON.parse(t) : t);

        const pending = parsedTasks.filter(t => t.status === "pending");

        // Update status to processing for pulled tasks
        for (const t of pending) {
            t.status = "processing";
        }

        // Update the tasks in KV (note: this is inefficient but follows the architecture)
        await kv.del("tasks");
        for (const t of parsedTasks) {
            await kv.rpush("tasks", JSON.stringify(t));
        }

        return res.json(pending);
    }

    if (req.method === "POST" && req.url.includes("push-result")) {
        const { id, result } = req.body;

        const tasks = await kv.lrange("tasks", 0, -1);
        const parsedTasks = tasks.map(t => typeof t === 'string' ? JSON.parse(t) : t);

        const taskIndex = parsedTasks.findIndex(t => t.id === id);
        if (taskIndex !== -1) {
            parsedTasks[taskIndex].status = "done";
            parsedTasks[taskIndex].result = result;

            // Update the tasks in KV
            await kv.del("tasks");
            for (const t of parsedTasks) {
                await kv.rpush("tasks", JSON.stringify(t));
            }
        }
        return res.json({ ok: true });
    }

    res.status(404).end();
}
