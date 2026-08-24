import React from 'react';

export const CitedSources: React.FC = () => {
  return (
    <section className="space-y-4">
      <div className="flex justify-between items-end">
        <div>
          <h3 className="font-headline-md text-headline-md text-on-background">AI-Cited Raw Feedback</h3>
          <p className="font-body-sm text-body-sm text-on-surface-variant">Selected verbatim reviews driving the current 'Checkout Latency' anomaly.</p>
        </div>
        <a className="font-label-md text-label-md text-primary hover:underline flex items-center gap-1" href="#">
          View All Sources <span className="material-symbols-outlined text-[16px]">chevron_right</span>
        </a>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {/* Card 1 */}
        <div className="glass-panel rounded-xl p-6 flex flex-col h-full border-t-2 border-t-error">
          <div className="flex justify-between items-start mb-3">
            <div className="flex items-center gap-2">
              <span className="px-2 py-1 bg-surface-container text-on-surface-variant rounded font-label-md text-label-md flex items-center gap-1">
                <span className="material-symbols-outlined text-[14px]">phone_iphone</span> App Store
              </span>
              <span className="text-xs text-outline font-body-sm">2 hours ago</span>
            </div>
            <span className="px-2 py-1 bg-error-container/50 text-error rounded font-label-md text-[10px] uppercase tracking-wider border border-error/20">Negative</span>
          </div>
          <p className="font-body-md text-body-md text-on-surface italic flex-grow">
            "Love the clothes but the app is unusable lately. Every time I try to go to my cart to pay, it just spins for like 30 seconds before crashing."
          </p>
          <div className="mt-4 pt-4 border-t border-outline-variant/30 flex items-center justify-between">
            <span className="font-body-sm text-body-sm text-outline">User ID: a8f9...2c</span>
            <a href="https://apps.apple.com/in/app/myntra-fashion-shopping-app/id907394059" target="_blank" rel="noopener noreferrer" className="text-primary hover:bg-primary/5 p-1 rounded transition-colors inline-block" title="View in App Store">
              <span className="material-symbols-outlined text-[18px]">open_in_new</span>
            </a>
          </div>
        </div>

        {/* Card 2 */}
        <div className="glass-panel rounded-xl p-6 flex flex-col h-full border-t-2 border-t-error">
          <div className="flex justify-between items-start mb-3">
            <div className="flex items-center gap-2">
              <span className="px-2 py-1 bg-surface-container text-on-surface-variant rounded font-label-md text-label-md flex items-center gap-1">
                <span className="material-symbols-outlined text-[14px]">android</span> Play Store
              </span>
              <span className="text-xs text-outline font-body-sm">5 hours ago</span>
            </div>
            <span className="px-2 py-1 bg-error-container/50 text-error rounded font-label-md text-[10px] uppercase tracking-wider border border-error/20">Negative</span>
          </div>
          <p className="font-body-md text-body-md text-on-surface italic flex-grow">
            "Payment keeps failing. I hit complete order, it loads forever, then says error. Tried 3 different cards. Giving up."
          </p>
          <div className="mt-4 pt-4 border-t border-outline-variant/30 flex items-center justify-between">
            <span className="font-body-sm text-body-sm text-outline">User ID: v7x2...9m</span>
            <a href="https://play.google.com/store/apps/details?id=com.myntra.android" target="_blank" rel="noopener noreferrer" className="text-primary hover:bg-primary/5 p-1 rounded transition-colors inline-block" title="View in Play Store">
              <span className="material-symbols-outlined text-[18px]">open_in_new</span>
            </a>
          </div>
        </div>

        {/* Card 3 */}
        <div className="glass-panel rounded-xl p-6 flex flex-col h-full border-t-2 border-t-secondary">
          <div className="flex justify-between items-start mb-3">
            <div className="flex items-center gap-2">
              <span className="px-2 py-1 bg-surface-container text-on-surface-variant rounded font-label-md text-label-md flex items-center gap-1">
                <span className="material-symbols-outlined text-[14px]">support_agent</span> Helpdesk
              </span>
              <span className="text-xs text-outline font-body-sm">1 day ago</span>
            </div>
            <span className="px-2 py-1 bg-secondary-container/30 text-secondary rounded font-label-md text-[10px] uppercase tracking-wider border border-secondary/20">Neutral</span>
          </div>
          <p className="font-body-md text-body-md text-on-surface italic flex-grow">
            "I managed to order but the checkout process felt extremely sluggish compared to last month. Is there an issue with the servers?"
          </p>
          <div className="mt-4 pt-4 border-t border-outline-variant/30 flex items-center justify-between">
            <span className="font-body-sm text-body-sm text-outline">Ticket: #48291</span>
            <a href="https://www.myntra.com/contactus" target="_blank" rel="noopener noreferrer" className="text-primary hover:bg-primary/5 p-1 rounded transition-colors inline-block" title="View Ticket">
              <span className="material-symbols-outlined text-[18px]">open_in_new</span>
            </a>
          </div>
        </div>
      </div>
    </section>
  );
};
