import { kv } from "@vercel/kv";

export default async function handler(req, res) {
  const { method } = req;
  const token = req.headers.authorization;
  const SECURE_TOKEN = process.env.RELAY_TOKEN || "GODMODE_SECURE_TOKEN";

  if (token !== `Bearer ${SECURE_TOKEN}`) {
    return res.status(401).json({ error: "unauthorized" });
  }

  const STATE_KEY = "godmode_state";

  try {
    let state;
    try {
        state = await kv.get(STATE_KEY);
    } catch (e) {
        console.warn("KV get failed", e);
    }

    const defaultAgents = [
        { name: "Python Agent", status: "idle", output: "" },
        { name: "Node Agent", status: "idle", output: "" },
        { name: "HTML Agent", status: "idle", output: "" },
        { name: "React Agent", status: "idle", output: "" },
        { name: "Integration Agent", status: "idle", output: "" },
        { name: "Deploy Agent", status: "idle", output: "" },
        { name: "CI/CD Agent", status: "idle", output: "" },
        { name: "Test Agent", status: "idle", output: "" },
        { name: "Security Agent", status: "idle", output: "" },
        { name: "UI Agent", status: "idle", output: "" }
    ];

    if (!state) {
      state = {
        chats: {
            "default": {
                id: "default",
                name: "God Mode",
                messages: [
                    {
                        id: "initial",
                        role: "system",
                        text: "God Mode Online. À espera de comandos.",
                        timestamp: new Date().toISOString()
                    }
                ]
            }
        },
        activeChat: "default",
        agents: defaultAgents
      };
    } else if (typeof state === 'string') {
        state = JSON.parse(state);
    }

    if (!state.agents || state.agents.length < 10) {
        state.agents = defaultAgents;
    }

    if (method === "GET") {
      return res.json(state);
    }

    if (method === "POST") {
      const { type, payload } = req.body;

      if (type === "UPDATE_AGENTS") {
          const { name, status, output } = payload;
          const agentIndex = state.agents.findIndex(a => a.name === name);
          if (agentIndex !== -1) {
              state.agents[agentIndex].status = status;
              state.agents[agentIndex].output = output;
          }
      }

      if (type === "MESSAGE") {
        const { chatId, message } = payload;
        const targetChatId = (chatId === "auto" || !chatId) ? state.activeChat : chatId;

        if (targetChatId && state.chats[targetChatId]) {
            state.chats[targetChatId].messages.push({
                ...message,
                id: message.id || Date.now().toString(),
                timestamp: message.timestamp || new Date().toISOString()
            });
        }
      }

      if (type === "NEW_CHAT") {
        const id = Date.now().toString();
        state.chats[id] = { id, name: payload?.name || "Novo chat", messages: [], unread: false };
        state.activeChat = id;
      }

      if (type === "SET_ACTIVE") {
          const { chatId } = payload;
          if (state.chats[chatId]) state.activeChat = chatId;
      }

      await kv.set(STATE_KEY, JSON.stringify(state));
      return res.json({ ok: true });
    }
  } catch (error) {
    return res.status(500).json({ error: error.message });
  }
}
