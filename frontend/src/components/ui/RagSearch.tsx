import React, { useState } from 'react';
import axios from 'axios';
import { AlertCircle } from 'lucide-react';

interface Citation {
  content: string;
  metadata: {
    source: string;
    sentiment: string;
  };
}

interface QueryResponse {
  answer: string;
  sources: Citation[];
}

export const RagSearch: React.FC = () => {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [response, setResponse] = useState<QueryResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    setError(null);
    setResponse(null);

    try {
      const apiUrl = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8080';
      const res = await axios.post<QueryResponse>(`${apiUrl}/api/v1/query`, {
        query,
        top_k: 5
      });
      setResponse(res.data);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch insights');
    } finally {
      setLoading(false);
    }
  };

  return (
    <section 
      className="glass-panel rounded-lg p-8 relative overflow-hidden" 
      style={{
        border: '2px solid transparent', 
        backgroundImage: 'linear-gradient(rgba(255,255,255,0.85), rgba(255,255,255,0.85)), linear-gradient(135deg, #2563eb, #8a4cfc)', 
        backgroundOrigin: 'border-box', 
        backgroundClip: 'padding-box, border-box'
      }}
    >
      {/* Abstract Background for Search */}
      <div className="absolute inset-0 bg-gradient-to-br from-surface-container-lowest to-surface-container-low opacity-50 z-0"></div>
      <div className="absolute -top-24 -right-24 w-64 h-64 bg-primary/10 rounded-full blur-3xl z-0 pointer-events-none"></div>
      <div className="absolute -bottom-24 -left-24 w-64 h-64 bg-secondary/10 rounded-full blur-3xl z-0 pointer-events-none"></div>
      
      <div className="relative z-10 max-w-4xl mx-auto flex flex-col items-center text-center">
        <h2 className="font-headline-lg text-headline-lg text-on-background mb-2">Ask the Data</h2>
        <p className="font-body-md text-body-md text-on-surface-variant mb-6 max-w-2xl">
          Query thousands of reviews, support tickets, and app store feedback using natural language to uncover hidden consumer insights.
        </p>
        
        <form onSubmit={handleSearch} className="w-full flex flex-col sm:flex-row gap-4 mb-8">
          <div className="relative flex-grow">
            <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
              <span className="material-symbols-outlined text-outline">search</span>
            </div>
            <input 
              className="w-full pl-12 pr-4 py-4 bg-white/95 border-0 rounded-md shadow-sm focus:ring-2 focus:ring-primary focus:outline-none font-body-md text-body-md text-on-background placeholder-outline transition-shadow" 
              placeholder="e.g., 'Why are users abandoning carts on Android during the evening?'" 
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              disabled={loading}
            />
          </div>
          <button 
            type="submit"
            disabled={loading || !query.trim()}
            className="bg-gradient-primary text-white px-8 py-4 rounded-md font-label-md text-label-md font-bold shadow-md hover:shadow-lg transition-all flex items-center justify-center gap-2 group flex-shrink-0 disabled:opacity-50"
          >
            {loading ? 'Analyzing...' : 'Analyze'}
            {!loading && <span className="material-symbols-outlined group-hover:scale-110 transition-transform text-[18px]">temp_preferences_custom</span>}
          </button>
        </form>

        {!response && !error && (
          <div className="mt-4 flex flex-wrap justify-center gap-2">
            <span className="font-label-md text-label-md text-outline mr-2 self-center">Suggested:</span>
            <button type="button" onClick={() => setQuery('Return policy complaints')} className="px-3 py-1 bg-surface-container-highest/50 border border-outline-variant/30 rounded-full font-body-sm text-body-sm text-on-surface-variant hover:bg-surface-container hover:text-primary transition-colors">Return policy complaints</button>
            <button type="button" onClick={() => setQuery('Sizing issues on dresses')} className="px-3 py-1 bg-surface-container-highest/50 border border-outline-variant/30 rounded-full font-body-sm text-body-sm text-on-surface-variant hover:bg-surface-container hover:text-primary transition-colors">Sizing issues on dresses</button>
          </div>
        )}

        {error && (
          <div className="w-full mt-4 flex items-center gap-3 p-4 bg-error-container/30 border border-error/50 rounded-lg text-error">
            <AlertCircle size={20} />
            <span className="font-body-md">{error}</span>
          </div>
        )}

        {response && (
          <div className="w-full mt-8 text-left animate-in fade-in slide-in-from-bottom-4 duration-500">
            <h3 className="font-headline-md text-headline-md mb-4 text-gradient-primary">AI Synthesis</h3>
            <div className="font-body-lg text-body-lg text-on-surface mb-8 whitespace-pre-wrap leading-relaxed">
              {response.answer
                .replace(/\*\*/g, '')
                .replace(/\*/g, '')
                .replace(/#+\s/g, '')
                .replace(/\[Source:\s*[^\]]+\]/gi, '')
                .replace(/\(?\[?chunk\s*\d+\]?\)?/gi, '')
                .replace(/\(?\[?review\s*\d+\]?\)?/gi, '')}
            </div>

            <h4 className="font-label-md text-label-md text-outline uppercase tracking-wider mb-4">Cited Sources</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {response.sources.map((source, i) => {
                const isPositive = source.metadata.sentiment?.toLowerCase() === 'positive';
                const isNegative = source.metadata.sentiment?.toLowerCase() === 'negative';
                return (
                  <div key={i} className={`glass-panel rounded-lg p-4 flex flex-col h-full border-t-2 ${isPositive ? 'border-t-green-500' : isNegative ? 'border-t-error' : 'border-t-secondary'}`}>
                    <div className="flex justify-between items-start mb-3">
                      <span className="px-2 py-1 bg-surface-container text-on-surface-variant rounded font-label-md text-label-md">{source.metadata.source}</span>
                      <span className={`px-2 py-1 rounded font-label-md text-[10px] uppercase tracking-wider border ${isPositive ? 'bg-green-100 text-green-700 border-green-200' : isNegative ? 'bg-error-container/50 text-error border-error/20' : 'bg-secondary-container/30 text-secondary border-secondary/20'}`}>
                        {source.metadata.sentiment}
                      </span>
                    </div>
                    <p className="font-body-sm text-body-sm text-on-surface italic line-clamp-4">
                      "{source.content}"
                    </p>
                  </div>
                );
              })}
            </div>
          </div>
        )}
      </div>
    </section>
  );
};
