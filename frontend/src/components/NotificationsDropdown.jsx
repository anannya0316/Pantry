import { useState, useEffect, useRef } from "react"
import { useNavigate } from "react-router-dom"
import { getNotifications } from "../services/api"

// --- Icons ---
const BellIcon = ({ hasUnread }) => (
  <svg width="22" height="22" viewBox="0 0 24 24" fill="none"
    stroke={hasUnread ? "#206c1b" : "#6b7280"}
    strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
    <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9" />
    <path d="M13.73 21a2 2 0 0 1-3.46 0" />
  </svg>
)

const InventoryIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z" />
    <polyline points="3.27 6.96 12 12.01 20.73 6.96" />
    <line x1="12" y1="22.08" x2="12" y2="12" />
  </svg>
)

const MealIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <rect x="3" y="4" width="18" height="18" rx="2" ry="2" />
    <line x1="16" y1="2" x2="16" y2="6" />
    <line x1="8" y1="2" x2="8" y2="6" />
    <line x1="3" y1="10" x2="21" y2="10" />
  </svg>
)

const ShoppingIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="9" cy="21" r="1" />
    <circle cx="20" cy="21" r="1" />
    <path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6" />
  </svg>
)

const NutritionIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M12 2a10 10 0 0 1 10 10H2A10 10 0 0 1 12 2z" />
    <path d="M12 22c4 0 7-2 8-6H4c1 4 4 6 8 6z" />
  </svg>
)

const ProfileIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
    <circle cx="12" cy="7" r="4" />
  </svg>
)

const ArrowRight = () => (
  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
    <path d="M5 12h14M12 5l7 7-7 7" />
  </svg>
)

const SEVERITY_STYLES = {
  danger:  { bg: "#fef2f2", border: "#fecaca", icon: "#dc2626", dot: "#dc2626" },
  warning: { bg: "#fffbeb", border: "#fde68a", icon: "#d97706", dot: "#d97706" },
  info:    { bg: "#f0fdf4", border: "#bbf7d0", icon: "#206c1b", dot: "#206c1b" },
}

const TYPE_ICON = {
  inventory: InventoryIcon,
  meal:      MealIcon,
  shopping:  ShoppingIcon,
  nutrition: NutritionIcon,
  profile:   ProfileIcon,
}

const TYPE_LABEL = {
  inventory: "Inventory",
  meal:      "Meal Plan",
  shopping:  "Shopping",
  nutrition: "Nutrition",
  profile:   "Profile",
}

export default function NotificationsDropdown({ userId }) {
  const navigate = useNavigate()
  const [open, setOpen] = useState(false)
  const [notifications, setNotifications] = useState([])
  const [loading, setLoading] = useState(false)
  const ref = useRef(null)

  useEffect(() => {
    if (!userId) return
    setLoading(true)
    getNotifications(userId)
      .then(data => setNotifications(Array.isArray(data) ? data : []))
      .catch(() => setNotifications([]))
      .finally(() => setLoading(false))
  }, [userId])

  // Close on outside click
  useEffect(() => {
    const handler = (e) => {
      if (ref.current && !ref.current.contains(e.target)) setOpen(false)
    }
    document.addEventListener("mousedown", handler)
    return () => document.removeEventListener("mousedown", handler)
  }, [])

  const unreadCount = notifications.length

  return (
    <div ref={ref} style={{ position: "relative" }}>
      {/* Bell button */}
      <button
        onClick={() => setOpen(o => !o)}
        style={{
          background: open ? "#f0fdf4" : "none",
          border: open ? "1.5px solid #bbf7d0" : "1.5px solid transparent",
          borderRadius: 10,
          width: 38,
          height: 38,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          cursor: "pointer",
          position: "relative",
          transition: "background 0.15s, border 0.15s",
        }}
      >
        <BellIcon hasUnread={unreadCount > 0} />
        {unreadCount > 0 && (
          <span style={{
            position: "absolute",
            top: 5,
            right: 5,
            width: 8,
            height: 8,
            background: "#dc2626",
            borderRadius: "50%",
            border: "1.5px solid #fff",
          }} />
        )}
      </button>

      {/* Dropdown panel */}
      {open && (
        <div style={{
          position: "absolute",
          top: 46,
          right: 0,
          width: 360,
          background: "#fff",
          borderRadius: 16,
          border: "1px solid #e8ede2",
          boxShadow: "0 8px 32px rgba(0,0,0,0.10)",
          zIndex: 1000,
          overflow: "hidden",
          fontFamily: "'DM Sans', sans-serif",
        }}>
          {/* Header */}
          <div style={{
            padding: "14px 18px 12px",
            borderBottom: "1px solid #f3f4f6",
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
          }}>
            <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
              <span style={{ fontSize: 15, fontWeight: 700, color: "#1a2e1a" }}>Notifications</span>
              {unreadCount > 0 && (
                <span style={{
                  background: "#E4F2DB",
                  color: "#206c1b",
                  fontSize: 12,
                  fontWeight: 700,
                  borderRadius: 999,
                  padding: "1px 8px",
                }}>
                  {unreadCount}
                </span>
              )}
            </div>
          </div>

          {/* Body */}
          <div style={{ maxHeight: 420, overflowY: "auto" }}>
            {loading ? (
              <div style={{ padding: "32px 18px", textAlign: "center", color: "#9ca3af", fontSize: 14 }}>
                Loading...
              </div>
            ) : notifications.length === 0 ? (
              <div style={{ padding: "36px 18px", textAlign: "center" }}>
                <div style={{ fontSize: 28, marginBottom: 8 }}>🎉</div>
                <div style={{ fontSize: 14, fontWeight: 600, color: "#374151", marginBottom: 4 }}>All caught up!</div>
                <div style={{ fontSize: 13, color: "#9ca3af" }}>No notifications right now.</div>
              </div>
            ) : (
              <div style={{ padding: "8px 0" }}>
                {notifications.map((n) => {
                  const s = SEVERITY_STYLES[n.severity] || SEVERITY_STYLES.info
                  const Icon = TYPE_ICON[n.type] || InventoryIcon
                  return (
                    <div
                      key={n.id}
                      onClick={() => { setOpen(false); navigate(n.action_url) }}
                      style={{
                        display: "flex",
                        alignItems: "flex-start",
                        gap: 12,
                        padding: "11px 18px",
                        cursor: "pointer",
                        borderBottom: "1px solid #f9fafb",
                        transition: "background 0.12s",
                      }}
                      onMouseEnter={e => e.currentTarget.style.background = "#f9fafb"}
                      onMouseLeave={e => e.currentTarget.style.background = "transparent"}
                    >
                      {/* Icon badge */}
                      <div style={{
                        width: 34,
                        height: 34,
                        borderRadius: 10,
                        background: s.bg,
                        border: `1px solid ${s.border}`,
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                        color: s.icon,
                        flexShrink: 0,
                        marginTop: 1,
                      }}>
                        <Icon />
                      </div>

                      {/* Text */}
                      <div style={{ flex: 1, minWidth: 0 }}>
                        <div style={{ display: "flex", alignItems: "center", gap: 6, marginBottom: 2 }}>
                          <span style={{
                            fontSize: 10,
                            fontWeight: 600,
                            color: s.icon,
                            textTransform: "uppercase",
                            letterSpacing: "0.04em",
                          }}>
                            {TYPE_LABEL[n.type] || n.type}
                          </span>
                        </div>
                        <div style={{ fontSize: 13, fontWeight: 600, color: "#1a2e1a", marginBottom: 2 }}>
                          {n.title}
                        </div>
                        <div style={{ fontSize: 12, color: "#6b7280", lineHeight: 1.4 }}>
                          {n.message}
                        </div>
                      </div>

                      {/* Arrow */}
                      <div style={{ color: "#9ca3af", flexShrink: 0, marginTop: 10 }}>
                        <ArrowRight />
                      </div>
                    </div>
                  )
                })}
              </div>
            )}
          </div>

          {/* Footer */}
          {notifications.length > 0 && (
            <div style={{
              padding: "10px 18px",
              borderTop: "1px solid #f3f4f6",
              textAlign: "center",
            }}>
              <span style={{ fontSize: 12, color: "#9ca3af" }}>
                {unreadCount} active alert{unreadCount !== 1 ? "s" : ""}
              </span>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
