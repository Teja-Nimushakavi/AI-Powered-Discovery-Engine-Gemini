import React from 'react';

import type { PageId } from '../../pages/Dashboard';

interface HeaderProps {
  activePage?: PageId;
  onNavigate?: (page: PageId) => void;
}

export const Header: React.FC<HeaderProps> = ({ activePage = 'dashboard', onNavigate }) => {
  return (
    <header className="flex justify-between items-center w-full px-8 h-20 max-w-full md:max-w-full docked top-0 border-b border-black/10 bg-white/85 backdrop-blur-xl shadow-sm z-40 sticky">
      {/* Brand Logo / Product Name */}
      <div className="font-display-lg text-headline-md font-bold text-primary truncate">
        Myntra Consumer Insights
      </div>

      {/* Navigation Links (Center-ish, hidden on mobile) */}
      <nav className="hidden lg:flex items-center gap-6">
        <a 
          className={`font-body-md text-body-md ${activePage === 'dashboard' ? 'text-primary border-b-2 border-primary pb-2 font-semibold' : 'text-on-surface-variant hover:text-primary transition-colors'}`} 
          href="#"
          onClick={(e) => { e.preventDefault(); onNavigate?.('dashboard'); }}
        >
          Overview
        </a>
        <a 
          className={`font-body-md text-body-md ${activePage === 'analytics' ? 'text-primary border-b-2 border-primary pb-2 font-semibold' : 'text-on-surface-variant hover:text-primary transition-colors'}`} 
          href="#"
          onClick={(e) => { e.preventDefault(); onNavigate?.('analytics'); }}
        >
          Metrics
        </a>
        <a 
          className={`font-body-md text-body-md ${activePage === 'feedback' ? 'text-primary border-b-2 border-primary pb-2 font-semibold' : 'text-on-surface-variant hover:text-primary transition-colors'}`} 
          href="#"
          onClick={(e) => { e.preventDefault(); onNavigate?.('feedback'); }}
        >
          Sources
        </a>
      </nav>

      {/* Trailing Actions */}
      <div className="flex items-center gap-4">
        {/* Icon Actions */}
        <div className="flex items-center gap-2">
          <button className="p-2 rounded-full text-on-surface-variant hover:bg-surface-container hover:text-primary transition-colors">
            <span className="material-symbols-outlined">notifications</span>
          </button>
          <button className="p-2 rounded-full text-on-surface-variant hover:bg-surface-container hover:text-primary transition-colors">
            <span className="material-symbols-outlined">account_circle</span>
          </button>
        </div>
        
        {/* Trailing Primary Action */}
        <button className="hidden sm:block py-2 px-4 border border-black/10 bg-white/85 rounded-md text-primary font-label-md text-label-md hover:bg-surface-container transition-colors shadow-sm">
          Export
        </button>
      </div>
    </header>
  );
};
