from flask import Flask, render_template, request, redirect, url_for, jsonify
#from flask import Flask, request,
import sqlite3
import socket

hostname = socket.gethostname()
ip_address = socket.gethostbyname(hostname)
print("IP Address:", ip_address)

app = Flask(__name__)
DB_NAME = 'database.db'


def init_db():
    with sqlite3.connect(DB_NAME) as conn:
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
        conn.commit()


@app.route('/')
def index():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('SELECT * FROM kelas')
    kelas = c.fetchall()
    c.execute('''
        SELECT barang.id, barang.nama_barang, barang.jumlah, kelas.nama_kelas 
        FROM barang LEFT JOIN kelas ON barang.id_kelas = kelas.id
    ''')
    barang = c.fetchall()
    conn.close()
    return render_template('index.html', kelas=kelas, barang=barang)


@app.route('/tambah_kelas', methods=['POST'])
def tambah_kelas():
    nama = request.form['nama_kelas']
    wali = request.form['wali_kelas']
    conn = sqlite3.connect(DB_NAME)
    conn.execute('INSERT INTO kelas (nama_kelas, wali_kelas) VALUES (?, ?)', (nama, wali))
    conn.commit()
    return redirect(url_for('index'))


@app.route('/hapus_kelas/<int:id>')
def hapus_kelas(id):
    conn = sqlite3.connect(DB_NAME)
    conn.execute('DELETE FROM kelas WHERE id = ?', (id,))
    conn.commit()
    return redirect(url_for('index'))


@app.route('/tambah_barang', methods=['POST'])
def tambah_barang():
    nama = request.form['nama_barang']
    jumlah = request.form['jumlah']
    id_kelas = request.form['id_kelas']
    conn = sqlite3.connect(DB_NAME)
    conn.execute('INSERT INTO barang (nama_barang, jumlah, id_kelas) VALUES (?, ?, ?)', (nama, jumlah, id_kelas))
    conn.commit()
    return redirect(url_for('index'))


@app.route('/hapus_barang/<int:id>')
def hapus_barang(id):
    conn = sqlite3.connect(DB_NAME)
    conn.execute('DELETE FROM barang WHERE id = ?', (id,))
    conn.commit()
    return redirect(url_for('index'))

@app.route('/edit_kelas/<int:id>', methods=['GET', 'POST'])
def edit_kelas(id):
    if request.method == 'POST':
        nama_kelas = request.form['nama_kelas']
        wali_kelas = request.form['wali_kelas']
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("UPDATE kelas SET nama_kelas = ?, wali_kelas = ? WHERE id = ?", (nama_kelas, wali_kelas, id))
        conn.commit()
        conn.close()
        return redirect('/')
    else:
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("SELECT * FROM kelas WHERE id = ?", (id,))
        data = c.fetchone()
        conn.close()
        return render_template('edit_kelas.html', data=data)

@app.route('/edit_barang/<int:id>', methods=['GET', 'POST'])
def edit_barang(id):
    if request.method == 'POST':
        nama_barang = request.form['nama_barang']
        jumlah = request.form['jumlah']
        id_kelas = request.form['id_kelas']
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("UPDATE barang SET nama_barang = ?, jumlah = ?, id_kelas = ? WHERE id = ?", (nama_barang, jumlah, id_kelas, id))
        conn.commit()
        conn.close()
        return redirect('/')
    else:
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("SELECT * FROM barang WHERE id = ?", (id,))
        barang = c.fetchone()
        kelas = c.execute("SELECT * FROM kelas").fetchall()
        conn.close()
        return render_template('edit_barang.html', barang=barang, kelas=kelas)

if __name__ == '__main__':
    init_db()
    #app.run(debug=True)
    app.run(host='0.0.0.0', port=5000, debug=True)

