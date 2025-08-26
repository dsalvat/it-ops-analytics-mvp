import React, { useState, useEffect } from 'react';

function HomePage() {
  const [reportsData, setReportsData] = useState([]);

  useEffect(() => {
    const fetchConfig = async () => {
      try {
        const response = await fetch('http://localhost:8000/api/v1/eazybi/config');
        const config = await response.json();
        setReportsData(config.map(report => ({
          ...report,
          eazybiResult: null,
          llmPrompt: report.llm_analysis_call || '',
          llmResult: null,
          loadingEazybi: false,
          loadingLlm: false,
          errorEazybi: null,
          errorLlm: null,
        })));
      } catch (error) {
        console.error("Error fetching Eazybi config:", error);
      }
    };

    fetchConfig();
  }, []); // Empty dependency array means this runs once on mount

  const handleGetEazybiReport = async (index) => {
    const report = reportsData[index];
    setReportsData(prevReports => prevReports.map((r, i) =>
      i === index ? { ...r, loadingEazybi: true, errorEazybi: null } : r
    ));

    try {
      const response = await fetch(`http://localhost:8000/api/v1/eazybi/report/${report.report_id}`);
      const data = await response.json();

      setReportsData(prevReports => prevReports.map((r, i) =>
        i === index ? {
          ...r,
          eazybiResult: data.result || data.detail || "No data found or unexpected format.",
          errorEazybi: data.detail ? data.detail : null,
          loadingEazybi: false,
        } : r
      ));
    } catch (error) {
      console.error(`Error fetching Eazybi report (${report.name}):`, error);
      setReportsData(prevReports => prevReports.map((r, i) =>
        i === index ? {
          ...r,
          eazybiResult: null,
          errorEazybi: `Error fetching report: ${error.message}`,
          loadingEazybi: false,
        } : r
      ));
    }
  };

  const handleLLMPromptChange = (index, value) => {
    setReportsData(prevReports => prevReports.map((r, i) =>
      i === index ? { ...r, llmPrompt: value } : r
    ));
  };

  const handleCallLLM = async (index) => {
    const report = reportsData[index];
    setReportsData(prevReports => prevReports.map((r, i) =>
      i === index ? { ...r, loadingLlm: true, errorLlm: null, llmResult: null } : r
    ));

    if (!report.llmPrompt) {
      setReportsData(prevReports => prevReports.map((r, i) =>
        i === index ? { ...r, errorLlm: "Prompt cannot be empty.", loadingLlm: false } : r
      ));
      return;
    }

    // Placeholder for LLM API call
    // In a real application, this would call a backend endpoint
    // that integrates with an LLM (e.g., OpenAI, Gemini).
    try {
      // Example: Sending Eazybi result and prompt to LLM backend
      const llmResponse = await fetch('http://localhost:8000/api/v1/llm/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          prompt: report.llmPrompt,
          context: String(report.eazybiResult), // Ensure context is a string
        }),
      });
      const llmData = await llmResponse.json();

      setReportsData(prevReports => prevReports.map((r, i) =>
        i === index ? {
          ...r,
          llmResult: llmData.response || llmData.detail || "No LLM response.",
          errorLlm: llmData.detail ? llmData.detail : null,
          loadingLlm: false,
        } : r
      ));
    } catch (error) {
      console.error(`Error calling LLM for report (${report.name}):`, error);
      setReportsData(prevReports => prevReports.map((r, i) =>
        i === index ? {
          ...r,
          llmResult: null,
          errorLlm: `Error calling LLM: ${error.message}`,
          loadingLlm: false,
        } : r
      ));
    }
  };

  return (
    <div>
      <h1>IT Operations Analytics Dashboard</h1>
      <p>Interact with Eazybi reports and generate insights using LLMs.</p>

      <table border="1" style={{ width: '100%', borderCollapse: 'collapse' }}>
        <thead>
          <tr>
            <th>#</th>
            <th>Report Name</th>
            <th>Get Eazybi Report</th>
            <th>Eazybi Report Result</th>
            <th>LLM Prompt</th>
            <th>Call LLM</th>
            <th>LLM Result</th>
          </tr>
        </thead>
        <tbody>
          {reportsData.map((report, index) => (
            <tr key={report.report_id || index}>
              <td>{index + 1}</td>
              <td>{report.name}</td>
              <td>
                <button
                  onClick={() => handleGetEazybiReport(index)}
                  disabled={report.loadingEazybi}
                >
                  {report.loadingEazybi ? 'Loading...' : 'Get Report'}
                </button>
              </td>
              <td>
                {report.errorEazybi ? (
                  <p style={{ color: 'red' }}>Error: {report.errorEazybi}</p>
                ) : (
                  report.eazybiResult && <pre>{JSON.stringify(report.eazybiResult, null, 2)}</pre>
                )}
              </td>
              <td>
                <textarea
                  id={report.name || `llmPrompt-${index}`}
                  name={report.name || `llmPrompt-${index}`}
                  value={report.llmPrompt}
                  onChange={(e) => handleLLMPromptChange(index, e.target.value)}
                  placeholder="Ask LLM about this report..."
                  rows="3"
                  cols="30"
                />
              </td>
              <td>
                <button
                  onClick={() => handleCallLLM(index)}
                  disabled={report.loadingLlm || !report.eazybiResult}
                >
                  {report.loadingLlm ? 'Calling...' : 'Call LLM'}
                </button>
              </td>
              <td>
                {report.errorLlm ? (
                  <p style={{ color: 'red' }}>Error: {report.errorLlm}</p>
                ) : (
                  report.llmResult && <pre>{JSON.stringify(report.llmResult, null, 2)}</pre>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default HomePage;