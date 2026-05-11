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
    let state = await kv.get(STATE_KEY);
    if (!state) {
      state = {
        chats: {},
        activeChat: null
      };
    } else if (typeof state === 'string') {
        state = JSON.parse(state);
    }

    if (method === "GET") {
      return res.json(state);
    }

    if (method === "POST") {
      const { type, payload } = req.body;

      if (type === "NEW_CHAT") {
        const id = Date.now().toString();
        state.chats[id] = {
          id,
          name: "Novo chat",
          messages: [],
          unread: false
        };
        state.activeChat = id;
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

      if (type === "RENAME") {
        const { chatId, name } = payload;
        if (state.chats[chatId]) {
            state.chats[chatId].name = name;
        }
      }

      if (type === "UPDATE_CHAT") {
          const { id, messages, name } = payload;
          if (state.chats[id]) {
              state.chats[id].messages = messages || state.chats[id].messages;
              state.chats[id].name = name || state.chats[id].name;
          }
      }

      if (type === "SET_ACTIVE") {
          const { chatId } = payload;
          if (state.chats[chatId]) {
              state.activeChat = chatId;
          }
      }

      await kv.set(STATE_KEY, JSON.stringify(state));
      return res.json({ ok: true });
    }
  } catch (error) {
    console.error("State API Error:", error);
    return res.status(500).json({ error: error.message });
  }

  res.status(405).end();
}
