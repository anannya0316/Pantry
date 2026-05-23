import { useState } from "react"
import { login, googleAuth } from "../services/api"
import { useNavigate, Link } from "react-router-dom"
import { GoogleLogin } from "@react-oauth/google"

const LeafIcon = ({ size = 18, color = "#2E7D32" }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
    <path d="M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.48 19 2c1 2 2 4.18 2 8 0 5.5-4.78 10-10 10z" />
    <path d="M2 21c0-3 1.85-5.36 5.08-6C9.5 14.52 12 13 13 12" />
  </svg>
)

const EyeIcon = ({ open }) => open ? (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7z" /><circle cx="12" cy="12" r="3" />
  </svg>
) : (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94" /><path d="M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19" /><line x1="1" y1="1" x2="23" y2="23" />
  </svg>
)

const styles = `
  @import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700;0,9..40,800&display=swap');
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
  .field-label { display: block; font-size: 13px; font-weight: 500; color: #374151; margin-bottom: 7px; }
  .input-wrapper { position: relative; display: flex; align-items: center; }
  .input-icon { position: absolute; left: 14px; color: #b0b0b0; display: flex; align-items: center; pointer-events: none; }
  .eye-toggle { position: absolute; right: 14px; color: #b0b0b0; display: flex; align-items: center; cursor: pointer; background: none; border: none; padding: 0; }
  .eye-toggle:hover { color: #6b7280; }
  .auth-input {
    width: 100%; height: 50px; padding: 0 14px 0 44px;
    background: #f7f8f5; border: 1.5px solid #e8ede2;
    border-radius: 10px; font-size: 14px; font-family: 'DM Sans', sans-serif;
    color: #111; outline: none; transition: border-color 0.15s, background 0.15s;
  }
  .auth-input::placeholder { color: #c0c0bc; }
  .auth-input:focus { background: #fff; border-color: #1B4332; }
  .btn-green {
    width: 100%; height: 52px; background: #1B4332; color: #fff; border: none;
    border-radius: 12px; font-size: 15px; font-weight: 600; font-family: 'DM Sans', sans-serif;
    cursor: pointer; display: flex; align-items: center; justify-content: center; gap: 10px;
    transition: opacity 0.15s, transform 0.1s; margin-top: 4px;
  }
  .btn-green:hover:not(:disabled) { opacity: 0.9; }
  .btn-green:active:not(:disabled) { transform: scale(0.99); }
  .btn-green:disabled { opacity: 0.6; cursor: not-allowed; }
`

function Login() {
  const navigate = useNavigate()
  const [form, setForm] = useState({ email: "", password: "" })
  const [error, setError] = useState("")
  const [loading, setLoading] = useState(false)
  const [showPassword, setShowPassword] = useState(false)

  const handleChange = (e) => setForm({ ...form, [e.target.name]: e.target.value })

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true); setError("")
    try {
      if (!form.email || !form.password) { setError("Please fill in all fields"); setLoading(false); return }
      const res = await login(form)
      if (res.detail) { setError(res.detail); setLoading(false); return }
      if (!res.access_token) { setError("Login failed. Please check your credentials and try again."); setLoading(false); return }
      localStorage.setItem("token", res.access_token)
      localStorage.setItem("userId", res.user_id)
      navigate(res.onboarding_complete ? "/dashboard" : "/getting-started")
    } catch (err) {
      setError(err.response?.data?.detail || err.message || "Login failed. Please check your credentials.")
    } finally {
      setLoading(false)
    }
  }

  const handleGoogleSuccess = async ({ credential }) => {
    setLoading(true); setError("")
    try {
      const res = await googleAuth(credential, "login")
      if (res.detail) { setError(res.detail); return }
      if (!res.access_token) { setError("Google login failed. Please try again."); return }
      localStorage.setItem("token", res.access_token)
      localStorage.setItem("userId", res.user_id)
      navigate(res.onboarding_complete ? "/dashboard" : "/getting-started")
    } catch (err) {
      setError(err.message || "Google login failed.")
    } finally {
      setLoading(false)
    }
  }

  return (
    <>
      <style>{styles}</style>
      <div style={{ height: "100vh", display: "flex", flexDirection: "column", fontFamily: "'DM Sans', sans-serif" }}>

        {/* Navbar — normal flow so panels start below it */}
        <nav style={{
          display: "flex", justifyContent: "space-between", alignItems: "center",
          padding: "20px 52px", flexShrink: 0, background: "#fff"
        }}>
          <div style={{ display: "flex", alignItems: "center", gap: 9 }}>
            <div style={{
              width: 36, height: 36, background: "#E4F2DB", border: "1px solid #c6deb0",
              borderRadius: 9, display: "flex", alignItems: "center", justifyContent: "center"
            }}>
              <LeafIcon size={18} color="#2E7D32" />
            </div>
            <span style={{ fontSize: 17, fontWeight: 700, color: "#1a2e1a" }}>Pantry</span>
          </div>
        </nav>

        {/* Content row — fills remaining height */}
        <div style={{ flex: 1, display: "flex", minHeight: 0 }}>

          {/* Left panel */}
          <div style={{
            width: "47%", flexShrink: 0, background: "#e5ebe0",
            borderTopRightRadius: 220, overflow: "hidden",
            display: "flex", flexDirection: "column"
          }}>
            <div style={{ padding: "52px 52px 0" }}>
              <h2 style={{
                fontSize: 42, fontWeight: 800, lineHeight: 1.15,
                color: "#1a2e1a", letterSpacing: "-1px", marginBottom: 14
              }}>
                Welcome<br /><span style={{ color: "#2E7D32" }}>back!</span>
              </h2>
              <p style={{ fontSize: 15, color: "#5a7a5a", lineHeight: 1.6, maxWidth: 260 }}>
                Log in to continue your healthy cooking journey.
              </p>
            </div>
            <div style={{ flex: 1 }} />
            <img
              src="/login.png"
              alt=""
              style={{ width: "100%", display: "block", objectFit: "cover", objectPosition: "center top", maxHeight: "65%" }}
            />
          </div>

          {/* Right panel */}
          <div style={{
            flex: 1, background: "#fff",
            display: "flex", alignItems: "center", justifyContent: "center",
            padding: "48px 64px"
          }}>
          <div style={{ width: "100%", maxWidth: 400 }}>
            <h1 style={{ fontSize: 32, fontWeight: 800, color: "#111", letterSpacing: "-0.6px", marginBottom: 8 }}>
              Log in
            </h1>
            <p style={{ fontSize: 14, color: "#6b7280", marginBottom: 36 }}>
              Don't have an account?{" "}
              <Link to="/signup" style={{ color: "#1B4332", fontWeight: 600, textDecoration: "none" }}>Sign up</Link>
            </p>

            {error && (
              <div style={{
                padding: "10px 14px", borderRadius: 8, marginBottom: 20,
                fontSize: 13, background: "#fef2f2", border: "1px solid #fecaca", color: "#dc2626"
              }}>{error}</div>
            )}

            <form onSubmit={handleSubmit}>
              <div style={{ display: "flex", flexDirection: "column", gap: 18, marginBottom: 8 }}>
                <div>
                  <label className="field-label">Email</label>
                  <div className="input-wrapper">
                    <span className="input-icon">
                      <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <rect width="20" height="16" x="2" y="4" rx="2" /><path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7" />
                      </svg>
                    </span>
                    <input className="auth-input" name="email" type="email" placeholder="Enter your email" value={form.email} onChange={handleChange} />
                  </div>
                </div>
                <div>
                  <label className="field-label">Password</label>
                  <div className="input-wrapper">
                    <span className="input-icon">
                      <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <rect width="18" height="11" x="3" y="11" rx="2" /><path d="M7 11V7a5 5 0 0 1 10 0v4" />
                      </svg>
                    </span>
                    <input className="auth-input" style={{ paddingRight: 42 }} name="password" type={showPassword ? "text" : "password"} placeholder="Enter your password" value={form.password} onChange={handleChange} />
                    <button className="eye-toggle" type="button" onClick={() => setShowPassword(v => !v)}>
                      <EyeIcon open={showPassword} />
                    </button>
                  </div>
                </div>
              </div>

              <div style={{ textAlign: "right", marginBottom: 28 }}>
                <span style={{ fontSize: 13, color: "#1B4332", fontWeight: 600, cursor: "pointer" }}>Forgot password?</span>
              </div>

              <button type="submit" className="btn-green" disabled={loading}>
                {loading ? "Logging in..." : "Log in"}
                {!loading && (
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M5 12h14M12 5l7 7-7 7" />
                  </svg>
                )}
              </button>
            </form>

            <div style={{ display: "flex", alignItems: "center", gap: 12, margin: "24px 0 20px" }}>
              <div style={{ flex: 1, height: 1, background: "#e5e7eb" }} />
              <span style={{ fontSize: 13, color: "#9ca3af", whiteSpace: "nowrap" }}>or continue with</span>
              <div style={{ flex: 1, height: 1, background: "#e5e7eb" }} />
            </div>

            <div style={{ display: "flex", justifyContent: "center" }}>
              <GoogleLogin
                onSuccess={handleGoogleSuccess}
                onError={() => setError("Google login failed.")}
                width={400}
                theme="outline"
                size="large"
                text="continue_with"
                shape="rectangular"
              />
            </div>
          </div>
        </div>
        </div> {/* content row */}
      </div>
    </>
  )
}

export default Login
