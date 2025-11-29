"use client";
import { useState } from "react";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

type RAGProps = {
  transcriptText: string;
  segments?: any[];
};

type ChunkInfo = {
  chunk_id: string;
  score: number;
  text_preview: string;
  start_time?: number;
  end_time?: number;
};

type RAGResponse = {
  answer: string;
  elapsed_ms: number;
  top_chunks: ChunkInfo[];
  from_cache: boolean;
};

export default function RAGComponent({ transcriptText, segments }: RAGProps) {
  const [question, setQuestion] = useState("");
  const [indexing, setIndexing] = useState(false);
  const [querying, setQuerying] = useState(false);
  const [indexed, setIndexed] = useState(false);
  const [error, setError] = useState("");
  const [response, setResponse] = useState<RAGResponse | null>(null);
  const [showChunks, setShowChunks] = useState(false);

  async function handleIndex() {
    setIndexing(true);
    setError("");
    try {
      const res = await fetch(`${API_BASE}/api/llm/rag/index`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
          transcript_text: transcriptText,
          segments: segments 
        }),
      });
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || "Index failed");
      }
      setIndexed(true);
    } catch (e: any) {
      setError(e.message || "Unknown error");
    } finally {
      setIndexing(false);
    }
  }

  async function handleQuery() {
    if (!question.trim()) return;
    setQuerying(true);
    setError("");
    setResponse(null);
    try {
      const res = await fetch(`${API_BASE}/api/llm/rag/query`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question }),
      });
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || "Query failed");
      }
      setResponse(await res.json());
    } catch (e: any) {
      setError(e.message || "Unknown error");
    } finally {
      setQuerying(false);
    }
  }

  function formatTime(s?: number) {
    if (s == null) return "";
    const m = Math.floor(s / 60);
    const sec = Math.floor(s % 60).toString().padStart(2, "0");
    return `${m}:${sec}`;
  }

  return (
    <div className="mt-8 border-t pt-6">
      <h2 className="text-2xl font-bold mb-4">Ask Questions (RAG)</h2>
      
      {!indexed && (
        <div className="mb-4">
          <button
            onClick={handleIndex}
            disabled={indexing || !transcriptText}
            className="px-4 py-2 bg-purple-600 text-white rounded font-semibold disabled:bg-gray-400"
          >
            {indexing ? "Indexing transcript..." : "Index Transcript for Q&A"}
          </button>
          <p className="text-sm text-gray-600 mt-2">Index the transcript first to enable question answering.</p>
        </div>
      )}

      {indexed && (
        <div>
          <div className="mb-4">
            <input
              type="text"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleQuery()}
              placeholder="Ask a question about the transcript..."
              className="w-full border px-3 py-2 rounded mb-2"
            />
            <button
              onClick={handleQuery}
              disabled={querying || !question.trim()}
              className="px-4 py-2 bg-purple-600 text-white rounded font-semibold disabled:bg-gray-400"
            >
              {querying ? "Thinking..." : "Ask"}
            </button>
          </div>

          {error && <div className="text-red-600 mb-4">{error}</div>}

          {response && (
            <div className="border rounded p-4 bg-white shadow">
              <div className="flex justify-between items-start mb-3">
                <h3 className="font-semibold">Answer</h3>
                <div className="flex items-center gap-2">
                  <span className="text-xs text-gray-500">
                    Took {(response.elapsed_ms / 1000).toFixed(2)}s
                    {response.from_cache && " (cached)"}
                  </span>
                  {response.top_chunks.length > 0 && (
                    <button
                      onClick={() => setShowChunks(!showChunks)}
                      className="text-blue-600 hover:text-blue-800 text-xs"
                      title="Show source chunks"
                    >
                      ℹ️
                    </button>
                  )}
                </div>
              </div>
              <div className="text-sm whitespace-pre-line mb-4">{response.answer}</div>

              {showChunks && response.top_chunks.length > 0 && (
                <div className="border-t pt-3 mt-3">
                  <h4 className="font-semibold text-sm mb-2">Top 3 Source Chunks:</h4>
                  {response.top_chunks.map((chunk, i) => (
                    <div key={chunk.chunk_id} className="mb-2 p-2 bg-gray-50 rounded text-xs">
                      <div className="flex justify-between mb-1">
                        <span className="font-medium">Chunk {i + 1} (score: {chunk.score.toFixed(2)})</span>
                        {(chunk.start_time != null || chunk.end_time != null) && (
                          <span className="text-gray-500">
                            {formatTime(chunk.start_time)} - {formatTime(chunk.end_time)}
                          </span>
                        )}
                      </div>
                      <div className="text-gray-700">{chunk.text_preview}</div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
