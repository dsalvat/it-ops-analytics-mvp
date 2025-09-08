import React, { useState, useEffect } from 'react';

function HomePage() {
  const [reportsData, setReportsData] = useState([]);
  const [isFinalReportButtonEnabled, setIsFinalReportButtonEnabled] = useState(false);
  const [finalReportResult, setFinalReportResult] = useState(null);
  const [loadingFinalReport, setLoadingFinalReport] = useState(false);
  const [errorFinalReport, setErrorFinalReport] = useState(null);
  const [isProcessingAll, setIsProcessingAll] = useState(false);
  const [llmModel, setLlmModel] = useState({ platform: 'Gemini', model: 'gemini-1.5-flash-latest' });
  const [language, setLanguage] = useState('Català');
  const [isStopping, setIsStopping] = useState(false);
  const [lastPrompt, setLastPrompt] = useState(null);

  const getWeekOfYear = (date) => {
    const target = new Date(date.valueOf());
    const dayNr = (date.getDay() + 6) % 7;
    target.setDate(target.getDate() - dayNr + 3);
    const firstThursday = target.valueOf();
    target.setMonth(0, 1);
    if (target.getDay() !== 4) {
      target.setMonth(0, 1 + ((4 - target.getDay()) + 7) % 7);
    }
    return 1 + Math.ceil((firstThursday - target) / 604800000);
  }

  const [week, setWeek] = useState(getWeekOfYear(new Date()));
  const [year, setYear] = useState(new Date().getFullYear());

  // Function to check if all LLM results are filled
  const checkFinalReportButtonStatus = () => {
    const allLlmResultsFilled = reportsData.every(report =>
      report.llmResult !== null && report.llmResult !== undefined && report.llmResult !== '' && !report.loadingLlm
    );
    setIsFinalReportButtonEnabled(allLlmResultsFilled && reportsData.length > 0);
  };

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
          getReportTimestamp: null,
          callLlmTimestamp: null,
          stopping: false,
        })));
      } catch (error) {
        console.error("Error fetching Eazybi config:", error);
      }
    };

    fetchConfig();
  }, []); // Empty dependency array means this runs once on mount

  // Effect to re-check button status whenever reportsData changes
  useEffect(() => {
    checkFinalReportButtonStatus();
  }, [reportsData]);

  const handleFinalReport = async () => {
    setLoadingFinalReport(true);
    setErrorFinalReport(null);
    setFinalReportResult(null);

    const allLlmResults = reportsData.map(report => report.llmResult);

    try {
      const llmResponse = await fetch(`http://localhost:8000/api/v1/llm/generate_final_report?platform=${llmModel.platform}&model=${llmModel.model}&language=${language}&week=${week}&year=${year}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          data: allLlmResults,
        }),
      });
      const llmData = await llmResponse.json();

      setFinalReportResult(llmData.response || llmData.detail || "No final LLM response.");
      if (llmData.detail) {
        setErrorFinalReport(llmData.detail);
      }
    } catch (error) {
      console.error("Error calling LLM for final report:", error);
      setErrorFinalReport(`Error generating final report: ${error.message}`);
    } finally {
      setLoadingFinalReport(false);
    }
  };

  const handleGetEazybiReport = async (index) => {
    const report = reportsData[index];
    setReportsData(prevReports => prevReports.map((r, i) =>
      i === index ? { ...r, loadingEazybi: true, errorEazybi: null } : r
    ));

    try {
      const response = await fetch(`http://localhost:8000/api/v1/eazybi/report/${report.report_id}`);
      const data = await response.json();

      if (response.ok) {
        setReportsData(prevReports => prevReports.map((r, i) =>
          i === index ? {
            ...r,
            eazybiResult: data.result || data.detail || "No data found or unexpected format.",
            errorEazybi: data.detail ? data.detail : null,
            loadingEazybi: false,
            getReportTimestamp: new Date().toLocaleString(),
          } : r
        ));
        return true;
      } else {
        throw new Error(data.detail || "Failed to fetch Eazybi report");
      }
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
      return false;
    }
  };

  const handleLLMPromptChange = (index, value) => {
    setReportsData(prevReports => prevReports.map((r, i) =>
      i === index ? { ...r, llmPrompt: value } : r
    ));
  };

  const handleCallLLM = async (index) => {
    const report = reportsData[index];
    setLastPrompt(report.llmPrompt);
    setReportsData(prevReports => prevReports.map((r, i) =>
      i === index ? { ...r, loadingLlm: true, errorLlm: null, llmResult: null } : r
    ));

    if (!report.llmPrompt) {
      setReportsData(prevReports => prevReports.map((r, i) =>
        i === index ? { ...r, errorLlm: "Prompt cannot be empty.", loadingLlm: false } : r
      ));
      return false;
    }

    try {
      const llmResponse = await fetch(`http://localhost:8000/api/v1/llm/generate?platform=${llmModel.platform}&model=${llmModel.model}&language=${language}&week=${week}&year=${year}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          prompt: report.llmPrompt,
          context: JSON.stringify(report.eazybiResult), // Ensure context is a string
        }),
      });
      const llmData = await llmResponse.json();

      if (llmResponse.ok) {
        setReportsData(prevReports => prevReports.map((r, i) =>
          i === index ? {
            ...r,
            llmResult: llmData.response || llmData.detail || "No LLM response.",
            errorLlm: llmData.detail ? llmData.detail : null,
            loadingLlm: false,
            callLlmTimestamp: `${new Date().toLocaleString()} (Model: ${llmModel.model})`,
          } : r
        ));
        return true;
      } else {
        throw new Error(llmData.detail || "Failed to call LLM");
      }
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
      return false;
    }
  };

  const executeWithRetry = async (action, retries = 2) => {
    for (let i = 0; i <= retries; i++) {
      const success = await action();
      if (success) {
        return true;
      }
      if (i < retries) {
        console.log(`Action failed, retrying... (${i + 1}/${retries})`);
      }
    }
    return false;
  };

  const handleGetAllReportsAndCallLLM = async () => {
    setIsProcessingAll(true);
    setIsStopping(false);

    for (let i = 0; i < reportsData.length; i++) {
      if (isStopping) {
        setIsStopping(false);
        break;
      }

      const reportSuccess = await executeWithRetry(() => handleGetEazybiReport(i));
      if (!reportSuccess) {
        setReportsData(prevReports => prevReports.map((r, idx) =>
          idx === i ? { ...r, eazybiResult: "Report unavailable", errorEazybi: "Report unavailable after multiple retries." } : r
        ));
      }

      if (isStopping) {
        setIsStopping(false);
        break;
      }

      const llmSuccess = await executeWithRetry(() => handleCallLLM(i));
      if (!llmSuccess) {
        setReportsData(prevReports => prevReports.map((r, idx) =>
          idx === i ? { ...r, llmResult: "LLM call failed", errorLlm: "LLM call failed after multiple retries." } : r
        ));
      }
    }

    setIsProcessingAll(false);
  };

  const handleGetReportAndCallLLM = async (index) => {
    setReportsData(prevReports => prevReports.map((r, i) =>
      i === index ? { ...r, stopping: false } : r
    ));

    const reportSuccess = await handleGetEazybiReport(index);

    if (reportsData[index].stopping) {
      setReportsData(prevReports => prevReports.map((r, i) =>
        i === index ? { ...r, stopping: false, loadingEazybi: false, loadingLlm: false } : r
      ));
      return;
    }

    if (reportSuccess) {
      await handleCallLLM(index);
    }
  };

  return (
    <div>
      <h1>IT Operations Analytics Dashboard</h1>
      <p>Interact with Eazybi reports and generate insights using LLMs.</p>

      <div style={{ margin: '20px 0' }}>
        <button
          onClick={handleGetAllReportsAndCallLLM}
          disabled={isProcessingAll}
          style={{ backgroundColor: 'red', color: 'white', padding: '10px 20px', border: 'none', borderRadius: '5px' }}
        >
          {isProcessingAll ? 'Processing...' : 'Get All Reports and Call LLM'}
        </button>
        <button
          onClick={() => setIsStopping(true)}
          disabled={!isProcessingAll}
          style={{ marginLeft: '10px', padding: '10px' }}
        >
          Stop
        </button>
        <select 
          value={JSON.stringify(llmModel)} 
          onChange={(e) => setLlmModel(JSON.parse(e.target.value))} 
          style={{ marginLeft: '10px', padding: '10px' }}
        >
          <optgroup label="OpenAI">
            <option value={JSON.stringify({ platform: 'OpenAI', model: 'gpt-4o' })}>gpt-4o</option>
            <option value={JSON.stringify({ platform: 'OpenAI', model: 'gpt-4-turbo' })}>gpt-4-turbo</option>
            <option value={JSON.stringify({ platform: 'OpenAI', model: 'gpt-3.5-turbo' })}>gpt-3.5-turbo</option>
          </optgroup>
          <optgroup label="Gemini">
            <option value={JSON.stringify({ platform: 'Gemini', model: 'gemini-1.5-pro-latest' })}>gemini-1.5-pro-latest</option>
            <option value={JSON.stringify({ platform: 'Gemini', model: 'gemini-1.5-flash-latest' })}>gemini-1.5-flash-latest</option>
            <option value={JSON.stringify({ platform: 'Gemini', model: 'gemini-pro' })}>gemini-pro</option>
          </optgroup>
        </select>
        <select value={language} onChange={(e) => setLanguage(e.target.value)} style={{ marginLeft: '10px', padding: '10px' }}>
          <option value="English">English</option>
          <option value="Català">Català</option>
          <option value="Castellano">Castellano</option>
        </select>
        <select value={week} onChange={(e) => setWeek(e.target.value)} style={{ marginLeft: '10px', padding: '10px' }}>
          {Array.from({ length: 52 }, (_, i) => i + 1).map(w => <option key={w} value={w}>Week {w}</option>)}
        </select>
        <select value={year} onChange={(e) => setYear(e.target.value)} style={{ marginLeft: '10px', padding: '10px' }}>
          <option value="2025">2025</option>
          <option value="2026">2026</option>
        </select>
      </div>

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
            <th>Get Report and Call LLM</th>
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
                  disabled={report.loadingEazybi || isProcessingAll}
                >
                  {report.loadingEazybi ? 'Loading...' : 'Get Report'}
                </button>
                {report.getReportTimestamp && (
                  <p style={{ color: 'red' }}>Report retrieved at {report.getReportTimestamp}</p>
                )}
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
                  disabled={isProcessingAll}
                />
              </td>
              <td>
                <button
                  onClick={() => handleCallLLM(index)}
                  disabled={report.loadingLlm || !report.eazybiResult || isProcessingAll}
                >
                  {report.loadingLlm ? 'Calling...' : 'Call LLM'}
                </button>
                {report.callLlmTimestamp && (
                  <p style={{ color: 'red' }}>LLM called at {report.callLlmTimestamp}</p>
                )}
              </td>
              <td>
                {report.errorLlm ? (
                  <p style={{ color: 'red' }}>Error: {report.errorLlm}</p>
                ) : (
                  report.llmResult && <pre>{JSON.stringify(report.llmResult, null, 2)}</pre>
                )}
              </td>
              <td>
                <button
                  onClick={() => handleGetReportAndCallLLM(index)}
                  disabled={report.loadingEazybi || report.loadingLlm || isProcessingAll}
                >
                  Get Report and Call LLM
                </button>
                <button
                  onClick={() => setReportsData(prevReports => prevReports.map((r, i) => i === index ? { ...r, stopping: true } : r))}
                  disabled={!report.loadingEazybi && !report.loadingLlm}
                  style={{ marginLeft: '10px' }}
                >
                  Stop
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      <div style={{ marginTop: '20px', textAlign: 'center' }}>
        <button
          onClick={handleFinalReport}
          disabled={!isFinalReportButtonEnabled || loadingFinalReport || isProcessingAll}
        >
          {loadingFinalReport ? 'Generating Final Report...' : 'Final Weekly Report'}
        </button>

        {finalReportResult && (
          <div style={{ marginTop: '20px', textAlign: 'left', border: '1px solid #ddd', padding: '15px', borderRadius: '8px', backgroundColor: '#f9f9f9' }}>
            <h3>Final Weekly Report Summary:</h3>
            <pre>{JSON.stringify(finalReportResult, null, 2)}</pre>
          </div>
        )}

        {errorFinalReport && (
          <p style={{ color: 'red', marginTop: '10px' }}>Error: {errorFinalReport}</p>
        )}

        {lastPrompt && (
          <div style={{ marginTop: '20px', textAlign: 'left', border: '1px solid #ddd', padding: '15px', borderRadius: '8px', backgroundColor: '#f0f0f0' }}>
            <h3>Last Prompt:</h3>
            <pre>{lastPrompt}</pre>
          </div>
        )}
      </div>
    </div>
  );
}

export default HomePage;

