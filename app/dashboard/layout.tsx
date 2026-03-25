import { DashboardSidebar } from '@/components/dashboard-sidebar';

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="flex h-screen bg-background">
      <DashboardSidebar />
      
      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden md:ml-0 pt-16 md:pt-0">
        {/* Header */}
        <header className="hidden md:flex h-16 bg-card border-b border-border items-center justify-between px-8">
          <div>
            <h1 className="text-2xl font-bold text-foreground">Energy Management</h1>
          </div>
          <div className="flex items-center gap-4">
            <div className="text-right">
              <p className="text-sm font-medium text-foreground">Campus Power System</p>
              <p className="text-xs text-muted-foreground">Real-time Monitoring Active</p>
            </div>
            <div className="w-10 h-10 rounded-full bg-primary flex items-center justify-center">
              <span className="text-primary-foreground font-bold">C</span>
            </div>
          </div>
        </header>

        {/* Page Content */}
        <main className="flex-1 overflow-auto">
          <div className="p-4 md:p-8 animate-in fade-in duration-500">{children}</div>
        </main>
      </div>
    </div>
  );
}
