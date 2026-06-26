import { Download, FileText, Loader2, Sparkles } from "lucide-react";
import { useState } from "react";
import { createRoot } from "react-dom/client";
import "./styles.css";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

function App() {
  const [form, setForm] = useState({
    topic: "Artificial Intelligence in Education",
    slide_count: 8,
    audience: "college students",
    tone: "clear and practical",
    theme: "modern",
  });
  const [status, setStatus] = useState("idle");
  const [error, setError] = useState("");

  const updateField = (field, value) => {
    setForm((current) => ({ ...current, [field]: value }));
  };

  const generateDeck = async (event) => {
    event.preventDefault();
    setStatus("loading");
    setError("");

    try {
      const response = await fetch(`${API_URL}/api/generate-ppt`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          ...form,
          slide_count: Number(form.slide_count),
        }),
      });

      if (!response.ok) {
        throw new Error("Presentation generate nahi ho payi. Backend check karo.");
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = `${form.topic.toLowerCase().replace(/[^a-z0-9]+/g, "-") || "presentation"}.pptx`;
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      setStatus("success");
    } catch (caughtError) {
      setError(caughtError.message);
      setStatus("error");
    }
  };

  return (
    <main className="app-shell">
      <section className="workspace">
        <div className="intro">
          <div className="brand-row">
            <span className="brand-mark">
              <Sparkles size={22} />
            </span>
            <span>AI PPT Slide Generator</span>
          </div>
          <h1>Prompt se editable PowerPoint deck banao.</h1>
          <p>
            Topic, audience aur tone select karo. Backend AI outline banata hai aur `.pptx`
            file download ke liye ready kar deta hai.
          </p>
        </div>

        <form className="generator-panel" onSubmit={generateDeck}>
          <label>
            Topic
            <textarea
              value={form.topic}
              onChange={(event) => updateField("topic", event.target.value)}
              rows={3}
              required
            />
          </label>

          <div className="grid-two">
            <label>
              Slides
              <input
                type="number"
                min="3"
                max="15"
                value={form.slide_count}
                onChange={(event) => updateField("slide_count", event.target.value)}
              />
            </label>
            <label>
              Theme
              <select value={form.theme} onChange={(event) => updateField("theme", event.target.value)}>
                <option value="modern">Modern</option>
                <option value="dark">Dark</option>
                <option value="warm">Warm</option>
              </select>
            </label>
          </div>

          <label>
            Audience
            <input value={form.audience} onChange={(event) => updateField("audience", event.target.value)} />
          </label>

          <label>
            Tone
            <input value={form.tone} onChange={(event) => updateField("tone", event.target.value)} />
          </label>

          <button type="submit" disabled={status === "loading"}>
            {status === "loading" ? <Loader2 className="spin" size={18} /> : <Download size={18} />}
            Generate PPT
          </button>

          {error && <p className="error">{error}</p>}
          {status === "success" && <p className="success">Deck download ho gaya.</p>}
        </form>
      </section>

      <aside className="preview-strip">
        <div className="mini-slide title-slide">
          <FileText size={24} />
          <strong>{form.topic || "Presentation Topic"}</strong>
          <span>{form.audience}</span>
        </div>
        <div className="mini-slide">
          <strong>Overview</strong>
          <span>Key context</span>
          <span>Benefits</span>
          <span>Challenges</span>
        </div>
        <div className="mini-slide">
          <strong>Conclusion</strong>
          <span>Recommendations</span>
          <span>Next steps</span>
        </div>
      </aside>
    </main>
  );
}

createRoot(document.getElementById("root")).render(<App />);
