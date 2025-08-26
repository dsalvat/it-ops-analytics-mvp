import React, { useState, useEffect } from 'react';

// Hardcode the list of reports.
const eazybiReportsConfig = [
  { "name": "SLA Overview (TTFR)", "report_id": "1075280" },
  { "name": "SLA TTF - TEAMS", "report_id": "1095990" },
  { "name": "Ticket Creation per Issue Type (Weekly - Chart)", "report_id": "858437" },
  { "name": "Ticket Creation per Issue Type (Table)", "report_id": "1604290" },
  { "name": "Ticket Creation vs Resolved (Weekly - chart)", "report_id": "858454" },
  { "name": "Department IT - Incident Impact / Severity Weekly", "report_id": "1609156" },
  { "name": "Ticket Creation vs Resolved (Last Week - Per Team)", "report_id": "1604297" },
  { "name": "Service Desk - Average age report (table)", "report_id": "3413353" },
  { "name": "Service Desk - Average age report", "report_id": "1086738" },
  { "name": "Time Spent per Service - Weeks", "report_id": "1020308" },
  { "name": "Time Spent per Project - Weeks", "report_id": "1020304" },
  { "name": "Logged hours by Customer Category per week (chart)", "report_id": "859985" },
  { "name": "Logged hours by Customer Category per week - Unresolved issues (chart)", "report_id": "1604329" },
  { "name": "Time Spent per Customer Unit - Weeks (% Category)", "report_id": "3438163" },
  { "name": "Time Spent per Customer Unit - Weeks ", "report_id": "1025891" },
  { "name": "Time Spetn per Customer Unit - Weeks (Service Desk)", "report_id": "1604335" },
  { "name": "Department IT - Average satisfaction and SLA met (weekly)", "report_id": "1470702" },
  { "name": "Department IT - Average satisfaction and SLA met (yearly - team)", "report_id": "1471880" },
  { "name": "Logger hours by team member - Weekly", "report_id": "1025957" },
  { "name": "Version releases - Table - Last 4 weeks", "report_id": "1150054" },
  { "name": "Resolution Ranking", "report_id": "1604365" },
  { "name": "Time Spent per Project - Last Week", "report_id": "1665456" },
  { "name": "Ticket Creation per Request Type - Previous Week (Table)", "report_id": "2592318" },
  { "name": "Ticket Resolution per Issuet Type (Table)", "report_id": "2662868" },
  { "name": "Level Resolution (Last WEek - Per Team)", "report_id": "3481850" },
  { "name": "Last Week's Issues with Satisfaction Data", "report_id": "3657228" },
  { "name": "SDIT issues wiwth running TTFR SLA", "report_id": "3657397" },
  { "name": "Unresolved isues from SDIT not updated in over 21 days", "report_id": "3657439" },
  { "name": "P1 and P2 incidents from SDIT", "report_id": "3657466" },
  { "name": "Unresolved issues from SDIT with label 'coordinacio'", "report_id": "3659882" },
  { "name": "SDIT issues resolved last week with coordinacio label", "report_id": "3659884" },
  { "name": "Unresolved issues with more than 14 days in Testing status", "report_id": "3675904" },
  { "name": "Unresolved issues from Service Desk Department IT with no updated in last 14 days", "report_id": "3675782" }
];

function HomePage() {
  const [reportsData, setReportsData] = useState([]);

  useEffect(() => {
    // Initialize reportsData from eazybiReportsConfig on component mount
    setReportsData(eazybiReportsConfig.map(report => ({
      ...report,
      eazybiResult: null,
      llmPrompt: '',
      llmResult: null,
      loadingEazybi: false,
      loadingLlm: false,
      errorEazybi: null,
      errorLlm: null,
    })));
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
          context: report.eazybiResult, // Pass Eazybi result as context
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