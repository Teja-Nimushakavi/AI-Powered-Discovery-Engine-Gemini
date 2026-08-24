import React from 'react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const mockData = [
  { date: 'Oct 1', sentiment: 45 },
  { date: 'Oct 5', sentiment: 52 },
  { date: 'Oct 10', sentiment: 38 },
  { date: 'Oct 15', sentiment: 65 },
  { date: 'Oct 20', sentiment: 58 },
  { date: 'Oct 25', sentiment: 72 },
  { date: 'Oct 30', sentiment: 68 },
];

export const SentimentTimeline: React.FC = () => {
  return (
    <div className="lg:col-span-7 glass-panel rounded-lg p-container-padding flex flex-col h-96">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h3 className="font-headline-md text-headline-md text-on-background">Sentiment Timeline</h3>
          <p className="font-body-sm text-body-sm text-on-surface-variant">Rolling 30 days overall brand perception</p>
        </div>
        <button className="p-2 hover:bg-surface-container rounded-lg text-on-surface-variant transition-colors">
          <span className="material-symbols-outlined">more_vert</span>
        </button>
      </div>

      <div className="flex-1 w-full h-full pb-2">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={mockData} margin={{ top: 10, right: 0, left: -20, bottom: 0 }}>
            <defs>
              <linearGradient id="colorSentiment" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#004ac6" stopOpacity={0.3}/>
                <stop offset="95%" stopColor="#004ac6" stopOpacity={0}/>
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="rgba(0,0,0,0.05)" />
            <XAxis 
              dataKey="date" 
              axisLine={false} 
              tickLine={false} 
              tick={{ fontSize: 12, fill: '#737686' }} 
              dy={10}
            />
            <YAxis 
              axisLine={false} 
              tickLine={false} 
              tick={{ fontSize: 12, fill: '#737686' }} 
            />
            <Tooltip 
              contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)' }}
            />
            <Area 
              type="monotone" 
              dataKey="sentiment" 
              stroke="#004ac6" 
              strokeWidth={2}
              fillOpacity={1} 
              fill="url(#colorSentiment)" 
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};
