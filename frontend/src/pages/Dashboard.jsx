import { useNavigate } from "react-router-dom"
import { useEffect, useState } from "react"
import { getProfile } from "../services/api"
import NotificationsDropdown from "../components/NotificationsDropdown"

// --- Icons ---
const LeafIcon = ({ size = 22 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="#2E7D32" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
    <path d="M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.48 19 2c1 2 2 4.18 2 8 0 5.5-4.78 10-10 10z" />
    <path d="M2 21c0-3 1.85-5.36 5.08-6C9.5 14.52 12 13 13 12" />
  </svg>
)

const BellIcon = () => (
  <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#6b7280" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
    <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9" />
    <path d="M13.73 21a2 2 0 0 1-3.46 0" />
  </svg>
)

const UserIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#6b7280" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
    <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
    <circle cx="12" cy="7" r="4" />
  </svg>
)

const ChevronDown = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#6b7280" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
    <polyline points="6 9 12 15 18 9" />
  </svg>
)

const ArrowRight = ({ color = "#206C1B", size = 16 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M5 12h14M12 5l7 7-7 7" />
  </svg>
)

const SearchIcon = ({ color }) => (
  <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="11" cy="11" r="8" /><path d="m21 21-4.35-4.35" />
  </svg>
)

const BoxIcon = ({ color }) => (
  <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z" />
    <polyline points="3.27 6.96 12 12.01 20.73 6.96" /><line x1="12" y1="22.08" x2="12" y2="12" />
  </svg>
)

const BowlIcon = ({ color }) => (
  <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M12 2a10 10 0 0 1 10 10H2A10 10 0 0 1 12 2z" />
    <path d="M12 22c4 0 7-2 8-6H4c1 4 4 6 8 6z" />
  </svg>
)

const CalendarIcon = ({ color }) => (
  <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <rect x="3" y="4" width="18" height="18" rx="2" ry="2" /><line x1="16" y1="2" x2="16" y2="6" /><line x1="8" y1="2" x2="8" y2="6" /><line x1="3" y1="10" x2="21" y2="10" />
  </svg>
)

const HeartIcon = ({ color }) => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z" />
  </svg>
)

const TrashIcon = ({ color }) => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <polyline points="3 6 5 6 21 6" /><path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6" /><path d="M10 11v6M14 11v6" /><path d="M9 6V4a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v2" />
  </svg>
)

const BoltIcon = ({ color }) => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2" />
  </svg>
)

// --- Data ---
const cards = [
  { id: "recipes", title: "Smart Recipes", desc: "AI powered recipe suggestions based on your ingredients and dietary goals.", bg: "#f0f9f4", iconColor: "#206C1B", iconBg: "#E4F2DB", linkColor: "#206C1B", linkText: "Explore Recipes", Icon: SearchIcon, img: "/smart_recipe.png" },
  { id: "inventory", title: "Inventory", desc: "Real-time pantry monitoring with smart explanation alerts and categorization.", bg: "#f5f3ff", iconColor: "#7c3aed", iconBg: "#ede9fe", linkColor: "#7c3aed", linkText: "View Inventory", Icon: BoxIcon, img: "/inventory.png" },
  { id: "nutrition", title: "Insights", desc: "Track macros, calories and nutritional goals with detailed analytics.", bg: "#fff7ed", iconColor: "#ea580c", iconBg: "#ffedd5", linkColor: "#ea580c", linkText: "View Insights", Icon: BowlIcon, img: "/nutrition.png" },
  { id: "meal-plans", title: "Meal Plan", desc: "Personalized weekly meal plans that adapt to schedule and preferences.", bg: "#eff6ff", iconColor: "#2563eb", iconBg: "#dbeafe", linkColor: "#2563eb", linkText: "Plan Meals", Icon: CalendarIcon, img: "/meal_plan.png" },
]

const STATS = [
  { key: "health_alignment", label: "Health Alignment Score", subKey: "health_alignment_sub", valueColor: "#206C1B", barColor: "#206C1B", iconBg: "#E4F2DB", Icon: HeartIcon, suffix: "/100", img: "/health.png" },
  { key: "diet_balance", label: "Diet Balance Insight", subKey: "diet_balance_sub", valueColor: "#2563eb", barColor: "#2563eb", iconBg: "#dbeafe", Icon: BoxIcon, suffix: "", img: "/thaali.png" },
  { key: "food_waste_risk", label: "Food Waste Risk", subKey: "food_waste_sub", valueColor: "#ea580c", barColor: "#f97316", iconBg: "#ffedd5", Icon: TrashIcon, suffix: "", img: "/waste.png" },
  { key: "grocery_efficiency", label: "Grocery Efficiency", subKey: "grocery_efficiency_sub", valueColor: "#7c3aed", barColor: "#8b5cf6", iconBg: "#f3e8ff", Icon: BoltIcon, suffix: "%", img: "/diet.png" },
]

const statBarWidth = (key, value) => {
  if (key === "health_alignment") return Math.min(value, 100)
  if (key === "grocery_efficiency") return Math.min(value, 100)
  if (key === "diet_balance") return ({ Excellent: 95, Great: 75, Good: 50, Fair: 25 }[value] ?? 50)
  if (key === "food_waste_risk") return ({ Low: 20, Medium: 55, High: 85 }[value] ?? 30)
  return 50
}

function Dashboard() {
  const navigate = useNavigate()
  const [insights, setInsights] = useState(null)
  const [userName, setUserName] = useState("")
  const [userId, setUserId] = useState(null)

useEffect(() => {
    const userId = localStorage.getItem("userId")
    if (!userId) { navigate("/login"); return }
    setUserId(userId)

    // Fetch the name from the new Profile structure
    getProfile(userId).then(p => {
      // Logic: Prioritize p.name from the Profile collection
      setUserName(p.name || p.email || "there")
    })

    fetch("http://localhost:8000/profile/insights", { headers: { "user-id": userId } })
      .then(r => r.json()).then(setInsights).catch(() => { })
  }, [navigate])

  const handleLogout = () => {
    localStorage.removeItem("userId")
    localStorage.removeItem("token")
    navigate("/login")
  }

  const firstName = userName.split(" ")[0]

  return (
    <div style={{ height: "100vh", background: "#fff", fontFamily: "'DM Sans', sans-serif", display: "flex", flexDirection: "column", overflow: "hidden" }}>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700;800&display=swap');
        * { box-sizing: border-box; margin: 0; padding: 0; }
      `}</style>

      {/* Navbar */}
      <nav style={{ display: "flex", alignItems: "center", justifyContent: "space-between", padding: "0 52px", height: 64, borderBottom: "1px solid #f0f0ee", flexShrink: 0 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 9 }}>
            <div style={{ width: 36, height: 36, background: "#E4F2DB", border: "1px solid #c6deb0", borderRadius: 9, display: "flex", alignItems: "center", justifyContent: "center" }}>
              <LeafIcon size={18} />
            </div>
            <span style={{ fontSize: 17, fontWeight: 700, color: "#1a2e1a" }}>Pantry</span>
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: 6, border: "1.5px solid #c6deb0", borderRadius: 999, padding: "5px 14px", fontSize: 13, color: "#206c1b", fontWeight: 500 }}>
            <span style={{ fontSize: 11 }}>✦</span> Your personalized kitchen assistant
          </div>
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
          <NotificationsDropdown userId={userId} />
          <div onClick={() => navigate("/profile")} style={{ display: "flex", alignItems: "center", gap: 8, padding: "6px 12px", borderRadius: 999, border: "1.5px solid #e8ede2", cursor: "pointer" }}>
            <div style={{ width: 28, height: 28, borderRadius: "50%", background: "#f3f4f6", display: "flex", alignItems: "center", justifyContent: "center" }}>
              <UserIcon />
            </div>
            <span style={{ fontSize: 14, fontWeight: 500, color: "#374151" }}>{firstName || "—"}</span>
          </div>
          <button onClick={handleLogout} style={{ background: "none", border: "1.5px solid #e0e0e0", borderRadius: 8, padding: "7px 16px", fontSize: 13, fontWeight: 500, color: "#6b7280", cursor: "pointer", fontFamily: "'DM Sans', sans-serif" }}>Log out</button>
        </div>
      </nav>

      <div style={{ display: "flex", flex: 1, overflow: "hidden" }}>
        {/* Main Content Area */}
        <main style={{ flex: 1, display: "flex", flexDirection: "column", gap: "20px" }}>

{/* Hero Section */}
<div style={{ position: "relative", background: "#fff", overflow: "hidden", display: "flex", alignItems: "center", flexShrink: 0, minHeight: 320 }}>
  
  {/* 1. The ClipPath Definition (Hidden) */}
  <svg width="0" height="0" style={{ position: 'absolute' }}>
    <defs>
      <clipPath id="sinWaveClip" clipPathUnits="objectBoundingBox">
        {/* 
          This path creates a horizontal S-curve (sine-like).
          It starts at the top-right, moves to the middle, 
          curves left then right, and closes back.
        */}
        <path d="M 1,0 
                 L 0.4,0 
                 C 0,0.2 0.5,0.8,0.1,1 
                 L 1,1 
                 Z" />
      </clipPath>
    </defs>
  </svg>

  {/* 2. Text Content */}
  <div style={{ position: "relative", zIndex: 1, padding: "32px 20px 32px 52px", maxWidth: 450 }}>
    <h1 style={{ fontSize: 44, fontWeight: 800, color: "#0d1a0d", letterSpacing: "-1.2px", marginBottom: 12 }}>Hi {firstName}!</h1>
    <p style={{ fontSize: 18, fontWeight: 500, color: "#4b5563", marginBottom: 8 }}>Here's what your kitchen looks like today.</p>
    <p style={{ fontSize: 15, color: "#6b7280", lineHeight: 1.6, marginBottom: 32 }}>Track inventory, discover recipes, plan meals, and<br />monitor nutrition — all in one place.</p>
    <button
      onClick={() => navigate("/profile")}
      style={{ background: "#166534", color: "#fff", border: "none", padding: "14px 28px", borderRadius: 12, fontWeight: 700, fontSize: 15, display: "flex", alignItems: "center", gap: 10, cursor: "pointer", fontFamily: "'DM Sans', sans-serif" }}
    >
      Customise your prefrences <ArrowRight color="#fff" size={18} />
    </button>
  </div>

  {/* 3. Hero image with the Wave Cutout */}
  <img 
    src="/dashboard.png" 
    alt="" 
    style={{ 
      position: "absolute", 
      right: 0, 
      top: 0, 
      height: "100%", 
      width: "50%", 
      objectFit: "cover", 
      zIndex: 1,
      /* This references the ID defined in the SVG above */
      clipPath: "url(#sinWaveClip)",
      WebkitClipPath: "url(#sinWaveClip)" 
    }} 
  />
</div>

          {/* Cards Grid */}
          <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: "20px", flex: 1, padding: "0 20px 20px 52px" }}>
            {cards.map(card => (
              <div 
                key={card.id} 
                onClick={() => navigate(`/${card.id === 'meal-plans' ? 'meal-plan' : card.id}`)} 
                style={{ background: card.bg, borderRadius: 20, padding: 0, cursor: "pointer", display: "flex", flexDirection: "column", border: "1px solid rgba(0,0,0,0.02)", overflow: "hidden" }}
              >
                <div style={{ padding: "20px 20px 0 20px" }}>
                  <div style={{ width: 44, height: 44, borderRadius: "50%", background: "#fff", display: "flex", alignItems: "center", justifyContent: "center", marginBottom: 12, border: `1px solid ${card.iconBg}` }}>
                    <card.Icon color={card.iconColor} />
                  </div>
                  <h3 style={{ fontSize: 17, fontWeight: 700, marginBottom: 6 }}>{card.title}</h3>
                  <p style={{ fontSize: 13, color: "#6b7280", lineHeight: 1.5, marginBottom: 14 }}>{card.desc}</p>
                </div>
                <div style={{ flex: 1, minHeight: 150 }}>
                  <img src={card.img} style={{ width: "100%", height: "100%", objectFit: "cover", display: "block" }} alt="" />
                </div>
                <div style={{ padding: "0 14px 12px" }}>
                  <div style={{
                    background: "#fff",
                    borderRadius: "30px",
                    padding: "10px 15px",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    gap: 10,
                    fontSize: 14,
                    fontWeight: 700,
                    color: card.linkColor,
                    boxShadow: "0 2px 8px rgba(0,0,0,0.04)",
                    border: "1px solid rgba(0,0,0,0.05)"
                  }}>
                    {card.linkText} <ArrowRight color={card.linkColor} size={16} />
                  </div>
                </div>
              </div>
            ))}
          </div>
        </main>

        {/* Sidebar Insights */}
        <aside style={{ width: 480, borderLeft: "1px solid #f3f4f6", padding: "16px 52px 16px 24px", display: "flex", flexDirection: "column", flexShrink: 0, overflow: "hidden" }}>
          <h2 style={{ fontSize: 18, fontWeight: 700, marginBottom: "10px" }}>Your Insights</h2>

          <div style={{ display: "flex", flexDirection: "column", flex: 1, gap: "10px" }}>
            {STATS.map(stat => {
              const raw = insights?.[stat.key]
              const value = raw != null ? `${raw}${stat.suffix}` : "—"
              const sub = insights?.[stat.subKey] ?? "Loading..."
              const bar = raw != null ? statBarWidth(stat.key, raw) : 0

              return (
                <div key={stat.key} style={{ border: "1px solid #f3f4f6", borderRadius: 16, padding: "10px 14px", display: "flex", alignItems: "center", flex: 1 }}>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", width: "100%" }}>
                    <div style={{ flex: 1 }}>
                      <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 6 }}>
                        <div style={{ width: 28, height: 28, borderRadius: "50%", background: stat.iconBg, display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0 }}>
                          <stat.Icon color={stat.valueColor} />
                        </div>
                        <span style={{ fontSize: 14, fontWeight: 700, color: "#4b5563" }}>{stat.label}</span>
                      </div>
                      <div style={{ fontSize: 20, fontWeight: 800, color: stat.valueColor, marginBottom: 6 }}>
                        {stat.key === "diet_balance" || stat.key === "food_waste_risk" ? raw : value}
                      </div>
                      <div style={{ height: 6, background: "#f3f4f6", borderRadius: 10, marginBottom: 6, width: "90%" }}>
                        <div style={{ height: "100%", width: `${bar}%`, background: stat.barColor, borderRadius: 10 }} />
                      </div>
                      <p style={{ fontSize: 13, color: "#9ca3af", maxWidth: "90%", lineHeight: 1.4 }}>{sub}</p>
                    </div>
                    <img src={stat.img} style={{ width: 64, height: 64, objectFit: "contain" }} alt="" />
                  </div>
                </div>
              )
            })}

            <div style={{ background: "#E4F2DB", borderRadius: 14, padding: "10px 14px", display: "flex", gap: 12, alignItems: "center", border: "1px solid #E4F2DB" }}>
              <LeafIcon size={22} />
              <div>
                <div style={{ fontSize: 13, fontWeight: 700, color: "#166534" }}>Small steps, big impact.</div>
                <div style={{ fontSize: 12, color: "#166534" }}>Every healthy choice counts!</div>
              </div>
            </div>
          </div>
        </aside>
      </div>
    </div>
  )
}

export default Dashboard