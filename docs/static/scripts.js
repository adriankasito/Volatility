/// Function to update selected minutes display when the slider value changes
document.getElementById("minutesSlider").addEventListener("input", function () {
    document.getElementById("selectedMinutes").textContent =
      "Selected minutes: " + this.value;
  });
  
  // Function to handle the forecast button click
  document
    .getElementById("forecastButton")
    .addEventListener("click", function () {
      const selectedMinutes = document.getElementById("minutesSlider").value;
  
      // Make a POST request to "/predict" with the selected minutes
      fetch("/predict", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ ticker: "MSFT", n_minutes: selectedMinutes }),
      })
        .then((response) => response.json())
        .then((data) => {
          // Update the table with the forecast data
          const table = document.querySelector("table");
          table.innerHTML = `
        <tr>
          <th>MSFT</th>
          <th>Date</th>
          <th>Time</th>
          <th>Volatility</th>
        </tr>`;
          let rowNumber = 1;
          for (const [timestamp, volatility] of Object.entries(data.forecast)) {
            const [date, time] = timestamp.split("T");
            const className = rowNumber % 2 === 0 ? "even" : "odd";
            table.innerHTML += `
          <tr class="${className}">
            <td>${rowNumber}</td>
            <td>${date}</td>
            <td>${time}</td>
            <td>${volatility}</td>
          </tr>`;
            rowNumber++;
          }
        })
        .catch((error) => {
          // Display an error message in the table in case of an error
          const table = document.querySelector("table");
          table.innerHTML = `<tr><td colspan="4">Error: ${error.message}</td></tr>`;
        });
    });
  
  // Function to handle the reset button click
  document.getElementById("resetButton").addEventListener("click", function () {
    // Clear the table and reset it to its initial state
    const table = document.querySelector("table");
    table.innerHTML = `
      <tr>
        <th>Microsoft Corporation Volatility By Minute</th>
        <th>Date</th>
        <th>Time</th>
        <th>Volatility</th>
      </tr>`;
  });
  
  // Add interactivity to the title with moving colors
  const title = document.getElementById("interactiveTitle");
  setInterval(function () {
    // Change the title color randomly every second
    const randomColor = "#" + Math.floor(Math.random() * 16777215).toString(16);
    title.style.color = randomColor;
  }, 1000); // Change the interval as needed
  