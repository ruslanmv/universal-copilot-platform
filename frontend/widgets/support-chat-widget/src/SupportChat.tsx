import React, { useState } from "react";

interface Message {
  role: "user" | "assistant";
  content: string;
}

interface SupportChatProps {
  apiBaseUrl: string;
  tenantId: string;
}

export function SupportChat({ apiBaseUrl, tenantId }: SupportChatProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  const sendMessage = async () => {
    if (!input.trim()) return;
    const newMessages = [...messages, { role: "user", content: input }];
    setMessages(newMessages);
    setInput("");
    setLoading(true);

    const res = await fetch(`${apiBaseUrl}/api/v1/support/query`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-Tenant-ID": tenantId,
      },
      body: JSON.stringify({ message: input, channel: "web" }),
    });
    const data = await res.json();
    setMessages([
      ...newMessages,
      { role: "assistant", content: data.answer ?? "[no answer]" },
    ]);
    setLoading(false);
  };

  return (
    <div className="ucp-support-chat">
      <div className="messages">
        {messages.map((m, idx) => (
          <div key={idx} className={`msg msg-${m.role}`}>
            {m.content}
          </div>
        ))}
        {loading && <div className="msg msg-assistant">Thinking…</div>}
      </div>
      <div className="input-row">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask support…"
        />
        <button onClick={sendMessage} disabled={loading}>
          Send
        </button>
      </div>
    </div>
  );
}
