import { useEffect, useRef, useState } from "react"
import { useNavigate, useSearchParams } from "react-router-dom"
import axios from "axios"

const BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000"

const LeafIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#2E7D32" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
    <path d="M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.48 19 2c1 2 2 4.18 2 8 0 5.5-4.78 10-10 10z" />
    <path d="M2 21c0-3 1.85-5.36 5.08-6C9.5 14.52 12 13 13 12" />
  </svg>
)

export default function VerifyEmail() {
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const [status, setStatus] = useState("verifying") // verifying | success | error
  const [errorMsg, setErrorMsg] = useState("")
  const called = useRef(false)

  useEffect(() => {
    if (called.current) return
    called.current = true

    const token = searchParams.get("token")
    if (!token) {
      setStatus("error")
      setErrorMsg("No verification token found in the link.")
      return
    }

    axios.post(`${BASE_URL}/auth/verify-email`, { token })
      .then(() => {
        setStatus("success")
      })
      .catch(err => {
        setStatus("error")
        setErrorMsg(err.response?.data?.detail || "Verification failed. The link may have expired.")
      })
  }, [])

  return (
    <div style={{ minHeight: "100vh", background: "#fff", fontFamily: "'DM Sans', sans-serif", display: "flex", flexDirection: "column" }}>
      <style>{`@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700;800&display=swap');`}</style>

      <nav style={{ display: "flex", alignItems: "center", padding: "20px 52px", borderBottom: "1px solid #f0f0ee" }}>
        <div style={{ display: "flex", alignItems: "center", gap: 9 }}>
          <div style={{ width: 36, height: 36, background: "#E4F2DB", border: "1px solid #c6deb0", borderRadius: 9, display: "flex", alignItems: "center", justifyContent: "center" }}>
            <LeafIcon />
          </div>
          <span style={{ fontSize: 17, fontWeight: 700, color: "#1a2e1a" }}>Pantry</span>
        </div>
      </nav>

      <div style={{ flex: 1, display: "flex", alignItems: "center", justifyContent: "center", padding: "48px 24px" }}>
        <div style={{ maxWidth: 420, width: "100%", textAlign: "center" }}>

          {status === "verifying" && (
            <>
              <div style={{ width: 64, height: 64, borderRadius: "50%", background: "#E4F2DB", display: "flex", alignItems: "center", justifyContent: "center", margin: "0 auto 24px" }}>
                <div style={{ width: 24, height: 24, border: "3px solid #c6deb0", borderTopColor: "#166534", borderRadius: "50%", animation: "spin 0.8s linear infinite" }} />
              </div>
              <h2 style={{ fontSize: 22, fontWeight: 800, color: "#111", marginBottom: 10 }}>Verifying your emailâ€¦</h2>
              <p style={{ fontSize: 14, color: "#9ca3af" }}>Just a moment</p>
            </>
          )}

          {status === "success" && (
            <>
              <div style={{ width: 64, height: 64, borderRadius: "50%", background: "#E4F2DB", display: "flex", alignItems: "center", justifyContent: "center", margin: "0 auto 24px" }}>
                <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#166534" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M20 6 9 17l-5-5" />
                </svg>
              </div>
              <h2 style={{ fontSize: 22, fontWeight: 800, color: "#111", marginBottom: 10 }}>Email verified!</h2>
              <p style={{ fontSize: 14, color: "#6b7280", marginBottom: 8 }}>Your account has been created.</p>
              <p style={{ fontSize: 13, color: "#9ca3af" }}>You can close this tab â€” your original window is continuing.</p>
            </>
          )}

          {status === "error" && (
            <>
              <div style={{ width: 64, height: 64, borderRadius: "50%", background: "#fef2f2", display: "flex", alignItems: "center", justifyContent: "center", margin: "0 auto 24px" }}>
                <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#dc2626" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                  <circle cx="12" cy="12" r="10" /><line x1="12" y1="8" x2="12" y2="12" /><line x1="12" y1="16" x2="12.01" y2="16" />
                </svg>
              </div>
              <h2 style={{ fontSize: 22, fontWeight: 800, color: "#111", marginBottom: 10 }}>Verification failed</h2>
              <p style={{ fontSize: 14, color: "#6b7280", marginBottom: 28, lineHeight: 1.6 }}>{errorMsg}</p>
              <button
                onClick={() => navigate("/signup")}
                style={{ height: 48, padding: "0 28px", background: "#166534", color: "#fff", border: "none", borderRadius: 10, fontSize: 14, fontWeight: 600, cursor: "pointer", fontFamily: "'DM Sans', sans-serif" }}
              >
                Back to sign up
              </button>
            </>
          )}
        </div>
      </div>

      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
    </div>
  )
}
