import { kv } from "@vercel/kv";

export async function pushTask(task: any) {
  await kv.rpush("task_queue", JSON.stringify(task));
}

export async function pullTasks() {
  const tasks = await kv.lrange("task_queue", 0, -1);
  await kv.del("task_queue");
  return tasks.map(t => typeof t === 'string' ? JSON.parse(t) : t);
}

export async function pushResult(result: any) {
  await kv.rpush("result_queue", JSON.stringify(result));
}

export async function pullResults() {
  const results = await kv.lrange("result_queue", 0, -1);
  await kv.del("result_queue");
  return results.map(r => typeof r === 'string' ? JSON.parse(r) : r);
}
