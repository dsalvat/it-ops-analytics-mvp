import React, { useState } from 'react';

function HomePage() {
  const [apiResult, setApiResult] = useState(null);

  const handleApiCall = async () => {
    try {
      // Placeholder for Eazybi API call
      // Replace with actual API endpoint and logic
      const response = await fetch('http://localhost:8000/api/v1/eazybi/eazybi-data'); // Assuming a proxy or direct call
      const data = await response.json();
      setApiResult(data.firstResult); // Assuming the API returns an object with a 'firstResult' key
    } catch (error) {
      console.error('Error fetching data from Eazybi API:', error);
      setApiResult('Error fetching data.');
    }
  };

  return (
    <div>
      <h1>Welcome to IT Operations Analytics!</h1>
      <p>This is the front page of your application.</p>
      <button onClick={handleApiCall}>Get First Result from Eazybi</button>
      {apiResult && (
        <div>
          <h2>API Result:</h2>
          <p>{apiResult}</p>
        </div>
      )}
    </div>
  );
}

export default HomePage;