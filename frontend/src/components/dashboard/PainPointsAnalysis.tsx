import React from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from 'recharts';

const painPointsData = [
  { name: 'Sizing & Fit Issues', value: 37, color: '#ef4444' }, // red
  { name: 'Trust Deficit', value: 29, color: '#8b5cf6' }, // purple
  { name: 'Quality Uncertainty', value: 15, color: '#eab308' }, // yellow
  { name: 'Discount Waiting', value: 11, color: '#f97316' }, // orange
  { name: 'Choice Overload', value: 8, color: '#3b82f6' }, // blue
];

const analyticalQuestions = [
  "Why do users add fashion products to their wishlist?",
  "What prevents wishlisted products from eventually being purchased?",
  "What uncertainties remain after users have identified a product they like?",
  "What causes users to postpone a purchase?",
  "How do users compare multiple shortlisted products?",
  "What information do users seek outside Myntra/AJIO before purchasing?",
  "What role do fit, size, styling, price, reviews, occasion and social validation play?",
  "When do users use the wishlist as genuine purchase intent versus simply as a bookmarking mechanism?",
  "How do these behaviors differ across user segments?",
  "What unmet needs emerge consistently across user conversations?"
];

export const PainPointsAnalysis: React.FC<{ onSearchClick?: (query: string) => void }> = ({ onSearchClick }) => {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
      {/* Pain Points Chart */}
      <section className="glass-panel rounded-lg p-6 flex flex-col h-[500px]">
        <div className="flex justify-between items-center mb-6">
          <div>
            <h3 className="font-headline-md text-headline-md text-on-surface">Wishlist Purchase Barriers</h3>
            <p className="font-body-sm text-body-sm text-on-surface-variant">Breakdown of reasons for wishlist abandonment</p>
          </div>
          <span className="material-symbols-outlined text-outline">pie_chart</span>
        </div>
        
        <div className="flex-1 w-full relative">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={painPointsData}
                cx="50%"
                cy="45%"
                innerRadius={80}
                outerRadius={130}
                paddingAngle={5}
                dataKey="value"
                stroke="none"
              >
                {painPointsData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip 
                formatter={(value: any) => [`${value}%`, 'Percentage']}
                contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
              />
              <Legend 
                verticalAlign="bottom" 
                height={80}
                content={(props) => {
                  const { payload } = props;
                  return (
                    <ul className="grid grid-cols-2 gap-x-4 gap-y-2 mt-4 text-body-sm text-on-surface-variant">
                      {payload?.map((entry: any, index: number) => (
                        <li key={`item-${index}`} className="flex items-center gap-2">
                          <span className="w-3 h-3 rounded-full" style={{ backgroundColor: entry.color }}></span>
                          <span className="truncate">{entry.value} ({painPointsData[index].value}%)</span>
                        </li>
                      ))}
                    </ul>
                  );
                }}
              />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </section>

      {/* Analytical Deep Dives */}
      <section className="glass-panel rounded-lg p-6 flex flex-col h-[500px]">
        <div className="flex justify-between items-center mb-6 shrink-0">
          <div>
            <h3 className="font-headline-md text-headline-md text-on-surface">Analytical Deep Dives</h3>
            <p className="font-body-sm text-body-sm text-on-surface-variant">Key wishlist-to-purchase questions for RAG analysis</p>
          </div>
          <span className="material-symbols-outlined text-outline">psychology</span>
        </div>
        
        <div className="overflow-y-auto pr-2 custom-scrollbar space-y-3">
          {analyticalQuestions.map((q, i) => (
            <div 
              key={i} 
              className="p-4 rounded-lg bg-surface-container-lowest border border-outline-variant/30 hover:border-primary/50 hover:bg-primary/5 transition-all cursor-pointer group flex gap-3 items-start"
              onClick={() => onSearchClick?.(q)}
            >
              <span className="material-symbols-outlined text-primary/70 mt-0.5 group-hover:text-primary transition-colors text-[20px]">
                search_spark
              </span>
              <p className="font-body-md text-body-md text-on-surface group-hover:text-primary transition-colors">
                {q}
              </p>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
};
