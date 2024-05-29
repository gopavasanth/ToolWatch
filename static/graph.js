const ctx = document.getElementById("availability_graph");

// Check if data doesnt exists
if (!days.length) {
  ctx.hidden = true;
  const no_data = document.createElement("h3");
  no_data.textContent = "No data available!";
  no_data.classList.add("text-center", "mt-5");
  ctx.parentElement.appendChild(no_data);
} 
else {
  new Chart(ctx, {
    type: "line",
    data: {
      labels: days,
      datasets: [
        {
          label: "Availability",
          data: health_statuses,
          borderWidth: 2,
        },
      ],
    },
    options: {
      maintainAspectRatio: false,
      scales: {
        y: {
          beginAtZero: true,
          ticks: {
            stepSize: 1,
            min: 0,
            max: 1,
          },
        },
        x: {
          ticks: {
            font: {
              size: 18,
            },
          },
        },
      },
      plugins: {
        legend: {
          position: "bottom",
          align: "center",
        },
      },
    },
  });
}

const currentYear = new Date().getFullYear();
const yearSelect = document.getElementById("year");

// Dynamically generate years
for (let year = currentYear; year >= 2022; year--) {
  const option = document.createElement("option");
  option.value = year;
  option.textContent = year;
  if (year == selected_year) option.selected = true;
  yearSelect.appendChild(option);
}

const monthSelect = document.getElementById("month");

for (var i = 0; i < monthSelect.options.length; i++) {
  var option = monthSelect.options[i];
  if (option.value == selected_month) option.selected = true;
}

const form = document.getElementById("form");
monthSelect.addEventListener("change", () => {
  form.submit();
});
yearSelect.addEventListener("change", () => {
  form.submit();
});
