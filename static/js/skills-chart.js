document.addEventListener("DOMContentLoaded", () => {
  const canvas = document.getElementById("skills-chart");
  const source = document.getElementById("skills-chart-data");
  if (!canvas || !source || typeof Chart === "undefined") return;
  const skills = JSON.parse(source.textContent);
  new Chart(canvas, { type: "bar", data: { labels: skills.map((s) => s.name), datasets: [{ label: "Proficiency", data: skills.map((s) => s.level), backgroundColor: "#6d28d9", borderRadius: 6 }] }, options: { indexAxis: "y", plugins: { legend: { display: false } }, scales: { x: { min: 0, max: 4, ticks: { stepSize: 1 } } } } });
});
