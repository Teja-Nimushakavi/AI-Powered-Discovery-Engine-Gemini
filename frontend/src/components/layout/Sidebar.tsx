import React from 'react';
import type { PageId } from '../../pages/Dashboard';

interface SidebarProps {
  activePage?: PageId;
  onNavigate?: (page: PageId) => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ activePage = 'dashboard', onNavigate }) => {
  return (
    <nav className="hidden md:flex flex-col h-full py-8 px-4 fixed left-0 top-0 w-64 border-r border-black/10 bg-white/85 backdrop-blur-xl shadow-sm z-50">
      {/* Header Avatar & Title */}
      <div className="flex items-center gap-3 mb-12 px-2">
        <div className="w-10 h-10 rounded-full bg-surface-container-highest overflow-hidden border border-outline-variant flex-shrink-0">
          <img
            alt="User Profile"
            className="w-full h-full object-cover"
            src="https://lh3.googleusercontent.com/aida-public/AB6AXuCXOUXSXrlVMhiDgkqE3VqxXH7a83Gv4jmJgThJOCvd1kY8BCsD2uz5RJ7YxnIcTeJPQ3HZeucR1-ThmOgHYQNAeIt55CMQizLCMwwASpO1NFSc9ja7wEEEI4Jusnmg3vsudoZNdzA_lACSj5fAwF3hb9TmleXiAC-xuLVem9RuUhnx3X2w2TSszCueWTrzz_zXXCGLtvrU8HKy-MdxdJvGD2P6eNBf6dDJ8eHD332QwlPuAuLbhde9PA"
          />
        </div>
        <div>
          <h2 className="font-headline-md text-headline-md font-bold text-primary">RAG Engine</h2>
          <p className="font-label-md text-label-md text-on-surface-variant">Discovery Mode</p>
        </div>
      </div>

      {/* CTA */}
      <button className="w-full mb-8 py-3 px-4 bg-gradient-primary text-white rounded-md shadow-sm hover:opacity-90 transition-opacity font-label-md text-label-md flex justify-center items-center gap-2">
        <span className="material-symbols-outlined text-[18px]">add</span>
        New Analysis
      </button>

      {/* Main Navigation Links */}
      <div className="flex-grow space-y-2">
        <a 
          className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-200 ${activePage === 'dashboard' ? 'text-primary font-bold bg-primary/5' : 'text-on-surface-variant hover:bg-primary/5 group'}`} 
          href="#"
          onClick={(e) => { e.preventDefault(); onNavigate?.('dashboard'); }}
        >
          <span className={`material-symbols-outlined ${activePage !== 'dashboard' ? 'group-hover:text-primary transition-colors' : ''}`}>dashboard</span>
          <span className={`font-body-md text-body-md ${activePage !== 'dashboard' ? 'group-hover:text-primary transition-colors' : ''}`}>Dashboard</span>
        </a>
        <a 
          className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-200 ${activePage === 'search' ? 'text-primary font-bold bg-primary/5' : 'text-on-surface-variant hover:bg-primary/5 group'}`} 
          href="#"
          onClick={(e) => { e.preventDefault(); onNavigate?.('search'); }}
        >
          <span className={`material-symbols-outlined ${activePage !== 'search' ? 'group-hover:text-primary transition-colors' : ''}`}>manage_search</span>
          <span className={`font-body-md text-body-md ${activePage !== 'search' ? 'group-hover:text-primary transition-colors' : ''}`}>Semantic Search</span>
        </a>
        <a 
          className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-200 ${activePage === 'analytics' ? 'text-primary font-bold bg-primary/5' : 'text-on-surface-variant hover:bg-primary/5 group'}`} 
          href="#"
          onClick={(e) => { e.preventDefault(); onNavigate?.('analytics'); }}
        >
          <span className={`material-symbols-outlined ${activePage !== 'analytics' ? 'group-hover:text-primary transition-colors' : ''}`}>insights</span>
          <span className={`font-body-md text-body-md ${activePage !== 'analytics' ? 'group-hover:text-primary transition-colors' : ''}`}>Analytics</span>
        </a>
        <a 
          className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-200 ${activePage === 'feedback' ? 'text-primary font-bold bg-primary/5' : 'text-on-surface-variant hover:bg-primary/5 group'}`} 
          href="#"
          onClick={(e) => { e.preventDefault(); onNavigate?.('feedback'); }}
        >
          <span className={`material-symbols-outlined ${activePage !== 'feedback' ? 'group-hover:text-primary transition-colors' : ''}`}>forum</span>
          <span className={`font-body-md text-body-md ${activePage !== 'feedback' ? 'group-hover:text-primary transition-colors' : ''}`}>Raw Feedback</span>
        </a>
        <a 
          className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-200 ${activePage === 'painpoints' ? 'text-primary font-bold bg-primary/5' : 'text-on-surface-variant hover:bg-primary/5 group'}`} 
          href="#"
          onClick={(e) => { e.preventDefault(); onNavigate?.('painpoints'); }}
        >
          <span className={`material-symbols-outlined ${activePage !== 'painpoints' ? 'group-hover:text-primary transition-colors' : ''}`}>warning</span>
          <span className={`font-body-md text-body-md ${activePage !== 'painpoints' ? 'group-hover:text-primary transition-colors' : ''}`}>Pain Points</span>
        </a>
        <a 
          className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-200 ${activePage === 'report' ? 'text-primary font-bold bg-primary/5' : 'text-on-surface-variant hover:bg-primary/5 group'}`} 
          href="#"
          onClick={(e) => { e.preventDefault(); onNavigate?.('report'); }}
        >
          <span className={`material-symbols-outlined ${activePage !== 'report' ? 'group-hover:text-primary transition-colors' : ''}`}>assignment</span>
          <span className={`font-body-md text-body-md ${activePage !== 'report' ? 'group-hover:text-primary transition-colors' : ''}`}>Final Report</span>
        </a>
      </div>

      {/* Footer Navigation Links */}
      <div className="mt-auto space-y-2 border-t border-outline-variant/30 pt-4">
        <a className="flex items-center gap-3 px-4 py-2 rounded-lg text-on-surface-variant hover:bg-primary/5 transition-all duration-200 group" href="#">
          <span className="material-symbols-outlined group-hover:text-primary transition-colors text-[20px]">settings</span>
          <span className="font-body-sm text-body-sm group-hover:text-primary transition-colors">Settings</span>
        </a>
        <a className="flex items-center gap-3 px-4 py-2 rounded-lg text-on-surface-variant hover:bg-primary/5 transition-all duration-200 group" href="#">
          <span className="material-symbols-outlined group-hover:text-primary transition-colors text-[20px]">help_outline</span>
          <span className="font-body-sm text-body-sm group-hover:text-primary transition-colors">Support</span>
        </a>
      </div>
    </nav>
  );
};
