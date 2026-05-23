import { useState, useEffect } from "react"
import { useNavigate } from "react-router-dom"
import axios from "axios"
import { getProfile } from "../services/api"
import NotificationsDropdown from "../components/NotificationsDropdown"

const BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000"
const DAYS = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]
const DAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
const MEAL_TYPES = ["breakfast", "lunch", "dinner"]
const MEAL_CUTOFF = { breakfast: 8, lunch: 13, dinner: 20 }

function getTodayDow() {
  return (new Date().getDay() + 6) % 7
}

function getWeekDates() {
  const today = new Date()
  const dow = getTodayDow()
  const monday = new Date(today)
  monday.setDate(today.getDate() - dow)
  return Array.from({ length: 7 }, (_, i) => {
    const d = new Date(monday)
    d.setDate(monday.getDate() + i)
    return d
  })
}

function formatDayDate(date) {
  return date.toLocaleDateString("en-US", { month: "short", day: "numeric" })
}

function shouldShowTick(meal, todayDow, currentHour) {
  const mealDow = DAY_NAMES.indexOf(meal.day)
  if (meal.consumed) return true
  if (mealDow < todayDow) return true
  if (mealDow === todayDow && currentHour >= (MEAL_CUTOFF[meal.meal_type] ?? 24)) return true
  return false
}

// --- Nav icons ---
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
const BarChartIcon = ({ color }) => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
    <line x1="18" y1="20" x2="18" y2="10" /><line x1="12" y1="20" x2="12" y2="4" /><line x1="6" y1="20" x2="6" y2="14" />
  </svg>
)
const NutritionIcon = ({ color }) => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
    <path d="M12 2a10 10 0 0 1 10 10H2A10 10 0 0 1 12 2z" /><path d="M12 22c4 0 7-2 8-6H4c1 4 4 6 8 6z" />
  </svg>
)
const PersonIcon = ({ color }) => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
    <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" /><circle cx="12" cy="7" r="4" />
  </svg>
)

const NAV_ITEMS = [
  { label: "Home",          Icon: HomeIcon,        path: "/dashboard" },
  { label: "Smart Recipes", Icon: SearchNavIcon,   path: "/recipes"   },
  { label: "Inventory",     Icon: BoxIcon,         path: "/inventory" },
  { label: "Meal Planning", Icon: CalendarNavIcon, path: "/meal-plan" },
  { label: "Insights",       Icon: BarChartIcon,    path: "/nutrition"   },
  { label: "Profile",       Icon: PersonIcon,      path: "/profile"   },
]

const MEAL_COLORS = { breakfast: "#f97316", lunch: "#22c55e", dinner: "#3b82f6" }
const MEAL_BG = { breakfast: "#fff7ed", lunch: "#E4F2DB", dinner: "#eff6ff" }
const MEAL_TEXT = { breakfast: "#111", lunch: "#111", dinner: "#111" }
const MEAL_ICON_SRC = {
  breakfast: "/noun-breakfast-8152061.svg",
  lunch:     "/noun-lunch-8183054.svg",
  dinner:    "/noun-dinner-8247474.svg",
}
const MEAL_ICON_FILTER = {
  breakfast: "brightness(0) saturate(100%) invert(57%) sepia(93%) saturate(1185%) hue-rotate(1deg) brightness(105%)",
  lunch:     "brightness(0) saturate(100%) invert(56%) sepia(72%) saturate(559%) hue-rotate(104deg) brightness(100%)",
  dinner:    "brightness(0) saturate(100%) invert(42%) sepia(94%) saturate(1000%) hue-rotate(207deg) brightness(104%)",
}

function MealTypeIcon({ type, size = 14 }) {
  return (
    <img
      src={MEAL_ICON_SRC[type]}
      width={size}
      height={size}
      alt={type}
      style={{ objectFit: "contain", filter: MEAL_ICON_FILTER[type] }}
    />
  )
}

// --- MealCard ---
function MealCard({ meal, onDelete, todayDow, currentHour, mealType }) {
  const [confirmDelete, setConfirmDelete] = useState(false)
  const ticked = shouldShowTick(meal, todayDow, currentHour)
  return (
    <div style={{ background: MEAL_BG[mealType] || "#f9fafb", border: "none", borderRadius: 12, padding: "10px 12px", position: "relative", minHeight: 60 }}>
      {!confirmDelete ? (
        <button onClick={() => setConfirmDelete(true)} style={{ position: "absolute", top: 5, right: 6, background: "none", border: "none", cursor: "pointer", color: "#ccc", fontSize: 16, lineHeight: 1, padding: 0 }}>×</button>
      ) : (
        <div style={{ position: "absolute", top: 5, right: 6, display: "flex", gap: 3 }}>
          <button onClick={() => onDelete(meal.day, mealType)} style={{ fontSize: 10, background: "#fee2e2", color: "#dc2626", border: "none", borderRadius: 4, padding: "2px 6px", cursor: "pointer", fontFamily: "'DM Sans', sans-serif", fontWeight: 600 }}>Delete</button>
          <button onClick={() => setConfirmDelete(false)} style={{ fontSize: 10, background: "#d4ead0", color: "#166534", border: "none", borderRadius: 4, padding: "2px 6px", cursor: "pointer", fontFamily: "'DM Sans', sans-serif" }}>No</button>
        </div>
      )}
      <div style={{ fontSize: 13, fontWeight: 700, color: MEAL_TEXT[mealType] || "#111", paddingRight: 18, lineHeight: 1.4 }}>{meal.meal_name}</div>
      {ticked && (
        <div style={{ position: "absolute", bottom: 8, right: 8, width: 18, height: 18, background: "#206C1B", borderRadius: "50%", display: "flex", alignItems: "center", justifyContent: "center" }}>
          <svg width="9" height="9" viewBox="0 0 24 24" fill="none" stroke="#fff" strokeWidth="3.5" strokeLinecap="round" strokeLinejoin="round">
            <path d="M20 6 9 17l-5-5" />
          </svg>
        </div>
      )}
    </div>
  )
}

// --- AddMealModal ---
function AddMealModal({ modal, availableTypes, onAdd, onClose }) {
  const [mealName, setMealName] = useState("")
  const [mealType, setMealType] = useState(modal.meal_type || availableTypes[0])
  const [loading, setLoading] = useState(false)

  const handleSubmit = async () => {
    if (!mealName.trim()) return
    setLoading(true)
    try {
      await onAdd({ day: modal.day, meal_type: mealType, meal_name: mealName.trim() })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ position: "fixed", inset: 0, background: "rgba(0,0,0,0.25)", display: "flex", alignItems: "center", justifyContent: "center", zIndex: 100 }} onClick={onClose}>
      <div style={{ background: "#fff", borderRadius: 20, padding: 28, width: 360, boxShadow: "0 20px 60px rgba(0,0,0,0.15)" }} onClick={e => e.stopPropagation()}>
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 18 }}>
          <h2 style={{ fontSize: 16, fontWeight: 700, color: "#111", margin: 0 }}>{modal.day}</h2>
          <button onClick={onClose} style={{ background: "none", border: "none", cursor: "pointer", fontSize: 22, color: "#bbb", lineHeight: 1, padding: 0 }}>×</button>
        </div>

        {!modal.meal_type && availableTypes.length > 1 && (
          <div style={{ display: "flex", gap: 6, marginBottom: 16 }}>
            {availableTypes.map(t => (
              <button key={t} onClick={() => setMealType(t)} style={{ flex: 1, padding: "7px 0", borderRadius: 10, border: `1.5px solid ${mealType === t ? MEAL_COLORS[t] : "#e0e0e0"}`, background: mealType === t ? `${MEAL_COLORS[t]}18` : "none", color: mealType === t ? MEAL_COLORS[t] : "#aaa", cursor: "pointer", fontSize: 12, fontWeight: 600, textTransform: "capitalize", fontFamily: "'DM Sans', sans-serif" }}>
                {t}
              </button>
            ))}
          </div>
        )}

        {(modal.meal_type || availableTypes.length === 1) && (
          <div style={{ fontSize: 13, color: "#aaa", textTransform: "capitalize", marginBottom: 14 }}>{mealType}</div>
        )}

        <input
          autoFocus
          value={mealName}
          onChange={e => setMealName(e.target.value)}
          onKeyDown={e => e.key === "Enter" && handleSubmit()}
          placeholder="Meal name"
          style={{ width: "100%", height: 42, border: "1.5px solid #e8e8e8", borderRadius: 10, padding: "0 14px", fontSize: 14, fontFamily: "'DM Sans', sans-serif", outline: "none", boxSizing: "border-box", marginBottom: 14 }}
        />

        {loading && (
          <div style={{ display: "flex", alignItems: "center", gap: 8, fontSize: 12, color: "#aaa", marginBottom: 14 }}>
            <div style={{ width: 12, height: 12, border: "2px solid #e0e0e0", borderTopColor: "#111", borderRadius: "50%", animation: "spin 0.7s linear infinite", flexShrink: 0 }} />
            Fetching ingredients…
          </div>
        )}

        <div style={{ display: "flex", gap: 8 }}>
          <button onClick={onClose} style={{ flex: 1, height: 40, background: "none", border: "1.5px solid #e0e0e0", borderRadius: 10, cursor: "pointer", fontSize: 14, color: "#888", fontFamily: "'DM Sans', sans-serif" }}>Cancel</button>
          <button onClick={handleSubmit} disabled={loading || !mealName.trim()} style={{ flex: 1, height: 40, background: "#166534", color: "#fff", border: "none", borderRadius: 10, cursor: loading || !mealName.trim() ? "not-allowed" : "pointer", fontSize: 14, fontWeight: 600, fontFamily: "'DM Sans', sans-serif", opacity: loading || !mealName.trim() ? 0.6 : 1 }}>
            {loading ? "Adding…" : "Add"}
          </button>
        </div>
      </div>
    </div>
  )
}

const resetMealRow = () => ({ meal_name: "", day: "Monday", meal_type: "breakfast" })

// --- Main ---
export default function MealPlan() {
  const navigate = useNavigate()
  const [meals, setMeals] = useState({})
  const [modal, setModal] = useState(null)
  const [restocked, setRestocked] = useState(false)
  const [collapsed, setCollapsed] = useState(false)
  const [userName, setUserName] = useState("")
  const [showBulkModal, setShowBulkModal] = useState(false)
  const [bulkRows, setBulkRows] = useState([resetMealRow()])
  const [bulkError, setBulkError] = useState("")
  const [bulkAdding, setBulkAdding] = useState(false)
  const userId = localStorage.getItem("userId")

  const now = new Date()
  const todayDow = getTodayDow()
  const currentHour = now.getHours()
  const weekDates = getWeekDates()

  useEffect(() => {
    if (!userId) { navigate("/login"); return }
    getProfile(userId).then(p => setUserName(p.name || p.email || "")).catch(() => {})
  }, [])
  useEffect(() => { fetchMeals() }, [])

  const fetchMeals = async () => {
    try {
      const res = await axios.get(`${BASE_URL}/meal-plan`, { headers: { "user-id": userId } })
      setMeals(res.data.meals)
      setRestocked(res.data.restocked)
    } catch (e) { console.error(e) }
  }

  const getSlotMeal = (dayIndex, mealType) => {

  const day = DAY_NAMES[dayIndex]

  const slotMeals =
    meals?.[day]?.[mealType] || []

  // Get latest valid meal
  for (let i = slotMeals.length - 1; i >= 0; i--) {

    if (slotMeals[i]?.valid === true) {
      return slotMeals[i]
        }
      }

    return null
    }

  const getEmptyTypes = (dayIndex) => {

    return MEAL_TYPES.filter(type => {

      const meal = getSlotMeal(dayIndex, type)

      return !meal
    })
  }

  const handleAddClick = (dayIndex) => {
    const empty = getEmptyTypes(dayIndex)
    if (empty.length === 0) return
    setModal({ day: DAY_NAMES[dayIndex], meal_type: empty.length === 1 ? empty[0] : null, _emptyTypes: empty, _dayIndex: dayIndex })
  }

  const handleAdd = async (payload) => {
    await axios.post(`${BASE_URL}/meal-plan/add`, payload, { headers: { "user-id": userId } })
    setModal(null)
    fetchMeals()
  }

  const handleDelete = async (day, mealType) => {

    await axios.post(
      `${BASE_URL}/meal-plan/delete`,
      {
        day,
        meal_type: mealType
      },
      {
        headers: { "user-id": userId }
      }
    )

    fetchMeals()
  }

  const updateBulkRow = (idx, field, value) =>
    setBulkRows(rows => rows.map((r, i) => i === idx ? { ...r, [field]: value } : r))

  const handleBulkAdd = async () => {
    const validRows = bulkRows.filter(r => r.meal_name.trim())
    if (validRows.length === 0) { setBulkError("Please fill in at least one meal name"); return }
    // Last row wins for same (day, meal_type)
    const dedupedMap = new Map()
    validRows.forEach(r => dedupedMap.set(`${r.day}__${r.meal_type}`, r))
    const deduped = [...dedupedMap.values()]
    setBulkAdding(true)
    setBulkError("")
    try {
      await Promise.all(deduped.map(r =>
        axios.post(`${BASE_URL}/meal-plan/add`, { day: r.day, meal_type: r.meal_type, meal_name: r.meal_name.trim() }, { headers: { "user-id": userId } })
      ))
      setShowBulkModal(false)
      setBulkRows([resetMealRow()])
      fetchMeals()
    } catch (err) {
      setBulkError(err?.response?.data?.detail || err?.message || "Failed to add meals")
    } finally {
      setBulkAdding(false)
    }
  }

  const firstName = userName.split(" ")[0]

  return (
    <div style={{ height: "100vh", background: "#fff", fontFamily: "'DM Sans', sans-serif", display: "flex", flexDirection: "column", overflow: "hidden" }}>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700;800&display=swap');
        * { box-sizing: border-box; margin: 0; padding: 0; }
        @keyframes spin { to { transform: rotate(360deg); } }
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
          <button onClick={() => { localStorage.removeItem("userId"); localStorage.removeItem("token"); navigate("/login") }} style={{ background: "none", border: "1.5px solid #e0e0e0", borderRadius: 8, padding: "7px 16px", fontSize: 14, fontWeight: 500, color: "#6b7280", cursor: "pointer", fontFamily: "'DM Sans', sans-serif" }}>Log out</button>
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
              const active = path === "/meal-plan"
              return (
                <div key={label}>
                  {path === "/profile" && <div style={{ height: 1, background: "#f0f0ee", margin: "6px 0" }} />}
                  <button onClick={() => navigate(path)} title={collapsed ? label : undefined} style={{ width: "100%", display: "flex", alignItems: "center", justifyContent: collapsed ? "center" : "flex-start", gap: 10, padding: collapsed ? "10px 0" : "10px 14px", borderRadius: 10, border: "none", cursor: "pointer", textAlign: "left", background: active ? "#E4F2DB" : "transparent", color: active ? "#166534" : "#6b7280", fontWeight: active ? 600 : 500, fontSize: 14, fontFamily: "'DM Sans', sans-serif", transition: "background 0.15s" }}>
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
          <div style={{ padding: "24px 32px 0", flexShrink: 0, display: "flex", alignItems: "center", justifyContent: "space-between" }}>
            <div>
              <h1 style={{ fontSize: 24, fontWeight: 800, color: "#0d1a0d", marginBottom: 4 }}>Meal Planning</h1>
              <p style={{ fontSize: 14, color: "#6b7280" }}>Your weekly template — edit anytime</p>
            </div>
            <button
              onClick={() => { setShowBulkModal(true); setBulkRows([resetMealRow()]); setBulkError("") }}
              style={{ height: 44, background: "#166534", color: "#fff", border: "none", borderRadius: 12, padding: "0 22px", fontSize: 14, fontWeight: 600, cursor: "pointer", fontFamily: "'DM Sans', sans-serif", display: "flex", alignItems: "center", gap: 6 }}>
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
              Add Meals
            </button>
          </div>

          {/* Scrollable area */}
          <div style={{ flex: 1, overflow: "hidden", padding: "20px 32px 32px", display: "flex", flexDirection: "column" }}>

            {/* Restock notice */}
            {restocked && (
              <div style={{ display: "flex", alignItems: "center", gap: 10, background: "#E4F2DB", border: "1.5px solid #bbf7d0", borderRadius: 12, padding: "12px 18px", marginBottom: 16, fontSize: 13, color: "#15803d", fontWeight: 500 }}>
                <span>🛒</span>
                <span>Your inventory has been restocked for the new week based on your meal plan.</span>
                <button onClick={() => setRestocked(false)} style={{ marginLeft: "auto", background: "none", border: "none", cursor: "pointer", color: "#86efac", fontSize: 18, lineHeight: 1, padding: 0 }}>×</button>
              </div>
            )}

            {/* Info banner */}
            <div style={{ display: "flex", alignItems: "flex-start", gap: 10, background: "#f7fef7", border: "1.5px solid #e0f2e0", borderRadius: 12, padding: "14px 18px", marginBottom: 24, fontSize: 13, color: "#374151", lineHeight: 1.6 }}>
              <div style={{ width: 20, height: 20, borderRadius: "50%", background: "#E4F2DB", display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0, marginTop: 1 }}>
                <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="#206C1B" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                  <line x1="12" y1="16" x2="12" y2="12" /><line x1="12" y1="8" x2="12.01" y2="8" />
                </svg>
              </div>
              <span>
                <strong style={{ color: "#166534" }}>Weekly grocery assumption:</strong> Meals from past days are automatically marked as consumed and deducted from your inventory. Every Monday, your inventory is restocked based on your meal plan — simulating a weekly grocery run.
              </span>
            </div>

            {/* Calendar */}
            <div style={{ border: "1px solid #f0f0f0", borderRadius: 20, overflow: "hidden", flex: 1, display: "flex", flexDirection: "column" }}>

              {/* Day headers */}
              <div style={{ display: "grid", gridTemplateColumns: "repeat(7, 1fr)", flexShrink: 0 }}>
                {DAYS.map((day, i) => {
                  const isToday = i === todayDow
                  return (
                    <div key={i} style={{ padding: "14px 12px 12px", textAlign: "center", borderRight: i < 6 ? "1px solid #f0f0f0" : "none", background: isToday ? "#f2f9ec" : "#fff", boxShadow: isToday ? "inset 2px 0 0 #166534, inset -2px 0 0 #166534, inset 0 2px 0 #166534" : "none" }}>
                      <div style={{ fontSize: 12, fontWeight: 700, color: isToday ? "#166534" : "#9ca3af", textTransform: "uppercase", letterSpacing: "0.08em" }}>{day}</div>
                    </div>
                  )
                })}
              </div>

              {/* Meal type rows */}
              {MEAL_TYPES.map((mealType) => {
                const color = MEAL_COLORS[mealType]
                return (
                  <div key={mealType} style={{ display: "grid", gridTemplateColumns: "repeat(7, 1fr)", flex: 1 }}>
                    {DAYS.map((_, di) => {
                      const rawMeal = getSlotMeal(di, mealType)

                      const meal = rawMeal
                        ? {
                            ...rawMeal,
                            day: DAY_NAMES[di],
                            meal_type: mealType
                          }
                        : null
                      const isToday = di === todayDow
                      return (
                        <div key={di} style={{ padding: "12px 12px 14px", borderRight: di < 6 ? "1px solid #f0f0f0" : "none", background: isToday ? "#f2f9ec" : "#fff", boxShadow: isToday ? "inset 2px 0 0 #166534, inset -2px 0 0 #166534" : "none" }}>
                          <div style={{ display: "flex", alignItems: "center", gap: 5, marginBottom: 10 }}>
                            <MealTypeIcon type={mealType} size={14} />
                            <span style={{ fontSize: 10.5, fontWeight: 600, color, textTransform: "capitalize", letterSpacing: "0.03em" }}>{mealType}</span>
                          </div>
                          {meal && (
                            <MealCard meal={meal} onDelete={handleDelete} todayDow={todayDow} currentHour={currentHour} mealType={mealType} />
                          )}
                        </div>
                      )
                    })}
                  </div>
                )
              })}

              {/* Add meal row */}
              <div style={{ display: "grid", gridTemplateColumns: "repeat(7, 1fr)", flexShrink: 0 }}>
                {DAYS.map((_, di) => {
                  const isToday = di === todayDow
                  const empty = getEmptyTypes(di)
                  return (
                    <div key={di} style={{ padding: "10px 12px", borderRight: di < 6 ? "1px solid #f0f0f0" : "none", background: isToday ? "#f2f9ec" : "#fff", boxShadow: isToday ? "inset 2px 0 0 #166534, inset -2px 0 0 #166534, inset 0 -2px 0 #166534" : "none" }}>
                      {empty.length > 0 && (
                        <button
                          onClick={() => handleAddClick(di)}
                          style={{ width: "100%", background: "none", border: "none", cursor: "pointer", color: "#166534", fontSize: 13, fontFamily: "'DM Sans', sans-serif", display: "flex", alignItems: "center", justifyContent: "center", gap: 4, padding: "6px 0", transition: "color 0.15s" }}
                          onMouseEnter={e => e.currentTarget.style.color = "#374151"}
                          onMouseLeave={e => e.currentTarget.style.color = "#166534"}
                        >
                          + Add meal
                        </button>
                      )}
                    </div>
                  )
                })}
              </div>
            </div>

            
          </div>
        </div>
      </div>

      {modal && (
        <AddMealModal
          modal={modal}
          availableTypes={modal._emptyTypes || (modal.meal_type ? [modal.meal_type] : MEAL_TYPES)}
          onAdd={handleAdd}
          onClose={() => setModal(null)}
        />
      )}

      {/* Bulk Add Meals Modal */}
      {showBulkModal && (
        <div onClick={e => { if (e.target === e.currentTarget) { setShowBulkModal(false); setBulkRows([resetMealRow()]) } }}
          style={{ position: "fixed", inset: 0, background: "rgba(0,0,0,0.3)", display: "flex", alignItems: "center", justifyContent: "center", zIndex: 200 }}>
          <div style={{ background: "#fff", borderRadius: 22, padding: "32px 32px 28px", width: "100%", maxWidth: 680, boxShadow: "0 24px 64px rgba(0,0,0,0.14)" }}>

            {/* Header */}
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 24 }}>
              <div>
                <h2 style={{ fontSize: 20, fontWeight: 700, color: "#0d1a0d" }}>Add Meals</h2>
                <p style={{ fontSize: 13, color: "#9ca3af", marginTop: 3 }}>Plan multiple meals at once</p>
              </div>
              <button onClick={() => { setShowBulkModal(false); setBulkRows([resetMealRow()]) }}
                style={{ background: "none", border: "1.5px solid #e8ede2", borderRadius: 10, cursor: "pointer", width: 36, height: 36, display: "flex", alignItems: "center", justifyContent: "center", color: "#6b7280" }}>
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M18 6 6 18M6 6l12 12"/></svg>
              </button>
            </div>

            {bulkError && <div style={{ background: "#fee2e2", color: "#dc2626", padding: "10px 14px", borderRadius: 8, fontSize: 13, marginBottom: 16 }}>{bulkError}</div>}

            {/* Table */}
            <div style={{ border: "1.5px solid #e8ede2", borderRadius: 14, overflow: "hidden", marginBottom: 16 }}>
              <table style={{ width: "100%", borderCollapse: "collapse", fontFamily: "'DM Sans', sans-serif" }}>
                <thead>
                  <tr style={{ background: "#f9fafb", borderBottom: "1.5px solid #e8ede2" }}>
                    {["Meal Name", "Day", "Meal Type", ""].map(h => (
                      <th key={h} style={{ padding: "10px 14px", textAlign: "left", fontSize: 11, fontWeight: 700, color: "#9ca3af", textTransform: "uppercase", letterSpacing: "0.06em", whiteSpace: "nowrap" }}>{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {bulkRows.map((row, idx) => (
                    <tr key={idx} style={{ borderBottom: idx < bulkRows.length - 1 ? "1px solid #f5f5f5" : "none" }}>
                      <td style={{ padding: "10px 14px" }}>
                        <input
                          placeholder="e.g. Chicken Curry"
                          value={row.meal_name}
                          onChange={e => updateBulkRow(idx, "meal_name", e.target.value)}
                          onKeyDown={e => { if (e.key === "Enter" && idx === bulkRows.length - 1) setBulkRows(r => [...r, resetMealRow()]) }}
                          style={{ width: "100%", height: 38, border: "1.5px solid #e8ede2", borderRadius: 9, padding: "0 12px", fontSize: 13, outline: "none", fontFamily: "'DM Sans', sans-serif", boxSizing: "border-box", color: "#111" }}
                        />
                      </td>
                      <td style={{ padding: "10px 10px", width: 130 }}>
                        <select value={row.day} onChange={e => updateBulkRow(idx, "day", e.target.value)}
                          style={{ width: "100%", height: 38, border: "1.5px solid #e8ede2", borderRadius: 9, padding: "0 8px", fontSize: 13, outline: "none", background: "#fff", fontFamily: "'DM Sans', sans-serif", cursor: "pointer" }}>
                          {DAY_NAMES.map(d => <option key={d} value={d}>{d}</option>)}
                        </select>
                      </td>
                      <td style={{ padding: "10px 10px", width: 130 }}>
                        <select value={row.meal_type} onChange={e => updateBulkRow(idx, "meal_type", e.target.value)}
                          style={{ width: "100%", height: 38, border: "1.5px solid #e8ede2", borderRadius: 9, padding: "0 8px", fontSize: 13, outline: "none", background: "#fff", fontFamily: "'DM Sans', sans-serif", cursor: "pointer" }}>
                          {MEAL_TYPES.map(t => <option key={t} value={t} style={{ color: MEAL_COLORS[t] }}>{t.charAt(0).toUpperCase() + t.slice(1)}</option>)}
                        </select>
                      </td>
                      <td style={{ padding: "10px 10px", width: 40, textAlign: "center" }}>
                        {bulkRows.length > 1 && (
                          <button onClick={() => setBulkRows(r => r.filter((_, i) => i !== idx))}
                            style={{ width: 28, height: 28, background: "none", border: "1.5px solid #e8ede2", borderRadius: 7, cursor: "pointer", display: "flex", alignItems: "center", justifyContent: "center", color: "#9ca3af" }}>
                            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M18 6 6 18M6 6l12 12"/></svg>
                          </button>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Add row */}
            <button onClick={() => setBulkRows(r => [...r, resetMealRow()])}
              style={{ display: "flex", alignItems: "center", gap: 6, background: "none", border: "1.5px dashed #c6deb0", borderRadius: 9, padding: "7px 16px", fontSize: 13, color: "#166534", cursor: "pointer", fontFamily: "'DM Sans', sans-serif", fontWeight: 500, marginBottom: 24 }}>
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
              Add row
            </button>

            {/* Footer */}
            <div style={{ display: "flex", gap: 12, justifyContent: "flex-end" }}>
              <button onClick={() => { setShowBulkModal(false); setBulkError(""); setBulkRows([resetMealRow()]) }}
                style={{ height: 44, border: "1.5px solid #e8ede2", borderRadius: 11, background: "#fff", fontSize: 14, cursor: "pointer", fontFamily: "'DM Sans', sans-serif", color: "#6b7280", padding: "0 24px" }}>Cancel</button>
              <button onClick={handleBulkAdd} disabled={bulkAdding}
                style={{ height: 44, border: "none", borderRadius: 11, background: "#166534", color: "#fff", fontSize: 14, fontWeight: 600, cursor: "pointer", fontFamily: "'DM Sans', sans-serif", padding: "0 28px", opacity: bulkAdding ? 0.6 : 1 }}>
                {bulkAdding ? "Adding..." : `Add ${bulkRows.filter(r => r.meal_name.trim()).length || ""} Meal${bulkRows.filter(r => r.meal_name.trim()).length !== 1 ? "s" : ""}`}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
