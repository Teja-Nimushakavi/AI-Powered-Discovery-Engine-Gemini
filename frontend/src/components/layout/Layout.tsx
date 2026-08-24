import React from 'react';
import { Sidebar } from './Sidebar';
import { Header } from './Header';
import type { PageId } from '../../pages/Dashboard';

interface LayoutProps {
  children: React.ReactNode;
  activePage?: PageId;
  onNavigate?: (page: PageId) => void;
}

export const Layout: React.FC<LayoutProps> = ({ children, activePage, onNavigate }) => {
  return (
    <div className="font-body-md text-on-surface antialiased overflow-x-hidden min-h-screen flex">
      <Sidebar activePage={activePage} onNavigate={onNavigate} />
      <main className="flex-1 ml-0 md:ml-64 flex flex-col min-h-screen">
        <Header activePage={activePage} onNavigate={onNavigate} />
        <div className="flex-1 p-6 md:p-8 space-y-section-gap max-w-7xl mx-auto w-full">
          {children}
        </div>
      </main>
    </div>
  );
};
