import { NavLink, Outlet } from 'react-router-dom';
import {
  LayoutDashboard, Search, Camera, Wrench, BookOpen, Settings, Cpu,
} from 'lucide-react';

const links = [
  { to: '/', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/analyze', label: 'Analyze Problem', icon: Search },
  { to: '/photo', label: 'Photo Detection', icon: Camera },
  { to: '/troubleshoot', label: 'Troubleshooting', icon: Wrench },
  { to: '/knowledge', label: 'Knowledge Base', icon: BookOpen },
  { to: '/settings', label: 'Settings', icon: Settings },
];

export default function Layout() {
  return (
    <div className="flex h-screen overflow-hidden">
      {/* Sidebar */}
      <aside className="w-64 bg-industrial-900 border-r border-industrial-700 flex flex-col shrink-0">
        {/* Brand */}
        <div className="p-6 border-b border-industrial-700">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-accent-500/20 flex items-center justify-center">
              <Cpu className="w-6 h-6 text-accent-500" />
            </div>
            <div>
              <h1 className="text-lg font-bold text-white tracking-tight">ExtrusionAI</h1>
              <p className="text-xs text-industrial-400">Manufacturing Assistant</p>
            </div>
          </div>
        </div>

        {/* Navigation */}
        <nav className="flex-1 p-4 space-y-1 overflow-y-auto">
          {links.map(({ to, label, icon: Icon }) => (
            <NavLink
              key={to}
              to={to}
              end={to === '/'}
              className={({ isActive }) =>
                `flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-all duration-200 ${
                  isActive
                    ? 'bg-primary-800 text-accent-400 border border-primary-600'
                    : 'text-industrial-300 hover:bg-industrial-800 hover:text-white'
                }`
              }
            >
              <Icon className="w-5 h-5 shrink-0" />
              {label}
            </NavLink>
          ))}
        </nav>

        {/* Footer */}
        <div className="p-4 border-t border-industrial-700">
          <div className="text-xs text-industrial-500 text-center">v2.0.0 • AI-Powered</div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-y-auto">
        <div className="max-w-7xl mx-auto p-8">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
