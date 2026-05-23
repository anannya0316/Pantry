import { useState, useEffect } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";
import { getProfile } from "../services/api";

const LeafIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#2E7D32" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
    <path d="M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.48 19 2c1 2 2 4.18 2 8 0 5.5-4.78 10-10 10z" />
    <path d="M2 21c0-3 1.85-5.36 5.08-6C9.5 14.52 12 13 13 12" />
  </svg>
)

const BasketIcon = () => (
  <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#1B4332" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M6 2 3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4z"/><line x1="3" y1="6" x2="21" y2="6"/><path d="M16 10a4 4 0 0 1-8 0"/>
  </svg>
)

const foodItems = {
  veg: [
    { icon: "/noun-tomato-7967282.svg",    name: "Tomatoes" },
    { icon: "/noun-lettuce-8313885.svg",   name: "Lettuce" },
    { icon: "/noun-carrot-2996726.svg",    name: "Carrots" },
    { icon: "/noun-broccoli-5234393.svg",  name: "Broccoli" },
    { icon: "/noun-potato-8351315.svg",    name: "Potatoes" },
    { icon: "/noun-onion-8374667.svg",     name: "Onions" },
    { icon: "/noun-capsicum-3019287.svg",  name: "Bell Peppers" },
    { icon: "/noun-cucumber-7489409.svg",  name: "Cucumbers" },
    { icon: "/noun-apple-71043.svg",       name: "Apples" },
    { icon: "/noun-banana-8381896.svg",    name: "Bananas" },
    { icon: "/noun-orange-3376433.svg",    name: "Oranges" },
    { icon: "/noun-berries-8362293.svg",   name: "Berries" },
    { icon: "/noun-grapes-1286196.svg",    name: "Grapes" },
    { icon: "/noun-avocado-3126624.svg",   name: "Avocado" },
    { icon: "/noun-egg-7992083.svg",       name: "Eggs" },
    { icon: "/noun-bean-8345930.svg",      name: "Beans" },
    { icon: "/noun-milk-8053511.svg",      name: "Milk" },
    { icon: "/noun-cheese-2819022.svg",    name: "Cheese" },
    { icon: "/noun-yogurt-8011170.svg",    name: "Yogurt" },
    { icon: "/noun-butter-8134436.svg",    name: "Butter" },
    { icon: "/noun-rice-8381967.svg",      name: "Rice" },
    { icon: "/noun-pasta-7827011.svg",     name: "Pasta" },
    { icon: "/noun-bread-8273560.svg",     name: "Bread" },
    { icon: "/noun-oats-6878311.svg",      name: "Oats" },
  ],
  non_veg: [
    { icon: "/noun-tomato-7967282.svg",    name: "Tomatoes" },
    { icon: "/noun-lettuce-8313885.svg",   name: "Lettuce" },
    { icon: "/noun-carrot-2996726.svg",    name: "Carrots" },
    { icon: "/noun-broccoli-5234393.svg",  name: "Broccoli" },
    { icon: "/noun-potato-8351315.svg",    name: "Potatoes" },
    { icon: "/noun-onion-8374667.svg",     name: "Onions" },
    { icon: "/noun-capsicum-3019287.svg",  name: "Bell Peppers" },
    { icon: "/noun-cucumber-7489409.svg",  name: "Cucumbers" },
    { icon: "/noun-apple-71043.svg",       name: "Apples" },
    { icon: "/noun-banana-8381896.svg",    name: "Bananas" },
    { icon: "/noun-orange-3376433.svg",    name: "Oranges" },
    { icon: "/noun-berries-8362293.svg",   name: "Berries" },
    { icon: "/noun-grapes-1286196.svg",    name: "Grapes" },
    { icon: "/noun-avocado-3126624.svg",   name: "Avocado" },
    { icon: "/noun-chicken-8360430.svg",   name: "Chicken" },
    { icon: "/noun-beef-8374675.svg",      name: "Beef" },
    { icon: "/noun-fish-367762.svg",       name: "Fish" },
    { icon: "/noun-egg-7992083.svg",       name: "Eggs" },
    { icon: "/noun-bean-8345930.svg",      name: "Beans" },
    { icon: "/noun-milk-8053511.svg",      name: "Milk" },
    { icon: "/noun-cheese-2819022.svg",    name: "Cheese" },
    { icon: "/noun-yogurt-8011170.svg",    name: "Yogurt" },
    { icon: "/noun-butter-8134436.svg",    name: "Butter" },
    { icon: "/noun-rice-8381967.svg",      name: "Rice" },
    { icon: "/noun-pasta-7827011.svg",     name: "Pasta" },
    { icon: "/noun-bread-8273560.svg",     name: "Bread" },
    { icon: "/noun-oats-6878311.svg",      name: "Oats" },
  ],
};

const goalsList = [
  { icon: "/noun-healthy-7975861.svg",       name: "Eat healthier", desc: "Make better food choices and nourish your body.",         color: "#e8f5e9" },
  { icon: "/noun-money-save-7779458.svg",    name: "Save money",    desc: "Plan smarter and reduce food waste to save more.",        color: "#fce4ec" },
  { icon: "/noun-fast-6719283.svg",          name: "Cook faster",   desc: "Find quick recipes and spend less time in the kitchen.", color: "#fff3e0" },
  { icon: "/noun-muscle-8107841.svg",        name: "Gain muscle",   desc: "Find high-protein meals to support your goals.",         color: "#fff8e1" },
  { icon: "/noun-weight-check-3039725.svg",  name: "Lose weight",   desc: "Discover balanced meals and portion control tips.",      color: "#f3e5f5" },
];

export default function GettingStarted() {
  const navigate = useNavigate();
  const [step, setStep] = useState(1);
  const [selectedFoods, setSelectedFoods] = useState([]);
  const [selectedGoals, setSelectedGoals] = useState([]);
  const [preference, setPreference] = useState("veg");
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    const userId = localStorage.getItem("userId");
    if (!userId) return;
    getProfile(userId).then(profile => setPreference(profile.diet || "veg"));
  }, []);

  const availableFoods = foodItems[preference] || foodItems.veg;

  const toggleFood = (name) => {
    if (selectedFoods.includes(name)) {
      setSelectedFoods(selectedFoods.filter(f => f !== name));
    } else if (selectedFoods.length < 5) {
      setSelectedFoods([...selectedFoods, name]);
    }
  };

  const toggleGoal = (name) => {
    setSelectedGoals(prev =>
      prev.includes(name) ? prev.filter(g => g !== name) : [...prev, name]
    );
  };

  const handleComplete = async () => {
    setSaving(true);
    try {
      const userId = localStorage.getItem("userId");
      await axios.post(
        `${import.meta.env.VITE_API_URL || "http://localhost:8000"}/auth/complete-onboarding`,
        { household_items: selectedFoods, goals: selectedGoals },
        { headers: { "user-id": userId } }
      );
navigate("/dashboard");
    } catch (err) {
      console.error(err);
      alert("Failed to save preferences");
      setSaving(false);
    }
  };

  const steps = [
    { n: 1, label: "Your staples" },
    { n: 2, label: "Your goals" },
  ];

  return (
    <div style={{ minHeight: "100vh", background: "#fff", fontFamily: "'DM Sans', sans-serif", display: "flex", flexDirection: "column", position: "relative" }}>
      <style>{`@import url('https://fonts.googleapis.com/css2?family=DM+Sans:opsz,wght@9..40,400;9..40,500;9..40,600;9..40,700;9..40,800&display=swap'); * { box-sizing: border-box; margin: 0; padding: 0; } button, input, select, textarea { font-family: 'DM Sans', sans-serif; }`}</style>


      {/* Navbar */}
      <nav style={{
        display: "flex", alignItems: "center", justifyContent: "space-between",
        padding: "0 52px", height: 68, flexShrink: 0, background: "#fff",
        position: "relative", zIndex: 1
      }}>
        {/* Logo */}
        <div style={{ display: "flex", alignItems: "center", gap: 9, minWidth: 120 }}>
          <div style={{
            width: 36, height: 36, background: "#E4F2DB", border: "1px solid #c6deb0",
            borderRadius: 9, display: "flex", alignItems: "center", justifyContent: "center"
          }}>
            <LeafIcon />
          </div>
          <span style={{ fontSize: 17, fontWeight: 700, color: "#1a2e1a" }}>Pantry</span>
        </div>

        {/* Step tabs */}
        <div style={{ display: "flex", alignItems: "center", gap: 0 }}>
          {steps.map(({ n, label }, i) => (
            <div key={n} style={{ display: "flex", alignItems: "center" }}>
              <div style={{
                display: "flex", alignItems: "center", gap: 10,
                padding: "0 24px", height: 68,
                borderBottom: "none",
                cursor: n < step ? "pointer" : "default"
              }} onClick={() => n < step && setStep(n)}>
                <div style={{
                  width: 26, height: 26, borderRadius: "50%",
                  background: step >= n ? "#206c1b" : "#fff",
                  border: step >= n ? "none" : "1.5px solid #d0d5c8",
                  display: "flex", alignItems: "center", justifyContent: "center",
                  fontSize: 12, fontWeight: 700,
                  color: step >= n ? "#fff" : "#9ca3af",
                  flexShrink: 0
                }}>{n}</div>
                <span style={{
                  fontSize: 14, fontWeight: step === n ? 600 : 400,
                  color: step === n ? "#206c1b" : "#9ca3af",
                  whiteSpace: "nowrap"
                }}>{label}</span>
              </div>
              {i < steps.length - 1 && (
                <div style={{ width: 48, height: 1.5, background: step > n ? "#206c1b" : "#e0e0da" }} />
              )}
            </div>
          ))}
        </div>

        <div style={{ minWidth: 120 }} />
      </nav>

      {/* Content */}
      <div style={{ flex: 1, overflowY: "auto", position: "relative", zIndex: 1 }}>
        <div style={{ maxWidth: 1120, margin: "0 auto", padding: "48px 12px 24px" }}>

          {step === 1 && (
            <>
              <h1 style={{ fontSize: 32, fontWeight: 800, color: "#0d1a0d", letterSpacing: "-0.6px", marginBottom: 8 }}>
                What do you usually have at home?
              </h1>
              <p style={{ fontSize: 15, color: "#6b7280", marginBottom: 36 }}>
                Select <strong style={{ color: "#1B4332" }}>5</strong> things you keep in your fridge regularly
              </p>

              <div style={{
                display: "grid",
                gridTemplateColumns: "repeat(7, 1fr)",
                gap: 10
              }}>
                {availableFoods.map((item) => {
                  const selected = selectedFoods.includes(item.name);
                  const disabled = !selected && selectedFoods.length >= 5;
                  return (
                    <button
                      key={item.name}
                      onClick={() => toggleFood(item.name)}
                      style={{
                        position: "relative",
                        background: selected ? "#f6f7f0" : "#fff",
                        border: selected ? "1.5px solid #206c1b" : "1.5px solid #e8ede2",
                        borderRadius: 12, padding: "22px 12px 16px",
                        cursor: disabled ? "not-allowed" : "pointer",
                        display: "flex", flexDirection: "column", alignItems: "center", gap: 12,
                        transition: "border-color 0.15s, background 0.15s",
                        opacity: disabled ? 0.4 : 1
                      }}
                    >
                      {selected && (
                        <div style={{
                          position: "absolute", top: 8, right: 8,
                          width: 22, height: 22, borderRadius: "50%",
                          background: "#206c1b",
                          display: "flex", alignItems: "center", justifyContent: "center"
                        }}>
                          <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="3.5" strokeLinecap="round" strokeLinejoin="round">
                            <polyline points="20 6 9 17 4 12" />
                          </svg>
                        </div>
                      )}
                      <img
                        src={item.icon}
                        alt={item.name}
                        style={{
                          width: 48, height: 48, objectFit: "contain",
                          filter: "brightness(0) saturate(100%) invert(18%) sepia(50%) saturate(600%) hue-rotate(115deg) brightness(90%)"
                        }}
                      />
                      <span style={{ fontSize: 13, fontWeight: 500, color: selected ? "#206c1b" : "#374151", textAlign: "center", lineHeight: 1.3 }}>
                        {item.name}
                      </span>
                    </button>
                  );
                })}
              </div>
            </>
          )}

          {step === 2 && (
            <>
              <h1 style={{ fontSize: 32, fontWeight: 800, color: "#0d1a0d", letterSpacing: "-0.6px", marginBottom: 8 }}>
                What are you trying to do right now?
              </h1>
              <p style={{ fontSize: 15, color: "#6b7280", marginBottom: 36 }}>
                Select all that apply. We'll personalize everything for you.
              </p>

              <div style={{ display: "grid", gridTemplateColumns: "repeat(5, 1fr)", gap: 14 }}>
                {goalsList.map((goal) => {
                  const selected = selectedGoals.includes(goal.name);
                  return (
                    <button
                      key={goal.name}
                      onClick={() => toggleGoal(goal.name)}
                      style={{
                        background: selected ? "#f6f7f0" : "#fff",
                        border: selected ? "2px solid #206c1b" : "1.5px solid #e8ede2",
                        borderRadius: 16, padding: "32px 20px 28px",
                        cursor: "pointer", textAlign: "center",
                        display: "flex", flexDirection: "column", alignItems: "center", gap: 14,
                        minHeight: 280,
                        transition: "border-color 0.15s",
                      }}
                    >
                      <div style={{
                        width: 72, height: 72, borderRadius: "50%",
                        background: "#f6f7f0",
                        display: "flex", alignItems: "center", justifyContent: "center",
                      }}>
                        <img src={goal.icon} alt={goal.name} style={{ width: 38, height: 38, objectFit: "contain", filter: "brightness(0) saturate(100%) invert(28%) sepia(40%) saturate(700%) hue-rotate(90deg) brightness(85%)" }} />
                      </div>
                      <div style={{ flex: 1 }}>
                        <div style={{ fontSize: 15, fontWeight: 700, color: "#0d1a0d", marginBottom: 8 }}>{goal.name}</div>
                        <div style={{ fontSize: 13, color: "#6b7280", lineHeight: 1.6 }}>{goal.desc}</div>
                      </div>
                      <div style={{
                        width: 22, height: 22, borderRadius: 6,
                        background: selected ? "#206c1b" : "#fff",
                        border: selected ? "none" : "1.5px solid #d1d5db",
                        display: "flex", alignItems: "center", justifyContent: "center",
                      }}>
                        {selected && (
                          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="3.5" strokeLinecap="round" strokeLinejoin="round">
                            <polyline points="20 6 9 17 4 12" />
                          </svg>
                        )}
                      </div>
                    </button>
                  );
                })}
              </div>
            </>
          )}

        {step === 1 ? (
          <div style={{
            marginTop: 36,
            background: "#f5f6f1", border: "1px solid #e8ede2",
            borderRadius: 16, padding: "14px 20px",
            display: "flex", alignItems: "center", justifyContent: "space-between",
          }}>
            <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
              <div style={{
                width: 44, height: 44, borderRadius: 12,
                background: "#E4F2DB", border: "1px solid #c6deb0",
                display: "flex", alignItems: "center", justifyContent: "center"
              }}>
                <BasketIcon />
              </div>
              <div>
                <div style={{ fontSize: 14, fontWeight: 700, color: "#1B4332" }}>
                  {selectedFoods.length} of 5 selected
                </div>
                <div style={{ fontSize: 13, color: "#6b7280" }}>
                  Pick 5 items to help us personalize your experience.
                </div>
              </div>
            </div>
            <button
              onClick={() => setStep(2)}
              disabled={selectedFoods.length !== 5}
              style={{
                display: "flex", alignItems: "center", gap: 10,
                height: 48, padding: "0 28px",
                background: selectedFoods.length === 5 ? "#206c1b" : "#d1d5db",
                color: "#fff", border: "none", borderRadius: 12,
                fontSize: 15, fontWeight: 600, cursor: selectedFoods.length === 5 ? "pointer" : "not-allowed",
                fontFamily: "'DM Sans', sans-serif", transition: "background 0.15s"
              }}
            >
              Continue
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M5 12h14M12 5l7 7-7 7" />
              </svg>
            </button>
          </div>
        ) : (
          <>
            {/* Info strip */}
            <div style={{
              marginTop: 36,
              background: "#f5f6f1", border: "1px solid #e8ede2",
              borderRadius: 16, padding: "16px 24px",
              display: "flex", alignItems: "center", gap: 14,
            }}>
              <div style={{
                width: 40, height: 40, borderRadius: 10,
                background: "#E4F2DB", border: "1px solid #c6deb0",
                display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0
              }}>
                <LeafIcon />
              </div>
              <span style={{ fontSize: 14, color: "#4b5563" }}>
                Your goals help us tailor recipes, meal plans, and insights that truly fit your lifestyle.
              </span>
            </div>

            {/* Back / Get Started */}
            <div style={{ marginTop: 20, display: "flex", alignItems: "center", justifyContent: "space-between" }}>
              <button
                onClick={() => setStep(1)}
                style={{
                  display: "flex", alignItems: "center", gap: 8,
                  height: 48, padding: "0 24px",
                  background: "#fff", border: "1.5px solid #e8ede2", borderRadius: 12,
                  fontSize: 15, fontWeight: 500, color: "#374151",
                  cursor: "pointer", fontFamily: "'DM Sans', sans-serif"
                }}
              >
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M19 12H5M12 19l-7-7 7-7" />
                </svg>
                Back
              </button>
              <button
                onClick={handleComplete}
                disabled={saving}
                style={{
                  display: "flex", alignItems: "center", gap: 10,
                  height: 48, padding: "0 28px",
                  background: "#206c1b", color: "#fff", border: "none", borderRadius: 12,
                  fontSize: 15, fontWeight: 600, cursor: saving ? "not-allowed" : "pointer",
                  fontFamily: "'DM Sans', sans-serif", opacity: saving ? 0.7 : 1
                }}
              >
                {saving ? "Setting up..." : "Get Started"}
                {!saving && (
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M5 12h14M12 5l7 7-7 7" />
                  </svg>
                )}
              </button>
            </div>
          </>
        )}

        </div>{/* content inner */}
      </div>{/* scroll wrapper */}
    </div>
  );
}
