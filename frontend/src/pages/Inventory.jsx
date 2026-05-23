import { useState, useEffect, useRef } from "react"
import { useNavigate } from "react-router-dom"
import axios from "axios"
import { getProfile } from "../services/api"
import NotificationsDropdown from "../components/NotificationsDropdown"

const BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000"

const CATEGORIES = ["Dairy", "Protein", "Produce", "Grains", "Nuts", "Other"]
const UNITS = ["unit", "kg", "g", "liter", "ml", "pieces", "lbs", "loaf"]
const MONTHS = ["January","February","March","April","May","June","July","August","September","October","November","December"]
const WEEK_DAYS = ["Su","Mo","Tu","We","Th","Fr","Sa"]

const CATEGORY_STYLE = {
  Dairy:   { bg: "#dbeafe", color: "#1d4ed8" },
  Protein: { bg: "#fee2e2", color: "#dc2626" },
  Produce: { bg: "#E4F2DB", color: "#206C1B" },
  Grains:  { bg: "#fef9c3", color: "#ca8a04" },
  Nuts:    { bg: "#fde8c8", color: "#92400e" },
  Other:   { bg: "#f0f0f0", color: "#6b7280" },
}

const CATEGORY_SVG = {
  Produce: "/noun-produce-8213752.svg",
  Grains:  "/noun-grains-5837828.svg",
  Dairy:   "/noun-milk-8053511.svg",
  Protein: "/noun-protein-5994480.svg",
  Nuts:    "/noun-nuts-7474838.svg",
  Other:   "/noun-other-5783429.svg",
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

function CategoryIcon({ category, size = 44 }) {
  const r = Math.round(size * 0.25)
  const imgSize = Math.round(size * 0.6)
  return (
    <div style={{ width: size, height: size, background: "#fff", border: "1.5px solid #e8ede2", borderRadius: r, display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0 }}>
      <img src={CATEGORY_SVG[category] || CATEGORY_SVG.Other} alt={category} width={imgSize} height={imgSize} style={{ objectFit: "contain", filter: "brightness(0) saturate(100%) invert(18%) sepia(50%) saturate(600%) hue-rotate(115deg) brightness(90%)" }} />
    </div>
  )
}

function getStatus(purchasedDate, shelfLifeDays = 7) {
  if (!purchasedDate) return { label: "Fresh", color: "#206C1B", bg: "#E4F2DB", dot: "#206C1B", type: "fresh" }
  const diffDays = Math.floor((Date.now() - new Date(purchasedDate + "T00:00:00")) / 86400000)
  const left = shelfLifeDays - diffDays
  if (left <= 0)  return { label: "Expired",           color: "#6b7280", bg: "#f3f4f6", dot: "#9ca3af", type: "expired" }
  if (left === 1) return { label: "Expires tomorrow!", color: "#dc2626", bg: "#fee2e2", dot: "#dc2626", type: "warning" }
  if (left <= 3)  return { label: `${left} days left`, color: "#ea580c", bg: "#fff4e8", dot: "#f97316", type: "warning" }
  return { label: "Fresh", color: "#206C1B", bg: "#E4F2DB", dot: "#206C1B", type: "fresh" }
}

function DatePicker({ value, onChange, max }) {
  const [open, setOpen] = useState(false)
  const [view, setView] = useState(null)
  const [pos, setPos] = useState({ top: 0, left: 0 })
  const ref = useRef()
  const btnRef = useRef()

  const parsed = value ? new Date(value + "T00:00:00") : new Date()
  const displayDate = value
    ? parsed.toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" })
    : "Select date"

  useEffect(() => {
    const handler = (e) => { if (ref.current && !ref.current.contains(e.target)) setOpen(false) }
    document.addEventListener("mousedown", handler)
    return () => document.removeEventListener("mousedown", handler)
  }, [])

  const toggle = () => {
    const p = value ? new Date(value + "T00:00:00") : new Date()
    setView({ year: p.getFullYear(), month: p.getMonth() })
    if (btnRef.current) {
      const r = btnRef.current.getBoundingClientRect()
      setPos({ top: r.bottom + 8, left: Math.max(8, r.right - 264) })
    }
    setOpen(o => !o)
  }
  const prevMonth = () => setView(v => v.month === 0 ? { year: v.year - 1, month: 11 } : { ...v, month: v.month - 1 })
  const nextMonth = () => setView(v => v.month === 11 ? { year: v.year + 1, month: 0 } : { ...v, month: v.month + 1 })
  const getDays = () => {
    if (!view) return []
    const firstDay = new Date(view.year, view.month, 1).getDay()
    const daysInMonth = new Date(view.year, view.month + 1, 0).getDate()
    return [...Array(firstDay).fill(null), ...Array.from({ length: daysInMonth }, (_, i) => i + 1)]
  }
  const toStr = (d) => !view || !d ? "" : `${view.year}-${String(view.month + 1).padStart(2, "0")}-${String(d).padStart(2, "0")}`
  const handleDay = (d) => {
    const s = toStr(d)
    if (!d || (max && s > max)) return
    onChange(s); setOpen(false)
  }

  return (
    <div ref={ref} style={{ position: "relative", display: "inline-block" }}>
      <button ref={btnRef} onClick={toggle} style={{ display: "flex", alignItems: "center", gap: 8, border: "1.5px solid #e8e8e8", borderRadius: 10, padding: "6px 12px", background: "#fafafa", cursor: "pointer", fontSize: 13, color: "#444", fontFamily: "inherit", whiteSpace: "nowrap" }}>
        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#888" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <rect x="3" y="4" width="18" height="18" rx="2"/><path d="M16 2v4M8 2v4M3 10h18"/>
        </svg>
        {displayDate}
      </button>
      {open && view && (
        <div style={{ position: "fixed", top: pos.top, left: pos.left, background: "#fff", border: "1.5px solid #ececec", borderRadius: 16, padding: 16, boxShadow: "0 8px 32px rgba(0,0,0,0.12)", zIndex: 1000, width: 264 }}>
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 14 }}>
            <button onClick={prevMonth} style={{ background: "none", border: "1.5px solid #e8e8e8", borderRadius: 8, cursor: "pointer", width: 30, height: 30, display: "flex", alignItems: "center", justifyContent: "center", color: "#555", fontFamily: "inherit" }}>â€¹</button>
            <span style={{ fontWeight: 600, fontSize: 14, color: "#111" }}>{MONTHS[view.month]} {view.year}</span>
            <button onClick={nextMonth} style={{ background: "none", border: "1.5px solid #e8e8e8", borderRadius: 8, cursor: "pointer", width: 30, height: 30, display: "flex", alignItems: "center", justifyContent: "center", color: "#555", fontFamily: "inherit" }}>â€º</button>
          </div>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(7, 1fr)", marginBottom: 6 }}>
            {WEEK_DAYS.map(d => <div key={d} style={{ textAlign: "center", fontSize: 11, color: "#bbb", fontWeight: 600, padding: "4px 0" }}>{d}</div>)}
          </div>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(7, 1fr)", gap: 2 }}>
            {getDays().map((d, i) => {
              const s = toStr(d); const sel = d && value === s; const dis = d && max && s > max
              return (
                <button key={i} onClick={() => handleDay(d)} disabled={!d || !!dis} style={{ height: 34, border: "none", cursor: d && !dis ? "pointer" : "default", borderRadius: 8, fontSize: 13, fontFamily: "inherit", background: sel ? "#166534" : "transparent", color: sel ? "#fff" : !d || dis ? "#ddd" : "#333", fontWeight: sel ? 700 : 400 }}>
                  {d || ""}
                </button>
              )
            })}
          </div>
        </div>
      )}
    </div>
  )
}

const resetItem = () => ({ display_name: "", quantity: "", unit: "unit", category: "Other", purchase_date: new Date().toISOString().split("T")[0] })
const inputStyle = (extra = {}) => ({ border: "1.5px solid #e8e8e8", borderRadius: 10, padding: "7px 12px", fontSize: 14, outline: "none", fontFamily: "inherit", background: "#fff", width: "100%", boxSizing: "border-box", ...extra })
const selectStyle = (extra = {}) => ({ border: "1.5px solid #e8e8e8", borderRadius: 10, padding: "7px 10px", fontSize: 14, outline: "none", fontFamily: "inherit", background: "#fff", cursor: "pointer", width: "100%", ...extra })

const formatDate = (d) => d ? new Date(d + "T00:00:00").toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" }) : "â€”"

export default function Inventory() {
  const navigate = useNavigate()
  const [userName, setUserName]       = useState("")
  const [collapsed, setCollapsed]     = useState(false)
  const [items, setItems]             = useState([])
  const [search, setSearch]           = useState("")
  const [activeTab, setActiveTab]     = useState("All Items")
  const [loading, setLoading]         = useState(true)
  const [viewMode, setViewMode]       = useState("grid")
  const [editingIdx, setEditingIdx]   = useState(null)
  const [editValues, setEditValues]   = useState({})
  const [saving, setSaving]           = useState(false)
  const [statsModal, setStatsModal]   = useState(null)
  const [showModal, setShowModal]       = useState(false)
  const [newItems, setNewItems]         = useState([resetItem()])
  const [addError, setAddError]         = useState("")
  const [adding, setAdding]             = useState(false)
  const [classifyingRows, setClassifyingRows] = useState({})
  const [lowStockNames, setLowStockNames] = useState(null)

  const userId = localStorage.getItem("userId")
  const today = new Date().toISOString().split("T")[0]

  useEffect(() => {
    if (!userId) { navigate("/login"); return }
    getProfile(userId).then(p => setUserName(p.name || p.email || "")).catch(() => {})
    fetchInventory()
  }, [])

  const fetchLowStock = async () => {
    try {
      const res = await axios.get(`${BASE_URL}/inventory/low-stock`, { headers: { "user-id": userId } })
      setLowStockNames(res.data || [])
    } catch (err) { console.error(err) }
  }

  const fetchInventory = async () => {
    try {
      const res = await axios.get(`${BASE_URL}/inventory/`, { headers: { "user-id": userId } })
      setItems(res.data || [])
      fetchLowStock()
    } catch (err) { console.error(err) }
    finally { setLoading(false) }
  }

  const startEdit = (item) => {
    setEditingIdx(item.idx)
    setEditValues({ display_name: item.display_name, quantity: String(item.quantity), unit: item.unit, category: item.category || "Other", purchase_date: item.purchase_date || "" })
  }
  const cancelEdit = () => { setEditingIdx(null); setEditValues({}) }
  const saveEdit = async (item) => {
    setSaving(true);
    try {
      await axios.put(`${BASE_URL}/inventory/update`,
        { 
          index: item.idx, 
          display_name: editValues.display_name, // Use display_name
          quantity: Number(editValues.quantity) || 0, 
          unit: editValues.unit, 
          category: editValues.category, 
          purchase_date: editValues.purchase_date || null // Use purchase_date
        },
        { headers: { "user-id": userId } });
      setEditingIdx(null);
      setEditValues({});
      fetchInventory();
    } catch { 
      /* handle error */ 
    } finally { 
      setSaving(false); 
    }
  }
  const setEV = (field, value) => setEditValues(v => ({ ...v, [field]: value }))

  const handleClassifyRow = async (rowIdx, name) => {
    if (!name.trim()) return
    setClassifyingRows(r => ({ ...r, [rowIdx]: true }))
    try {
      const res = await axios.post(`${BASE_URL}/inventory/classify`, { display_name: name.trim() }, { headers: { "user-id": userId } })
      setNewItems(rows => rows.map((row, i) =>
        i === rowIdx ? { ...row, category: res.data.category ?? "Other", unit: res.data.unit ?? row.unit } : row
      ))
    } catch { /* noop */ } finally { setClassifyingRows(r => ({ ...r, [rowIdx]: false })) }
  }

  const updateRow = (rowIdx, field, value) =>
    setNewItems(rows => rows.map((row, i) => i === rowIdx ? { ...row, [field]: value } : row))

  const addRow = () => setNewItems(rows => [...rows, resetItem()])

  const removeRow = (rowIdx) => setNewItems(rows => rows.filter((_, i) => i !== rowIdx))

  const handleAdd = async () => {
    const validItems = newItems.filter(item => item.display_name.trim() && item.quantity)
    if (validItems.length === 0) {
      setAddError("Please fill in item name and quantity for at least one row")
      return
    }
    // Last row wins for duplicate names
    const dedupedMap = new Map()
    validItems.forEach(item => dedupedMap.set(item.display_name.trim().toLowerCase(), item))
    const dedupedItems = [...dedupedMap.values()]
    setAdding(true)
    try {
      await axios.post(
        `${BASE_URL}/inventory/add`,
        { items: dedupedItems.map(item => ({ display_name: item.display_name.trim(), quantity: Number(item.quantity), unit: item.unit, category: item.category, purchase_date: item.purchase_date || null })) },
        { headers: { "user-id": userId } }
      )
      setNewItems([resetItem()])
      setShowModal(false)
      fetchInventory()
    } catch (err) {
      const message = err?.response?.data?.detail || err?.message || "Failed to add items"
      setAddError(message)
    } finally {
      setAdding(false)
    }
  }

  const enriched = items.map((item, i) => ({ ...item, idx: i, category: item.category || "Other" }))
  const uniqueCategories = Array.from(new Set(enriched.map(i => i.category)))
  const tabs = ["All Items", ...uniqueCategories]
  const countByCategory = {}
  enriched.forEach(i => { countByCategory[i.category] = (countByCategory[i.category] || 0) + 1 })
  const visible = enriched.filter(item =>
    item.display_name.toLowerCase().includes(search.toLowerCase()) &&
    (activeTab === "All Items" || item.category === activeTab)
  )

  const statsData = [
    { type: "total",      label: "Total Items",       sub: "items in stock",          value: enriched.length,                                                                              items: enriched,                                                                              bg: "#E4F2DB", iconBg: "#E4F2DB", iconColor: "#206C1B" },
    { type: "low",        label: "Low Stock Items",   sub: "items running low",       value: lowStockNames === null ? "â€¦" : enriched.filter(i => i.quantity !== 0 && i.quantity !== "0" && lowStockNames.includes(i.display_name)).length, items: enriched.filter(i => i.quantity !== 0 && i.quantity !== "0" && (lowStockNames || []).includes(i.display_name)), bg: "#fffbeb", iconBg: "#fef3c7", iconColor: "#d97706" },
    { type: "expired",    label: "Expired Items",     sub: "past expiration",         value: enriched.filter(i => i.quantity !== 0 && i.quantity !== "0" && getStatus(i.purchase_date, i.shelf_life_days).type === "expired").length, items: enriched.filter(i => i.quantity !== 0 && i.quantity !== "0" && getStatus(i.purchase_date, i.shelf_life_days).type === "expired"), bg: "#fff5f5", iconBg: "#fee2e2", iconColor: "#dc2626" },
    { type: "outofstock", label: "Out of Stock Items",sub: "currently out of stock",  value: enriched.filter(i => i.quantity === 0).length,                                                items: enriched.filter(i => i.quantity === 0),                                                bg: "#f9fafb", iconBg: "#f3f4f6", iconColor: "#6b7280" },
  ]

  const STAT_ICONS = {
    total:      <><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/><polyline points="3.27 6.96 12 12.01 20.73 6.96"/></>,
    low:        <><circle cx="12" cy="12" r="9"/><polyline points="12 7 12 12 15 15"/></>,
    expired:    <><rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/><path d="M9 16l2 2 4-4"/></>,
    outofstock: <><path d="M6 2 3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4z"/><line x1="3" y1="6" x2="21" y2="6"/><path d="M16 10a4 4 0 0 1-8 0"/></>,
  }

  const firstName = userName.split(" ")[0]

  return (
    <div style={{ height: "100vh", background: "#fff", fontFamily: "'DM Sans', sans-serif", display: "flex", flexDirection: "column", overflow: "hidden" }}>
      <style>{`@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700;800&display=swap'); * { box-sizing: border-box; margin: 0; padding: 0; }`}</style>

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
              const active = path === "/inventory"
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

        {/* Main */}
        <div style={{ flex: 1, display: "flex", flexDirection: "column", overflow: "hidden" }}>

          {/* Page header */}
          <div style={{ padding: "24px 40px 0px", flexShrink: 0, display: "flex", alignItems: "center", justifyContent: "space-between" }}>
            <div>
              <h1 style={{ fontSize: 22, fontWeight: 800, color: "#0d1a0d", marginBottom: 4 }}>My Inventory</h1>
              <p style={{ fontSize: 14, color: "#6b7280" }}>Track what's in your fridge and manage expiration dates</p>
            </div>
          </div>

          {/* Search + Filter + Add â€” fixed, does not scroll */}
          <div style={{ padding: "16px 40px", flexShrink: 0, display: "flex", gap: 12, alignItems: "center" }}>
            <div style={{ flex: 1, position: "relative" }}>
              <svg style={{ position: "absolute", left: 16, top: "50%", transform: "translateY(-50%)", pointerEvents: "none" }} width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#9ca3af" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/>
              </svg>
              <input value={search} onChange={e => setSearch(e.target.value)} placeholder="Search items..."
                style={{ width: "100%", height: 48, border: "1.5px solid #e8ede2", borderRadius: 12, paddingLeft: 46, paddingRight: 16, fontSize: 14, outline: "none", fontFamily: "'DM Sans', sans-serif", boxSizing: "border-box", color: "#111", background: "#fff" }} />
            </div>
            <div style={{ display: "flex", border: "1.5px solid #e8ede2", borderRadius: 12, overflow: "hidden", flexShrink: 0 }}>
              {[
                { mode: "grid",  icon: <><rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/></> },
                { mode: "table", icon: <><line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="18" x2="21" y2="18"/></> },
              ].map(({ mode, icon }, idx) => (
                <button key={mode} onClick={() => setViewMode(mode)} style={{ width: 48, height: 48, border: "none", borderLeft: idx > 0 ? "1.5px solid #e8ede2" : "none", background: viewMode === mode ? "#166534" : "#fff", color: viewMode === mode ? "#fff" : "#6b7280", cursor: "pointer", display: "flex", alignItems: "center", justifyContent: "center", transition: "background 0.15s" }}>
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">{icon}</svg>
                </button>
              ))}
            </div>
            <button onClick={() => { setShowModal(true); setAddError(""); setNewItems([resetItem()]) }}
              style={{ height: 48, background: "#166534", color: "#fff", border: "none", borderRadius: 12, padding: "0 22px", fontSize: 14, fontWeight: 600, cursor: "pointer", fontFamily: "'DM Sans', sans-serif", whiteSpace: "nowrap", display: "flex", alignItems: "center", gap: 6 }}>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
              Add Item
            </button>
          </div>

          {/* Scrollable content */}
          <div style={{ flex: 1, overflowY: "auto", padding: "28px 40px" }}>

            {/* Stats */}
            <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 16, marginBottom: 28 }}>
              {statsData.map(stat => (
                <div key={stat.type} onClick={() => setStatsModal(stat)} style={{ border: "1.5px solid #f0f0ee", borderRadius: 16, padding: "20px 22px", cursor: "pointer", background: "#fff", boxShadow: "0 1px 4px rgba(0,0,0,0.05)", transition: "box-shadow 0.15s, border-color 0.15s" }}
                  onMouseEnter={e => { e.currentTarget.style.borderColor = "#c6deb0"; e.currentTarget.style.boxShadow = "0 4px 16px rgba(0,0,0,0.08)" }}
                  onMouseLeave={e => { e.currentTarget.style.borderColor = "#f0f0ee"; e.currentTarget.style.boxShadow = "0 1px 4px rgba(0,0,0,0.05)" }}>
                  <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
                    <div style={{ width: 56, height: 56, background: stat.iconBg, borderRadius: "50%", display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0 }}>
                      <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke={stat.iconColor} strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">{STAT_ICONS[stat.type]}</svg>
                    </div>
                    <div>
                      <div style={{ fontSize: 14, fontWeight: 600, color: "#374151", marginBottom: 6 }}>{stat.label}</div>
                      <div style={{ display: "flex", alignItems: "baseline", gap: 6 }}>
                        <span style={{ fontSize: 28, fontWeight: 800, color: "#0d1a0d", lineHeight: 1 }}>{stat.value}</span>
                        <span style={{ fontSize: 13, color: "#9ca3af" }}>{stat.sub}</span>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {/* Category tabs */}
            <div style={{ display: "flex", gap: 8, marginBottom: 24, flexWrap: "wrap" }}>
              {tabs.map(tab => {
                const count = tab === "All Items" ? enriched.length : (countByCategory[tab] || 0)
                const active = activeTab === tab
                return (
                  <button key={tab} onClick={() => setActiveTab(tab)} style={{ display: "flex", alignItems: "center", gap: 6, padding: "7px 16px", borderRadius: 999, border: "1.5px solid", borderColor: active ? "#166534" : "#e8ede2", background: active ? "#166534" : "#fff", color: active ? "#fff" : "#374151", fontSize: 13, fontWeight: 600, cursor: "pointer", fontFamily: "'DM Sans', sans-serif", transition: "all 0.15s" }}>
                    {tab !== "All Items" && (
                      <img src={CATEGORY_SVG[tab] || CATEGORY_SVG.Other} alt={tab} width={14} height={14} style={{ objectFit: "contain", filter: active ? "brightness(0) invert(1)" : "none", opacity: 0.85 }} />
                    )}
                    {tab} ({count})
                  </button>
                )
              })}
            </div>

            {/* Items grid */}
            {loading ? (
              <div style={{ textAlign: "center", color: "#9ca3af", padding: "80px 0", fontSize: 14 }}>Loading inventory...</div>
            ) : visible.length === 0 ? (
              <div style={{ textAlign: "center", color: "#9ca3af", padding: "80px 0", fontSize: 14 }}>No items found</div>
            ) : viewMode === "table" ? (
              <div style={{ border: "1.5px solid #e8ede2", borderRadius: 16, overflow: "hidden", marginBottom: 40 }}>
                <table style={{ width: "100%", borderCollapse: "collapse", fontFamily: "'DM Sans', sans-serif" }}>
                  <thead>
                    <tr style={{ background: "#f9fafb", borderBottom: "1.5px solid #e8ede2" }}>
                      {["Item", "Category", "Status", "Quantity", "Purchased", ""].map(h => (
                        <th key={h} style={{ padding: "12px 20px", textAlign: "left", fontSize: 11, fontWeight: 700, color: "#9ca3af", textTransform: "uppercase", letterSpacing: "0.06em" }}>{h}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {visible.map((item, rowIdx) => {
                      const isEditing = editingIdx === item.idx
                      const status = getStatus(item.purchase_date, item.shelf_life_days)
                      const cs = CATEGORY_STYLE[item.category] || CATEGORY_STYLE.Other
                      return (
                        <tr key={item.idx} style={{ borderBottom: rowIdx < visible.length - 1 ? "1px solid #f5f5f5" : "none", background: isEditing ? "#f9fafb" : "#fff" }}>
                          <td style={{ padding: "14px 20px" }}>
                            <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
                              <CategoryIcon category={isEditing ? (editValues.category || "Other") : item.category} size={36} />
                              <span style={{ fontSize: 14, fontWeight: 600, color: "#0d1a0d" }}>{item.display_name}</span>
                            </div>
                          </td>
                          <td style={{ padding: "14px 20px" }}>
                            {isEditing ? (
                              <select value={editValues.category} onChange={e => setEV("category", e.target.value)} style={selectStyle({ width: 120 })}>
                                {CATEGORIES.map(c => <option key={c} value={c}>{c}</option>)}
                              </select>
                            ) : (
                              <span style={{ fontSize: 12, fontWeight: 600, color: cs.color, background: cs.bg, padding: "3px 10px", borderRadius: 6 }}>{item.category}</span>
                            )}
                          </td>
                          <td style={{ padding: "14px 20px" }}>
                            {item.quantity === 0 || item.quantity === "0"
                              ? <span style={{ fontSize: 13, color: "#9ca3af" }}>â€”</span>
                              : <span style={{ fontSize: 12, fontWeight: 600, color: status.color, background: status.bg, padding: "3px 10px", borderRadius: 6 }}>{status.label}</span>}
                          </td>
                          <td style={{ padding: "14px 20px" }}>
                            {isEditing ? (
                              <div style={{ display: "flex", gap: 6 }}>
                                <input type="text" inputMode="decimal" value={editValues.quantity} onChange={e => setEV("quantity", e.target.value.replace(/[^0-9.]/g, ""))} style={inputStyle({ width: 64, textAlign: "center" })} />
                                <select value={editValues.unit} onChange={e => setEV("unit", e.target.value)} style={selectStyle({ width: 90 })}>
                                  {UNITS.map(u => <option key={u} value={u}>{u}</option>)}
                                </select>
                              </div>
                            ) : (
                              <span style={{ fontSize: 14, color: "#374151" }}>{item.quantity} {item.unit}</span>
                            )}
                          </td>
                          <td style={{ padding: "14px 20px" }}>
                            {isEditing ? (
                              <DatePicker value={editValues.purchase_date} onChange={v => setEV("purchase_date", v)} max={today} />
                            ) : (
                              <span style={{ fontSize: 13, color: "#6b7280" }}>{formatDate(item.purchase_date)}</span>
                            )}
                          </td>
                          <td style={{ padding: "14px 20px", textAlign: "right", whiteSpace: "nowrap" }}>
                            {isEditing ? (
                              <div style={{ display: "flex", gap: 8, justifyContent: "flex-end" }}>
                                <button onClick={cancelEdit} style={{ border: "1.5px solid #e8ede2", borderRadius: 8, background: "#fff", cursor: "pointer", padding: "6px 14px", fontSize: 13, color: "#6b7280", fontFamily: "'DM Sans', sans-serif" }}>Cancel</button>
                                <button onClick={() => saveEdit(item)} disabled={saving} style={{ border: "none", borderRadius: 8, background: "#166534", color: "#fff", cursor: "pointer", padding: "6px 14px", fontSize: 13, fontWeight: 600, fontFamily: "'DM Sans', sans-serif", opacity: saving ? 0.6 : 1 }}>{saving ? "Saving..." : "Save"}</button>
                              </div>
                            ) : (
                              <div style={{ display: "flex", gap: 6, justifyContent: "flex-end" }}>
                                <button onClick={() => startEdit(item)} style={{ width: 30, height: 30, background: "none", border: "1.5px solid #e8ede2", borderRadius: 8, cursor: "pointer", display: "flex", alignItems: "center", justifyContent: "center", color: "#6b7280" }}>
                                  <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
                                </button>
                              </div>
                            )}
                          </td>
                        </tr>
                      )
                    })}
                  </tbody>
                </table>
              </div>
            ) : (
              <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 18, paddingBottom: 40 }}>
                {visible.map(item => {
                  const isEditing = editingIdx === item.idx
                  const status = getStatus(item.purchase_date, item.shelf_life_days)
                  const cs = CATEGORY_STYLE[item.category] || CATEGORY_STYLE.Other

                  return (
                    <div key={item.idx} style={{ border: `1.5px solid ${isEditing ? "#c6deb0" : "#e8ede2"}`, borderRadius: 18, background: "#fff", display: "flex", flexDirection: "column", transition: "border-color 0.15s", position: "relative" }}>

                      {/* Card header */}
                      <div style={{ padding: "18px 18px 14px", display: "flex", alignItems: "flex-start", justifyContent: "space-between" }}>
                        <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
                          <CategoryIcon category={isEditing ? (editValues.category || "Other") : item.category} />
                          <div>
                            <div style={{ fontSize: 15, fontWeight: 700, color: "#0d1a0d", marginBottom: 4 }}>{item.display_name}</div>
                            <span style={{ background: cs.bg, color: cs.color, fontSize: 11, fontWeight: 600, padding: "2px 8px", borderRadius: 6 }}>
                              {isEditing ? editValues.category : item.category}
                            </span>
                          </div>
                        </div>
                        {isEditing ? (
                          <button onClick={cancelEdit} style={{ background: "none", border: "1.5px solid #e8ede2", borderRadius: 8, cursor: "pointer", padding: "5px 10px", fontSize: 12, color: "#6b7280", fontFamily: "'DM Sans', sans-serif" }}>Cancel</button>
                        ) : (
                          <div style={{ display: "flex", gap: 6 }}>
                            <button onClick={() => startEdit(item)} style={{ width: 30, height: 30, background: "none", border: "1.5px solid #e8ede2", borderRadius: 8, cursor: "pointer", display: "flex", alignItems: "center", justifyContent: "center", color: "#6b7280" }}>
                              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                                <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
                              </svg>
                            </button>
                          </div>
                        )}
                      </div>

                      {isEditing ? (
                        <div style={{ padding: "0 18px 18px", display: "flex", flexDirection: "column", gap: 10 }}>
                          <select value={editValues.category} onChange={e => setEV("category", e.target.value)} style={selectStyle()}>
                            {CATEGORIES.map(c => <option key={c} value={c}>{c}</option>)}
                          </select>
                          <div style={{ display: "flex", gap: 8 }}>
                            <input type="text" inputMode="decimal" placeholder="Qty" value={editValues.quantity}
                              onChange={e => setEV("quantity", e.target.value.replace(/[^0-9.]/g, ""))}
                              style={inputStyle({ width: 80, flex: "none" })} />
                            <select value={editValues.unit} onChange={e => setEV("unit", e.target.value)} style={selectStyle({ flex: 1 })}>
                              {UNITS.map(u => <option key={u} value={u}>{u}</option>)}
                            </select>
                          </div>
                          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", border: "1.5px solid #e8e8e8", borderRadius: 10, padding: "6px 12px" }}>
                            <span style={{ fontSize: 13, color: "#9ca3af" }}>Purchased</span>
                            <DatePicker value={editValues.purchase_date} onChange={v => setEV("purchase_date", v)} max={today} />
                          </div>
                          <button onClick={() => saveEdit(item)} disabled={saving}
                            style={{ height: 40, border: "none", borderRadius: 10, background: "#166534", color: "#fff", fontSize: 14, fontWeight: 600, cursor: "pointer", fontFamily: "'DM Sans', sans-serif", opacity: saving ? 0.6 : 1 }}>
                            {saving ? "Saving..." : "Save changes"}
                          </button>
                        </div>
                      ) : (
                        <>
                          {/* Status bar */}
                          <div style={{ padding: "0 16px 14px" }}>
                            {item.quantity === 0 || item.quantity === "0" ? (
                              <div style={{ borderRadius: 10, padding: "8px 14px", display: "flex", alignItems: "center" }}>
                                <span style={{ fontSize: 13, color: "#9ca3af" }}>â€”</span>
                              </div>
                            ) : (
                              <div style={{ background: status.bg, borderRadius: 10, padding: "8px 14px", display: "flex", alignItems: "center", gap: 8 }}>
                                <div style={{ width: 7, height: 7, borderRadius: "50%", background: status.dot, flexShrink: 0 }} />
                                <span style={{ fontSize: 13, fontWeight: 600, color: status.color }}>{status.label}</span>
                              </div>
                            )}
                          </div>
                          {/* Quantity + date */}
                          <div style={{ padding: "14px 18px", display: "flex", alignItems: "center", justifyContent: "space-between" }}>
                            <span style={{ fontSize: 14, fontWeight: 700, color: "#0d1a0d" }}>{item.quantity} {item.unit}</span>
                            <div style={{ display: "flex", alignItems: "center", gap: 5, color: "#9ca3af", fontSize: 13 }}>
                              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                <rect x="3" y="4" width="18" height="18" rx="2"/><path d="M16 2v4M8 2v4M3 10h18"/>
                              </svg>
                              {formatDate(item.purchase_date)}
                            </div>
                          </div>
                        </>
                      )}
                    </div>
                  )
                })}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Stats Modal */}
      {statsModal && (
        <div onClick={e => { if (e.target === e.currentTarget) setStatsModal(null) }}
          style={{ position: "fixed", inset: 0, background: "rgba(0,0,0,0.3)", display: "flex", alignItems: "center", justifyContent: "center", zIndex: 200 }}>
          <div style={{ background: "#fff", borderRadius: 22, width: "100%", maxWidth: 480, maxHeight: "80vh", display: "flex", flexDirection: "column", boxShadow: "0 24px 64px rgba(0,0,0,0.14)", overflow: "hidden" }}>
            <div style={{ padding: "28px 28px 0" }}>
              <div style={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between", marginBottom: 4 }}>
                <div>
                  <h2 style={{ fontSize: 20, fontWeight: 700, color: "#0d1a0d" }}>{statsModal.label}</h2>
                  <p style={{ fontSize: 13, color: "#9ca3af", marginTop: 4 }}>{statsModal.value} item{statsModal.value !== 1 ? "s" : ""}</p>
                </div>
                <button onClick={() => setStatsModal(null)} style={{ background: "none", border: "1.5px solid #e8ede2", borderRadius: 10, cursor: "pointer", width: 36, height: 36, display: "flex", alignItems: "center", justifyContent: "center", color: "#6b7280" }}>
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M18 6 6 18M6 6l12 12"/></svg>
                </button>
              </div>
              <div style={{ height: 1, background: "#f0f0ee", marginTop: 20 }} />
            </div>
            <div style={{ overflowY: "auto", padding: "12px 28px 28px" }}>
              {statsModal.items.length === 0 ? (
                <p style={{ textAlign: "center", color: "#9ca3af", padding: "32px 0", fontSize: 14 }}>No items here</p>
              ) : statsModal.items.map(item => {
                const status = getStatus(item.purchase_date, item.shelf_life_days)
                const cs = CATEGORY_STYLE[item.category] || CATEGORY_STYLE.Other
                return (
                  <div key={item.idx} style={{ display: "flex", alignItems: "center", gap: 14, padding: "14px 0", borderBottom: "1px solid #f5f5f5" }}>
                    <CategoryIcon category={item.category} size={40} />
                    <div style={{ flex: 1, minWidth: 0 }}>
                      <div style={{ fontSize: 15, fontWeight: 700, color: "#0d1a0d", marginBottom: 3 }}>{item.display_name}</div>
                      <div style={{ fontSize: 12, color: "#9ca3af" }}>{item.quantity} {item.unit} Â· <span style={{ color: cs.color }}>{item.category}</span></div>
                    </div>
                    <div style={{ display: "flex", flexDirection: "column", alignItems: "flex-end", gap: 5 }}>
                      <span style={{ fontSize: 12, color: "#9ca3af" }}>{formatDate(item.purchase_date)}</span>
                      {item.quantity === 0 || item.quantity === "0"
                        ? <span style={{ fontSize: 11, color: "#9ca3af" }}>â€”</span>
                        : <span style={{ fontSize: 11, fontWeight: 600, color: status.color, background: status.bg, padding: "2px 8px", borderRadius: 6, whiteSpace: "nowrap" }}>{status.label}</span>}
                    </div>
                  </div>
                )
              })}
            </div>
          </div>
        </div>
      )}

      {/* Add Items Modal */}
      {showModal && (
        <div onClick={e => { if (e.target === e.currentTarget) { setShowModal(false); setNewItems([resetItem()]) } }}
          style={{ position: "fixed", inset: 0, background: "rgba(0,0,0,0.3)", display: "flex", alignItems: "center", justifyContent: "center", zIndex: 200 }}>
          <div style={{ background: "#fff", borderRadius: 22, padding: "32px 32px 28px", width: "100%", maxWidth: 820, boxShadow: "0 24px 64px rgba(0,0,0,0.14)" }}>

            {/* Header */}
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 24 }}>
              <div>
                <h2 style={{ fontSize: 20, fontWeight: 700, color: "#0d1a0d" }}>Add Items</h2>
                <p style={{ fontSize: 13, color: "#9ca3af", marginTop: 3 }}>Add one or more items to your inventory</p>
              </div>
              <button onClick={() => { setShowModal(false); setNewItems([resetItem()]) }}
                style={{ background: "none", border: "1.5px solid #e8ede2", borderRadius: 10, cursor: "pointer", width: 36, height: 36, display: "flex", alignItems: "center", justifyContent: "center", color: "#6b7280" }}>
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M18 6 6 18M6 6l12 12"/></svg>
              </button>
            </div>

            {addError && <div style={{ background: "#fee2e2", color: "#dc2626", padding: "10px 14px", borderRadius: 8, fontSize: 13, marginBottom: 16 }}>{addError}</div>}

            {/* Table */}
            <div style={{ border: "1.5px solid #e8ede2", borderRadius: 14, overflow: "hidden", marginBottom: 16 }}>
              <table style={{ width: "100%", borderCollapse: "collapse", fontFamily: "'DM Sans', sans-serif" }}>
                <thead>
                  <tr style={{ background: "#f9fafb", borderBottom: "1.5px solid #e8ede2" }}>
                    {["Item Name", "Qty", "Unit", "Category", "Purchase Date", ""].map(h => (
                      <th key={h} style={{ padding: "10px 14px", textAlign: "left", fontSize: 11, fontWeight: 700, color: "#9ca3af", textTransform: "uppercase", letterSpacing: "0.06em", whiteSpace: "nowrap" }}>{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {newItems.map((row, rowIdx) => (
                    <tr key={rowIdx} style={{ borderBottom: rowIdx < newItems.length - 1 ? "1px solid #f5f5f5" : "none" }}>
                      <td style={{ padding: "10px 14px", minWidth: 180 }}>
                        <div style={{ position: "relative" }}>
                          <input
                            placeholder="e.g. Chicken Breast"
                            value={row.display_name}
                            onChange={e => {
                              const val = e.target.value
                              updateRow(rowIdx, "display_name", val)
                              clearTimeout(window[`classifyTimer_${rowIdx}`])
                              window[`classifyTimer_${rowIdx}`] = setTimeout(() => handleClassifyRow(rowIdx, val), 500)
                            }}
                            style={{ width: "100%", height: 38, border: "1.5px solid #e8ede2", borderRadius: 9, padding: "0 12px", fontSize: 13, outline: "none", fontFamily: "'DM Sans', sans-serif", boxSizing: "border-box", color: "#111" }}
                          />
                          {classifyingRows[rowIdx] && (
                            <span style={{ position: "absolute", right: 10, top: "50%", transform: "translateY(-50%)", fontSize: 11, color: "#9ca3af" }}>â€¦</span>
                          )}
                        </div>
                      </td>
                      <td style={{ padding: "10px 10px", width: 80 }}>
                        <input
                          type="text" inputMode="decimal" placeholder="0"
                          value={row.quantity}
                          onChange={e => updateRow(rowIdx, "quantity", e.target.value.replace(/[^0-9.]/g, ""))}
                          style={{ width: "100%", height: 38, border: "1.5px solid #e8ede2", borderRadius: 9, padding: "0 10px", fontSize: 13, outline: "none", fontFamily: "'DM Sans', sans-serif", boxSizing: "border-box", textAlign: "center" }}
                        />
                      </td>
                      <td style={{ padding: "10px 10px", width: 100 }}>
                        <select value={row.unit} onChange={e => updateRow(rowIdx, "unit", e.target.value)}
                          style={{ width: "100%", height: 38, border: "1.5px solid #e8ede2", borderRadius: 9, padding: "0 8px", fontSize: 13, outline: "none", background: "#fff", fontFamily: "'DM Sans', sans-serif", cursor: "pointer" }}>
                          {UNITS.map(u => <option key={u} value={u}>{u}</option>)}
                        </select>
                      </td>
                      <td style={{ padding: "10px 10px", width: 120 }}>
                        <select value={row.category} onChange={e => updateRow(rowIdx, "category", e.target.value)}
                          style={{ width: "100%", height: 38, border: "1.5px solid #e8ede2", borderRadius: 9, padding: "0 8px", fontSize: 13, outline: "none", background: "#fff", fontFamily: "'DM Sans', sans-serif", cursor: "pointer" }}>
                          {CATEGORIES.map(c => <option key={c} value={c}>{c}</option>)}
                        </select>
                      </td>
                      <td style={{ padding: "10px 10px", width: 150 }}>
                        <DatePicker value={row.purchase_date} onChange={v => updateRow(rowIdx, "purchase_date", v)} max={today} />
                      </td>
                      <td style={{ padding: "10px 10px", width: 40, textAlign: "center" }}>
                        {newItems.length > 1 && (
                          <button onClick={() => removeRow(rowIdx)}
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
            <button onClick={addRow}
              style={{ display: "flex", alignItems: "center", gap: 6, background: "none", border: "1.5px dashed #c6deb0", borderRadius: 9, padding: "7px 16px", fontSize: 13, color: "#166534", cursor: "pointer", fontFamily: "'DM Sans', sans-serif", fontWeight: 500, marginBottom: 24 }}>
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
              Add row
            </button>

            {/* Footer */}
            <div style={{ display: "flex", gap: 12, justifyContent: "flex-end" }}>
              <button onClick={() => { setShowModal(false); setAddError(""); setNewItems([resetItem()]) }}
                style={{ height: 44, border: "1.5px solid #e8ede2", borderRadius: 11, background: "#fff", fontSize: 14, cursor: "pointer", fontFamily: "'DM Sans', sans-serif", color: "#6b7280", padding: "0 24px" }}>Cancel</button>
              <button onClick={handleAdd} disabled={adding}
                style={{ height: 44, border: "none", borderRadius: 11, background: "#166534", color: "#fff", fontSize: 14, fontWeight: 600, cursor: "pointer", fontFamily: "'DM Sans', sans-serif", padding: "0 28px", opacity: adding ? 0.6 : 1 }}>
                {adding ? "Adding..." : `Add ${newItems.filter(r => r.display_name.trim()).length || ""} Item${newItems.filter(r => r.display_name.trim()).length !== 1 ? "s" : ""}`}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
