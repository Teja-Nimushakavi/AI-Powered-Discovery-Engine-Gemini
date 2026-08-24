import React from 'react';

export const MetricsRow: React.FC = () => {
  return (
    <section className="grid grid-cols-1 md:grid-cols-3 gap-6">
      {/* Metric 1 */}
      <div className="glass-panel glass-inset-glow rounded-lg p-container-padding flex flex-col">
        <div className="flex justify-between items-start mb-4">
          <h3 className="font-label-md text-label-md text-on-surface-variant uppercase tracking-wider">Total Feedback Indexed</h3>
          <div className="p-2 bg-surface-container-highest rounded-lg text-primary">
            <span className="material-symbols-outlined text-[20px]">database</span>
          </div>
        </div>
        <div className="mt-auto flex items-baseline gap-2">
          <span className="font-display-lg text-display-lg text-on-background">1,000</span>
          <span className="font-body-sm text-body-sm text-secondary font-medium flex items-center">
            Reviews
          </span>
        </div>
      </div>

      {/* Metric 2 */}
      <div className="glass-panel glass-inset-glow rounded-lg p-container-padding flex flex-col border border-primary/20 relative overflow-hidden">
        {/* Subtle accent gradient for the 'top' friction point */}
        <div className="absolute top-0 right-0 w-32 h-32 bg-secondary/10 rounded-full blur-2xl -mr-10 -mt-10 pointer-events-none"></div>
        <div className="flex justify-between items-start mb-4 relative z-10">
          <h3 className="font-label-md text-label-md text-on-surface-variant uppercase tracking-wider">Top Friction Point</h3>
          <div className="p-2 bg-error-container rounded-lg text-error">
            <span className="material-symbols-outlined text-[20px]">warning</span>
          </div>
        </div>
        <div className="mt-auto relative z-10">
          <span className="font-headline-lg text-headline-lg text-on-background block leading-tight">Trust Deficit</span>
          <span className="font-body-sm text-body-sm text-on-surface-variant mt-1 block">410 Priority Mentions</span>
        </div>
      </div>

      {/* Metric 3 */}
      <div className="glass-panel glass-inset-glow rounded-lg p-container-padding flex flex-col">
        <div className="flex justify-between items-start mb-4">
          <h3 className="font-label-md text-label-md text-on-surface-variant uppercase tracking-wider">Dataset Relevance</h3>
          <div className="p-2 bg-surface-container-highest rounded-lg text-tertiary">
            <span className="material-symbols-outlined text-[20px]">fact_check</span>
          </div>
        </div>
        <div className="mt-auto flex items-baseline gap-2">
          <span className="font-display-lg text-display-lg text-on-background">95.7<span className="text-headline-md text-outline">%</span></span>
          <span className="font-body-sm text-body-sm text-outline font-medium">Relevant</span>
        </div>
      </div>
    </section>
  );
};
