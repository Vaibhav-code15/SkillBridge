document.addEventListener("DOMContentLoaded", () => {
  const canvas = document.getElementById("applications-chart");
  const data = document.getElementById("applications-chart-data");
  if (!canvas || !data || typeof Chart === "undefined") return;
  const rows = JSON.parse(data.textContent);
  if (!rows.length) return;
  new Chart(canvas, {
    type: "bar",
    data: {
      labels: rows.map((row) => row.status),
      datasets: [{ label: "Applications", data: rows.map((row) => row.total), backgroundColor: "#6d28d9", borderRadius: 5 }],
    },
    options: { responsive: true, plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true, ticks: { precision: 0 } } } },
  });
});
