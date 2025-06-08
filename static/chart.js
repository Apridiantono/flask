// Cek plugin gauge sudah load
console.log("Chart:", Chart);
console.log("Gauge plugin:", window.ChartjsChartGauge);

if (window.ChartjsChartGauge) {
  // Daftarkan controller dan elemen gauge
  Chart.register(window.ChartjsChartGauge.GaugeController, window.ChartjsChartGauge.ArcElement);
} else {
  console.error("Gauge plugin belum ter-load!");
}

// Inisialisasi gauge suhu
const ctxSuhu = document.getElementById("gaugeSuhu").getContext("2d");
const suhuGauge = new Chart(ctxSuhu, {
  type: "gauge",
  data: {
    labels: ["Dingin", "Normal", "Panas"],
    datasets: [{
      value: 25,
      data: [15, 20, 15],
      backgroundColor: ["blue", "green", "red"]
    }]
  },
  options: {
    responsive: true,
    needle: {
      radiusPercentage: 2,
      widthPercentage: 3,
      lengthPercentage: 80,
      color: "black"
    },
    valueLabel: {
      display: true,
      formatter: (val) => val + " °C"
    },
    plugins: {
      legend: { display: false }
    },
    scales: {
      r: {
        min: 0,
        max: 50
      }
    }
  }
});

// Update nilai suhu secara simulasi setiap 3 detik
setInterval(() => {
  const newVal = Math.round(Math.random() * 50);
  suhuGauge.data.datasets[0].value = newVal;
  suhuGauge.update();

  document.getElementById("suhu").textContent = newVal + " °C";
}, 3000);
