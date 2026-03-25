'use client';

import { useState } from 'react';
import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import {
  LayoutDashboard,
  Zap,
  TrendingUp,
  Lightbulb,
  Globe,
  BarChart3,
  Leaf,
  FileText,
  Settings,
  HelpCircle,
  Menu,
  X,
  LogOut,
} from 'lucide-react';

const navItems = [
  { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
  { name: 'Monitoring', href: '/dashboard/monitoring', icon: Zap },
  { name: 'Forecasting', href: '/dashboard/forecasting', icon: TrendingUp },
  { name: 'Optimization', href: '/dashboard/optimization', icon: Lightbulb },
  { name: 'Digital Twin', href: '/dashboard/digital-twin', icon: Globe },
  { name: 'Analytics', href: '/dashboard/analytics', icon: BarChart3 },
  { name: 'Carbon Analytics', href: '/dashboard/carbon-analytics', icon: Leaf },
  { name: 'Reports', href: '/dashboard/reports', icon: FileText },
  { name: 'Settings', href: '/dashboard/settings', icon: Settings },
  { name: 'Help', href: '/dashboard/help', icon: HelpCircle },
];

export function DashboardSidebar() {
  const [isOpen, setIsOpen] = useState(false);
  const pathname = usePathname();
  const router = useRouter();

  const handleLogout = () => {
    router.push('/login');
  };

  return (
    <>
      {/* Mobile menu button */}
      <div className="fixed top-4 left-4 z-50 md:hidden">
        <Button
          variant="ghost"
          size="icon"
          onClick={() => setIsOpen(!isOpen)}
          className="text-foreground"
        >
          {isOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
        </Button>
      </div>

      {/* Sidebar */}
      <aside
        className={`
          fixed top-0 left-0 h-screen w-64 bg-sidebar border-r border-sidebar-border
          transition-transform duration-300 ease-in-out z-40
          ${isOpen ? 'translate-x-0' : '-translate-x-full'}
          md:translate-x-0 md:sticky md:top-0
        `}
      >
        <div className="flex flex-col h-full p-6">
          {/* Logo */}
          <Link href="/dashboard" className="flex items-center gap-3 mb-8 mt-2 md:mt-0">
            <div className="w-10 h-10 rounded-lg bg-sidebar-primary flex items-center justify-center">
              <span className="text-sidebar-primary-foreground font-bold">⚡</span>
            </div>
            <div>
              <div className="font-bold text-sidebar-foreground">EnergyOS</div>
              <div className="text-xs text-sidebar-accent">Energy Management</div>
            </div>
          </Link>

          {/* Navigation */}
          <nav className="flex-1 space-y-2">
            {navItems.map((item) => {
              const isActive = pathname === item.href || pathname.startsWith(item.href + '/');
              const Icon = item.icon;
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  onClick={() => setIsOpen(false)}
                  className={`
                    flex items-center gap-3 px-4 py-3 rounded-lg transition-colors
                    ${
                      isActive
                        ? 'bg-sidebar-primary text-sidebar-primary-foreground'
                        : 'text-sidebar-foreground hover:bg-sidebar-accent hover:text-sidebar-accent-foreground'
                    }
                  `}
                >
                  <Icon className="w-5 h-5 flex-shrink-0" />
                  <span className="font-medium">{item.name}</span>
                </Link>
              );
            })}
          </nav>

          {/* User section */}
          <div className="border-t border-sidebar-border pt-4 space-y-3">
            <div className="px-4 py-3 bg-sidebar-accent rounded-lg">
              <p className="text-xs text-sidebar-accent-foreground font-medium">Logged in as</p>
              <p className="text-sm text-sidebar-foreground font-semibold">Demo User</p>
              <p className="text-xs text-sidebar-muted">demo@energyos.com</p>
            </div>
            <Button
              onClick={handleLogout}
              variant="outline"
              className="w-full justify-start border-sidebar-border text-sidebar-foreground hover:bg-sidebar-accent"
            >
              <LogOut className="w-4 h-4 mr-2" />
              Logout
            </Button>
          </div>
        </div>
      </aside>

      {/* Mobile overlay */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-30 md:hidden"
          onClick={() => setIsOpen(false)}
        />
      )}
    </>
  );
}
