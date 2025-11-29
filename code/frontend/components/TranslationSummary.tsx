"use client";
import { useState } from "react";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

type TranslationSummaryProps = {
  transcriptText: string;
};

type TranslationResponse = {
  source_language: string;
  target_language: string;
  translated_text: string;
  elapsed_ms: number;
  from_cache: boolean;
};

type SummaryResponse = {
  english_summary: string;
  burmese_summary: string;
  elapsed_ms: number;
  from_cache: boolean;
};

export default function TranslationSummary({ transcriptText }: TranslationSummaryProps) {
  const [translating, setTranslating] = useState(false);
  const [summarizing, setSummarizing] = useState(false);
  const [translationError, setTranslationError] = useState("");
  const [summaryError, setSummaryError] = useState("");
  const [translation, setTranslation] = useState<TranslationResponse | null>(null);
  const [summaries, setSummaries] = useState<SummaryResponse | null>(null);

  async function handleTranslate() {
    setTranslating(true);
    setTranslationError("");
    setTranslation(null);
    try {
      const res = await fetch(`${API_BASE}/api/llm/translate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ transcript_text: transcriptText }),
      });
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || "Translation failed");
      }
      setTranslation(await res.json());
    } catch (e: any) {
      setTranslationError(e.message || "Unknown error");
    } finally {
      setTranslating(false);
    }
  }

  async function handleSummarize() {
    setSummarizing(true);
    setSummaryError("");
    setSummaries(null);
    try {
      const res = await fetch(`${API_BASE}/api/llm/summarize`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ transcript_text: transcriptText }),
      });
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || "Summarization failed");
      }
      setSummaries(await res.json());
    } catch (e: any) {
      setSummaryError(e.message || "Unknown error");
    } finally {
      setSummarizing(false);
    }
  }

  return (
    <div className="mt-8 border-t pt-6">
      <h2 className="text-2xl font-bold mb-4">Translation & Summary</h2>
      
      {/* Current Transcript */}
      <div className="mb-4">
        <h3 className="font-semibold mb-2">Current English Transcript</h3>
        <div className="border rounded p-3 bg-gray-50 max-h-40 overflow-y-auto text-sm whitespace-pre-line">
          {transcriptText || "(No transcript available)"}
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex gap-3 mb-6">
        <button
          onClick={handleTranslate}
          disabled={translating || !transcriptText}
          className="px-4 py-2 bg-blue-600 text-white rounded font-semibold disabled:bg-gray-400"
        >
          {translating ? "Translating..." : "Translate to Burmese"}
        </button>
        <button
          onClick={handleSummarize}
          disabled={summarizing || !transcriptText}
          className="px-4 py-2 bg-green-600 text-white rounded font-semibold disabled:bg-gray-400"
        >
          {summarizing ? "Generating Summaries..." : "Generate Summaries"}
        </button>
      </div>

      {/* Translation Result */}
      {translationError && <div className="text-red-600 mb-4">{translationError}</div>}
      {translation && (
        <div className="mb-6">
          <div className="flex justify-between items-center mb-2">
            <h3 className="font-semibold">Burmese Translation</h3>
            <span className="text-xs text-gray-500">
              Took {(translation.elapsed_ms / 1000).toFixed(2)}s
              {translation.from_cache && " (cached)"}
            </span>
          </div>
          <div className="border rounded p-4 bg-gray-50 max-h-60 overflow-y-auto whitespace-pre-line">
            {translation.translated_text}
          </div>
        </div>
      )}

      {/* Summary Results */}
      {summaryError && <div className="text-red-600 mb-4">{summaryError}</div>}
      {summaries && (
        <>
          <div className="text-xs text-gray-500 mb-2 text-right">
            Took {(summaries.elapsed_ms / 1000).toFixed(2)}s
            {summaries.from_cache && " (cached)"}
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="border rounded p-4 bg-white shadow">
              <h3 className="font-semibold mb-2">English Summary</h3>
              <div className="text-sm whitespace-pre-line max-h-60 overflow-y-auto">
                {summaries.english_summary}
              </div>
            </div>
            <div className="border rounded p-4 bg-white shadow">
              <h3 className="font-semibold mb-2">Burmese Summary</h3>
              <div className="text-sm whitespace-pre-line max-h-60 overflow-y-auto">
                {summaries.burmese_summary}
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
