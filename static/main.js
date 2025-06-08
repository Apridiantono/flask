//==================== FUNCTION SESSION ===================

let chartArus; // Pastikan chartArus dideklarasikan di luar agar bisa diakses di sini

function navigateTo(sectionId) {
  const sections = ['home', 'inventaris', 'riwayat', 'kontak'];
  sections.forEach(id => {
    document.getElementById(id).style.display = 'none';
  });

  const targetSection = document.getElementById(sectionId);
  if (targetSection) {
    targetSection.style.display = 'block';

    // Jika bagian 'riwayat' ditampilkan, resize chart
    if (sectionId === 'riwayat' && chartArus) {
      setTimeout(() => {
        chartArus.resize();
      }, 100); // beri delay agar elemen benar-benar terlihat
    }
  }

  window.scrollTo({ top: 0, behavior: 'smooth' });
}

// Tampilkan 'home' saat pertama kali dimuat
document.addEventListener('DOMContentLoaded', () => {
  navigateTo('home');
});


// ================== FETCH DATA DARI FLASK ==================
async function updateSensorData() {
  try {
    //const response = await fetch('http://192.168.0.114:5000/api/monitor');
    const response = await fetch('/api/monitor');
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

//=============Load sensor==========
function loadLogSensor() {
    fetch('/api/riwayat')
      .then(response => response.json())
      .then(data => {
        const tbody = document.querySelector('#log-tbody');
        const dayaInfo = document.getElementById('daya-info');
        tbody.innerHTML = '';

        if (data.length > 0) {
          data.forEach(row => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
              <td>${row.timestamp || '-'}</td>
              <td>${parseFloat(row.suhu).toFixed(2) || '-'}</td>
              <td>${parseFloat(row.kelembapan).toFixed(2) || '-'}</td>
              <td>${parseFloat(row.arus).toFixed(2) || '-'}</td>
              <td>${row.gerakan ? 'ADA ORANG' : 'KOSONG'}</td>
            `;
            tbody.appendChild(tr);
          });

          const daya = parseFloat(data[0].arus || 0) * 220;
          dayaInfo.textContent = `🔌 Daya yang terpakai saat ini: ${daya.toFixed(2)} Watt`;
        } else {
          tbody.innerHTML = '<tr><td colspan="5" class="text-center">Tidak ada data sensor terbaru.</td>';
          dayaInfo.textContent = '';
        }
      });
}

loadLogSensor();
setInterval(loadLogSensor, 10000);

//========= Chart Pemakaian Arus / Jam
// Fungsi render chart pemakaian arus per jam
    function renderArusPerJamChart() {
      fetch('/api/arus_per_jam')
        .then(res => res.json())
        .then(data => {
          const ctx = document.getElementById('chartArusPerJam').getContext('2d');

          const labels = data.map(item => item.jam.substring(11,16)); // "HH:MM"
          const values = data.map(item => item.rata_rata_arus ? parseFloat(item.rata_rata_arus.toFixed(2)) : 0);

          if (window.arusChart) {
            window.arusChart.destroy();
          }

          window.arusChart = new Chart(ctx, {
            type: 'line',
            data: {
              labels: labels,
              datasets: [{
                label: 'Rata-rata Arus (A)',
                data: values,
                borderColor: 'rgba(54, 162, 235, 1)',
                backgroundColor: 'rgba(54, 162, 235, 0.2)',
                fill: true,
                tension: 0.3,
                pointRadius: 3,
                pointHoverRadius: 6,
              }]
            },
            options: {
              responsive: true,
              scales: {
                x: {
                  title: { display: true, text: 'Jam' }
                },
                y: {
                  beginAtZero: true,
                  title: { display: true, text: 'Arus (Ampere)' }
                }
              },
              plugins: {
                legend: { display: true, position: 'top' },
                tooltip: { mode: 'index', intersect: false }
              }
            }
          });
        });
    }

    // Load dan render semua data saat halaman siap
    loadLogSensor();
    renderArusPerJamChart();

    // Refresh tiap 10 detik
    setInterval(() => {
      loadLogSensor();
      renderArusPerJamChart();
    }, 10000);

