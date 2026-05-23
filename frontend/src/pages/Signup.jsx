import { useState, useEffect } from "react";
import axios from "axios";
import { useNavigate, Link } from "react-router-dom";
import { GoogleLogin } from "@react-oauth/google";
import { googleAuth } from "../services/api";

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

function StepIndicator({ step }) {
  return (
    <div style={{ display: "flex", alignItems: "flex-start", marginBottom: 32 }}>
      {[{ n: 1, label: "Account" }, { n: 2, label: "Preferences" }].map(({ n, label }, i) => (
        <div key={n} style={{ display: "flex", alignItems: "flex-start", flex: i === 0 ? 1 : "none" }}>
          <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 6 }}>
            <div style={{
              width: 34, height: 34, borderRadius: "50%",
              background: step === n ? "#1B4332" : "white",
              border: step === n ? "none" : "1.5px solid #d0d5c8",
              display: "flex", alignItems: "center", justifyContent: "center",
              fontSize: 13, fontWeight: 600,
              color: step === n ? "white" : "#9ca3af", flexShrink: 0
            }}>{n}</div>
            <span style={{ fontSize: 12, fontWeight: 500, color: step === n ? "#1B4332" : "#9ca3af", whiteSpace: "nowrap" }}>
              {label}
            </span>
          </div>
          {i === 0 && (
            <div style={{
              flex: 1, height: 1.5, background: step === 2 ? "#1B4332" : "#e0e0da",
              marginTop: 17, marginLeft: 8, marginRight: 8
            }} />
          )}
        </div>
      ))}
    </div>
  )
}

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
  .auth-select {
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='%23b0b0b0' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='m6 9 6 6 6-6'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 14px center;
}
  .custom-select-container {
  position: relative;
  width: 100%;
}

.custom-select-list {
  position: absolute;
  top: 105%;
  left: 0;
  width: 100%;
  background: white;
  border: 1.5px solid #e8ede2;
  border-radius: 10px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.05);
  z-index: 10;
  overflow: hidden;
  padding: 4px;
}

.custom-option {
  padding: 10px 14px;
  font-size: 14px;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.2s;
}

/* This is the light green hover you wanted */
.custom-option:hover {
  background-color: #E4F2DB; 
  color: #1B4332;
}
  .auth-select:hover {
  background-color: #f0f4ed; /* Your light green bg */
  border-color: #1B4332;
}

.auth-select option:hover,
.auth-select option:focus,
.auth-select option:active {
  background-color: #E4F2DB !important; 
  color: #1B4332 !important;
}
  .auth-select {
    width: 100%; height: 50px; padding: 0 14px 0 44px;
    background: #f7f8f5; border: 1.5px solid #e8ede2;
    border-radius: 10px; font-size: 14px; font-family: 'DM Sans', sans-serif;
    color: #111; outline: none; cursor: pointer; -webkit-appearance: none;
    transition: border-color 0.15s, background 0.15s;
  }
  .auth-select:focus { background: #fff; border-color: #1B4332; }
  .btn-green {
    width: 100%; height: 52px; background: #1B4332; color: #fff; border: none;
    border-radius: 12px; font-size: 15px; font-weight: 600; font-family: 'DM Sans', sans-serif;
    cursor: pointer; display: flex; align-items: center; justify-content: center; gap: 10px;
    transition: opacity 0.15s, transform 0.1s;
  }
  .btn-green:hover { opacity: 0.9; }
  .btn-green:active { transform: scale(0.99); }
`

export default function Signup() {
  const navigate = useNavigate();
  const [step, setStep] = useState(1);
  const [showPassword, setShowPassword] = useState(false);
  const [googleCredential, setGoogleCredential] = useState(null);
  const [form, setForm] = useState({
    name: "", email: "", password: "",
    phone: "", household_size: "", preferences: "veg", cooking_frequency: "daily", grocery_shopping_day: "Sunday"
  });
  const [isPrefOpen, setIsPrefOpen] = useState(false);
  const [isFreqOpen, setIsFreqOpen] = useState(false);
  const [isRestockOpen, setIsRestockOpen] = useState(false);
  const [error, setError] = useState("");
  const handleChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  useEffect(() => {
    if (step !== 3) return
    const interval = setInterval(async () => {
      try {
        const res = await axios.get(`${import.meta.env.VITE_API_URL || "http://localhost:8000"}/auth/check-verification?email=${encodeURIComponent(form.email)}`)
        if (res.data.verified) {
          localStorage.setItem("userId", res.data.user_id)
          navigate("/getting-started")
        }
      } catch {}
    }, 2000)
    return () => clearInterval(interval)
  }, [step])

  const handleStep1 = () => {
    if (!form.name || !form.email || !form.password || !form.phone) { setError("Please fill in all fields"); return; }
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email)) { setError("Please enter a valid email address"); return; }
    if (form.password.length < 7) { setError("Password must be at least 7 characters long"); return; }
    if (!/^[0-9]{10}$/.test(form.phone)) { setError("Phone number must be exactly 10 digits"); return; }
    setError(""); setStep(2);
  };

  const handleGoogleSuccess = ({ credential }) => {
    setError("");
    setGoogleCredential(credential);
    setStep(2);
  };

  const handleSubmit = async () => {
    if (!form.household_size) { setError("Please fill in all fields"); return; }
    try {
      setError("");
      if (googleCredential) {
        const res = await googleAuth(googleCredential, "signup", {
          household_size: Number(form.household_size),
          preferences: form.preferences,
          cooking_frequency: form.cooking_frequency,
          grocery_shopping_day: form.grocery_shopping_day
        });
        if (res.detail) { setError(res.detail); return; }
        if (!res.access_token) { setError("Sign-up failed. Please try again."); return; }
        localStorage.setItem("token", res.access_token);
        localStorage.setItem("userId", res.user_id);
        navigate("/getting-started");
      } else {
        await axios.post(`${import.meta.env.VITE_API_URL || "http://localhost:8000"}/auth/create-account`, {
          email: form.email, password: form.password, name: form.name,
          phone: form.phone, household_size: Number(form.household_size),
          diet: form.preferences, cooking_frequency: form.cooking_frequency,
          grocery_shopping_day: form.grocery_shopping_day
        });
        setStep(3);
      }
    } catch (err) {
      setError(err.response?.data?.detail || err.message || "Signup failed. Please try again.");
    }
  };

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
                fontSize: 38, fontWeight: 800, lineHeight: 1.2,
                color: "#1a2e1a", letterSpacing: "-0.8px", marginBottom: 14
              }}>
                {step === 1 ? (
                  <>Create your<br /><span style={{ color: "#2E7D32" }}>Pantry</span> account</>
                ) : (
                  <>Your<br /><span style={{ color: "#2E7D32" }}>preferences</span></>
                )}
              </h2>
              <p style={{ fontSize: 15, color: "#5a7a5a", lineHeight: 1.6, maxWidth: 260 }}>
                {step === 1
                  ? "Let's get you started on a healthier cooking journey."
                  : "Help us personalise your Pantry experience."}
              </p>
            </div>
            <div style={{ flex: 1 }} />
            <img
              src="/signup.png"
              alt=""
              style={{ width: "100%", display: "block", objectFit: "cover", objectPosition: "center top", maxHeight: "70%" }}
            />
          </div>

          {/* Right panel */}
          <div style={{
            flex: 1, background: "#fff",
            display: "flex", alignItems: "center", justifyContent: "center",
            padding: "48px 64px"
          }}>
          <div style={{ width: "100%", maxWidth: 420 }}>
            {step < 3 && <StepIndicator step={step} />}

            {step < 3 && (
              <>
                <h1 style={{ fontSize: 28, fontWeight: 800, color: "#111", letterSpacing: "-0.5px", marginBottom: 6 }}>
                  {step === 1 ? "Create Account" : "Set Preferences"}
                </h1>
                <p style={{ fontSize: 14, color: "#6b7280", marginBottom: 28 }}>
                  {step === 1 ? (
                    <>Already have an account? <Link to="/login" style={{ color: "#1B4332", fontWeight: 600, textDecoration: "none" }}>Log in</Link></>
                  ) : (
                    <button onClick={() => setStep(1)} style={{
                      background: "none", border: "none", color: "#1B4332", fontWeight: 600,
                      fontSize: 14, cursor: "pointer", padding: 0, fontFamily: "inherit"
                    }}>← Back to account</button>
                  )}
                </p>
              </>
            )}

            {error && step < 3 && (
              <div style={{
                padding: "10px 14px", borderRadius: 8, marginBottom: 20,
                fontSize: 13, background: "#fef2f2", border: "1px solid #fecaca", color: "#dc2626"
              }}>{error}</div>
            )}

            {step === 1 && (
              <>
                <div style={{ display: "flex", flexDirection: "column", gap: 14, marginBottom: 22 }}>
                  <div>
                    <label className="field-label">Full Name</label>
                    <div className="input-wrapper">
                      <span className="input-icon">
                        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                          <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" /><circle cx="12" cy="7" r="4" />
                        </svg>
                      </span>
                      <input className="auth-input" name="name" placeholder="Enter your full name" onChange={handleChange} />
                    </div>
                  </div>
                  <div>
                    <label className="field-label">Email</label>
                    <div className="input-wrapper">
                      <span className="input-icon">
                        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                          <rect width="20" height="16" x="2" y="4" rx="2" /><path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7" />
                        </svg>
                      </span>
                      <input className="auth-input" name="email" type="email" placeholder="Enter your email" onChange={handleChange} required />
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
                      <input className="auth-input" style={{ paddingRight: 42 }} name="password" type={showPassword ? "text" : "password"} placeholder="Create a password" onChange={handleChange} required minLength="7" />
                      <button className="eye-toggle" type="button" onClick={() => setShowPassword(v => !v)}><EyeIcon open={showPassword} /></button>
                    </div>
                  </div>
                  <div>
                    <label className="field-label">Phone Number</label>
                    <div className="input-wrapper">
                      <span className="input-icon">
                        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                          <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07A19.5 19.5 0 0 1 4.15 12 19.79 19.79 0 0 1 1.08 3.4 2 2 0 0 1 3.06 1.3h3a2 2 0 0 1 2 1.72c.127.96.361 1.903.7 2.81a2 2 0 0 1-.45 2.11L7.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45c.907.339 1.85.573 2.81.7A2 2 0 0 1 21 16.92z" />
                        </svg>
                      </span>
                      <input className="auth-input" name="phone" type="tel" placeholder="Enter 10-digit phone number" onChange={handleChange} required pattern="[0-9]{10}" title="Phone number must be exactly 10 digits" />
                    </div>
                  </div>
                </div>

                <button className="btn-green" onClick={handleStep1}>
                  Create Account
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M5 12h14M12 5l7 7-7 7" />
                  </svg>
                </button>

                <div style={{ display: "flex", alignItems: "center", gap: 12, margin: "24px 0 20px" }}>
                  <div style={{ flex: 1, height: 1, background: "#e5e7eb" }} />
                  <span style={{ fontSize: 13, color: "#9ca3af", whiteSpace: "nowrap" }}>or continue with</span>
                  <div style={{ flex: 1, height: 1, background: "#e5e7eb" }} />
                </div>

                <div style={{ display: "flex", justifyContent: "center" }}>
                  <GoogleLogin
                    onSuccess={handleGoogleSuccess}
                    onError={() => setError("Google sign-up failed.")}
                    width={420}
                    theme="outline"
                    size="large"
                    text="continue_with"
                    shape="rectangular"
                  />
                </div>
              </>
            )}

            {step === 2 && (
              <>
                <div style={{ display: "flex", flexDirection: "column", gap: 16, marginBottom: 28 }}>
                  <div>
                    <label className="field-label">Household Size</label>
                    <div className="input-wrapper">
                      <span className="input-icon">
                        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                          <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" /><circle cx="9" cy="7" r="4" /><path d="M23 21v-2a4 4 0 0 0-3-3.87" /><path d="M16 3.13a4 4 0 0 1 0 7.75" />
                        </svg>
                      </span>
                      <input className="auth-input" name="household_size" placeholder="e.g. 4" onChange={handleChange} />
                    </div>
                  </div>
                  <div>
                    <div>
                      <label className="field-label">Diet Preference</label>
                      <div style={{ position: "relative" }}>
                        {/* This looks like your input but is actually a clickable div */}
                        <div 
                          className="auth-input" 
                          style={{ 
                            display: "flex", 
                            alignItems: "center", 
                            cursor: "pointer",
                            paddingRight: "14px"
                          }}
                          onClick={() => setIsPrefOpen(!isPrefOpen)}
                        >
                          <span className="input-icon">
                            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                              <path d="M12 2a10 10 0 1 0 0 20 10 10 0 0 0 0-20z" /><path d="M12 8v4l3 3" />
                            </svg>
                          </span>
                          
                          {/* Dynamic text based on selection */}
                          {form.preferences === "veg" ? "Vegetarian" : "Non-Vegetarian"}

                          {/* Down arrow icon */}
                          <span style={{ marginLeft: "auto", fontSize: "10px", color: "#b0b0b0" }}>▼</span>
                        </div>

                        {/* The actual dropdown menu */}
                        {isPrefOpen && (
                          <div style={{
                            position: "absolute",
                            top: "110%",
                            left: 0,
                            width: "100%",
                            background: "white",
                            border: "1.5px solid #e8ede2",
                            borderRadius: "10px",
                            boxShadow: "0 10px 25px rgba(0,0,0,0.05)",
                            zIndex: 100,
                            padding: "4px",
                            overflow: "hidden"
                          }}>
                            <div 
                              className="custom-option"
                              onClick={() => {
                                setForm({ ...form, preferences: "veg" });
                                setIsPrefOpen(false);
                              }}
                            >
                              Vegetarian
                            </div>
                            <div 
                              className="custom-option"
                              onClick={() => {
                                setForm({ ...form, preferences: "non_veg" });
                                setIsPrefOpen(false);
                              }}
                            >
                              Non-Vegetarian
                            </div>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                  <div>
                    <label className="field-label">Cooking Frequency</label>
                    <div style={{ position: "relative" }}>
                      <div 
                        className="auth-input" 
                        style={{ display: "flex", alignItems: "center", cursor: "pointer", paddingRight: "14px" }}
                        onClick={() => setIsFreqOpen(!isFreqOpen)}
                      >
                        <span className="input-icon">
                          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                            <path d="M3 11l19-9-9 19-2-8-8-2z" />
                          </svg>
                        </span>

                        {/* Map the value to a readable label */}
                        {form.cooking_frequency === "daily" && "Daily"}
                        {form.cooking_frequency === "few_times" && "Few times a week"}
                        {form.cooking_frequency === "rarely" && "Rarely"}

                        <span style={{ marginLeft: "auto", fontSize: "10px", color: "#b0b0b0" }}>▼</span>
                      </div>

                      {isFreqOpen && (
                        <div style={{
                          position: "absolute", top: "110%", left: 0, width: "100%",
                          background: "white", border: "1.5px solid #e8ede2", borderRadius: "10px",
                          boxShadow: "0 10px 25px rgba(0,0,0,0.05)", zIndex: 100, padding: "4px"
                        }}>
                          {[
                            { value: "daily", label: "Daily" },
                            { value: "few_times", label: "Few times a week" },
                            { value: "rarely", label: "Rarely" }
                          ].map((option) => (
                            <div 
                              key={option.value}
                              className="custom-option"
                              onClick={() => {
                                setForm({ ...form, cooking_frequency: option.value });
                                setIsFreqOpen(false);
                              }}
                            >
                              {option.label}
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                </div>
                
                <div style={{ marginBottom: 28 }}>
                  <label className="field-label">Grocery Shopping Day</label>

                  <div style={{ position: "relative" }}>
                    <div
                      className="auth-input"
                      style={{
                        display: "flex",
                        alignItems: "center",
                        cursor: "pointer",
                        paddingRight: "14px"
                      }}
                      onClick={() => setIsRestockOpen(!isRestockOpen)}
                    >
                      <span className="input-icon">
                        🛒
                      </span>

                      {form.grocery_shopping_day}

                      <span
                        style={{
                          marginLeft: "auto",
                          fontSize: "10px",
                          color: "#b0b0b0"
                        }}
                      >
                        ▼
                      </span>
                    </div>

                    {isRestockOpen && (
                      <div
                        style={{
                          position: "absolute",
                          top: "110%",
                          left: 0,
                          width: "100%",
                          background: "white",
                          border: "1.5px solid #e8ede2",
                          borderRadius: "10px",
                          boxShadow: "0 10px 25px rgba(0,0,0,0.05)",
                          zIndex: 100,
                          padding: "4px"
                        }}
                      >
                        {[
                          "Monday",
                          "Tuesday",
                          "Wednesday",
                          "Thursday",
                          "Friday",
                          "Saturday",
                          "Sunday"
                        ].map((day) => (
                          <div
                            key={day}
                            className="custom-option"
                            onClick={() => {
                              setForm({
                                ...form,
                                grocery_shopping_day: day
                              });
                              setIsRestockOpen(false);
                            }}
                          >
                            {day}
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>

                <button className="btn-green" onClick={handleSubmit}>
                  Finish Setup
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M5 12h14M12 5l7 7-7 7" />
                  </svg>
                </button>
              </>
            )}

            {step === 3 && (
              <div style={{ textAlign: "center", padding: "16px 0" }}>
                <div style={{ width: 64, height: 64, borderRadius: "50%", background: "#E4F2DB", display: "flex", alignItems: "center", justifyContent: "center", margin: "0 auto 24px" }}>
                  <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#166534" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <rect width="20" height="16" x="2" y="4" rx="2" /><path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7" />
                  </svg>
                </div>
                <h2 style={{ fontSize: 22, fontWeight: 800, color: "#111", marginBottom: 10 }}>Check your inbox</h2>
                <p style={{ fontSize: 14, color: "#6b7280", lineHeight: 1.6, marginBottom: 8 }}>
                  We've sent a verification link to
                </p>
                <p style={{ fontSize: 14, fontWeight: 600, color: "#1B4332", marginBottom: 24 }}>{form.email}</p>
                <p style={{ fontSize: 13, color: "#9ca3af", lineHeight: 1.6 }}>
                  Click the link in the email to verify your address and create your account. The link expires in 24 hours.
                </p>
                <div style={{ marginTop: 28, padding: "14px 18px", background: "#f7fef7", border: "1px solid #e0f2e0", borderRadius: 10, fontSize: 13, color: "#374151", textAlign: "left" }}>
                  <strong style={{ color: "#166534" }}>Didn't get it?</strong> Check your spam folder, or{" "}
                  <button onClick={() => setStep(2)} style={{ background: "none", border: "none", color: "#1B4332", fontWeight: 600, cursor: "pointer", fontSize: 13, padding: 0, fontFamily: "inherit" }}>
                    go back and try again
                  </button>.
                </div>
              </div>
            )}
          </div>
        </div>
        </div> {/* content row */}
      </div>
    </>
  );
}
