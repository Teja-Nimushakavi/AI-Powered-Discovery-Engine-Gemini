import React from 'react';
import { Layout } from '../components/layout/Layout';
import { MetricsRow } from '../components/dashboard/MetricsRow';
import { RagSearch } from '../components/ui/RagSearch';
import { SentimentTimeline } from '../components/dashboard/SentimentTimeline';
import { OpportunityHeatmap } from '../components/dashboard/OpportunityHeatmap';
import { CitedSources } from '../components/dashboard/CitedSources';
import { PainPointsAnalysis } from '../components/dashboard/PainPointsAnalysis';
import { FinalReport } from '../components/dashboard/FinalReport';

export type PageId = 'dashboard' | 'search' | 'analytics' | 'feedback' | 'painpoints' | 'report';

interface DashboardProps {
  activePage?: PageId;
  onNavigate?: (page: PageId) => void;
}

export const Dashboard: React.FC<DashboardProps> = ({ activePage = 'dashboard', onNavigate }) => {
  const handleSearchClick = (_query: string) => {
    // If they click a question, we navigate to the search page, but wait, we need a way to pass the query.
    // For now, we'll just navigate to the search page. The user can manually type it in, or we can use a global state.
    // Since we don't have global state for search query, we will just navigate to search.
    onNavigate?.('search');
  };

  return (
    <Layout activePage={activePage} onNavigate={onNavigate}>
      {activePage === 'dashboard' && (
        <>
          <MetricsRow />
          <RagSearch />
          <section className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            <SentimentTimeline />
            <OpportunityHeatmap />
          </section>
          <CitedSources />
          <div className="mt-8">
            <FinalReport />
          </div>
        </>
      )}

      {activePage === 'search' && (
        <>
          <div className="mb-2">
            <h1 className="font-headline-lg text-headline-lg text-on-background">Semantic Search</h1>
            <p className="font-body-md text-body-md text-on-surface-variant">Query thousands of reviews using natural language powered by RAG.</p>
          </div>
          <RagSearch />
        </>
      )}

      {activePage === 'analytics' && (
        <>
          <div className="mb-2">
            <h1 className="font-headline-lg text-headline-lg text-on-background">Analytics</h1>
            <p className="font-body-md text-body-md text-on-surface-variant">Sentiment trends, friction point analysis, and opportunity mapping.</p>
          </div>
          <MetricsRow />
          <section className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            <SentimentTimeline />
            <OpportunityHeatmap />
          </section>
        </>
      )}

      {activePage === 'feedback' && (
        <>
          <div className="mb-2">
            <h1 className="font-headline-lg text-headline-lg text-on-background">Raw Feedback</h1>
            <p className="font-body-md text-body-md text-on-surface-variant">AI-cited verbatim reviews driving key insights.</p>
          </div>
          <CitedSources />
        </>
      )}

      {activePage === 'painpoints' && (
        <>
          <div className="mb-2">
            <h1 className="font-headline-lg text-headline-lg text-on-background">Pain Points & Insights</h1>
            <p className="font-body-md text-body-md text-on-surface-variant">Analyze major friction areas and drill down into specific behavioral questions.</p>
          </div>
          <PainPointsAnalysis onSearchClick={handleSearchClick} />
        </>
      )}

      {activePage === 'report' && (
        <FinalReport />
      )}
    </Layout>
  );
};
