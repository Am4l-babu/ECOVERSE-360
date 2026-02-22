"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { clsx } from "clsx";
import {
  LayoutDashboard,
  Leaf,
  MapPin,
  Trophy,
  Cpu,
  Settings,
  BarChart3,
  LogOut,
} from "lucide-react";
import { useAuthStore } from "@/lib/store";

const navItems = [
  { href: "/dashboard",      label: "Overview",     icon: LayoutDashboard },
  { href: "/dashboard/twin", label: "Digital Twin",  icon: MapPin },
  { href: "/dashboard/sensors", label: "Sensors",    icon: Cpu },
  { href: "/dashboard/eco",  label: "EcoPoints",    icon: Leaf },
  { href: "/dashboard/carbon", label: "Carbon",     icon: BarChart3 },
  { href: "/dashboard/leaderboard", label: "Leaderboard", icon: Trophy },
  { href: "/dashboard/settings",    label: "Settings",    icon: Settings },
];

export function Sidebar() {
  const pathname = usePathname();
  const { user, logout } = useAuthStore();

  return (
    <aside className="fixed inset-y-0 left-0 w-64 bg-white border-r border-gray-100 flex flex-col z-30">
      {/* Logo */}
      <div className="px-6 py-5 flex items-center gap-2 border-b border-gray-50">
        <Leaf className="w-7 h-7 text-eco-500" />
        <span className="text-lg font-bold tracking-tight">Ecoverse 360</span>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
        {navItems.map(({ href, label, icon: Icon }) => {
          const active = pathname === href || pathname.startsWith(href + "/");
          return (
            <Link
              key={href}
              href={href}
              className={clsx(
                "flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-colors",
                active
                  ? "bg-eco-50 text-eco-700"
                  : "text-gray-500 hover:bg-gray-50 hover:text-gray-900"
              )}
            >
              <Icon className="w-5 h-5" />
              {label}
            </Link>
          );
        })}
      </nav>

      {/* User footer */}
      <div className="px-4 py-4 border-t border-gray-100">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-full bg-eco-100 text-eco-700 flex items-center justify-center font-bold text-sm">
            {user?.username?.[0]?.toUpperCase() || "U"}
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium truncate">{user?.username || "User"}</p>
            <p className="text-xs text-gray-400 truncate">{user?.eco_level || "Seedling"}</p>
          </div>
          <button onClick={logout} className="text-gray-400 hover:text-red-500 transition-colors">
            <LogOut className="w-4 h-4" />
          </button>
        </div>
      </div>
    </aside>
  );
}
