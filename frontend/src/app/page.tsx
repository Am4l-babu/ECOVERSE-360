import Link from "next/link";
import {
  Leaf,
  BarChart3,
  Cpu,
  Zap,
  Users,
  Globe,
} from "lucide-react";

const features = [
  {
    icon: <Cpu className="w-6 h-6" />,
    title: "200+ IoT Sensors",
    desc: "Live air, water, waste, energy, and soil monitoring across campus zones.",
  },
  {
    icon: <Globe className="w-6 h-6" />,
    title: "Digital Twin",
    desc: 'Real-time campus replica for what-if sustainability simulations.',
  },
  {
    icon: <BarChart3 className="w-6 h-6" />,
    title: "ML Predictions",
    desc: "Waste overflow, AQI forecasting, energy demand, and crop-yield models.",
  },
  {
    icon: <Zap className="w-6 h-6" />,
    title: "EcoPoints",
    desc: "Gamified rewards — earn points for recycling, carpooling, planting trees.",
  },
  {
    icon: <Users className="w-6 h-6" />,
    title: "Community",
    desc: "Leaderboards, challenges, marketplace, and peer-to-peer sustainability.",
  },
  {
    icon: <Leaf className="w-6 h-6" />,
    title: "Carbon Tracking",
    desc: "Personal & campus-wide carbon footprint dashboards with reduction goals.",
  },
];

export default function Home() {
  return (
    <main className="min-h-screen">
      {/* ── Hero ──────────────────────────────────────────────── */}
      <section className="relative overflow-hidden bg-gradient-to-br from-eco-800 via-eco-700 to-eco-600 text-white">
        <div className="absolute inset-0 opacity-10">
          <div className="absolute top-20 left-10 w-72 h-72 bg-eco-300 rounded-full blur-3xl" />
          <div className="absolute bottom-10 right-20 w-96 h-96 bg-carbon-400 rounded-full blur-3xl" />
        </div>

        <nav className="relative z-10 max-w-7xl mx-auto px-6 py-5 flex items-center justify-between">
          <div className="flex items-center gap-2 text-xl font-bold">
            <Leaf className="w-7 h-7 text-eco-300" />
            Ecoverse 360
          </div>
          <div className="flex gap-3">
            <Link href="/login" className="eco-btn text-white/80 hover:text-white">
              Log In
            </Link>
            <Link href="/register" className="eco-btn-primary !bg-white !text-eco-700 hover:!bg-eco-50">
              Get Started
            </Link>
          </div>
        </nav>

        <div className="relative z-10 max-w-4xl mx-auto px-6 py-24 text-center">
          <p className="eco-badge bg-white/10 text-eco-200 mb-6 mx-auto">
            🌍 Sustainability Operating System
          </p>
          <h1 className="text-5xl sm:text-6xl font-extrabold leading-tight tracking-tight">
            Turn Your Campus Into a<br />
            <span className="text-eco-300">Living Ecosystem</span>
          </h1>
          <p className="mt-6 text-lg text-eco-100 max-w-2xl mx-auto leading-relaxed">
            Ecoverse 360 unifies IoT sensing, digital twin simulation, machine
            learning, and gamified engagement into one platform — making
            sustainability measurable, actionable, and rewarding.
          </p>
          <div className="mt-10 flex gap-4 justify-center">
            <Link href="/dashboard" className="eco-btn-primary text-base px-8 py-3">
              Open Dashboard
            </Link>
            <Link href="#features" className="eco-btn bg-white/10 text-white hover:bg-white/20 text-base px-8 py-3">
              Explore Features
            </Link>
          </div>
        </div>
      </section>

      {/* ── Live Stats Bar ────────────────────────────────────── */}
      <section className="bg-white border-b border-gray-100">
        <div className="max-w-7xl mx-auto px-6 py-8 grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
          {[
            { value: "42", unit: "AQI", label: "Air Quality", color: "text-eco-500" },
            { value: "1.2k", unit: "kg", label: "CO₂ Saved Today", color: "text-carbon-600" },
            { value: "87%", unit: "", label: "Bins Collected", color: "text-amber-500" },
            { value: "3,421", unit: "pts", label: "Points Earned", color: "text-blue-500" },
          ].map((s) => (
            <div key={s.label}>
              <p className={`stat-value ${s.color}`}>
                {s.value}
                <span className="text-lg font-medium ml-1">{s.unit}</span>
              </p>
              <p className="stat-label">{s.label}</p>
            </div>
          ))}
        </div>
      </section>

      {/* ── Features ──────────────────────────────────────────── */}
      <section id="features" className="max-w-7xl mx-auto px-6 py-20">
        <h2 className="text-3xl font-bold text-center mb-4">
          Everything You Need for a Greener Campus
        </h2>
        <p className="text-center text-gray-500 mb-14 max-w-xl mx-auto">
          Six integrated layers — from physical sensors to the incentive engine
          — working together in real time.
        </p>

        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {features.map((f) => (
            <div key={f.title} className="eco-card group">
              <div className="w-12 h-12 rounded-xl bg-eco-50 text-eco-600 flex items-center justify-center mb-4 group-hover:bg-eco-500 group-hover:text-white transition-colors">
                {f.icon}
              </div>
              <h3 className="font-semibold text-lg mb-1">{f.title}</h3>
              <p className="text-gray-500 text-sm leading-relaxed">{f.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* ── Footer ────────────────────────────────────────────── */}
      <footer className="bg-gray-900 text-gray-400 text-sm py-10">
        <div className="max-w-7xl mx-auto px-6 flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2 text-white font-semibold">
            <Leaf className="w-5 h-5 text-eco-400" />
            Ecoverse 360
          </div>
          <p>© {new Date().getFullYear()} Ecoverse 360. Built for a sustainable future.</p>
        </div>
      </footer>
    </main>
  );
}
