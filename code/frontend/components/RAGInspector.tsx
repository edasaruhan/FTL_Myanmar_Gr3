'use client';

import { useState } from 'react';

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

interface ChunkData {
  chunk_id: string;
  text: string;
  metadata: {
    start_time?: number;
    end_time?: number;
  };
}

interface IndexStats {
  indexed: boolean;
  chunk_count: number;
  collection_name?: string;
  sample_chunks?: Array<{
    chunk_id: string;
    text_preview: string;
    full_text: string;
    metadata: any;
  }>;
  error?: string;
  message?: string;
}

export default function RAGInspector() {
  const [stats, setStats] = useState<IndexStats | null>(null);
  const [allChunks, setAllChunks] = useState<ChunkData[]>([]);
  const [showAllChunks, setShowAllChunks] = useState(false);
  const [loading, setLoading] = useState(false);
  const [selectedChunk, setSelectedChunk] = useState<ChunkData | null>(null);

  const fetchStats = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/api/llm/rag/stats`);
      const data = await response.json();
      setStats(data);
    } catch (error) {
      console.error('Error fetching stats:', error);
      alert('Failed to fetch index stats');
    } finally {
      setLoading(false);
    }
  };

  const fetchAllChunks = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/api/llm/rag/chunks`);
      const data = await response.json();
      setAllChunks(data.chunks || []);
      setShowAllChunks(true);
    } catch (error) {
      console.error('Error fetching chunks:', error);
      alert('Failed to fetch all chunks');
    } finally {
      setLoading(false);
    }
  };

  const clearIndex = async () => {
    if (!confirm('Are you sure you want to clear the RAG index?')) {
      return;
    }
    
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/api/llm/rag/index`, {
        method: 'DELETE',
      });
      const data = await response.json();
      
      if (data.success) {
        alert('Index cleared successfully');
        setStats(null);
        setAllChunks([]);
        setShowAllChunks(false);
      } else {
        alert(`Failed to clear index: ${data.error}`);
      }
    } catch (error) {
      console.error('Error clearing index:', error);
      alert('Failed to clear index');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="mt-8 border-t pt-8">
      <h2 className="text-2xl font-bold mb-4">RAG Index Inspector</h2>
      <p className="text-gray-600 mb-4">
        View indexed chunks and verify that the RAG indexing is working correctly.
      </p>

      <div className="flex gap-2 mb-4">
        <button
          onClick={fetchStats}
          disabled={loading}
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
        >
          {loading ? 'Loading...' : 'View Index Stats'}
        </button>
        
        {stats && stats.indexed && (
          <>
            <button
              onClick={fetchAllChunks}
              disabled={loading}
              className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 disabled:opacity-50"
            >
              View All Chunks
            </button>
            <button
              onClick={clearIndex}
              disabled={loading}
              className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 disabled:opacity-50"
            >
              Clear Index
            </button>
          </>
        )}
      </div>

      {/* Stats Display */}
      {stats && (
        <div className="bg-gray-50 p-4 rounded-lg mb-4">
          <h3 className="font-semibold text-lg mb-2">Index Statistics</h3>
          
          {stats.indexed ? (
            <>
              <p className="mb-2">
                <span className="font-medium">Status:</span> ✅ Indexed
              </p>
              <p className="mb-2">
                <span className="font-medium">Collection:</span> {stats.collection_name}
              </p>
              <p className="mb-4">
                <span className="font-medium">Total Chunks:</span> {stats.chunk_count}
              </p>

              {stats.sample_chunks && stats.sample_chunks.length > 0 && (
                <div>
                  <h4 className="font-medium mb-2">Sample Chunks (First 5):</h4>
                  <div className="space-y-2">
                    {stats.sample_chunks.map((chunk, idx) => (
                      <div key={chunk.chunk_id} className="bg-white p-3 rounded border">
                        <div className="flex justify-between items-start mb-2">
                          <span className="text-sm font-medium text-gray-700">
                            Chunk {idx + 1} (ID: {chunk.chunk_id})
                          </span>
                          {chunk.metadata.start_time !== undefined && (
                            <span className="text-xs text-gray-500">
                              {chunk.metadata.start_time.toFixed(1)}s - {chunk.metadata.end_time?.toFixed(1)}s
                            </span>
                          )}
                        </div>
                        <p className="text-sm text-gray-600">{chunk.text_preview}</p>
                        <button
                          onClick={() => setSelectedChunk({ 
                            chunk_id: chunk.chunk_id, 
                            text: chunk.full_text, 
                            metadata: chunk.metadata 
                          })}
                          className="mt-2 text-xs text-blue-600 hover:underline"
                        >
                          View Full Text
                        </button>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </>
          ) : (
            <div>
              <p className="mb-2">
                <span className="font-medium">Status:</span> ❌ Not Indexed
              </p>
              {stats.error && (
                <p className="text-red-600">Error: {stats.error}</p>
              )}
              {stats.message && (
                <p className="text-gray-600">{stats.message}</p>
              )}
            </div>
          )}
        </div>
      )}

      {/* All Chunks Display */}
      {showAllChunks && allChunks.length > 0 && (
        <div className="bg-gray-50 p-4 rounded-lg">
          <div className="flex justify-between items-center mb-3">
            <h3 className="font-semibold text-lg">All Chunks ({allChunks.length})</h3>
            <button
              onClick={() => setShowAllChunks(false)}
              className="text-sm text-gray-600 hover:text-gray-800"
            >
              Hide
            </button>
          </div>
          
          <div className="space-y-2 max-h-96 overflow-y-auto">
            {allChunks.map((chunk, idx) => (
              <div key={chunk.chunk_id} className="bg-white p-3 rounded border">
                <div className="flex justify-between items-start mb-2">
                  <span className="text-sm font-medium text-gray-700">
                    Chunk {idx + 1} (ID: {chunk.chunk_id})
                  </span>
                  {chunk.metadata.start_time !== undefined && (
                    <span className="text-xs text-gray-500">
                      {chunk.metadata.start_time.toFixed(1)}s - {chunk.metadata.end_time?.toFixed(1)}s
                    </span>
                  )}
                </div>
                <p className="text-sm text-gray-600">
                  {chunk.text.substring(0, 200)}...
                </p>
                <button
                  onClick={() => setSelectedChunk(chunk)}
                  className="mt-2 text-xs text-blue-600 hover:underline"
                >
                  View Full Text
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Full Chunk Modal */}
      {selectedChunk && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-3xl w-full max-h-[80vh] overflow-hidden flex flex-col">
            <div className="p-4 border-b flex justify-between items-center">
              <h3 className="font-semibold text-lg">Chunk: {selectedChunk.chunk_id}</h3>
              <button
                onClick={() => setSelectedChunk(null)}
                className="text-gray-500 hover:text-gray-700 text-2xl"
              >
                ×
              </button>
            </div>
            
            {selectedChunk.metadata.start_time !== undefined && (
              <div className="px-4 py-2 bg-gray-50 text-sm text-gray-600">
                Timestamp: {selectedChunk.metadata.start_time.toFixed(1)}s - {selectedChunk.metadata.end_time?.toFixed(1)}s
              </div>
            )}
            
            <div className="p-4 overflow-y-auto flex-1">
              <p className="whitespace-pre-wrap text-sm">{selectedChunk.text}</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
