import React from 'react';

export const OpportunityHeatmap: React.FC = () => {
  return (
    <div className="lg:col-span-5 glass-panel rounded-lg p-container-padding flex flex-col h-96">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h3 className="font-headline-md text-headline-md text-on-background">Opportunity Heatmap</h3>
          <p className="font-body-sm text-body-sm text-on-surface-variant">Purchase barriers by volume &amp; impact</p>
        </div>
        <button className="p-2 hover:bg-surface-container rounded-lg text-on-surface-variant transition-colors">
          <span className="material-symbols-outlined">filter_list</span>
        </button>
      </div>

      <div className="flex-1 grid grid-cols-2 grid-rows-3 gap-2">
        {/* High Impact / High Volume */}
        <div className="bg-error-container/80 rounded-lg p-3 flex flex-col justify-between border border-error/20 hover:border-error/50 transition-colors cursor-pointer group">
          <span className="font-label-md text-label-md text-on-error-container block">Size/Fit Ambiguity</span>
          <div className="flex justify-between items-end">
            <span className="font-headline-md text-headline-md-mobile text-on-error-container">525</span>
            <span className="material-symbols-outlined text-[16px] text-error group-hover:translate-x-1 transition-transform">arrow_forward</span>
          </div>
        </div>

        {/* High Impact / Med Volume */}
        <div className="bg-secondary-container/30 rounded-lg p-3 flex flex-col justify-between border border-secondary/10 hover:border-secondary/30 transition-colors cursor-pointer group">
          <span className="font-label-md text-label-md text-on-surface block">Discount Waiting</span>
          <div className="flex justify-between items-end">
            <span className="font-headline-md text-headline-md-mobile text-on-surface">160</span>
            <span className="material-symbols-outlined text-[16px] text-on-surface-variant group-hover:translate-x-1 transition-transform">arrow_forward</span>
          </div>
        </div>

        {/* Med Impact / High Volume */}
        <div className="bg-primary-container/20 rounded-lg p-3 flex flex-col justify-between border border-primary/10 hover:border-primary/30 transition-colors cursor-pointer group">
          <span className="font-label-md text-label-md text-on-surface block">Quality Uncertainty</span>
          <div className="flex justify-between items-end">
            <span className="font-headline-md text-headline-md-mobile text-on-surface">215</span>
            <span className="material-symbols-outlined text-[16px] text-on-surface-variant group-hover:translate-x-1 transition-transform">arrow_forward</span>
          </div>
        </div>

        {/* Med Impact / Med Volume */}
        <div className="bg-surface-container-highest rounded-lg p-3 flex flex-col justify-between border border-outline-variant/30 hover:border-outline-variant/60 transition-colors cursor-pointer group">
          <span className="font-label-md text-label-md text-on-surface block">Choice Overload</span>
          <div className="flex justify-between items-end">
            <span className="font-headline-md text-headline-md-mobile text-on-surface">125</span>
            <span className="material-symbols-outlined text-[16px] text-on-surface-variant group-hover:translate-x-1 transition-transform">arrow_forward</span>
          </div>
        </div>

        {/* Low Impact / High Volume */}
        <div className="bg-surface-container-highest rounded-lg p-3 flex flex-col justify-between border border-outline-variant/30 hover:border-outline-variant/60 transition-colors cursor-pointer group col-span-2 sm:col-span-1">
          <span className="font-label-md text-label-md text-on-surface block">Trust &amp; Reviews</span>
          <div className="flex justify-between items-end">
            <span className="font-headline-md text-headline-md-mobile text-on-surface">410</span>
            <span className="material-symbols-outlined text-[16px] text-on-surface-variant group-hover:translate-x-1 transition-transform">arrow_forward</span>
          </div>
        </div>
      </div>
    </div>
  );
};
