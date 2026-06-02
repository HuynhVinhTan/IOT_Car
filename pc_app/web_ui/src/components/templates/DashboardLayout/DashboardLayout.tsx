import type { ReactNode } from "react";

interface DashboardLayoutProps {
  header: ReactNode;
  toolbar?: ReactNode;
  subHeader?: ReactNode;
  left: ReactNode;
  right: ReactNode;
  bottom: ReactNode;
}

export function DashboardLayout({ 
  header, 
  toolbar, 
  subHeader, 
  left, 
  right, 
  bottom 
}: DashboardLayoutProps) {
  return (
    <div className="dashboard-shell">
      <header className="dashboard-header">{header}</header>
      {toolbar && toolbar}
      {subHeader && subHeader}
      <main className="dashboard-main">
        <section className="dashboard-left">{left}</section>
        <aside className="dashboard-right">{right}</aside>
      </main>
      <section className="dashboard-bottom">{bottom}</section>
    </div>
  );
}
