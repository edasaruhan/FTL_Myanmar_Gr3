"use client";
import { useState } from "react";
import TranslationSummary from "@/components/TranslationSummary";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

type Segment = { start: number | null; end: number | null; text: string };
type TranscriptResponse = {
  source: string;
  transcript_text: string;
  segments: Segment[];
  file_type?: string;
};

function formatTime(s: number | null) {
  if (s == null) return "";
  const m = Math.floor(s / 60);
  const sec = Math.floor(s % 60).toString().padStart(2, "0");
  return `${m}:${sec}`;
}

export default function Home() {
  const [tab, setTab] = useState<"youtube" | "upload">("youtube");
  // YouTube
  const [youtubeUrl, setYoutubeUrl] = useState("");
  const [modelSize, setModelSize] = useState<"small" | "medium">("small");
  const [ytLoading, setYtLoading] = useState(false);
  const [ytError, setYtError] = useState("");
  const [ytResult, setYtResult] = useState<TranscriptResponse | null>(null);
  // Upload
  const [file, setFile] = useState<File | null>(null);
  const [upLoading, setUpLoading] = useState(false);
  const [upError, setUpError] = useState("");
  const [upResult, setUpResult] = useState<TranscriptResponse | null>(null);

  async function handleYoutube() {
    setYtLoading(true); setYtError(""); setYtResult(null);
    try {
      const res = await fetch(`${API_BASE}/api/transcribe/youtube`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ youtube_url: youtubeUrl, model_size: modelSize })
      });
      if (!res.ok) throw new Error((await res.json()).detail || "Error");
      setYtResult(await res.json());
    } catch (e: any) {
      setYtError(e.message || "Unknown error");
    } finally {
      setYtLoading(false);
    }
  }

  async function handleUpload() {
    if (!file) return;
    setUpLoading(true); setUpError(""); setUpResult(null);
    const form = new FormData();
    form.append("file", file);
    try {
      const res = await fetch(`${API_BASE}/api/transcribe/upload`, {
        method: "POST",
        body: form
      });
      if (!res.ok) throw new Error((await res.json()).detail || "Error");
      setUpResult(await res.json());
    } catch (e: any) {
      setUpError(e.message || "Unknown error");
    } finally {
      setUpLoading(false);
    }
  }

  return (
    <main className="max-w-2xl mx-auto py-10 px-4">
      <h1 className="text-3xl font-bold mb-6 text-center">Lecture Companion</h1>
      <div className="flex gap-2 mb-6">
        <button className={`flex-1 py-2 rounded-t ${tab==="youtube"?"bg-white border-b-2 border-blue-500":"bg-gray-200"}`} onClick={()=>setTab("youtube")}>From YouTube URL</button>
        <button className={`flex-1 py-2 rounded-t ${tab==="upload"?"bg-white border-b-2 border-blue-500":"bg-gray-200"}`} onClick={()=>setTab("upload")}>From Transcript File</button>
      </div>
      <div className="bg-white p-6 rounded shadow">
        {tab === "youtube" ? (
          <div>
            <label className="block mb-2 font-medium">YouTube URL</label>
            <input className="w-full border px-3 py-2 rounded mb-3" value={youtubeUrl} onChange={e=>setYoutubeUrl(e.target.value)} placeholder="https://youtube.com/watch?v=..." />
            <label className="block mb-2 font-medium">Model Size</label>
            <select className="w-full border px-3 py-2 rounded mb-3" value={modelSize} onChange={e=>setModelSize(e.target.value as any)}>
              <option value="small">small (fast)</option>
              <option value="medium">medium (better)</option>
            </select>
            <button className="w-full bg-blue-600 text-white py-2 rounded font-semibold" onClick={handleYoutube} disabled={ytLoading}>{ytLoading ? "Generating..." : "Generate Transcript"}</button>
            {ytError && <div className="text-red-600 mt-2">{ytError}</div>}
            {ytResult && (
              <div className="mt-6">
                <div className="font-bold mb-2">Transcript</div>
                <div className="border rounded p-3 max-h-40 overflow-y-auto whitespace-pre-line text-sm bg-gray-50 mb-4">{ytResult.transcript_text}</div>
                <div className="font-bold mb-2">Segments</div>
                <ul className="text-xs max-h-40 overflow-y-auto">
                  {ytResult.segments.map((seg,i)=>(
                    <li key={i} className="mb-1"><span className="text-gray-500">{formatTime(seg.start)} - {formatTime(seg.end)}</span> {seg.text}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        ) : (
          <div>
            <label className="block mb-2 font-medium">Upload File (.pdf, .txt, .srt, .vtt)</label>
            <input type="file" accept=".pdf,.txt,.srt,.vtt" className="mb-3" onChange={e=>setFile(e.target.files?.[0]||null)} />
            <button className="w-full bg-blue-600 text-white py-2 rounded font-semibold" onClick={handleUpload} disabled={upLoading || !file}>{upLoading ? "Parsing..." : "Parse Transcript"}</button>
            {upError && <div className="text-red-600 mt-2">{upError}</div>}
            {upResult && (
              <div className="mt-6">
                <div className="font-bold mb-2">Transcript</div>
                <div className="border rounded p-3 max-h-40 overflow-y-auto whitespace-pre-line text-sm bg-gray-50 mb-4">{upResult.transcript_text}</div>
                <div className="font-bold mb-2">Segments</div>
                <ul className="text-xs max-h-40 overflow-y-auto">
                  {upResult.segments.map((seg,i)=>(
                    <li key={i} className="mb-1"><span className="text-gray-500">{formatTime(seg.start)} - {formatTime(seg.end)}</span> {seg.text}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}
      </div>
      
      {/* Translation & Summary Section */}
      {(ytResult || upResult) && (
        <TranslationSummary transcriptText={ytResult?.transcript_text || upResult?.transcript_text || ""} />
      )}
    </main>
  );
}
