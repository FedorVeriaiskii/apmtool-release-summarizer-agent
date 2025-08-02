import React, { useState } from "react";

function App() {
  const [releaseNews, setReleaseNews] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  const releaseNoteItems = [
    "APM-Tool Managed release notes",
    "OneAgent release notes",
    "ActiveGate release notes",
    "APM-Tool API changelog",
    "APM-Tool Operator release notes"
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
    setIsLoading(true);
    setReleaseNews([]);
    
    // Function to convert display name to element id
    const getElementId = (itemName) => {
      const idMap = {
        "dynatrace_managed": "APM-Tool Managed release notes",
        "oneagent": "OneAgent release notes",
        "active_gate": "ActiveGate release notes",
        "dynatrace_api": "APM-Tool API changelog",
        "dynatrace_operator": "APM-Tool Operator release notes"
      };
      // Find the key that matches the itemName value
      const elementId = Object.keys(idMap).find(key => idMap[key] === itemName);
      return elementId || itemName.toLowerCase().replace(/\s+/g, '_');
    };
    
    // Get selected items as array of objects with element id as key and value as value
    const selectedItems = releaseNoteItems
      .map((item, idx) => ({
        elementId: getElementId(item),
        value: item,
        selected: checkedItems[idx]
      }))
      .filter(item => item.selected)
      .map(item => ({ [item.elementId]: item.value }));
    
    try {
      const res = await fetch("http://localhost:8000/api/dynatrace-release-news-summary", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ selectedItems: selectedItems }),
      });
      let data;
      console.log('Response data:', res);
      try {
        data = await res.json();
      } catch (jsonError) {
        // If response is not valid JSON, show raw text
        const text = await res.text();
        setReleaseNews([{ component: "Error", summary: "Unexpected response: " + text.slice(0, 200), version: "" }]);
        setIsLoading(false);
        return;
      }
      
      const summaries = [];

      // Helper function to create structured summary from new format
      const createStructuredSummary = (componentData, componentName) => {
        if (!componentData || !componentData.latestVersion) return null;
        
        const sections = [];
        if (componentData.breaking_changes) {
          sections.push(`**🚨 Breaking Changes:**\n${componentData.breaking_changes}`);
        }
        if (componentData.announcements) {
          sections.push(`**📢 Announcements:**\n${componentData.announcements}`);
        }
        if (componentData.new_features) {
          sections.push(`**✨ New Features:**\n${componentData.new_features}`);
        }
        if (componentData.technology_support) {
          sections.push(`**🔧 Technology Support:**\n${componentData.technology_support}`);
        }
        if (componentData.resolved_issues) {
          sections.push(`**🐛 Resolved Issues:**\n${componentData.resolved_issues}`);
        }
        
        return {
          component: componentName,
          summary: sections.join('\n\n'),
          version: componentData.latestVersion
        };
      };

      // Check and add APM-Tool Managed data if available
      const managedSummary = createStructuredSummary(data["dynatrace-managed"], "APM-Tool Managed");
      if (managedSummary) summaries.push(managedSummary);
      
      // Check and add OneAgent data if available
      const oneagentSummary = createStructuredSummary(data.oneagent, "OneAgent");
      if (oneagentSummary) summaries.push(oneagentSummary);
      
      // Check and add ActiveGate data if available
      const activegateSummary = createStructuredSummary(data["active-gate"], "ActiveGate");
      if (activegateSummary) summaries.push(activegateSummary);

      // Check and add APM-Tool API data if available
      const apiSummary = createStructuredSummary(data["dynatrace-api"], "APM-Tool API");
      if (apiSummary) summaries.push(apiSummary);
      
      // Check and add APM-Tool Operator data if available
      const operatorSummary = createStructuredSummary(data["dynatrace-operator"], "APM-Tool Operator");
      if (operatorSummary) summaries.push(operatorSummary);
      
      if (summaries.length > 0) {
        setReleaseNews(summaries);
      } else if (data.error) {
        setReleaseNews([{ component: "Error", summary: data.error, version: "" }]);
      } else {
        setReleaseNews([{ component: "Info", summary: "No summary data available for selected components.", version: "" }]);
      }
    } catch (error) {
      setReleaseNews([{ component: "Error", summary: error.message, version: "" }]);
    }
    setIsLoading(false);
  };

  // Download release news as PDF from backend using existing releaseNews data
  const handleDownloadPdf = async () => {
    try {
      console.log('Downloading PDF from backend using existing data...');
      const res = await fetch("http://localhost:8000/api/download-release-news-pdf", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ releaseNews: releaseNews }),
      });
      
      if (!res.ok) {
        const errorData = await res.json();
        console.error('PDF download error:', errorData);
        alert(`Error downloading PDF: ${errorData.error || 'Unknown error'}`);
        return;
      }
      
      // Get the PDF blob
      const blob = await res.blob();
      
      // Create download link
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      
      // Extract filename from response headers or use default
      const contentDisposition = res.headers.get('Content-Disposition');
      let filename = 'APM-Tool_Release_Notes.pdf';
      if (contentDisposition) {
        const filenameMatch = contentDisposition.match(/filename="?(.+)"?/);
        if (filenameMatch) {
          filename = filenameMatch[1];
        }
      }
      
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      
    } catch (error) {
      console.error('PDF download failed:', error);
      alert(`Error downloading PDF: ${error.message}`);
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
          APM-Tool Release Notes Summarizer Agent
        </h1>
        <p style={{
          color: '#e3e8ee',
          fontSize: '1.25rem',
          margin: '1.2rem auto 0 auto',
          maxWidth: '700px',
          fontWeight: 400,
        }}>
          These release notes for APM-Tool updates—showcasing new features, changes, and bug fixes—keep you informed and ahead of the game.<br />
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
              disabled={!checkedItems.some(item => item)}
              style={{
                padding: '0.85rem 1.7rem',
                background: checkedItems.some(item => item) 
                  ? 'linear-gradient(90deg, #1496FF 60%, #1a3a6b 100%)' 
                  : 'linear-gradient(90deg, #cccccc 60%, #999999 100%)',
                color: checkedItems.some(item => item) ? '#fff' : '#666',
                border: 'none',
                borderRadius: '8px',
                fontSize: '1.15rem',
                fontWeight: 600,
                cursor: checkedItems.some(item => item) ? 'pointer' : 'not-allowed',
                boxShadow: checkedItems.some(item => item) 
                  ? '0 2px 12px rgba(20,150,255,0.18)' 
                  : '0 2px 12px rgba(0,0,0,0.1)',
                transition: 'background 0.2s',
                opacity: checkedItems.some(item => item) ? 1 : 0.6,
              }}
              onMouseOver={e => {
                if (checkedItems.some(item => item)) {
                  e.target.style.background = '#1284EA';
                }
              }}
              onMouseOut={e => {
                if (checkedItems.some(item => item)) {
                  e.target.style.background = 'linear-gradient(90deg, #1496FF 60%, #1a3a6b 100%)';
                }
              }}
            >
              Read summarized Latest Release news
            </button>
            <button
              onClick={handleDownloadPdf}
              disabled={releaseNews.length === 0 || releaseNews.some(item => item.component === "Error")}
              style={{
                padding: '0.85rem 1.7rem',
                background: (releaseNews.length > 0 && !releaseNews.some(item => item.component === "Error"))
                  ? 'linear-gradient(90deg, #4CAF50 60%, #1a3a6b 100%)'
                  : 'linear-gradient(90deg, #cccccc 60%, #999999 100%)',
                color: (releaseNews.length > 0 && !releaseNews.some(item => item.component === "Error")) ? '#fff' : '#666',
                border: 'none',
                borderRadius: '8px',
                fontSize: '1.15rem',
                fontWeight: 600,
                cursor: (releaseNews.length > 0 && !releaseNews.some(item => item.component === "Error")) ? 'pointer' : 'not-allowed',
                opacity: (releaseNews.length > 0 && !releaseNews.some(item => item.component === "Error")) ? 1 : 0.6,
                boxShadow: (releaseNews.length > 0 && !releaseNews.some(item => item.component === "Error"))
                  ? '0 2px 12px rgba(76,175,80,0.18)'
                  : '0 2px 12px rgba(0,0,0,0.1)',
                transition: 'background 0.2s',
              }}
              onMouseOver={e => {
                if (releaseNews.length > 0 && !releaseNews.some(item => item.component === "Error")) {
                  e.target.style.background = '#388E3C';
                }
              }}
              onMouseOut={e => {
                if (releaseNews.length > 0 && !releaseNews.some(item => item.component === "Error")) {
                  e.target.style.background = 'linear-gradient(90deg, #4CAF50 60%, #1a3a6b 100%)';
                }
              }}
            >
              Download Latest Release news as pdf
            </button>
          </div>
        </div>
        {(isLoading || releaseNews.length > 0) && (
          <div style={{
            width: '100vw',
            padding: '0 2rem',
            boxSizing: 'border-box',
          }}>
            {isLoading && (
              <div style={{
                background: 'linear-gradient(135deg, #f7f9fa 0%, #e3e8ee 100%)',
                borderRadius: '22px',
                boxShadow: '0 8px 40px rgba(20,150,255,0.13)',
                padding: '3rem 2.5rem',
                width: '100%',
                marginBottom: '2.5rem',
                border: '1px solid #e3e8ee',
                position: 'relative',
                overflow: 'hidden',
                boxSizing: 'border-box',
                textAlign: 'center',
              }}>
                <h2 style={{
                  color: '#1496FF',
                  marginBottom: '1.5rem',
                  fontWeight: 700,
                  fontSize: '2rem',
                }}>
                  Loading...
                </h2>
              </div>
            )}
            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(450px, 1fr))',
              gap: '2rem',
              width: '100%',
            }}>
              {releaseNews.map((releaseData, index) => (
                <div key={index} style={{
                  background: 'linear-gradient(135deg, #f7f9fa 0%, #e3e8ee 100%)',
                  borderRadius: '22px',
                  boxShadow: '0 8px 40px rgba(20,150,255,0.13)',
                  padding: '2rem 1.5rem',
                  border: '1px solid #e3e8ee',
                  position: 'relative',
                  overflow: 'hidden',
                  boxSizing: 'border-box',
                  minHeight: '300px',
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
                    fontSize: '1.6rem',
                    letterSpacing: '0.01em',
                    textShadow: '0 2px 16px rgba(20,150,255,0.10)',
                    zIndex: 1,
                    position: 'relative',
                  }}>
                    Latest {releaseData.component} Release {releaseData.version && (
                      <span style={{ color: '#1a3a6b', fontWeight: 600 }}>({releaseData.version})</span>
                    )}
                  </h2>
                  <div 
                    style={{
                      fontSize: '1rem',
                      lineHeight: '1.6',
                      color: '#1a3a6b',
                      background: 'rgba(255, 255, 255, 0.7)',
                      border: '1px solid rgba(20, 150, 255, 0.15)',
                      borderRadius: '12px',
                      margin: 0,
                      fontFamily: 'Inter, Arial, sans-serif',
                      zIndex: 1,
                      position: 'relative',
                      padding: '1.2rem',
                      boxShadow: '0 2px 8px rgba(20, 150, 255, 0.08)',
                      backdropFilter: 'blur(10px)',
                      maxHeight: '600px',
                      overflowY: 'auto',
                      scrollbarWidth: 'thin',
                      scrollbarColor: '#1496FF rgba(255, 255, 255, 0.3)',
                      whiteSpace: 'pre-wrap',
                    }}
                    dangerouslySetInnerHTML={{
                      __html: releaseData.summary
                        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                        .replace(/\n/g, '<br/>')
                    }}
                  />
                </div>
              ))}
            </div>
          </div>
        )}
      </main>
      <style jsx global>{`
        div :global(h1) {
          color: #1496FF !important;
          font-size: 1.6rem !important;
          font-weight: 700 !important;
          margin: 1.5rem 0 1rem 0 !important;
          border-bottom: 2px solid #1496FF !important;
          padding-bottom: 0.5rem !important;
        }
        div :global(h2) {
          color: #1a3a6b !important;
          font-size: 1.4rem !important;
          font-weight: 600 !important;
          margin: 1.3rem 0 0.8rem 0 !important;
          border-left: 4px solid #1496FF !important;
          padding-left: 1rem !important;
        }
        div :global(h3) {
          color: #1a3a6b !important;
          font-size: 1.2rem !important;
          font-weight: 600 !important;
          margin: 1rem 0 0.6rem 0 !important;
          text-decoration: underline !important;
          text-decoration-color: #1496FF !important;
          text-underline-offset: 0.3rem !important;
        }
        div :global(p) {
          margin: 0.8rem 0 !important;
          line-height: 1.6 !important;
          white-space: pre-wrap !important;
        }
        div :global(ul) {
          margin: 1rem 0 !important;
          padding-left: 1.5rem !important;
        }
        div :global(li) {
          margin: 0.4rem 0 !important;
          list-style-type: disc !important;
        }
        div :global(strong) {
          font-weight: 700 !important;
          color: #1496FF !important;
          display: block !important;
          margin: 1.2rem 0 0.6rem 0 !important;
          border-left: 3px solid #1496FF !important;
          padding-left: 0.8rem !important;
          background: rgba(20, 150, 255, 0.05) !important;
          padding: 0.6rem 0.8rem !important;
          border-radius: 6px !important;
          font-size: 1.1rem !important;
        }
        div :global(em) {
          font-style: italic !important;
          color: #1a3a6b !important;
        }
        div :global(code) {
          background-color: rgba(20, 150, 255, 0.1) !important;
          padding: 0.2rem 0.4rem !important;
          border-radius: 4px !important;
          font-family: 'Courier New', monospace !important;
          font-size: 0.9em !important;
          color: #1496FF !important;
        }
        div :global(br) {
          margin: 0.5rem 0 !important;
        }
        /* Enhanced styling for structured sections */
        div [style*="white-space: pre-wrap"] {
          font-family: 'Inter', Arial, sans-serif !important;
        }
        div [style*="white-space: pre-wrap"] strong:first-child {
          margin-top: 0 !important;
        }
      `}</style>
    </div>
  );
}

export default App;
