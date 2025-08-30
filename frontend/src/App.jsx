import React, { useState } from "react";
import './App.css';

function App() {
  const [file, setFile] = useState(null);
  const [summary, setSummary] = useState("");
  const [loading, setLoading] = useState(false);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) return alert("Please select a PDF file");

    setLoading(true);
    setSummary("");

    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await fetch(
        "https://ai-tool-for-generating-patient-summary-gtna.onrender.com/summarize",
        {
          method: "POST",
          body: formData,
        }
      );

      if (!res.ok) throw new Error("Failed to fetch summary");

      const data = await res.json();
      setSummary(data.summary || "No summary generated.");
    } catch (err) {
      console.error(err);
      setSummary("❌ Error: " + err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      <div className="card">
        <img 
          src="https://img.icons8.com/ios-filled/80/ffffff/hospital-room.png" 
          alt="Hospital Icon" 
          style={{ marginBottom: "20px" }} 
        />
        <h1>Patient Discharge Report Summarizer</h1>

        <form className="form" onSubmit={handleSubmit}>
          <input type="file" accept="application/pdf" onChange={handleFileChange} />
          <button type="submit" disabled={loading}>
            {loading ? <div className="spinner"></div> : "Upload & Summarize"}
          </button>
        </form>

        {summary && (
          <div className="summary">
            <div style={{ display: "flex", alignItems: "center", gap: "10px", marginBottom: "10px" }}>
              <img 
                src="https://img.icons8.com/ios-filled/40/ffffff/medical-document.png" 
                alt="Report Icon" 
              />
              <h2>Summary</h2>
            </div>
            <p>{summary}</p>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
