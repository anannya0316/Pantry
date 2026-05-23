import { useNavigate } from "react-router-dom"

const LeafIcon = ({ size = 20, color = "#2E7D32" }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
    <path d="M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.48 19 2c1 2 2 4.18 2 8 0 5.5-4.78 10-10 10z" />
    <path d="M2 21c0-3 1.85-5.36 5.08-6C9.5 14.52 12 13 13 12" />
  </svg>
)

const Avatar = ({ color, zIndex }) => (
  <div style={{
    width: 36, height: 36,
    borderRadius: "50%",
    background: color,
    border: "2.5px solid white",
    marginLeft: -10,
    zIndex,
    display: "flex", alignItems: "center", justifyContent: "center",
    overflow: "hidden"
  }}>
    <svg width="18" height="18" viewBox="0 0 24 24" fill="rgba(255,255,255,0.9)">
      <path d="M12 12c2.7 0 4.8-2.1 4.8-4.8S14.7 2.4 12 2.4 7.2 4.5 7.2 7.2 9.3 12 12 12zm0 2.4c-3.2 0-9.6 1.6-9.6 4.8v2.4h19.2v-2.4c0-3.2-6.4-4.8-9.6-4.8z" />
    </svg>
  </div>
)

export default function LandingPage() {
  const navigate = useNavigate()

  return (
    <div style={{
      minHeight: "100vh",
      background: "#f5f7f2",
      fontFamily: "'DM Sans', sans-serif",
      overflow: "hidden",
      position: "relative"
    }}>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700;0,9..40,800&display=swap');
        * { box-sizing: border-box; margin: 0; padding: 0; }
        .nav-btn { transition: opacity 0.15s; }
        .nav-btn:hover { opacity: 0.85; }
        .cta-btn { transition: transform 0.15s, opacity 0.15s; }
        .cta-btn:hover { transform: translateY(-1px); opacity: 0.92; }
      `}</style>

      {/* Background image — same shape as the old green blob */}
      <img
        src="/pantry.png"
        alt=""
        style={{
          position: "absolute",
          top: "-8%",
          right: 0,
          width: "54%",
          height: "115%",
          objectFit: "cover",
          objectPosition: "center",
          borderRadius: "48% 0 0 48%",
          zIndex: 0
        }}
      />

      {/* Navbar */}
      <nav style={{
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
        padding: "22px 52px",
        position: "relative",
        zIndex: 10
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <div style={{
            width: 38, height: 38,
            background: "#E4F2DB",
            border: "1px solid #c6deb0",
            borderRadius: 10,
            display: "flex", alignItems: "center", justifyContent: "center"
          }}>
            <LeafIcon size={20} color="#2E7D32" />
          </div>
          <span style={{ fontSize: 18, fontWeight: 700, color: "#0f1a0e", letterSpacing: "-0.3px" }}>Pantry</span>
        </div>

        <div style={{ display: "flex", gap: 10 }}>
          <button
            className="nav-btn"
            onClick={() => navigate("/login")}
            style={{
              padding: "10px 22px",
              background: "white",
              border: "none",
              borderRadius: 8,
              fontSize: 14,
              fontWeight: 500,
              color: "#111",
              cursor: "pointer",
              fontFamily: "inherit"
            }}
          >
            Log in
          </button>
          <button
            className="nav-btn"
            onClick={() => navigate("/signup")}
            style={{
              padding: "10px 22px",
              background: "#1B4332",
              border: "none",
              borderRadius: 8,
              fontSize: 14,
              fontWeight: 600,
              color: "white",
              cursor: "pointer",
              fontFamily: "inherit"
            }}
          >
            Get Started
          </button>
        </div>
      </nav>

      {/* Hero */}
      <div style={{
        display: "flex",
        alignItems: "center",
        paddingLeft: 120,
        paddingTop: 30,
        paddingBottom: 60,
        position: "relative",
        zIndex: 1,
        minHeight: "calc(100vh - 84px)"
      }}>
        {/* Left content */}
        <div style={{ flex: "0 0 44%", paddingRight: 48 }}>
          {/* Badge */}
          <div style={{
            display: "inline-flex",
            alignItems: "center",
            gap: 7,
            background: "#E4F2DB",
            border: "1px solid #c6deb0",
            borderRadius: 100,
            padding: "7px 16px",
            marginBottom: 30
          }}>
            <LeafIcon size={13} color="#2E7D32" />
            <span style={{ fontSize: 13, color: "#2E7D32", fontWeight: 500 }}>Your smart kitchen companion</span>
          </div>

          {/* Heading */}
          <h1 style={{
            fontSize: "clamp(40px, 4.5vw, 58px)",
            fontWeight: 800,
            lineHeight: 1.1,
            color: "#0d1a0d",
            marginBottom: 22,
            letterSpacing: "-1.5px",
            fontFamily: "'DM Sans', sans-serif"
          }}>
            Smarter cooking<br />starts with<br />
            <span style={{ color: "#2E7D32" }}>what you have.</span>
          </h1>

          {/* Subtitle */}
          <p style={{
            fontSize: 16,
            color: "#6b7280",
            lineHeight: 1.65,
            marginBottom: 38,
            maxWidth: 400,
            fontWeight: 400
          }}>
            Pantry helps you track ingredients, discover recipes, and make healthier choices every day.
          </p>

          {/* CTA */}
          <button
            className="cta-btn"
            onClick={() => navigate("/signup")}
            style={{
              display: "inline-flex",
              alignItems: "center",
              gap: 12,
              background: "#1B4332",
              color: "white",
              border: "none",
              borderRadius: 12,
              padding: "16px 36px",
              fontSize: 16,
              fontWeight: 600,
              cursor: "pointer",
              marginBottom: 36,
              fontFamily: "inherit",
              letterSpacing: "-0.2px"
            }}
          >
            Get Started
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M5 12h14M12 5l7 7-7 7" />
            </svg>
          </button>

          {/* Social proof */}
          <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
          </div>
        </div>

        {/* Right spacer — image fills this area via the background clip */}
        <div style={{ flex: 1 }} />
      </div>
    </div>
  )
}
