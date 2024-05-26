const ctx = document.getElementById("availability_graph");

new Chart(ctx, {
  type: "line",
  data: {
    labels: days,
    datasets: [
      {
        label: "Availability",
        data: health_statuses,
        borderWidth: 1,
      },
    ],
  },
  options: {
    scales: {
      y: {
        beginAtZero: true,
      },
    },
  },
});
