import React from 'react';
import { useApp } from '../../contexts/AppContext';
import Sidebar from './Sidebar';
import Header from './Header';
import { cn } from '../../lib/utils';

interface MainLayoutProps {
  children: React.ReactNode;
  currentView: string;
  onNavigate: (view: string) => void;
}

export default function MainLayout({ children, currentView, onNavigate }: MainLayoutProps) {
  const { state } = useApp();
  const { sidebarOpen } = state;

  return (
    <div className="flex h-screen bg-background">
      {/* Sidebar */}
      <div className={cn(
        "transition-all duration-300 ease-in-out border-r bg-muted/40",
        sidebarOpen ? "w-80" : "w-0 overflow-hidden"
      )}>
        <Sidebar currentView={currentView} onNavigate={onNavigate} />
      </div>

      {/* Main Content */}
      <div className="flex flex-col flex-1 min-w-0">
        <Header />
        <main className="flex-1 overflow-hidden">
          {children}
        </main>
      </div>
    </div>
  );
}
