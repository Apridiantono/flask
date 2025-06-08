function navigateTo(sectionId) {
  document.querySelectorAll('main > section').forEach(section => {
    section.style.display = 'none';
  });
  const target = document.getElementById(sectionId);
  if (target) {
    target.style.display = 'block';
  }
}

// ================== FETCH DATA DARI FLASK ==================
async function updateSensorData() {
  try {
    const response = await fetch('http://192.168.0.114:5000/api/monitor');
    const data = await response.json();

    updateSuhuDisplay(data.suhu);
    document.getElementById('kelembapan').textContent = `${data.kelembapan} %`;
    document.getElementById('arus').textContent = `${data.arus} A`;
    document.getElementById('gerakan').textContent = data.gerakan ? 'Ada Orang' : 'Kosong';

    updateDeviceStatus('lampu', data.lampu);
    updateDeviceStatus('kipas1', data.kipas1);
    updateDeviceStatus('kipas2', data.kipas2);

  } catch (error) {
    console.error('Gagal mengambil data sensor:', error);
  }
}

// ================== TAMPILAN SUHU & WARNA ==================
function updateSuhuDisplay(nilai) {
  const suhuEl = document.getElementById('suhu');
  const cardEl = document.getElementById('suhu-card');

  suhuEl.textContent = `${nilai} °C`;
  cardEl.classList.remove('bg-success', 'bg-warning', 'bg-danger', 'text-white');

  if (nilai < 27) {
    cardEl.classList.add('bg-success', 'text-white');
  } else if (nilai >= 27 && nilai <= 29) {
    cardEl.classList.add('bg-warning');
  } else {
    cardEl.classList.add('bg-danger', 'text-white');
  }
}

// ================== STATUS PERANGKAT (TOMBOL) ==================
function updateDeviceStatus(device, status) {
  const btn = document.getElementById(`btn-${device}`);
  if (!btn) return;

  btn.textContent = `${device.toUpperCase()}: ${status ? "ON" : "OFF"}`;
  btn.classList.toggle("btn-success", status);
  btn.classList.toggle("btn-secondary", !status);
}

// ================== KONTROL MANUAL PERANGKAT ==================
async function toggleDevice(device) {
  const btn = document.getElementById(`btn-${device}`);
  const isOn = btn.textContent.includes("ON");
  const action = isOn ? 'off' : 'on';

  try {
    const response = await fetch(`http://192.168.0.115:5000/api/kontrol?device=${device}&action=${action}`);
    const result = await response.json();

    if (result.status === 'ok') {
      updateSensorData(); // Refresh tampilan setelah kontrol
    }
  } catch (error) {
    console.error(`Gagal mengontrol ${device}:`, error);
  }
}

// ================== GRAFIK ARUS ==================
let chart;
function initChart() {
  const ctx = document.getElementById("arusChart").getContext("2d");
  chart = new Chart(ctx, {
    type: "line",
    data: {
      labels: Array.from({ length: 10 }, (_, i) => i + 1),
      datasets: [{
        label: "Arus (A)",
        data: Array(10).fill(0),
        borderColor: "blue",
        tension: 0.3
      }]
    },
    options: {
      animation: false,
      scales: { y: { beginAtZero: true } }
    }
  });
}

function updateChartData() {
  if (chart) {
    const newValue = parseFloat(document.getElementById('arus').textContent) || 0;
    chart.data.datasets[0].data.shift();
    chart.data.datasets[0].data.push(newValue);
    chart.update();
  }
}

// ================== INISIALISASI ==================
window.onload = () => {
  navigateTo('home');
  updateSensorData();
  initChart();
  setInterval(() => {
    updateSensorData();
    updateChartData();
  }, 3000);
};
