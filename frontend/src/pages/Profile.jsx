import { useEffect, useState } from "react"
import { useNavigate } from "react-router-dom"
import { getProfile, updateProfile } from "../services/api"
import NotificationsDropdown from "../components/NotificationsDropdown"

// --- Icons ---
const LeafIcon = ({ size = 18, color = "#2E7D32" }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
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

const UserIcon = ({ size = 16, color = "#6b7280" }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
    <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
    <circle cx="12" cy="7" r="4" />
  </svg>
)

const ChevronDown = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#6b7280" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
    <polyline points="6 9 12 15 18 9" />
  </svg>
)

const HeartIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#206C1B" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
    <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z" />
  </svg>
)

const UtensilsIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#206C1B" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
    <path d="M3 2v7c0 1.1.9 2 2 2h4a2 2 0 0 0 2-2V2" />
    <path d="M7 2v20" />
    <path d="M21 15V2v0a5 5 0 0 0-5 5v6c0 1.1.9 2 2 2h3Zm0 0v7" />
  </svg>
)

const HomeIcon = ({ color }) => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
    <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" />
    <polyline points="9 22 9 12 15 12 15 22" />
  </svg>
)

const SearchIcon = ({ color }) => (
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

const CalendarIcon = ({ color }) => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
    <rect x="3" y="4" width="18" height="18" rx="2" ry="2" /><line x1="16" y1="2" x2="16" y2="6" /><line x1="8" y1="2" x2="8" y2="6" /><line x1="3" y1="10" x2="21" y2="10" />
  </svg>
)

const BarChartIcon = ({ color }) => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
    <line x1="18" y1="20" x2="18" y2="10" /><line x1="12" y1="20" x2="12" y2="4" /><line x1="6" y1="20" x2="6" y2="14" />
  </svg>
)

const EditIcon = () => (
  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7" />
    <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z" />
  </svg>
)

const PersonIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#206C1B" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
    <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
    <circle cx="12" cy="7" r="4" />
  </svg>
)

const MailIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#206C1B" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
    <rect width="20" height="16" x="2" y="4" rx="2" /><path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7" />
  </svg>
)

const CalSmallIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#206C1B" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
    <rect x="3" y="4" width="18" height="18" rx="2" ry="2" /><line x1="16" y1="2" x2="16" y2="6" /><line x1="8" y1="2" x2="8" y2="6" /><line x1="3" y1="10" x2="21" y2="10" />
  </svg>
)

const PersonSmallIcon = ({ color = "#206C1B" }) => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
    <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
    <circle cx="12" cy="7" r="4" />
  </svg>
)

const AlertIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#f97316" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
    <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z" /><line x1="12" y1="9" x2="12" y2="13" /><line x1="12" y1="17" x2="12.01" y2="17" />
  </svg>
)

const TargetIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#206C1B" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="12" cy="12" r="10" /><circle cx="12" cy="12" r="6" /><circle cx="12" cy="12" r="2" />
  </svg>
)

const SpiceIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#dc2626" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
    <path d="M12 2a10 10 0 0 1 10 10c0 5.52-4.48 10-10 10S2 17.52 2 12 6.48 2 12 2z" /><path d="M12 6v6l4 2" />
  </svg>
)

const LeafSmallIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#206C1B" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
    <path d="M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.48 19 2c1 2 2 4.18 2 8 0 5.5-4.78 10-10 10z" />
    <path d="M2 21c0-3 1.85-5.36 5.08-6C9.5 14.52 12 13 13 12" />
  </svg>
)

const ThumbUpIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#206C1B" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
    <path d="M14 9V5a3 3 0 0 0-3-3l-4 9v11h11.28a2 2 0 0 0 2-1.7l1.38-9a2 2 0 0 0-2-2.3H14z" /><path d="M7 22H4a2 2 0 0 1-2-2v-7a2 2 0 0 1 2-2h3" />
  </svg>
)

const FamilyIcon = () => (
  <svg
    width="16"
    height="16"
    viewBox="0 0 24 24"
    fill="none"
    stroke="#206C1B"
    strokeWidth="1.8"
    strokeLinecap="round"
    strokeLinejoin="round"
  >
    <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
    <circle cx="9" cy="7" r="4" />
    <path d="M23 21v-2a4 4 0 0 0-3-3.5" />
    <path d="M16 3.5a4 4 0 0 1 0 7" />
  </svg>
);

const CartIcon = () => (
  <svg
    width="16"
    height="16"
    viewBox="0 0 24 24"
    fill="none"
    stroke="#206C1B"
    strokeWidth="1.8"
    strokeLinecap="round"
    strokeLinejoin="round"
  >
    <circle cx="9" cy="20" r="1" />
    <circle cx="18" cy="20" r="1" />
    <path d="M3 3h2l2.4 10.5a2 2 0 0 0 2 1.5h7.9a2 2 0 0 0 2-1.5L21 7H7" />
  </svg>
);

const ThumbDownIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#dc2626" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
    <path d="M10 15v4a3 3 0 0 0 3 3l4-9V2H5.72a2 2 0 0 0-2 1.7l-1.38 9a2 2 0 0 0 2 2.3H10z" /><path d="M17 2h2.67A2.31 2.31 0 0 1 22 4v7a2.31 2.31 0 0 1-2.33 2H17" />
  </svg>
)

const GlobeIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#7c3aed" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="12" cy="12" r="10" /><line x1="2" y1="12" x2="22" y2="12" /><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z" />
  </svg>
)

const StarIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#2563eb" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
    <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2" />
  </svg>
)

const NAV_ITEMS = [
  { label: "Home", Icon: HomeIcon, path: "/dashboard" },
  { label: "Smart Recipes", Icon: SearchIcon, path: "/recipes" },
  { label: "Inventory", Icon: BoxIcon, path: "/inventory" },
  { label: "Meal Planning", Icon: CalendarIcon, path: "/meal-plan" },
  { label: "Insights", Icon: BarChartIcon, path: "/nutrition" },
  { label: "Profile", Icon: PersonIcon, path: "/profile" },
]

const inputStyle = {
  width: "100%", height: 40, padding: "0 12px",
  background: "#f7f8f5", border: "1.5px solid #e8ede2",
  borderRadius: 8, fontSize: 14, fontFamily: "'DM Sans', sans-serif",
  color: "#111", outline: "none",
}

const selectStyle = {
  ...inputStyle, cursor: "pointer", appearance: "none", WebkitAppearance: "none", paddingRight: 36,
}

function StyledSelect({ value, onChange, children }) {
  return (
    <div style={{ position: "relative" }}>
      <select style={selectStyle} value={value} onChange={onChange}>{children}</select>
      <span style={{ position: "absolute", right: 12, top: "50%", transform: "translateY(-50%)", pointerEvents: "none", color: "#9ca3af", display: "flex" }}>
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round"><polyline points="6 9 12 15 18 9" /></svg>
      </span>
    </div>
  )
}

function TagInput({ value, onChange, placeholder }) {
  const [input, setInput] = useState("")
  const tags = value || []

  const addTag = (val) => {
    const trimmed = val.trim()
    if (trimmed && !tags.includes(trimmed)) onChange([...tags, trimmed])
    setInput("")
  }

  const removeTag = (t) => onChange(tags.filter(x => x !== t))

  return (
    <div style={{ border: "1.5px solid #e8ede2", borderRadius: 8, padding: "6px 10px", background: "#f7f8f5", display: "flex", flexWrap: "wrap", gap: 6, minHeight: 40, alignItems: "center" }}>
      {tags.map(t => (
        <span key={t} style={{ background: "#e8f5e9", color: "#166534", borderRadius: 20, padding: "3px 10px", fontSize: 13, fontWeight: 500, display: "flex", alignItems: "center", gap: 5 }}>
          {t}
          <button onClick={() => removeTag(t)} style={{ background: "none", border: "none", cursor: "pointer", color: "#166534", padding: 0, lineHeight: 1, fontSize: 14 }}>×</button>
        </span>
      ))}
      <input
        style={{ border: "none", background: "transparent", outline: "none", fontSize: 14, fontFamily: "'DM Sans', sans-serif", color: "#111", flex: 1, minWidth: 80 }}
        placeholder={tags.length === 0 ? placeholder : "Add more..."}
        value={input}
        onChange={e => setInput(e.target.value)}
        onKeyDown={e => { if (e.key === "Enter" || e.key === ",") { e.preventDefault(); addTag(input) } }}
        onBlur={() => { if (input.trim()) addTag(input) }}
      />
    </div>
  )
}

function InfoRow({ icon, label, value }) {
  return (
    <div style={{ display: "flex", alignItems: "center", padding: "14px 0", borderBottom: "1px solid #f9fafb" }}>
      <div style={{ width: 32, display: "flex", alignItems: "center" }}>{icon}</div>
      <span style={{ width: 160, fontSize: 14, color: "#6b7280", flexShrink: 0 }}>{label}</span>
      <span style={{ fontSize: 14, fontWeight: 500, color: "#111" }}>{value || "—"}</span>
    </div>
  )
}

function GridRow({ icon, label, value, placeholder }) {
  const isEmpty = Array.isArray(value) ? value.length === 0 : !value
  const display = Array.isArray(value)
    ? value.length > 2 ? value.slice(0, 2).join(", ") + "..." : value.join(", ")
    : value
  return (
    <div style={{ background: "#f9fafb", borderRadius: 12, padding: "14px 16px", display: "flex", flexDirection: "column", gap: 4 }}>
      <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
        <div style={{ width: 28, height: 28, borderRadius: "50%", background: "#fff", display: "flex", alignItems: "center", justifyContent: "center", border: "1px solid #e8ede2" }}>{icon}</div>
        <span style={{ fontSize: 13, color: "#6b7280", fontWeight: 500 }}>{label}</span>
      </div>
      <span style={{ fontSize: 14, fontWeight: isEmpty ? 400 : 600, color: isEmpty ? "#c0c0bc" : "#111", paddingLeft: 2, lineHeight: 1.4, fontStyle: isEmpty ? "italic" : "normal" }}>
        {isEmpty ? (placeholder || "Not set") : display}
      </span>
    </div>
  )
}

function SectionCard({ title, icon, children, onEdit, editing, onSave, onCancel, saving }) {
  return (
    <div style={{ background: "#fff", border: "1px solid #f0f0ee", borderRadius: 16, padding: "24px 28px", marginBottom: 20 }}>
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 20 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <div style={{ width: 34, height: 34, borderRadius: "50%", background: "#E4F2DB", border: "1px solid #E4F2DB", display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0 }}>{icon}</div>
          <h2 style={{ fontSize: 17, fontWeight: 700, color: "#111" }}>{title}</h2>
        </div>
        {onEdit && (!editing ? (
          <button onClick={onEdit} style={{ display: "flex", alignItems: "center", gap: 6, background: "none", border: "1.5px solid #e8ede2", borderRadius: 8, padding: "7px 14px", fontSize: 13, fontWeight: 600, color: "#374151", cursor: "pointer", fontFamily: "'DM Sans', sans-serif" }}>
            <EditIcon /> Edit
          </button>
        ) : (
          <div style={{ display: "flex", gap: 8 }}>
            <button onClick={onCancel} style={{ background: "none", border: "1.5px solid #e8ede2", borderRadius: 8, padding: "7px 14px", fontSize: 13, fontWeight: 600, color: "#6b7280", cursor: "pointer", fontFamily: "'DM Sans', sans-serif" }}>Cancel</button>
            <button onClick={onSave} disabled={saving} style={{ background: "#166534", color: "#fff", border: "none", borderRadius: 8, padding: "7px 16px", fontSize: 13, fontWeight: 600, cursor: saving ? "not-allowed" : "pointer", opacity: saving ? 0.7 : 1, fontFamily: "'DM Sans', sans-serif" }}>{saving ? "Saving..." : "Save"}</button>
          </div>
        ))}
      </div>
      {children}
    </div>
  )
}

function FieldLabel({ children }) {
  return <label style={{ display: "block", fontSize: 13, fontWeight: 500, color: "#374151", marginBottom: 6 }}>{children}</label>
}

function Profile() {
  const navigate = useNavigate()
  const [profile, setProfile] = useState(null)
  const [loading, setLoading] = useState(true)

  const [collapsed, setCollapsed] = useState(false)
  const [editingPersonal, setEditingPersonal] = useState(false)
  const [editingHealth, setEditingHealth] = useState(false)
  const [editingFood, setEditingFood] = useState(false)
  const [saving, setSaving] = useState(false)
  const [savingSection, setSavingSection] = useState(null)

  const [draftPersonal, setDraftPersonal] = useState({})
  const [draftHealth, setDraftHealth] = useState({})
  const [draftFood, setDraftFood] = useState({})

  const userId = localStorage.getItem("userId")

  useEffect(() => {
    if (!userId) { navigate("/login"); return }
    getProfile(userId).then(p => {
      setProfile(p)
      setLoading(false)
    })
  }, [navigate, userId])

  const formatDate = (val) => val || "—"

  const handleLogout = () => {
    localStorage.removeItem("userId")
    localStorage.removeItem("token")
    navigate("/login")
  }

  const startEdit = (section) => {
    if (section === "personal") {
      setDraftPersonal({
      household_size: profile.household_size || "",
      grocery_shopping_day: profile.grocery_shopping_day || "Sunday"
    })
      setEditingPersonal(true)
    } else if (section === "health") {
      setDraftHealth({
        diet: profile.diet || "veg",
        allergies: profile.allergies || [],
        goals: profile.goals || [],
        spice_preference: profile.spice_preference || "",
      })
      setEditingHealth(true)
    } else if (section === "food") {
      setDraftFood({
        liked_ingredients: profile.liked_ingredients || [],
        disliked_ingredients: profile.disliked_ingredients || [],
        favorite_cuisines: profile.favorite_cuisines || [],
        special_preferences: profile.special_preferences || [],
      })
      setEditingFood(true)
    }
  }

  const saveSection = async (section, data) => {
    setSaving(true)
    setSavingSection(section)
    try {
      await updateProfile(data, userId)
      const updated = await getProfile(userId)
      setProfile(updated)
      if (section === "personal") setEditingPersonal(false)
      if (section === "health") setEditingHealth(false)
      if (section === "food") setEditingFood(false)
    } catch (e) {
      console.error(e)
    } finally {
      setSaving(false)
      setSavingSection(null)
    }
  }

  if (loading) return (
    <div style={{ height: "100vh", display: "flex", alignItems: "center", justifyContent: "center", fontFamily: "'DM Sans', sans-serif", color: "#6b7280" }}>
      Loading...
    </div>
  )

  const firstName = (profile.name || "").split(" ")[0]

  return (
    <div style={{ height: "100vh", display: "flex", flexDirection: "column", fontFamily: "'DM Sans', sans-serif", background: "#fff" }}>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&display=swap');
        *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
        button, input, select, textarea { font-family: 'DM Sans', sans-serif; }
        input:focus, select:focus { border-color: #1B4332 !important; background: #fff !important; }
        ::-webkit-scrollbar { width: 4px; } ::-webkit-scrollbar-thumb { background: #e5e7eb; border-radius: 4px; }
      `}</style>

      {/* Navbar */}
      <nav style={{ display: "flex", alignItems: "center", justifyContent: "space-between", padding: "0 52px", height: 64, borderBottom: "1px solid #f0f0ee", flexShrink: 0, background: "#fff" }}>
        <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 9 }}>
            <div style={{ width: 36, height: 36, background: "#E4F2DB", border: "1px solid #c6deb0", borderRadius: 9, display: "flex", alignItems: "center", justifyContent: "center" }}>
              <LeafIcon size={18} color="#2E7D32" />
            </div>
            <span style={{ fontSize: 17, fontWeight: 700, color: "#1a2e1a" }}>Pantry</span>
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: 6, border: "1.5px solid #c6deb0", borderRadius: 999, padding: "5px 14px", fontSize: 13, color: "#206c1b", fontWeight: 500 }}>
            <span style={{ fontSize: 11 }}>✦</span> Your personalized kitchen assistant
          </div>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
          <NotificationsDropdown userId={userId} />
          <div style={{ display: "flex", alignItems: "center", gap: 8, padding: "6px 12px", borderRadius: 999, border: "1.5px solid #e8ede2", cursor: "pointer" }} onClick={() => navigate("/profile")}>
            <div style={{ width: 28, height: 28, borderRadius: "50%", background: "#f3f4f6", display: "flex", alignItems: "center", justifyContent: "center" }}>
              <UserIcon size={16} color="#6b7280" />
            </div>
            <span style={{ fontSize: 14, fontWeight: 500, color: "#374151" }}>{firstName || "—"}</span>
          </div>
          <button onClick={handleLogout} style={{ background: "none", border: "1.5px solid #e0e0e0", borderRadius: 8, padding: "7px 16px", fontSize: 14, fontWeight: 500, color: "#6b7280", cursor: "pointer" }}>Log out</button>
        </div>
      </nav>

      <div style={{ flex: 1, display: "flex", overflow: "hidden" }}>
        {/* Sidebar */}
        <aside style={{ width: collapsed ? 56 : 240, flexShrink: 0, borderRight: "1px solid #f0f0ee", display: "flex", flexDirection: "column", padding: collapsed ? "24px 8px" : "24px 16px", overflow: "hidden", transition: "width 0.2s ease, padding 0.2s ease" }}>
          {/* Toggle button */}
          <button onClick={() => setCollapsed(c => !c)} style={{ alignSelf: collapsed ? "center" : "flex-end", background: "none", border: "1.5px solid #e8ede2", borderRadius: 8, width: 28, height: 28, display: "flex", alignItems: "center", justifyContent: "center", cursor: "pointer", marginBottom: 16, flexShrink: 0, color: "#9ca3af" }}>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
              {collapsed ? <path d="M9 18l6-6-6-6" /> : <path d="M15 18l-6-6 6-6" />}
            </svg>
          </button>

          <nav style={{ display: "flex", flexDirection: "column", gap: 4, flex: 1 }}>
            {NAV_ITEMS.map(({ label, Icon, path }) => {
              const active = path === "/profile"
              const isProfile = path === "/profile"
              return (
                <div key={label}>
                  {isProfile && <div style={{ height: 1, background: "#f0f0ee", margin: "6px 0" }} />}
                  <button onClick={() => navigate(path)} title={collapsed ? label : undefined} style={{
                    width: "100%", display: "flex", alignItems: "center", justifyContent: collapsed ? "center" : "flex-start", gap: 10, padding: collapsed ? "10px 0" : "10px 14px",
                    borderRadius: 10, border: "none", cursor: "pointer", textAlign: "left",
                    background: active ? "#E4F2DB" : "transparent",
                    color: active ? "#166534" : "#6b7280",
                    fontWeight: active ? 600 : 500, fontSize: 14,
                    transition: "background 0.15s",
                  }}>
                    <Icon color={active ? "#166534" : "#9ca3af"} />
                    {!collapsed && label}
                  </button>
                </div>
              )
            })}
          </nav>

          {/* Motivational card */}
          {!collapsed && (
            <div style={{ background: "#E4F2DB", borderRadius: 14, padding: "16px", border: "1px solid #E4F2DB" }}>
              <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 8 }}>
                <LeafIcon size={18} color="#166634" />
              </div>
              <div style={{ fontSize: 13, fontWeight: 700, color: "#166534", marginBottom: 4 }}>Small steps, big impact.</div>
              <div style={{ fontSize: 12, color: "#15803d", lineHeight: 1.5 }}>Every healthy choice counts!</div>
            </div>
          )}
          {collapsed && (
            <div style={{ display: "flex", justifyContent: "center", paddingBottom: 8 }}>
              <LeafIcon size={18} color="#166534" />
            </div>
          )}
        </aside>

        {/* Main Content */}
        <main style={{ flex: 1, overflowY: "auto", padding: "40px 52px" }}>
          <h1 style={{ fontSize: 22, fontWeight: 800, color: "#0d1a0d", marginBottom: 6 }}>Profile & Preferences</h1>
          <p style={{ fontSize: 14, color: "#6b7280", marginBottom: 32 }}>Manage your personal information and preferences.</p>

          {/* Personal Information */}
          <SectionCard
            title="Personal Information"
            icon={<PersonSmallIcon color="#206C1B" />}
            editing={editingPersonal}
            onEdit={() => startEdit("personal")}
            onCancel={() => setEditingPersonal(false)}
            onSave={() => saveSection("personal", draftPersonal)}
            saving={saving && savingSection === "personal"}
          >
            {!editingPersonal ? (
  <div
    style={{
      display: "grid",
      gridTemplateColumns: "1fr 1fr",
      columnGap: 40,
    }}
  >
    <div>
      <InfoRow
        icon={<PersonSmallIcon />}
        label="Full Name"
        value={profile.name}
      />

      <InfoRow
        icon={<MailIcon />}
        label="Email"
        value={profile.email}
      />

      <InfoRow
        icon={<CalSmallIcon />}
        label="Member Since"
        value={formatDate(profile.created_at)}
      />
    </div>

    <div>
      <InfoRow
        icon={<FamilyIcon />}
        label="Household Size"
        value={profile.household_size}
      />

      <InfoRow
        icon={<CartIcon />}
        label="Grocery Shopping Day"
        value={profile.grocery_shopping_day}
      />
    </div>
  </div>
) : (
  <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
    <div>
      <FieldLabel>Household Size</FieldLabel>

      <input
        type="number"
        style={inputStyle}
        value={draftPersonal.household_size}
        onChange={(e) =>
          setDraftPersonal((p) => ({
            ...p,
            household_size: e.target.value
          }))
        }
      />
    </div>

    <div>
      <FieldLabel>Grocery Shopping Day</FieldLabel>

      <StyledSelect
        value={draftPersonal.grocery_shopping_day}
        onChange={(e) =>
          setDraftPersonal((p) => ({
            ...p,
            grocery_shopping_day: e.target.value
          }))
        }
      >
        <option value="Monday">Monday</option>
        <option value="Tuesday">Tuesday</option>
        <option value="Wednesday">Wednesday</option>
        <option value="Thursday">Thursday</option>
        <option value="Friday">Friday</option>
        <option value="Saturday">Saturday</option>
        <option value="Sunday">Sunday</option>
      </StyledSelect>
    </div>
  </div>
)}
          </SectionCard>

          {/* Health Preferences */}
          <SectionCard
            title="Health Preferences"
            icon={<HeartIcon />}
            editing={editingHealth}
            onEdit={() => startEdit("health")}
            onCancel={() => setEditingHealth(false)}
            onSave={() => saveSection("health", draftHealth)}
            saving={saving && savingSection === "health"}
          >
            {!editingHealth ? (
              <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 12 }}>
                <GridRow icon={<LeafSmallIcon />} label="Diet Type" value={profile.diet === "veg" ? "Vegetarian" : profile.diet === "non_veg" ? "Non-Vegetarian" : null} placeholder="e.g. Vegetarian" />
                <GridRow icon={<AlertIcon />} label="Allergies" value={profile.allergies} placeholder="e.g. Nuts, Dairy" />
                <GridRow icon={<TargetIcon />} label="Health Goals" value={profile.goals} placeholder="e.g. Weight Management" />
                <GridRow icon={<SpiceIcon />} label="Spice Preference" value={profile.spice_preference} placeholder="e.g. Medium" />
              </div>
            ) : (
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
                <div>
                  <FieldLabel>Diet Type</FieldLabel>
                  <StyledSelect value={draftHealth.diet} onChange={e => setDraftHealth(p => ({ ...p, diet: e.target.value }))}>
                    <option value="veg">Vegetarian</option>
                    <option value="non_veg">Non-Vegetarian</option>
                  </StyledSelect>
                </div>
                <div>
                  <FieldLabel>Spice Preference</FieldLabel>
                  <StyledSelect value={draftHealth.spice_preference} onChange={e => setDraftHealth(p => ({ ...p, spice_preference: e.target.value }))}>
                    <option value="">Select...</option>
                    <option value="Low">Low</option>
                    <option value="Medium">Medium</option>
                    <option value="High">High</option>
                  </StyledSelect>
                </div>
                <div style={{ gridColumn: "1 / -1" }}>
                  <FieldLabel>Allergies (press Enter or comma to add)</FieldLabel>
                  <TagInput value={draftHealth.allergies} onChange={v => setDraftHealth(p => ({ ...p, allergies: v }))} placeholder="e.g. Nuts, Dairy" />
                </div>
                <div style={{ gridColumn: "1 / -1" }}>
                  <FieldLabel>Health Goals</FieldLabel>
                  <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
                    {["Eat healthier", "Save money", "Cook faster", "Gain muscle", "Lose weight"].map(goal => {
                      const selected = draftHealth.goals?.includes(goal)
                      return (
                        <button key={goal} type="button" onClick={() => setDraftHealth(p => ({ ...p, goals: selected ? p.goals.filter(g => g !== goal) : [...(p.goals || []), goal] }))}
                          style={{ padding: "8px 16px", borderRadius: 20, fontSize: 13, fontWeight: 500, cursor: "pointer", border: `1.5px solid ${selected ? "#166534" : "#e8ede2"}`, background: selected ? "#E4F2DB" : "#f7f8f5", color: selected ? "#166534" : "#6b7280", fontFamily: "'DM Sans', sans-serif", transition: "all 0.15s" }}>
                          {goal}
                        </button>
                      )
                    })}
                  </div>
                </div>
              </div>
            )}
          </SectionCard>

          {/* Food Preferences */}
          <SectionCard
            title="Food Preferences"
            icon={<UtensilsIcon />}
            editing={editingFood}
            onEdit={() => startEdit("food")}
            onCancel={() => setEditingFood(false)}
            onSave={() => saveSection("food", draftFood)}
            saving={saving && savingSection === "food"}
          >
            {!editingFood ? (
              <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 12 }}>
                <GridRow icon={<ThumbUpIcon />} label="Liked Ingredients" value={profile.liked_ingredients} placeholder="e.g. Spinach, Tofu" />
                <GridRow icon={<ThumbDownIcon />} label="Disliked Ingredients" value={profile.disliked_ingredients} placeholder="e.g. Mushrooms" />
                <GridRow icon={<GlobeIcon />} label="Favorite Cuisines" value={profile.favorite_cuisines} placeholder="e.g. Mediterranean" />
                <GridRow icon={<StarIcon />} label="Special Preferences" value={profile.special_preferences} placeholder="e.g. Low Oil, Gluten Free" />
              </div>
            ) : (
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
                <div>
                  <FieldLabel>Liked Ingredients</FieldLabel>
                  <TagInput value={draftFood.liked_ingredients} onChange={v => setDraftFood(p => ({ ...p, liked_ingredients: v }))} placeholder="e.g. Spinach, Tofu" />
                </div>
                <div>
                  <FieldLabel>Disliked Ingredients</FieldLabel>
                  <TagInput value={draftFood.disliked_ingredients} onChange={v => setDraftFood(p => ({ ...p, disliked_ingredients: v }))} placeholder="e.g. Mushrooms" />
                </div>
                <div>
                  <FieldLabel>Favorite Cuisines</FieldLabel>
                  <TagInput value={draftFood.favorite_cuisines} onChange={v => setDraftFood(p => ({ ...p, favorite_cuisines: v }))} placeholder="e.g. Mediterranean" />
                </div>
                <div>
                  <FieldLabel>Special Preferences</FieldLabel>
                  <TagInput value={draftFood.special_preferences} onChange={v => setDraftFood(p => ({ ...p, special_preferences: v }))} placeholder="e.g. Low Oil, Gluten Free" />
                </div>
              </div>
            )}
          </SectionCard>
        </main>
      </div>
    </div>
  )
}

export default Profile
