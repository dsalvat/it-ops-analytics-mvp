import React, { useState } from 'react';

function HomePage() {
  const [apiResults, setApiResults] = useState([]); // Changed to array

  const handleApiCall = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/eazybi/eazybi-data');
      const data = await response.json();
      if (data.results) { // Check if 'results' key exists
        setApiResults(data.results); // Set the array of results
      } else {
        setApiResults([{ error: "Unexpected response format from backend." }]);
      }
    } catch (error) {
      console.error('Error fetching data from Eazybi API:', error);
      setApiResults([{ error: `Error fetching data: ${error.message}` }]);
    }
  };

  return (
    <div>
      <h1>Welcome to IT Operations Analytics!</h1>
      <p>This is the front page of your application.</p>
      <button onClick={handleApiCall}>Get All Eazybi Results</button> {/* Changed button text */}
      {apiResults.length > 0 && (
        <div>
          <h2>API Results:</h2>
          {apiResults.map((item, index) => (
            <div key={index}>
              <h3>Report: {item.report_name}</h3>
              {item.error ? (
                <p style={{ color: 'red' }}>Error: {item.error}</p>
              ) : (
                <p>Result: {JSON.stringify(item.result)}</p> // Display result, stringify for complex objects
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default HomePage;