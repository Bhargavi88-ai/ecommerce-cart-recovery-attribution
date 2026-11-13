import React from 'react';
import { Sidebar, PageId } from './Sidebar';
import { Navbar } from './Navbar';

interface LayoutProps {
  currentPage: PageId;
  onNavigate: (page: PageId) => void;
  children: React.ReactNode;
  pageTitle: string;
  onRefresh?: () => void;
  isRefreshing?: boolean;
}

export const Layout: React.FC<LayoutProps> = ({
  currentPage,
  onNavigate,
  children,
  pageTitle,
  onRefresh,
  isRefreshing,
}) => {
  return (
    <div className="flex min-h-screen bg-slate-950 text-slate-100 font-sans">
      <Sidebar currentPage={currentPage} onNavigate={onNavigate} />
      <div className="flex-1 flex flex-col min-w-0">
        <Navbar pageTitle={pageTitle} onRefresh={onRefresh} isRefreshing={isRefreshing} />
        <main className="flex-1 p-8 overflow-y-auto">{children}</main>
      </div>
    </div>
  );
};

