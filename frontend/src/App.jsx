import { CheckCircle2, Download, FileText, Loader2, Sparkles, Wand2 } from "lucide-react";
import { useMemo, useState } from "react";
import { createRoot } from "react-dom/client";
import "./styles.css";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

const examples = [
  "AI tools for small businesses",
  "Startup pitch deck for a food delivery app",
  "Cybersecurity awareness for college students",
];

const themeLabels = {
  modern: "Modern",
  minimal: "Minimal",
  startup: "Startup",
  dark: "Dark",
  warm: "Warm",
};

function App() {
  const [form, setForm] = useState({
    topic: "Artificial Intelligence in Education",
    slide_count: 8,
    audience: "college students",
    tone: "educational",
    theme: "modern",
    language: "English",
    include_speaker_notes: true,
    extra_instructions: "Use simple examples and practical takeaways.",
  });
  const [status, setStatus] = useState("idle");
  const [previewStatus, setPreviewStatus] = useState("idle");
  const [error, setError] = useState("");
  const [deckPlan, setDeckPlan] = useState(null);

  const topicSlug = useMemo(
    () => form.topic.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "") || "presentation",
    [form.topic],
  );

  const updateField = (field, value) => {
    setForm((current) => ({ ...current, [field]: value }));
  };

  const requestBody = () => ({
    ...form,
    slide_count: Number(form.slide_count),
  });

  const previewDeck = async () => {
    setPreviewStatus("loading");
    setError("");
    try {
      const response = await fetch(`${API_URL}/api/preview-plan`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(requestBody()),
      });
      if (!response.ok) throw new Error("Preview generate nahi ho paya. Backend check karo.");
      setDeckPlan(await response.json());
      setPreviewStatus("success");
    } catch (caughtError) {
      setError(caughtError.message);
      setPreviewStatus("error");
    }
  };

  const generateDeck = async (event) => {
    event.preventDefault();
    setStatus("loading");
    setError("");

    try {
      const response = await fetch(`${API_URL}/api/generate-ppt`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(requestBody()),
      });

      if (!response.ok) throw new Error("Presentation generate nahi ho payi. Backend check karo.");

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = `${topicSlug}.pptx`;
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
            <span className="brand-mark"><Sparkles size={22} /></span>
            <span>AI PPT Slide Generator</span>
          </div>
          <h1>Prompt se polished PowerPoint deck banao.</h1>
          <p>
            Topic, audience, tone aur instructions do. App outline preview karta hai,
            speaker notes banata hai, aur editable `.pptx` download deta hai.
          </p>
          <div className="example-row">
            {examples.map((example) => (
              <button className="chip" type="button" key={example} onClick={() => updateField("topic", example)}>
                {example}
              </button>
            ))}
          </div>
        </div>

        <form className="generator-panel" onSubmit={generateDeck}>
          <label className="wide-field">
            Topic
            <textarea value={form.topic} onChange={(event) => updateField("topic", event.target.value)} rows={3} required />
          </label>

          <div className="grid-two">
            <label>
              Slides
              <input type="number" min="3" max="15" value={form.slide_count} onChange={(event) => updateField("slide_count", event.target.value)} />
            </label>
            <label>
              Language
              <input value={form.language} onChange={(event) => updateField("language", event.target.value)} />
            </label>
          </div>

          <div className="grid-two">
            <label>
              Audience
              <input value={form.audience} onChange={(event) => updateField("audience", event.target.value)} />
            </label>
            <label>
              Tone
              <select value={form.tone} onChange={(event) => updateField("tone", event.target.value)}>
                <option value="professional">Professional</option>
                <option value="friendly">Friendly</option>
                <option value="persuasive">Persuasive</option>
                <option value="educational">Educational</option>
                <option value="executive">Executive</option>
              </select>
            </label>
          </div>

          <div className="theme-grid" aria-label="Theme selector">
            {Object.entries(themeLabels).map(([value, label]) => (
              <button
                className={`theme-swatch ${form.theme === value ? "active" : ""}`}
                type="button"
                key={value}
                onClick={() => updateField("theme", value)}
              >
                <span className={`swatch ${value}`} />
                {label}
              </button>
            ))}
          </div>

          <label className="wide-field">
            Extra instructions
            <textarea value={form.extra_instructions} onChange={(event) => updateField("extra_instructions", event.target.value)} rows={2} />
          </label>

          <label className="toggle-line">
            <input type="checkbox" checked={form.include_speaker_notes} onChange={(event) => updateField("include_speaker_notes", event.target.checked)} />
            Add speaker notes
          </label>

          <div className="action-row">
            <button className="secondary" type="button" onClick={previewDeck} disabled={previewStatus === "loading"}>
              {previewStatus === "loading" ? <Loader2 className="spin" size={18} /> : <Wand2 size={18} />}
              Preview Outline
            </button>
            <button type="submit" disabled={status === "loading"}>
              {status === "loading" ? <Loader2 className="spin" size={18} /> : <Download size={18} />}
              Generate PPT
            </button>
          </div>

          {error && <p className="error">{error}</p>}
          {status === "success" && <p className="success"><CheckCircle2 size={16} /> Deck download ho gaya.</p>}
        </form>
      </section>

      <aside className="preview-strip">
        <div className={`mini-slide title-slide ${form.theme}`}>
          <FileText size={24} />
          <strong>{deckPlan?.title || form.topic || "Presentation Topic"}</strong>
          <span>{deckPlan?.subtitle || form.audience}</span>
        </div>
        <div className="outline-panel">
          <div className="outline-head">
            <strong>Deck Outline</strong>
            <span>{deckPlan ? `${deckPlan.slides.length} slides` : `${form.slide_count} planned slides`}</span>
          </div>
          {(deckPlan?.slides || [
            { title: "Overview", bullets: ["Key context", "Benefits", "Challenges"] },
            { title: "Action Plan", bullets: ["Steps", "Timeline", "Metrics"] },
            { title: "Conclusion", bullets: ["Recommendations", "Next steps"] },
          ]).slice(0, 6).map((slide, index) => (
            <div className="outline-item" key={`${slide.title}-${index}`}>
              <span>{index + 1}</span>
              <div>
                <strong>{slide.title}</strong>
                <p>{slide.bullets?.[0]}</p>
              </div>
            </div>
          ))}
        </div>
      </aside>
    </main>
  );
}

createRoot(document.getElementById("root")).render(<App />);
