from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_cors import CORS
from datetime import datetime
import sqlite3
import socket


DB_NAME = 'database.db'
hostname = socket.gethostname()
ip_address = socket.gethostbyname(hostname)
print("IP Address:", ip_address)

app = Flask(__name__)
CORS(app)

# Menyimpan data sensor terbaru
sensor_data = {
    'suhu': 0,
    'kelembapan': 0,
    'arus': 0,
    'lampu': 0,
    'kipas1': 0,
    'kipas2': 0,
    'gerakan': 0
}

# Endpoint POST dari ESP32
@app.route('/api/sensor', methods=['POST'])
def receive_sensor_data():
    global sensor_data
    data = request.get_json()
    if data:
        sensor_data.update(data)
        print("Data diterima:", data)

        # Simpan ke database
        conn = get_db_connection()
        conn.execute('''
            INSERT INTO log_sensor (suhu, kelembapan, arus, lampu, kipas1, kipas2, gerakan)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            data.get('suhu', 0),
            data.get('kelembapan', 0),
            data.get('arus', 0),
            data.get('lampu', 0),
            data.get('kipas1', 0),
            data.get('kipas2', 0),
            data.get('gerakan', 0)
        ))
        conn.commit()

        # Hapus data sensor kecuali 10 terakhir berdasarkan timestamp terbaru
        conn.execute('''
                    DELETE FROM log_sensor 
                    WHERE id NOT IN (
                        SELECT id FROM log_sensor ORDER BY timestamp DESC LIMIT 10
                    )
                ''')
        conn.commit()
        conn.close()

        return jsonify({'status': 'ok'})
    else:
        return jsonify({'status': 'error', 'message': 'No data received'}), 400


# Endpoint GET untuk memonitor data
@app.route('/api/monitor', methods=['GET'])
def monitor():
    return jsonify(sensor_data)



# Membuat database
def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row  # agar bisa akses data pake nama kolom
    return conn

def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS kelas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nama_kelas TEXT NOT NULL,
            wali_kelas TEXT NOT NULL
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS barang (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nama_barang TEXT NOT NULL,
            jumlah INTEGER NOT NULL,
            id_kelas INTEGER,
            FOREIGN KEY (id_kelas) REFERENCES kelas(id)
        )
    ''')

    # 🆕 Tabel untuk menyimpan data sensor
    c.execute('''
            CREATE TABLE IF NOT EXISTS log_sensor (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                suhu REAL,
                kelembapan REAL,
                arus REAL,
                lampu INTEGER,
                kipas1 INTEGER,
                kipas2 INTEGER,
                gerakan INTEGER
            )
        ''')

    conn.commit()
    conn.close()

@app.route('/')
def index():
    return render_template('index.html')
    #return render_template('gauge.html')


@app.route('/inventaris')
def inventaris():
    conn = get_db_connection()
    kelas = conn.execute('SELECT * FROM kelas').fetchall()
    barang = conn.execute('''
        SELECT barang.id, barang.nama_barang, barang.jumlah, kelas.nama_kelas 
        FROM barang LEFT JOIN kelas ON barang.id_kelas = kelas.id
    ''').fetchall()
    conn.close()
    return render_template('index.html', kelas=kelas, barang=barang)

@app.route('/tambah_kelas', methods=['POST'])
def tambah_kelas():
    nama = request.form['nama_kelas']
    wali = request.form['wali_kelas']
    conn = get_db_connection()
    conn.execute('INSERT INTO kelas (nama_kelas, wali_kelas) VALUES (?, ?)', (nama, wali))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/hapus_kelas/<int:id>')
def hapus_kelas(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM kelas WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/tambah_barang', methods=['POST'])
def tambah_barang():
    nama = request.form['nama_barang']
    jumlah = request.form.get('jumlah', 0)
    id_kelas = request.form.get('id_kelas', None)
    try:
        jumlah = int(jumlah)
    except:
        jumlah = 0
    if id_kelas == '':
        id_kelas = None
    else:
        id_kelas = int(id_kelas) if id_kelas else None

    conn = get_db_connection()
    conn.execute('INSERT INTO barang (nama_barang, jumlah, id_kelas) VALUES (?, ?, ?)', (nama, jumlah, id_kelas))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/hapus_barang/<int:id>')
def hapus_barang(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM barang WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/edit_kelas/<int:id>', methods=['GET', 'POST'])
def edit_kelas(id):
    conn = get_db_connection()
    if request.method == 'POST':
        nama_kelas = request.form['nama_kelas']
        wali_kelas = request.form['wali_kelas']
        conn.execute("UPDATE kelas SET nama_kelas = ?, wali_kelas = ? WHERE id = ?", (nama_kelas, wali_kelas, id))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    else:
        data = conn.execute("SELECT * FROM kelas WHERE id = ?", (id,)).fetchone()
        conn.close()
        return render_template('edit_kelas.html', data=data)

@app.route('/edit_barang/<int:id>', methods=['GET', 'POST'])
def edit_barang(id):
    conn = get_db_connection()
    if request.method == 'POST':
        nama_barang = request.form['nama_barang']
        jumlah = request.form.get('jumlah', 0)
        try:
            jumlah = int(jumlah)
        except:
            jumlah = 0
        id_kelas = request.form.get('id_kelas', None)
        if id_kelas == '':
            id_kelas = None
        else:
            id_kelas = int(id_kelas) if id_kelas else None
        conn.execute("UPDATE barang SET nama_barang = ?, jumlah = ?, id_kelas = ? WHERE id = ?", (nama_barang, jumlah, id_kelas, id))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    else:
        barang = conn.execute("SELECT * FROM barang WHERE id = ?", (id,)).fetchone()
        kelas = conn.execute("SELECT * FROM kelas").fetchall()
        conn.close()
        return render_template('edit_barang.html', barang=barang, kelas=kelas)

#Riwayat
@app.route('/riwayat')
def riwayat():
    conn = get_db_connection()
    log_data = conn.execute('SELECT * FROM log_sensor ORDER BY timestamp DESC LIMIT 10').fetchall()
    conn.close()

    # Ganti timestamp dari DB dengan waktu saat ini
    log = []
    now = datetime.now().strftime('%d %B %Y %H:%M:%S')
    for row in log_data:
        formatted_row = dict(row)
        formatted_row['timestamp'] = now  # Ganti dengan waktu server sekarang
        log.append(formatted_row)

    return render_template('index.html',  log=log)
    #return render_template('log_sensor.html', log=log)


if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)
