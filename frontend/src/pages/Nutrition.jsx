import { useState, useEffect } from "react"
import { useNavigate } from "react-router-dom"
import { getProfile } from "../services/api"
import NotificationsDropdown from "../components/NotificationsDropdown"

const BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000"
const FONT = "'DM Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif"

// â”€â”€ Nav icons â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
const LeafIcon = ({ size = 18, color = "#2E7D32" }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
    <path d="M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.48 19 2c1 2 2 4.18 2 8 0 5.5-4.78 10-10 10z" />
    <path d="M2 21c0-3 1.85-5.36 5.08-6C9.5 14.52 12 13 13 12" />
  </svg>
)
const BellIcon = () => (
  <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#6b7280" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
    <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9" /><path d="M13.73 21a2 2 0 0 1-3.46 0" />
  </svg>
)
const UserIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#6b7280" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
    <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" /><circle cx="12" cy="7" r="4" />
  </svg>
)
const HomeIcon = ({ color }) => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
    <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" /><polyline points="9 22 9 12 15 12 15 22" />
  </svg>
)
const SearchNavIcon = ({ color }) => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="11" cy="11" r="8" /><path d="m21 21-4.35-4.35" />
  </svg>
)
const BoxIcon = ({ color }) => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
    <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z" />
    <polyline points="3.27 6.96 12 12.01 20.73 6.96" /><line x1="12" y1="22.08" x2="12" y2="12" />
  </svg>
)
const CalendarNavIcon = ({ color }) => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
    <rect x="3" y="4" width="18" height="18" rx="2" ry="2" /><line x1="16" y1="2" x2="16" y2="6" /><line x1="8" y1="2" x2="8" y2="6" /><line x1="3" y1="10" x2="21" y2="10" />
  </svg>
)
const BarChartNavIcon = ({ color }) => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
    <line x1="18" y1="20" x2="18" y2="10" /><line x1="12" y1="20" x2="12" y2="4" /><line x1="6" y1="20" x2="6" y2="14" />
  </svg>
)
const NutritionNavIcon = ({ color }) => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
    <path d="M12 2a10 10 0 0 1 10 10H2A10 10 0 0 1 12 2z" /><path d="M12 22c4 0 7-2 8-6H4c1 4 4 6 8 6z" />
  </svg>
)
const PersonIcon = ({ color }) => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
    <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" /><circle cx="12" cy="7" r="4" />
  </svg>
)

// â”€â”€ Card metric icons â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
const IconDrop = ({ color, size = 20 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
    <path d="M12 2.69l5.66 5.66a8 8 0 1 1-11.31 0z" />
  </svg>
)
const IconFlame = ({ color, size = 20 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
    <path d="M8.5 14.5A2.5 2.5 0 0 0 11 17c1.38 0 2.5-1.12 2.5-2.5 0-1.14-.72-2.1-1.5-2.5.3 1.57-1 2.5-2 1.5C8.5 12 7 10 7 8c0-2 1-4 3-5-1 3 4 3 4 7" />
    <path d="M12 8c0-1.5 1-3 2-4 1 2 2 4 2 6a4 4 0 0 1-8 0" />
  </svg>
)
const IconClipboard = ({ color, size = 20 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
    <path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2" />
    <rect x="8" y="2" width="8" height="4" rx="1" ry="1" />
    <line x1="9" y1="12" x2="15" y2="12" /><line x1="9" y1="16" x2="13" y2="16" />
  </svg>
)
const IconHeart = ({ color, size = 20 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
    <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z" />
  </svg>
)
const IconTarget = ({ color, size = 18 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="12" cy="12" r="10" /><circle cx="12" cy="12" r="6" /><circle cx="12" cy="12" r="2" />
  </svg>
)
const IconZap = ({ color, size = 18 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
    <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2" />
  </svg>
)
const IconScales = ({ color, size = 22 }) => (
  <svg width={size} height={size} viewBox="-1 -1 26 26" fill="none" stroke={color} strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
    <path d="M12 3v18M3 7l9-4 9 4M5 21h14" />
    <path d="M5 7l-2 6c0 2 2 3 4 3s4-1 4-3L9 7" />
    <path d="M19 7l-2 6c0 2 2 3 4 3s4-1 4-3L19 7" />
  </svg>
)
const IconPlate = ({ color, size = 22 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
    <path d="M3 11l19-9-9 19-2-8-8-2z" />
  </svg>
)
const IconGoal = ({ color, size = 22 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="12" cy="12" r="10" />
    <path d="M12 8v4l3 3" />
    <path d="m16.24 7.76-1.06 1.06" />
  </svg>
)

const NAV_ITEMS = [
  { label: "Home",          Icon: HomeIcon,         path: "/dashboard" },
  { label: "Smart Recipes", Icon: SearchNavIcon,    path: "/recipes"   },
  { label: "Inventory",     Icon: BoxIcon,          path: "/inventory" },
  { label: "Meal Planning", Icon: CalendarNavIcon,  path: "/meal-plan" },
  { label: "Insights",       Icon: BarChartNavIcon,  path: "/nutrition"   },
  { label: "Profile",       Icon: PersonIcon,       path: "/profile"   },
]

function getWeekRange() {
  const today = new Date()
  const dow = (today.getDay() + 6) % 7
  const monday = new Date(today)
  monday.setDate(today.getDate() - dow)
  const sunday = new Date(monday)
  sunday.setDate(monday.getDate() + 6)
  const fmt = d => d.toLocaleDateString("en-US", { month: "short", day: "numeric" })
  return `${fmt(monday)} â€“ ${fmt(sunday)}, ${sunday.getFullYear()}`
}

// â”€â”€ Charts â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

function DonutChart({ segments, size = 160, stroke = 28 }) {
  const cx = size / 2, cy = size / 2
  const r = (size - stroke) / 2
  const C = 2 * Math.PI * r
  let cum = 0
  return (
    <svg width={size} height={size}>
      <circle cx={cx} cy={cy} r={r} fill="none" stroke="#f0f0f0" strokeWidth={stroke} />
      {segments.map((seg, i) => {
        if (!seg.pct) { cum += seg.pct; return null }
        const dash = (seg.pct / 100) * C
        const off = -(cum / 100) * C
        cum += seg.pct
        return (
          <circle key={i} cx={cx} cy={cy} r={r} fill="none"
            stroke={seg.color} strokeWidth={stroke}
            strokeDasharray={`${dash} ${C - dash}`}
            strokeDashoffset={off}
            transform={`rotate(-90,${cx},${cy})`}
          />
        )
      })}
      <text x={cx} y={cy - 6} textAnchor="middle" fontSize="16" fontWeight="700" fill="#111" fontFamily={FONT}>
        {segments[0]?.pct ?? 0}%
      </text>
      <text x={cx} y={cy + 12} textAnchor="middle" fontSize="11" fill="#9ca3af" fontFamily={FONT}>Protein</text>
    </svg>
  )
}

function LineChart({ data, height = 200 }) {
  const VW = 600, pad = { t: 16, r: 16, b: 32, l: 44 }
  const W = VW - pad.l - pad.r, H = height - pad.t - pad.b
  const vals = data.map(d => d.calories)
  const maxVal = Math.max(...vals, 400)
  const step = Math.ceil(maxVal / 3 / 200) * 200
  const grids = [0, step, step * 2, step * 3].filter(v => v <= maxVal * 1.15)
  const pts = data.map((d, i) => ({
    x: pad.l + (i / Math.max(data.length - 1, 1)) * W,
    y: pad.t + H - (d.calories / maxVal) * H,
    ...d,
  }))
  const lineD = pts.map((p, i) => `${i === 0 ? "M" : "L"}${p.x.toFixed(1)},${p.y.toFixed(1)}`).join(" ")
  const areaD = lineD + ` L${pts.at(-1).x.toFixed(1)},${(pad.t + H).toFixed(1)} L${pts[0].x.toFixed(1)},${(pad.t + H).toFixed(1)}Z`
  return (
    <svg viewBox={`0 0 ${VW} ${height}`} width="100%" height={height} style={{ display: "block", overflow: "visible" }}>
      <defs>
        <linearGradient id="lg" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="#206C1B" stopOpacity="0.13" />
          <stop offset="100%" stopColor="#206C1B" stopOpacity="0" />
        </linearGradient>
      </defs>
      {grids.map((v, i) => {
        const y = pad.t + H - (v / maxVal) * H
        return (
          <g key={i}>
            <line x1={pad.l} x2={VW - pad.r} y1={y} y2={y} stroke="#f0f0f0" strokeWidth="1" />
            <text x={pad.l - 8} y={y + 4} fontSize="10" fill="#bbb" textAnchor="end" fontFamily={FONT}>{v}</text>
          </g>
        )
      })}
      <path d={areaD} fill="url(#lg)" />
      <path d={lineD} fill="none" stroke="#206C1B" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" />
      {pts.map((p, i) => <circle key={i} cx={p.x} cy={p.y} r="4.5" fill="#fff" stroke="#206C1B" strokeWidth="2.5" />)}
      {pts.map((p, i) => <text key={i} x={p.x} y={height - 4} fontSize="10" fill="#bbb" textAnchor="middle" fontFamily={FONT}>{p.day}</text>)}
    </svg>
  )
}

function NutrientBarChart({ data, height = 200 }) {
  const VW = 560, pad = { t: 20, r: 16, b: 48, l: 44 }
  const W = VW - pad.l - pad.r, H = height - pad.t - pad.b
  const groupW = W / data.length
  const barW = groupW * 0.52
  return (
    <svg viewBox={`0 0 ${VW} ${height}`} width="100%" height={height} style={{ display: "block" }}>
      {[0, 50, 100].map((pct, i) => {
        const y = pad.t + H * (1 - pct / 100)
        return (
          <g key={i}>
            <line x1={pad.l} x2={VW - pad.r} y1={y} y2={y} stroke="#f0f0f0" strokeWidth="1" />
            <text x={pad.l - 8} y={y + 4} fontSize="10" fill="#bbb" textAnchor="end" fontFamily={FONT}>{pct}%</text>
          </g>
        )
      })}
      {data.map((d, i) => {
        const cx = pad.l + i * groupW + groupW / 2
        const pct = d.goal > 0 ? Math.min(d.current / d.goal, 1) : 0
        const currH = pct * H
        return (
          <g key={i}>
            <rect x={cx - barW / 2} y={pad.t} width={barW} height={H} fill="#e5e7eb" rx="5" />
            {currH > 0 && <rect x={cx - barW / 2} y={pad.t + H - currH} width={barW} height={currH} fill="#206C1B" rx="5" />}
            <text x={cx} y={pad.t + H + 16} fontSize="10" fill="#6b7280" textAnchor="middle" fontFamily={FONT}>{d.name}</text>
            <text x={cx} y={pad.t + H + 30} fontSize="9" fill="#bbb" textAnchor="middle" fontFamily={FONT}>{Math.round(pct * 100)}%</text>
          </g>
        )
      })}
    </svg>
  )
}

// â”€â”€ UI components â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

const SUB_COLORS = { green: "#206C1B", yellow: "#b45309", red: "#dc2626", grey: "#9ca3af" }

function StatCard({ iconBg, iconColor, Icon, label, value, sub, subGreen, subColor, badge, badgeUp }) {
  const resolvedColor = subColor ? SUB_COLORS[subColor] : (subGreen ? SUB_COLORS.green : SUB_COLORS.grey)
  const isBold = subColor ? subColor !== "grey" : subGreen
  return (
    <div style={{ background: "#fff", border: "1px solid #f0f0f0", borderRadius: 16, padding: "20px 22px", display: "flex", alignItems: "center", gap: 16 }}>
      <div style={{ width: 48, height: 48, borderRadius: "50%", background: iconBg, display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0 }}>
        <Icon color={iconColor} size={22} />
      </div>
      <div style={{ flex: 1, minWidth: 0 }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 6 }}>
          <span style={{ fontSize: 14, fontWeight: 600, color: "#374151", fontFamily: FONT }}>{label}</span>
          {badge != null && (
            <span style={{ fontSize: 11.5, fontWeight: 600, color: badgeUp ? "#206C1B" : "#dc2626", fontFamily: FONT }}>
              {badgeUp ? "â†—" : "â†˜"} {badge}
            </span>
          )}
        </div>
        <div style={{ display: "flex", alignItems: "baseline", gap: 6, fontFamily: FONT }}>
          <span style={{ fontSize: 28, fontWeight: 800, color: "#0d1a0d", lineHeight: 1 }}>{value ?? "â€”"}</span>
          {sub && <span style={{ fontSize: 13, color: resolvedColor, fontWeight: isBold ? 600 : 400 }}>{sub}</span>}
        </div>
      </div>
    </div>
  )
}

function MacroBar({ label, Icon, iconColor, current, target, unit, color }) {
  const pct = target > 0 ? Math.min(Math.round(current / target * 100), 100) : 0
  return (
    <div style={{ background: "#fff", border: "1px solid #f0f0f0", borderRadius: 16, padding: "20px 22px" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 12 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 7 }}>
          <Icon color={iconColor} size={16} />
          <span style={{ fontSize: 14, fontWeight: 600, color: "#374151", fontFamily: FONT }}>{label}</span>
        </div>
        <span style={{ fontSize: 12, fontWeight: 600, color: "#9ca3af", fontFamily: FONT }}>{pct}%</span>
      </div>
      <div style={{ display: "flex", alignItems: "baseline", gap: 6, marginBottom: 12, fontFamily: FONT }}>
        <span style={{ fontSize: 28, fontWeight: 800, color: "#0d1a0d", lineHeight: 1 }}>{current}</span>
        <span style={{ fontSize: 13, color: "#9ca3af" }}>/ {target} {unit}</span>
      </div>
      <div style={{ background: "#f0f0f0", borderRadius: 999, height: 5, overflow: "hidden" }}>
        <div style={{ width: `${pct}%`, height: "100%", background: color, borderRadius: 999 }} />
      </div>
    </div>
  )
}

function Stars({ count = 4, max = 5 }) {
  return (
    <div style={{ display: "flex", gap: 3, marginTop: 6 }}>
      {Array.from({ length: max }).map((_, i) => (
        <svg key={i} width="15" height="15" viewBox="0 0 24 24" fill={i < count ? "#3b82f6" : "#e5e7eb"} stroke="none">
          <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2" />
        </svg>
      ))}
    </div>
  )
}

// â”€â”€ Main page â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

export default function Nutrition() {
  const navigate = useNavigate()
  const [data, setData]       = useState(null)
  const [collapsed, setCollapsed] = useState(false)
  const [userName, setUserName]   = useState("")
  const [period, setPeriod]       = useState("weekly")
  const userId = localStorage.getItem("userId")

  useEffect(() => {
    if (!userId) { navigate("/login"); return }
    getProfile(userId).then(p => setUserName(p.name || p.email || "")).catch(() => {})
  }, [])

  useEffect(() => {
    if (!userId) return
    setData(null)
    fetch(`${BASE_URL}/nutrition/insights?period=${period}`, { headers: { "user-id": userId } })
      .then(r => r.json())
      .then(d => setData(d))
      .catch(() => {})
  }, [period])

  const firstName = userName.split(" ")[0]
  const tm = data?.today_macros || {}
  const md = data?.macro_distribution || {}

  const donutSegments = [
    { pct: md.protein_pct || 0, color: "#206C1B", label: "Protein", g: tm.protein_g?.current ?? 0 },
    { pct: md.carbs_pct   || 0, color: "#3b82f6", label: "Carbs",   g: tm.carbs_g?.current ?? 0   },
    { pct: md.fat_pct     || 0, color: "#f59e0b", label: "Fat",     g: tm.fat_g?.current ?? 0     },
  ]

  const CONSISTENCY_DISPLAY = {
    "Excellent":  { color: "#2563eb", stars: 5 },
    "Good":       { color: "#2563eb", stars: 3 },
    "Needs Work": { color: "#dc2626", stars: 2 },
  }
  const consistencyLabel = data?.meal_consistency ?? ""
  const consistency = CONSISTENCY_DISPLAY[consistencyLabel] ?? { color: "#9ca3af", stars: 0 }

  return (
    <div style={{ height: "100vh", background: "#fff", fontFamily: FONT, display: "flex", flexDirection: "column", overflow: "hidden" }}>
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
            <span style={{ fontSize: 11 }}>âœ¦</span> Your personalized kitchen assistant
          </div>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
          <NotificationsDropdown userId={userId} />
          <div onClick={() => navigate("/profile")} style={{ display: "flex", alignItems: "center", gap: 8, padding: "6px 12px", borderRadius: 999, border: "1.5px solid #e8ede2", cursor: "pointer" }}>
            <div style={{ width: 28, height: 28, borderRadius: "50%", background: "#f3f4f6", display: "flex", alignItems: "center", justifyContent: "center" }}>
              <UserIcon />
            </div>
            <span style={{ fontSize: 14, fontWeight: 500, color: "#374151" }}>{firstName || "â€”"}</span>
          </div>
          <button onClick={() => { localStorage.removeItem("userId"); localStorage.removeItem("token"); navigate("/login") }} style={{ background: "none", border: "1.5px solid #e0e0e0", borderRadius: 8, padding: "7px 16px", fontSize: 13, fontWeight: 500, color: "#6b7280", cursor: "pointer", fontFamily: FONT }}>Log out</button>
        </div>
      </nav>

      <div style={{ flex: 1, display: "flex", overflow: "hidden" }}>

        {/* Sidebar */}
        <aside style={{ width: collapsed ? 56 : 220, flexShrink: 0, borderRight: "1px solid #f0f0ee", display: "flex", flexDirection: "column", padding: collapsed ? "24px 8px" : "24px 16px", overflow: "hidden", transition: "width 0.2s ease, padding 0.2s ease" }}>
          <button onClick={() => setCollapsed(c => !c)} style={{ alignSelf: collapsed ? "center" : "flex-end", background: "none", border: "1.5px solid #e8ede2", borderRadius: 8, width: 28, height: 28, display: "flex", alignItems: "center", justifyContent: "center", cursor: "pointer", marginBottom: 16, flexShrink: 0, color: "#9ca3af" }}>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
              {collapsed ? <path d="M9 18l6-6-6-6" /> : <path d="M15 18l-6-6 6-6" />}
            </svg>
          </button>
          <nav style={{ display: "flex", flexDirection: "column", gap: 4, flex: 1 }}>
            {NAV_ITEMS.map(({ label, Icon, path }) => {
              const active = path === "/nutrition"
              return (
                <div key={label}>
                  {path === "/profile" && <div style={{ height: 1, background: "#f0f0ee", margin: "6px 0" }} />}
                  <button onClick={() => navigate(path)} title={collapsed ? label : undefined} style={{ width: "100%", display: "flex", alignItems: "center", justifyContent: collapsed ? "center" : "flex-start", gap: 10, padding: collapsed ? "10px 0" : "10px 14px", borderRadius: 10, border: "none", cursor: "pointer", textAlign: "left", background: active ? "#E4F2DB" : "transparent", color: active ? "#166534" : "#6b7280", fontWeight: active ? 600 : 500, fontSize: 14, fontFamily: FONT, transition: "background 0.15s" }}>
                    <Icon color={active ? "#166534" : "#9ca3af"} />
                    {!collapsed && label}
                  </button>
                </div>
              )
            })}
          </nav>
          {!collapsed && (
            <div style={{ background: "#E4F2DB", borderRadius: 14, padding: 16, border: "1px solid #E4F2DB" }}>
              <LeafIcon size={18} color="#166534" />
              <div style={{ fontSize: 13, fontWeight: 700, color: "#166534", marginTop: 8, marginBottom: 4 }}>Small steps, big impact.</div>
              <div style={{ fontSize: 12, color: "#15803d", lineHeight: 1.5 }}>Every healthy choice counts!</div>
            </div>
          )}
          {collapsed && (
            <div style={{ display: "flex", justifyContent: "center", paddingBottom: 8 }}>
              <LeafIcon size={18} color="#166534" />
            </div>
          )}
        </aside>

        {/* Main content */}
        <div style={{ flex: 1, display: "flex", flexDirection: "column", overflow: "hidden" }}>

          {/* Page header */}
          <div style={{ padding: "24px 32px 0", flexShrink: 0, display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
            <div>
              <h1 style={{ fontSize: 24, fontWeight: 800, color: "#0d1a0d", marginBottom: 4 }}>Nutrition Insights</h1>
              <p style={{ fontSize: 14, color: "#6b7280" }}>Track your nutrition goals and health metrics</p>
            </div>
            <div style={{ display: "flex", gap: 2, background: "#f3f4f6", borderRadius: 10, padding: 3, marginTop: 4 }}>
              {["weekly", "monthly"].map(p => (
                <button key={p} onClick={() => setPeriod(p)} style={{
                  padding: "7px 18px", borderRadius: 8, border: "none", cursor: "pointer",
                  fontSize: 13, fontWeight: 600, fontFamily: FONT,
                  background: period === p ? "#fff" : "transparent",
                  color: period === p ? "#0d1a0d" : "#6b7280",
                  boxShadow: period === p ? "0 1px 3px rgba(0,0,0,0.08)" : "none",
                  transition: "all 0.15s"
                }}>
                  {p.charAt(0).toUpperCase() + p.slice(1)}
                </button>
              ))}
            </div>
          </div>

          {/* Scrollable content */}
          <div style={{ flex: 1, overflowY: "auto", padding: "20px 32px 32px", display: "flex", flexDirection: "column", gap: 16 }}>

            {/* Row 1 â€” 4 stat cards */}
            <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 14 }}>
              <StatCard
                iconBg="#f0fdf4" iconColor="#16a34a" Icon={IconDrop}
                label="Current Streak"
                value={data ? `${data.streak ?? 0} days` : "â€”"}
                sub={data
                  ? (data.streak ?? 0) >= 7 ? "On fire! Keep going!"
                  : (data.streak ?? 0) >= 3 ? "Keep it going!"
                  : (data.streak ?? 0) >= 1 ? "Good start!"
                  : "Start your streak"
                  : undefined}
                subGreen={(data?.streak ?? 0) >= 3}
                badge={data && (data.streak ?? 0) > 7 ? (data.streak ?? 0) - 7 : null} badgeUp
              />
              <StatCard
                iconBg="#fff7ed" iconColor="#ea580c" Icon={IconFlame}
                label="Avg Calories"
                value={data?.avg_calories ?? "â€”"}
                sub={`daily avg this ${period === "monthly" ? "month" : "week"}`}
              />
              <StatCard
                iconBg="#eff6ff" iconColor="#3b82f6" Icon={IconClipboard}
                label="Meals Logged"
                value={data?.meals_logged ?? "â€”"}
                sub={`this ${period === "monthly" ? "month" : "week"}`}
              />
              <StatCard
                iconBg="#faf5ff" iconColor="#9333ea" Icon={IconHeart}
                label="Health Score"
                value={data ? `${data.health_score ?? 0}/100` : "â€”"}
                sub={data
                  ? (data.health_score ?? 0) >= 80 ? "Great job!"
                  : (data.health_score ?? 0) >= 60 ? "Good progress!"
                  : (data.health_score ?? 0) >= 40 ? "Keep improving"
                  : "Needs attention"
                  : undefined}
                subColor={!data ? undefined
                  : (data.health_score ?? 0) >= 60 ? "green"
                  : (data.health_score ?? 0) >= 40 ? "yellow"
                  : "red"}
              />
            </div>

            {/* Row 2 â€” 4 macro bars */}
            <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 14 }}>
              <MacroBar label="Daily Calories" Icon={IconFlame} iconColor="#ea580c"
                current={tm.calories?.current ?? 0} target={tm.calories?.target ?? 2000} unit="kcal" color="#ea580c" />
              <MacroBar label="Protein" Icon={IconTarget} iconColor="#206C1B"
                current={tm.protein_g?.current ?? 0} target={tm.protein_g?.target ?? 50} unit="g" color="#206C1B" />
              <MacroBar label="Carbohydrates" Icon={IconZap} iconColor="#3b82f6"
                current={tm.carbs_g?.current ?? 0} target={tm.carbs_g?.target ?? 250} unit="g" color="#3b82f6" />
              <MacroBar label="Healthy Fats" Icon={IconDrop} iconColor="#f59e0b"
                current={tm.fat_g?.current ?? 0} target={tm.fat_g?.target ?? 65} unit="g" color="#f59e0b" />
            </div>

            {/* Row 3 â€” donut + line chart */}
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 14 }}>

              {/* Macro Distribution */}
              <div style={{ border: "1px solid #f0f0f0", borderRadius: 16, padding: "22px 24px" }}>
                <h3 style={{ fontSize: 15, fontWeight: 700, color: "#111", marginBottom: 20 }}>Macro Distribution</h3>
                <div style={{ display: "flex", alignItems: "center", gap: 32 }}>
                  <DonutChart segments={donutSegments} size={160} stroke={28} />
                  <div style={{ display: "flex", flexDirection: "column", gap: 14, flex: 1 }}>
                    {donutSegments.map(seg => (
                      <div key={seg.label} style={{ display: "flex", alignItems: "center", gap: 10 }}>
                        <div style={{ width: 11, height: 11, borderRadius: 3, background: seg.color, flexShrink: 0 }} />
                        <span style={{ fontSize: 13, color: "#6b7280", minWidth: 52 }}>{seg.label}</span>
                        <span style={{ fontSize: 13, fontWeight: 700, color: "#111", minWidth: 36 }}>{seg.pct}%</span>
                        <span style={{ fontSize: 12, color: "#9ca3af" }}>{seg.g} g</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {/* Weekly Calorie Trend */}
              <div style={{ border: "1px solid #f0f0f0", borderRadius: 16, padding: "22px 24px" }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 20 }}>
                  <h3 style={{ fontSize: 15, fontWeight: 700, color: "#111" }}>{period === "monthly" ? "Monthly" : "Weekly"} Calorie Trend</h3>
                  <div style={{ display: "flex", alignItems: "center", gap: 6, border: "1px solid #e5e7eb", borderRadius: 8, padding: "5px 12px", fontSize: 12.5, color: "#374151", cursor: "pointer" }}>
                    Calories <span style={{ fontSize: 9, color: "#9ca3af" }}>â–¼</span>
                  </div>
                </div>
                {data?.weekly_trend?.length
                  ? <LineChart data={data.weekly_trend} height={170} />
                  : <div style={{ height: 170, display: "flex", alignItems: "center", justifyContent: "center", color: "#ccc", fontSize: 13 }}>Add meals to see trend</div>
                }
              </div>
            </div>

            {/* Row 4 â€” nutrient bar chart + 3 summary cards */}
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 14 }}>

              {/* Nutrient Goals Progress */}
              <div style={{ border: "1px solid #f0f0f0", borderRadius: 16, padding: "22px 24px" }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 4 }}>
                  <h3 style={{ fontSize: 15, fontWeight: 700, color: "#111" }}>Nutrient Goals Progress</h3>
                  <div style={{ display: "flex", gap: 14, fontSize: 11.5, color: "#6b7280" }}>
                    <span style={{ display: "flex", alignItems: "center", gap: 5 }}>
                      <span style={{ width: 10, height: 10, background: "#206C1B", borderRadius: 2, display: "inline-block" }} /> Current
                    </span>
                    <span style={{ display: "flex", alignItems: "center", gap: 5 }}>
                      <span style={{ width: 10, height: 10, background: "#e5e7eb", borderRadius: 2, display: "inline-block" }} /> Goal
                    </span>
                  </div>
                </div>
                {data?.nutrient_goals?.length
                  ? <NutrientBarChart data={data.nutrient_goals} height={200} />
                  : <div style={{ height: 200, display: "flex", alignItems: "center", justifyContent: "center", color: "#ccc", fontSize: 13 }}>Add meals to see nutrient data</div>
                }
              </div>

              {/* 3 summary cards */}
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 12 }}>

                {/* Nutrition Goals */}
                <div style={{ background: "#f0fdf4", borderRadius: 16, padding: "20px 16px", display: "flex", flexDirection: "column", gap: 6 }}>
                  <div style={{ width: 42, height: 42, borderRadius: 12, background: "#dcfce7", display: "flex", alignItems: "center", justifyContent: "center", marginBottom: 4 }}>
                    <IconGoal color="#16a34a" size={22} />
                  </div>
                  <div style={{ fontSize: 13.5, fontWeight: 700, color: "#111" }}>Nutrition Goals</div>
                  <div style={{ fontSize: 11.5, color: "#6b7280", lineHeight: 1.5 }}>Weekly average across calories, protein, carbs &amp; fat</div>
                  <div style={{ fontSize: 24, fontWeight: 700, color: "#16a34a", marginTop: 4 }}>
                    {data ? `${data.nutrition_goals_pct ?? 0}%` : "â€”"}
                  </div>
                </div>

                {/* Meal Consistency */}
                <div style={{ background: "#fff", border: "1px solid #f0f0f0", borderRadius: 16, padding: "20px 16px", display: "flex", flexDirection: "column", gap: 6 }}>
                  <div style={{ width: 42, height: 42, borderRadius: 12, background: "#eff6ff", display: "flex", alignItems: "center", justifyContent: "center", marginBottom: 4 }}>
                    <IconPlate color="#3b82f6" size={20} />
                  </div>
                  <div style={{ fontSize: 13.5, fontWeight: 700, color: "#111" }}>Meal Consistency</div>
                  <div style={{ fontSize: 11.5, color: "#6b7280", lineHeight: 1.5 }}>
                    {data?.meal_consistency_sub ?? `Logged 0 meals this ${period === "monthly" ? "month" : "week"}`}
                  </div>
                  <div style={{ fontSize: 20, fontWeight: 700, color: consistency.color, marginTop: 4 }}>
                    {data ? consistencyLabel : "â€”"}
                  </div>
                  {data && <Stars count={consistency.stars} />}
                </div>

                {/* Diet Balance */}
                <div style={{ background: "#faf5ff", borderRadius: 16, padding: "20px 16px", display: "flex", flexDirection: "column", gap: 6 }}>
                  <div style={{ width: 42, height: 42, borderRadius: 12, background: "#ede9fe", display: "flex", alignItems: "center", justifyContent: "center", marginBottom: 4, overflow: "visible" }}>
                    <IconScales color="#7c3aed" size={18} />
                  </div>
                  <div style={{ fontSize: 13.5, fontWeight: 700, color: "#111" }}>Diet Balance</div>
                  <div style={{ fontSize: 11.5, color: "#6b7280", lineHeight: 1.5 }}>Based on macro distribution this week</div>
                  <div style={{ fontSize: 24, fontWeight: 700, color: "#7c3aed", marginTop: 4 }}>
                    {data ? `${data.diet_balance_pct ?? 0}%` : "â€”"}
                  </div>
                  {data && (
                    <div style={{ background: "#ede9fe", borderRadius: 999, height: 5, overflow: "hidden", marginTop: 2 }}>
                      <div style={{ width: `${data.diet_balance_pct ?? 0}%`, height: "100%", background: "#7c3aed", borderRadius: 999 }} />
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* Tip bar */}
            <div style={{ display: "flex", alignItems: "center", gap: 10, background: "#f7fef7", border: "1px solid #e0f2e0", borderRadius: 12, padding: "12px 18px", fontSize: 12.5, color: "#374151" }}>
              <LeafIcon size={16} color="#206C1B" />
              <span>Tip: Consistency is the key to long-term results. Keep making healthy choices!</span>
            </div>

          </div>
        </div>
      </div>
    </div>
  )
}
