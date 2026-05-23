import { useState, useEffect, useRef } from "react"
import { useNavigate } from "react-router-dom"
import axios from "axios"
import { getProfile } from "../services/api"
import NotificationsDropdown from "../components/NotificationsDropdown"

const BASE_URL = "http://localhost:8000"

// --- Icons ---
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

const PROMPT_CHIPS = [
  "Chicken curry",
  "Pasta",
  "Vegetarian dinner",
  "Quick 20-min dinner",
  "Help me use my ingredients",
  "What can I make now?",
  "High-protein meal",
  "I bought 2 kg tomatoes",
]

const NAV_ITEMS = [
  { label: "Home",          Icon: HomeIcon,       path: "/dashboard" },
  { label: "Smart Recipes", Icon: SearchNavIcon,  path: "/recipes"   },
  { label: "Inventory",     Icon: BoxIcon,        path: "/inventory" },
  { label: "Meal Planning", Icon: CalendarIcon,   path: "/meal-plan" },
  { label: "Insights",       Icon: BarChartIcon,   path: "/nutrition"   },
  { label: "Profile",       Icon: PersonIcon,     path: "/profile"   },
]

// --- Recipe card ---
function RecipeCard({ recipe, userId }) {
  const [status, setStatus] = useState(null)

  const handleMadeThis = async () => {
    setStatus("loading")
    try {
      await axios.post(
        `${BASE_URL}/inventory/use-recipe`,
        { ingredients: recipe.ingredients, have: recipe.have, need_to_buy: recipe.need_to_buy },
        { headers: { "user-id": userId } }
      )
      axios.post(
        `${BASE_URL}/nutrition/log-recipe`,
        { meal_name: recipe.title },
        { headers: { "user-id": userId } }
      ).catch(() => {})
      setStatus("done")
    } catch {
      setStatus("error")
    }
  }

  return (
    <div style={{ border: "1.5px solid #e8ede2", borderRadius: 20, overflow: "hidden", background: "#fff" }}>
      <div style={{ padding: "24px 28px", borderBottom: "1.5px solid #f0f0ee" }}>
        <h2 style={{ fontSize: 20, fontWeight: 700, color: "#0d1a0d", marginBottom: 6 }}>{recipe.title}</h2>
        <p style={{ fontSize: 13, color: "#6b7280", lineHeight: 1.6, marginBottom: 16 }}>{recipe.description}</p>
        <div style={{ display: "flex", gap: 8 }}>
          {[
            { label: "Prep time", value: recipe.prep_time },
            { label: "Cook time", value: recipe.cook_time },
            { label: "Servings",  value: recipe.servings  },
          ].map(m => (
            <div key={m.label} style={{ background: "#f9fafb", border: "1.5px solid #f0f0ee", borderRadius: 10, padding: "7px 14px" }}>
              <div style={{ fontSize: 10, color: "#9ca3af", fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.06em", marginBottom: 2 }}>{m.label}</div>
              <div style={{ fontSize: 13, fontWeight: 700, color: "#111" }}>{m.value}</div>
            </div>
          ))}
        </div>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr" }}>
        <div style={{ padding: "20px 28px", borderBottom: "1.5px solid #f0f0ee", borderRight: "1.5px solid #f0f0ee" }}>
          <h3 style={{ fontSize: 10, fontWeight: 700, color: "#374151", textTransform: "uppercase", letterSpacing: "0.08em", marginBottom: 14 }}>Ingredients</h3>
          <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
            {recipe.ingredients?.map((ing, i) => (
              <div key={i} style={{ display: "flex", alignItems: "center", justifyContent: "space-between", borderBottom: "1px solid #f9fafb", paddingBottom: 7 }}>
                <span style={{ fontSize: 13, color: "#374151" }}>{ing.name}</span>
                <span style={{ fontSize: 12, color: "#9ca3af", fontWeight: 600 }}>{ing.quantity} {ing.unit}</span>
              </div>
            ))}
          </div>
        </div>

        <div style={{ padding: "20px 28px", borderBottom: "1.5px solid #f0f0ee" }}>
          <h3 style={{ fontSize: 10, fontWeight: 700, color: "#374151", textTransform: "uppercase", letterSpacing: "0.08em", marginBottom: 14 }}>Steps</h3>
          <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
            {recipe.steps?.map((step, i) => (
              <div key={i} style={{ display: "flex", gap: 10, alignItems: "flex-start" }}>
                <div style={{ width: 20, height: 20, background: "#166534", color: "#fff", borderRadius: 6, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 10, fontWeight: 700, flexShrink: 0, marginTop: 2 }}>{i + 1}</div>
                <p style={{ fontSize: 13, color: "#4b5563", lineHeight: 1.6, margin: 0 }}>{step}</p>
              </div>
            ))}
          </div>
        </div>

        <div style={{ padding: "20px 28px", borderRight: "1.5px solid #f0f0ee" }}>
          <h3 style={{ fontSize: 10, fontWeight: 700, color: "#374151", textTransform: "uppercase", letterSpacing: "0.08em", marginBottom: 12 }}>What you have</h3>
          {recipe.have?.length > 0 ? (
            <div style={{ display: "flex", flexWrap: "wrap", gap: 6 }}>
              {recipe.have.map((item, i) => (
                <span key={i} style={{ background: "#E4F2DB", color: "#166534", fontSize: 12, fontWeight: 600, padding: "3px 10px", borderRadius: 8 }}>{item}</span>
              ))}
            </div>
          ) : (
            <p style={{ fontSize: 13, color: "#9ca3af", margin: 0 }}>None from your inventory</p>
          )}
        </div>

        <div style={{ padding: "20px 28px" }}>
          <h3 style={{ fontSize: 10, fontWeight: 700, color: "#374151", textTransform: "uppercase", letterSpacing: "0.08em", marginBottom: 12 }}>Need to buy</h3>
          {recipe.need_to_buy?.length > 0 ? (
            <div style={{ display: "flex", flexWrap: "wrap", gap: 6 }}>
              {recipe.need_to_buy.map((item, i) => (
                <span key={i} style={{ background: "#f3f4f6", color: "#4b5563", fontSize: 12, fontWeight: 600, padding: "3px 10px", borderRadius: 8 }}>{item}</span>
              ))}
            </div>
          ) : (
            <p style={{ fontSize: 13, fontWeight: 600, color: "#206C1B", margin: 0 }}>You have everything!</p>
          )}
        </div>
      </div>

      <div style={{ padding: "16px 28px", borderTop: "1.5px solid #f0f0ee", display: "flex", alignItems: "center", justifyContent: "space-between" }}>
        {status === "done" ? (
          <div style={{ display: "flex", alignItems: "center", gap: 8, color: "#206C1B", fontSize: 13, fontWeight: 600 }}>
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M20 6 9 17l-5-5"/></svg>
            Inventory updated
          </div>
        ) : status === "error" ? (
          <span style={{ fontSize: 13, color: "#dc2626" }}>Failed to update. Try again.</span>
        ) : (
          <span style={{ fontSize: 13, color: "#9ca3af" }}>Cooked this? Update your inventory automatically.</span>
        )}
        <button
          onClick={handleMadeThis}
          disabled={status === "loading" || status === "done"}
          style={{ height: 38, background: status === "done" ? "#E4F2DB" : "#166534", color: status === "done" ? "#206C1B" : "#fff", border: "none", borderRadius: 10, padding: "0 18px", fontSize: 13, fontWeight: 600, cursor: status === "loading" || status === "done" ? "default" : "pointer", fontFamily: "'DM Sans', sans-serif", opacity: status === "loading" ? 0.6 : 1, transition: "background 0.2s" }}
        >
          {status === "loading" ? "Updating..." : status === "done" ? "Done" : "I made this"}
        </button>
      </div>
    </div>
  )
}

function SkeletonCard() {
  return (
    <div style={{ border: "1.5px solid #e8ede2", borderRadius: 20, padding: "24px 28px" }}>
      {[["45%", 18], ["65%", 13], ["100%", 13], ["85%", 13], ["90%", 13]].map(([w, h], i) => (
        <div key={i} style={{ height: h, background: "#f3f4f6", borderRadius: 6, width: w, marginBottom: i === 1 ? 16 : 8 }} />
      ))}
    </div>
  )
}

export default function SmartRecipes() {
  const navigate  = useNavigate()
  const [messages,  setMessages]  = useState([])
  const [history,   setHistory]   = useState([])
  const [query,     setQuery]     = useState("")
  const [loading,   setLoading]   = useState(false)
  const [collapsed, setCollapsed] = useState(false)
  const [userName,  setUserName]  = useState("")
  const [chatId,    setChatId]    = useState(null)
  const bottomRef = useRef()

  const userId = localStorage.getItem("userId")

  useEffect(() => {
    if (!userId) { navigate("/login"); return }
    getProfile(userId).then(p => setUserName(p.name || p.email || "")).catch(() => {})
  }, [])

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages])

  const downloadShoppingList = async () => {
    try {
      const res = await axios.get(`${BASE_URL}/recipes/shopping-list/download`, {
        headers: { "user-id": userId },
        responseType: "blob",
      })
      const url = window.URL.createObjectURL(new Blob([res.data]))
      const link = document.createElement("a")
      link.href = url
      link.setAttribute("download", "shopping_list.txt")
      document.body.appendChild(link)
      link.click()
      link.remove()
      window.URL.revokeObjectURL(url)
    } catch (e) {
      console.error("Download failed", e)
    }
  }

  const handleSearch = async () => {
    if (!query.trim() || loading) return
    const current = query.trim()
    setQuery("")
    setLoading(true)
    setMessages(prev => [...prev, { query: current, type: "loading" }])

    try {
      const res = await axios.post(
        `${BASE_URL}/recipes/suggest`,
        { query: current, history, chat_id: chatId },
        { headers: { "user-id": userId } }
      )
      const { type, data, text, success, chat_id } = res.data
      if (chat_id) setChatId(chat_id)

      setHistory(prev => [
        ...prev,
        { role: "user", content: current },
        { role: "assistant", content: type === "recipe" ? `Generated recipe: ${data?.title}. ${text}` : text },
      ])

      setMessages(prev => prev.map((m, i) =>
        i === prev.length - 1
          ? type === "recipe"
            ? { ...m, type: "recipe", recipes: Array.isArray(data) ? data : [data], text }
            : type === "inventory_update"
            ? { ...m, type: "inventory_update", text, success }
            : type === "shopping_list"
            ? { ...m, type: "shopping_list", shoppingList: data?.items || [], householdSize: data?.household_size || 1, text }
            : { ...m, type: "chat", text }
          : m
      ))
    } catch {
      setMessages(prev => prev.map((m, i) =>
        i === prev.length - 1 ? { ...m, type: "error", text: "Failed to get a response. Please try again." } : m
      ))
    } finally {
      setLoading(false)
    }
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
              const active = path === "/recipes"
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

        {/* Main area */}
        <div style={{ flex: 1, display: "flex", flexDirection: "column", overflow: "hidden" }}>

          {/* Page header */}
          <div style={{ padding: "24px 40px 20px", flexShrink: 0, display: "flex", alignItems: "center", justifyContent: "space-between" }}>
            <div>
              <h1 style={{ fontSize: 22, fontWeight: 800, color: "#0d1a0d", marginBottom: 4 }}>Smart Recipes</h1>
              <p style={{ fontSize: 14, color: "#6b7280" }}>Discover recipes tailored to your inventory and preferences</p>
            </div>
            {messages.length > 0 && (
              <button
                onClick={() => { setMessages([]); setHistory([]) }}
                style={{ display: "flex", alignItems: "center", gap: 6, background: "none", border: "1.5px solid #e8ede2", borderRadius: 10, cursor: "pointer", fontSize: 13, color: "#6b7280", fontFamily: "'DM Sans', sans-serif", padding: "8px 16px", fontWeight: 500 }}
              >
                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/><path d="M3 3v5h5"/></svg>
                New conversation
              </button>
            )}
          </div>

          {/* Messages */}
          <div style={{ flex: 1, overflowY: "auto", padding: "28px 40px", display: "flex", flexDirection: "column", gap: 28 }}>

            {messages.length === 0 && !loading && (
              <div style={{ flex: 1, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", textAlign: "center", gap: 0 }}>
                <img src="/search.png" alt="" style={{ width: 250, height: 250, objectFit: "contain", marginBottom: 20 }} />
                <p style={{ fontSize: 17, fontWeight: 700, color: "#0d1a0d", marginBottom: 8 }}>Ask for any recipe to get started</p>
                <p style={{ fontSize: 14, color: "#6b7280", maxWidth: 440, lineHeight: 1.7, marginBottom: 4 }}>
                  Get recipes tailored to your pantry, or ask me to update your inventory.
                </p>
              </div>
            )}

            {messages.map((msg, i) => (
              <div key={i} style={{ display: "flex", flexDirection: "column", gap: 14 }}>
                <div style={{ display: "flex", justifyContent: "flex-end" }}>
                  <div style={{ background: "#166534", color: "#fff", borderRadius: "14px 14px 4px 14px", padding: "10px 18px", fontSize: 14, fontWeight: 500, maxWidth: "60%" }}>
                    {msg.query}
                  </div>
                </div>

                {msg.type === "loading" && <SkeletonCard />}
                {msg.type === "error" && (
                  <div style={{ background: "#fee2e2", color: "#dc2626", padding: "12px 16px", borderRadius: 10, fontSize: 13 }}>{msg.text}</div>
                )}
                {msg.type === "recipe" && (
                  <>
                    {(msg.recipes || []).map((recipe, i) => (
                      <RecipeCard key={i} recipe={recipe} userId={userId} />
                    ))}
                  </>
                )}
                {msg.type === "chat" && (
                  <div style={{ display: "flex" }}>
                    <div style={{ background: "#f9fafb", border: "1px solid #f0f0ee", color: "#374151", borderRadius: "4px 14px 14px 14px", padding: "12px 18px", fontSize: 14, lineHeight: 1.7, maxWidth: "75%", whiteSpace: "pre-wrap" }}>
                      {msg.text}
                    </div>
                  </div>
                )}
                {msg.type === "inventory_update" && (
                  <div style={{ display: "flex" }}>
                    <div style={{ display: "flex", alignItems: "center", gap: 10, background: msg.success ? "#E4F2DB" : "#fff7ed", border: `1.5px solid ${msg.success ? "#bbf7d0" : "#fed7aa"}`, borderRadius: 12, padding: "12px 18px", fontSize: 14, color: msg.success ? "#15803d" : "#c2410c", fontWeight: 500 }}>
                      <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                        {msg.success ? <path d="M20 6 9 17l-5-5"/> : <><circle cx="12" cy="12" r="9"/><path d="M12 8v4M12 16h.01"/></>}
                      </svg>
                      {msg.text}
                    </div>
                  </div>
                )}
                {msg.type === "shopping_list" && (() => {
                  const sections = [
                    { reason: "out of stock",        label: "Out of stock" },
                    { reason: "expired",             label: "Expired — replace" },
                    { reason: "low stock",           label: "Running low" },
                    { reason: "needed for meal plan",label: "Needed for meal plan" },
                  ]
                  return (
                    <div style={{ display: "flex" }}>
                      <div style={{ background: "#f9fafb", border: "1px solid #f0f0ee", borderRadius: "4px 14px 14px 14px", padding: "16px 20px", maxWidth: "80%", minWidth: 260 }}>
                        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 14, gap: 16 }}>
                          <span style={{ fontSize: 14, fontWeight: 700, color: "#0d1a0d" }}>
                            Shopping List · {msg.householdSize} {msg.householdSize === 1 ? "person" : "people"}
                          </span>
                          <button
                            onClick={downloadShoppingList}
                            style={{ display: "flex", alignItems: "center", gap: 5, background: "#166534", color: "#fff", border: "none", borderRadius: 8, padding: "6px 12px", fontSize: 12, fontWeight: 600, cursor: "pointer", fontFamily: "'DM Sans', sans-serif", flexShrink: 0 }}
                          >
                            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
                            Download
                          </button>
                        </div>
                        {sections.map(({ reason, label }) => {
                          const items = (msg.shoppingList || []).filter(i => i.reason === reason)
                          if (!items.length) return null
                          return (
                            <div key={reason} style={{ marginBottom: 12 }}>
                              <div style={{ fontSize: 11, fontWeight: 700, color: "#9ca3af", textTransform: "uppercase", letterSpacing: "0.06em", marginBottom: 6 }}>{label}</div>
                              {items.map((item, idx) => (
                                <div key={idx} style={{ display: "flex", alignItems: "baseline", gap: 8, padding: "3px 0", fontSize: 14, color: "#374151" }}>
                                  <span style={{ color: "#9ca3af", flexShrink: 0 }}>•</span>
                                  <span style={{ flex: 1 }}>{item.name}</span>
                                  {item.suggested_quantity && item.unit && (
                                    <span style={{ fontSize: 12, color: "#166534", fontWeight: 600, flexShrink: 0 }}>
                                      {item.suggested_quantity} {item.unit}
                                    </span>
                                  )}
                                  {!item.suggested_quantity && item.quantity && item.unit && (
                                    <span style={{ fontSize: 12, color: "#9ca3af", flexShrink: 0 }}>
                                      {item.quantity} {item.unit} left
                                    </span>
                                  )}
                                </div>
                              ))}
                            </div>
                          )
                        })}
                        {(!msg.shoppingList || msg.shoppingList.length === 0) && (
                          <p style={{ fontSize: 14, color: "#6b7280" }}>Your pantry looks fully stocked!</p>
                        )}
                      </div>
                    </div>
                  )
                })()}
              </div>
            ))}

            <div ref={bottomRef} />
          </div>

          {/* Input bar */}
          <div style={{ padding: "16px 40px 24px", flexShrink: 0 }}>
            <div style={{ display: "flex", gap: 10, background: "#f9fafb", border: "1.5px solid #e8ede2", borderRadius: 14, padding: "6px 6px 6px 18px", alignItems: "center" }}>
              <input
                value={query}
                onChange={e => setQuery(e.target.value)}
                onKeyDown={e => e.key === "Enter" && handleSearch()}
                placeholder="Ask for a recipe..."
                disabled={loading}
                style={{ flex: 1, height: 40, border: "none", background: "transparent", fontSize: 14, outline: "none", fontFamily: "'DM Sans', sans-serif", color: "#111" }}
              />
              <button
                onClick={handleSearch}
                disabled={loading || !query.trim()}
                style={{ height: 40, background: loading || !query.trim() ? "#9ca3af" : "#166534", color: "#fff", border: "none", borderRadius: 10, padding: "0 22px", fontSize: 14, fontWeight: 600, cursor: loading || !query.trim() ? "not-allowed" : "pointer", fontFamily: "'DM Sans', sans-serif", transition: "background 0.2s", display: "flex", alignItems: "center", gap: 6 }}
              >
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><polygon points="22 2 11 13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>
                {loading ? "Thinking..." : "Ask"}
              </button>
            </div>

            {messages.length === 0 && !loading && (
              <div style={{ marginTop: 12, display: "flex", alignItems: "center", gap: 8, flexWrap: "wrap" }}>
                <span style={{ fontSize: 13, color: "#6b7280", fontWeight: 500, flexShrink: 0 }}>Try asking:</span>
                {PROMPT_CHIPS.map(label => (
                  <button
                    key={label}
                    onClick={() => setQuery(label)}
                    style={{ background: "#E4F2DB", border: "1.5px solid #c6deb0", borderRadius: 999, padding: "5px 12px", fontSize: 13, fontWeight: 500, color: "#166534", cursor: "pointer", fontFamily: "'DM Sans', sans-serif" }}
                  >
                    {label}
                  </button>
                ))}
              </div>
            )}
          </div>

        </div>
      </div>
    </div>
  )
}
