import React, { useState } from "react";

function App() {
  const [releaseNews, setReleaseNews] = useState("");
  const [latestVersion, setLatestVersion] = useState("");

  const releaseNoteItems = [
    "Dynatrace Managed release notes",
    "OneAgent release notes",
    "ActiveGate release notes",
    "Dynatrace API changelog",
    "Dynatrace Operator release notes"
  ];
  const [checkedItems, setCheckedItems] = useState(Array(releaseNoteItems.length).fill(false));

  const handleCheckboxChange = idx => {
    setCheckedItems(prev => {
      const updated = [...prev];
      updated[idx] = !updated[idx];
      return updated;
    });
  };

  const handleReleaseNewsClick = async () => {
    setReleaseNews("Loading...");
    try {
      const res = await fetch("http://localhost:8000/api/oneagent-release-news", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
      });
      let data;
      try {
        data = await res.json();
      } catch (jsonError) {
        // If response is not valid JSON, show raw text
        const text = await res.text();
        setReleaseNews("Error: Unexpected response: " + text.slice(0, 200));
        return;
      }
      if (data.summary) {
        setReleaseNews(data.summary);
        setLatestVersion(data.oneAgentLatestVersion);
      } else {
        setReleaseNews("Error: " + (data.error || "Unknown error"));
      }
    } catch (error) {
      setReleaseNews("Error: " + error.message);
    }
  };

  // Download release news as PDF (copy of fetch logic)
  const handleDownloadPdf = async () => {
    let summary = '';
    let version = '';
    try {
      console.log('Downloading full release news...');
      const res = await fetch("http://localhost:8000/api/download-full-release-news", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
      });
      let data;
      try {
        data = await res.json();
      } catch (jsonError) {
        // If response is not valid JSON, show raw text
        const text = await res.text();
        summary = "Error: Unexpected response: " + text.slice(0, 200);
        version = '';
      }
      if (data && data.summary) {
        summary = data.summary;
        version = data.oneAgentLatestVersion;
      } else {
        summary = "Error: " + (data.error || "Unknown error");
        version = '';
      }
    } catch (error) {
      summary = "Error: " + error.message;
      version = '';
    }
    const docTitle = version ? `Latest Oneagent Release (${version})` : 'Latest Release News';
    const content = `${docTitle}\n\n${summary}`;
    // Create a simple PDF using jsPDF
    const script = document.createElement('script');
    script.src = 'https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js';
    script.onload = () => {
      const { jsPDF } = window.jspdf;
      const pdf = new jsPDF();
      pdf.setFont('Arial');
      pdf.setFontSize(14);
      pdf.text(content, 10, 20, { maxWidth: 180 });
      pdf.save('Dynatrace_Release_News.pdf');
    };
    if (!window.jspdf) {
      document.body.appendChild(script);
    } else {
      const { jsPDF } = window.jspdf;
      const pdf = new jsPDF();
      pdf.setFont('Arial');
      pdf.setFontSize(14);
      pdf.text(content, 10, 20, { maxWidth: 180 });
      pdf.save('Dynatrace_Release_News.pdf');
    }
  };

  return (
    <div style={{
      minHeight: '100vh',
      width: '100%',
      background: 'linear-gradient(135deg, #0f1c3f 0%, #1a3a6b 60%, #1496FF 100%)',
      fontFamily: 'Inter, Arial, sans-serif',
      padding: 0,
      margin: 0,
      overflowX: 'hidden',
    }}>
      <header style={{
        padding: '2.5rem 0 1.5rem 0',
        textAlign: 'center',
        background: 'none',
      }}>
        <h1 style={{
          fontSize: '2.8rem',
          fontWeight: 700,
          color: '#fff',
          letterSpacing: '0.02em',
          margin: 0,
          textShadow: '0 2px 16px rgba(20,150,255,0.18)',
        }}>
          Dynatrace Release Notes Summarizer Agent
        </h1>
        <p style={{
          color: '#e3e8ee',
          fontSize: '1.25rem',
          margin: '1.2rem auto 0 auto',
          maxWidth: '700px',
          fontWeight: 400,
        }}>
          These release notes for Dynatrace updates—showcasing new features, changes, and bug fixes—keep you informed and ahead of the game.<br />
          <span style={{ display: 'block', marginTop: '0.5rem', color: '#fff', fontWeight: 500 }}>Please select the elements:</span>
        </p>
      </header>
      <main style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: '70vh',
      }}>
        <div style={{
          background: 'rgba(255,255,255,0.98)',
          borderRadius: '18px',
          boxShadow: '0 4px 32px rgba(20,150,255,0.10)',
          padding: '2.5rem 2rem',
          width: '100vw',
          marginBottom: '2rem',
          boxSizing: 'border-box',
        }}>
          <ul style={{
            listStyle: 'none',
            padding: 0,
            margin: 0,
            fontSize: '1.15rem',
            color: '#1a3a6b',
          }}>
            {releaseNoteItems.map((item, idx) => (
              <li key={item} style={{
                padding: '0.85rem 1.5rem',
                borderBottom: idx < releaseNoteItems.length - 1 ? '1px solid #e3e8ee' : 'none',
                display: 'flex',
                alignItems: 'center',
                fontWeight: 500,
              }}>
                <input
                  type="checkbox"
                  checked={checkedItems[idx]}
                  onChange={() => handleCheckboxChange(idx)}
                  style={{ marginRight: '1rem', accentColor: '#1496FF', width: '1.2em', height: '1.2em' }}
                />
                <span>{item}</span>
              </li>
            ))}
          </ul>
          <div style={{ display: 'flex', justifyContent: 'center', gap: '1rem', margin: '2rem 0 0 0' }}>
            <button
              onClick={handleReleaseNewsClick}
              style={{
                padding: '0.85rem 1.7rem',
                background: 'linear-gradient(90deg, #1496FF 60%, #1a3a6b 100%)',
                color: '#fff',
                border: 'none',
                borderRadius: '8px',
                fontSize: '1.15rem',
                fontWeight: 600,
                cursor: 'pointer',
                boxShadow: '0 2px 12px rgba(20,150,255,0.18)',
                transition: 'background 0.2s',
              }}
              onMouseOver={e => (e.target.style.background = '#1284EA')}
              onMouseOut={e => (e.target.style.background = 'linear-gradient(90deg, #1496FF 60%, #1a3a6b 100%)')}
            >
              Read summarized Latest Release news
            </button>
            <button
              onClick={handleDownloadPdf}
              style={{
                padding: '0.85rem 1.7rem',
                background: 'linear-gradient(90deg, #4CAF50 60%, #1a3a6b 100%)',
                color: '#fff',
                border: 'none',
                borderRadius: '8px',
                fontSize: '1.15rem',
                fontWeight: 600,
                cursor: 'pointer',
                opacity: 1,
                boxShadow: '0 2px 12px rgba(76,175,80,0.18)',
                transition: 'background 0.2s',
              }}
              onMouseOver={e => { e.target.style.background = '#388E3C'; }}
              onMouseOut={e => { e.target.style.background = 'linear-gradient(90deg, #4CAF50 60%, #1a3a6b 100%)'; }}
            >
              Download Latest Release news as pdf
            </button>
          </div>
        </div>
        {releaseNews && (
          <div style={{
            background: 'linear-gradient(135deg, #f7f9fa 0%, #e3e8ee 100%)',
            borderRadius: '22px',
            boxShadow: '0 8px 40px rgba(20,150,255,0.13)',
            padding: '3rem 2.5rem',
            width: '100vw',
            marginBottom: '2.5rem',
            border: '1px solid #e3e8ee',
            position: 'relative',
            overflow: 'hidden',
            boxSizing: 'border-box',
          }}>
            <div style={{
              position: 'absolute',
              top: '-40px',
              right: '-40px',
              width: '120px',
              height: '120px',
              background: 'radial-gradient(circle, #1496FF 0%, #1a3a6b 100%)',
              opacity: 0.12,
              borderRadius: '50%',
              zIndex: 0,
            }} />
            <h2 style={{
              color: '#1496FF',
              marginBottom: '1.5rem',
              fontWeight: 700,
              fontSize: '2rem',
              letterSpacing: '0.01em',
              textShadow: '0 2px 16px rgba(20,150,255,0.10)',
              zIndex: 1,
              position: 'relative',
            }}>
              Latest Oneagent Release <span style={{ color: '#1a3a6b', fontWeight: 600 }}>({latestVersion})</span>
            </h2>
            <pre style={{
              whiteSpace: 'pre-wrap',
              wordBreak: 'break-word',
              fontSize: '1.13rem',
              lineHeight: '1.8',
              color: '#1a3a6b',
              background: 'none',
              border: 'none',
              margin: 0,
              fontFamily: 'Inter, Arial, sans-serif',
              zIndex: 1,
              position: 'relative',
              padding: 0,
            }}>{releaseNews}</pre>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
