import React, { useState } from "react";

interface KnowledgeSearchProps {
  apiBaseUrl: string;
  tenantId: string;
}

export function KnowledgeSearch({ apiBaseUrl, tenantId }: KnowledgeSearchProps) {
  const [query, setQuery] = useState("");
  const [answer, setAnswer] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const runSearch = async () => {
    if (!query.trim()) return;
    setLoading(true);
    const res = await fetch(`${apiBaseUrl}/api/v1/knowledge/query`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-Tenant-ID": tenantId,
      },
      body: JSON.stringify({ query }),
    });
    const data = await res.json();
    setAnswer(data.answer ?? null);
    setLoading(false);
  };

  return (
    <div className="ucp-knowledge-search">
      <div className="search-row">
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search internal knowledge…"
        />
        <button onClick={runSearch} disabled={loading}>
          Search
        </button>
      </div>
      {loading && <p>Searching…</p>}
      {answer && <div className="answer">{answer}</div>}
    </div>
  );
}
