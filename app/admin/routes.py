from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import os
from werkzeug.utils import secure_filename
import mysql.connector
from werkzeug.security import check_password_hash

admin = Blueprint('admin', __name__, template_folder='templates')

def get_db():
    """Fungsi helper untuk koneksi ke database MySQL."""
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
        database='web_kominfo'
    )

@admin.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password_input = request.form['password']

        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        # FIX: Mengganti 'name' dengan 'usernama' sesuai dengan struktur tabel Anda
        cursor.execute('SELECT * FROM users WHERE usernama = %s', (username,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user and check_password_hash(user['password'], password_input):
            # FIX: Menyesuaikan kunci session dengan nama kolom yang benar
            session['user'] = user['usernama'] 
            return redirect(url_for('admin.dashboard'))
        else:
            return "Login Gagal. Periksa kembali username dan password Anda.", 401
    return render_template('admin/login.html')


@admin.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('admin.login'))
    return render_template('admin/dashboard.html')

@admin.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('admin.login'))

# ------------------ SENSOR KOMENTAR ------------------
@admin.route('/sensor_komentar')
def sensor_komentar():
    if 'user' not in session:
        return redirect(url_for('admin.login'))

    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM sensor_komentar')
    data = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('admin/sensor_komentar.html', data=data)

@admin.route('/tambah_sensor', methods=['POST'])
def tambah_sensor():
    if 'user' not in session:
        return redirect(url_for('admin.login'))

    kata = request.form['kata_jelek']
    ganti = request.form['ganti_menjadi']

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO sensor_komentar (kata_jelek, ganti_menjadi) VALUES (%s, %s)',
        (kata, ganti)
    )
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('admin.sensor_komentar'))


@admin.route('/edit_sensor/<int:id>', methods=['POST'])
def edit_sensor(id):
    if 'user' not in session:
        return redirect(url_for('admin.login'))

    kata = request.form['kata_jelek']
    ganti = request.form['ganti_menjadi']

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        'UPDATE sensor_komentar SET kata_jelek=%s, ganti_menjadi=%s WHERE id=%s',
        (kata, ganti, id)
    )
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('admin.sensor_komentar'))



@admin.route('/hapus_sensor/<int:id>')
def hapus_sensor(id):
    if 'user' not in session:
        return redirect(url_for('admin.login'))

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM sensor_komentar WHERE id=%s', (id,))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('admin.sensor_komentar'))


# ------------------ KATEGORI BERITA------------------
@admin.route('/kategori_berita')
def kategori_berita():
    db = get_db()
    cur = db.cursor(dictionary=True)
    cur.execute("SELECT id, nama_kategori, link, artikel, posisi, aktif FROM kategori_berita ORDER BY posisi, id")
    kategori = cur.fetchall()
    cur.close()
    db.close()
    return render_template('admin/kategori_berita.html', kategori=kategori)

@admin.route('/tambah_kategori', methods=['POST'])
def tambah_kategori():
    nama   = request.form.get('nama_kategori', '').strip()
    link   = request.form.get('link', '').strip()
    posisi = request.form.get('posisi', '0').strip()
    aktif  = request.form.get('aktif', 'Y').strip()

     # fallback angka
    try:
        posisi_int = int(posisi)
    except ValueError:
        posisi_int = 0

    db = get_db()
    cur = db.cursor()
    cur.execute(
        "INSERT INTO kategori_berita (nama_kategori, link, artikel, posisi, aktif) VALUES (%s, %s, %s, %s, %s)",
        (nama, link, 0, posisi_int, aktif)
    )
    db.commit()
    cur.close()
    db.close()
    return redirect(url_for('admin.kategori_berita'))

@admin.route('/edit_kategori/<int:id>', methods=['POST'])
def edit_kategori(id):
    nama   = request.form.get('nama_kategori', '').strip()
    link   = request.form.get('link', '').strip()
    posisi = request.form.get('posisi', '0').strip()
    aktif  = request.form.get('aktif', 'Y').strip()

    try:
        posisi_int = int(posisi)
    except ValueError:
        posisi_int = 0

    db = get_db()
    cur = db.cursor()
    cur.execute(
        "UPDATE kategori_berita SET nama_kategori=%s, link=%s, posisi=%s, aktif=%s WHERE id=%s",
        (nama, link, posisi_int, aktif, id)
    )
    db.commit()
    cur.close()
    db.close()
    return redirect(url_for('admin.kategori_berita'))

@admin.route('/hapus_kategori/<int:id>')
def hapus_kategori(id):
    db = get_db()
    cur = db.cursor()
    cur.execute("DELETE FROM kategori_berita WHERE id=%s", (id,))
    db.commit()
    cur.close()
    db.close()
    return redirect(url_for('admin.kategori_berita'))


# ------------------ VIDEO------------------
@admin.route('/video')
def video():
    if 'user' not in session:
        return redirect(url_for('admin.login'))

    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM video ORDER BY tanggal_video DESC")
    data = cursor.fetchall()
    conn.close()
    return render_template('admin/video.html', data=data)


@admin.route('/tambah_video', methods=['POST'])
def tambah_video():
    judul = request.form['judul']
    tanggal = request.form['tanggal']
    playlist = request.form['playlist']

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO video (judul_video, tanggal_video, playlist) VALUES (%s, %s, %s)",
        (judul, tanggal, playlist)
    )
    conn.commit()
    conn.close()
    return redirect(url_for('admin.video'))


@admin.route('/edit_video/<int:id>', methods=['POST'])
def edit_video(id):
    judul = request.form['judul']
    tanggal = request.form['tanggal']
    playlist = request.form['playlist']

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE video SET judul_video=%s, tanggal_video=%s, playlist=%s WHERE id=%s",
        (judul, tanggal, playlist, id)
    )
    conn.commit()
    conn.close()
    return redirect(url_for('admin.video'))


@admin.route('/hapus_video/<int:id>')
def hapus_video(id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM video WHERE id=%s", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin.video'))


# ------------------ TAG BERITA ------------------
@admin.route('/tag_berita')
def tag_berita():
    db = get_db()
    cur = db.cursor(dictionary=True)
    cur.execute("SELECT id, nama_tag, link FROM tag_berita ORDER BY id DESC")
    tag = cur.fetchall()
    cur.close()
    db.close()
    return render_template('admin/tag_berita.html', tag=tag)

@admin.route('/tambah_tag', methods=['POST'])
def tambah_tag():
    nama = request.form.get('nama_tag', '').strip()
    link = request.form.get('link', '').strip()

    db = get_db()
    cur = db.cursor()
    cur.execute(
        "INSERT INTO tag_berita (nama_tag, link) VALUES (%s, %s)",
        (nama, link)
    )
    db.commit()
    cur.close()
    db.close()
    return redirect(url_for('admin.tag_berita'))

@admin.route('/edit_tag/<int:id>', methods=['POST'])
def edit_tag(id):
    nama = request.form.get('nama_tag', '').strip()
    link = request.form.get('link', '').strip()

    db = get_db()
    cur = db.cursor()
    cur.execute(
        "UPDATE tag_berita SET nama_tag=%s, link=%s WHERE id=%s",
        (nama, link, id)
    )
    db.commit()
    cur.close()
    db.close()
    return redirect(url_for('admin.tag_berita'))

@admin.route('/hapus_tag/<int:id>')
def hapus_tag(id):
    db = get_db()
    cur = db.cursor()
    cur.execute("DELETE FROM tag_berita WHERE id=%s", (id,))
    db.commit()
    cur.close()
    db.close()
    return redirect(url_for('admin.tag_berita'))





# ------------------ JAJAk PENDAPAT ------------------
@admin.route('/jajak_pendapat')
def jajak_pendapat():
    db = get_db()
    cur = db.cursor(dictionary=True)
    cur.execute("SELECT id, pilihan, status, rating, aktif FROM jejak_pendapat ORDER BY id DESC")
    polling = cur.fetchall()
    cur.close()
    db.close()
    return render_template('admin/jejak_pendapat.html', polling=polling)

@admin.route('/tambah_polling', methods=['POST'])
def tambah_polling():
    pilihan = request.form.get('pilihan', '').strip()
    status  = request.form.get('status', '').strip()
    rating  = request.form.get('rating', '0').strip()
    aktif   = request.form.get('aktif', 'N').strip()

    try:
        rating_int = int(rating)
    except ValueError:
        rating_int = 0

    db = get_db()
    cur = db.cursor()
    cur.execute(
        "INSERT INTO jejak_pendapat (pilihan, status, rating, aktif) VALUES (%s, %s, %s, %s)",
        (pilihan, status, rating_int, aktif)
    )
    db.commit()
    cur.close()
    db.close()
    return redirect(url_for('admin.jajak_pendapat'))

@admin.route('/edit_polling/<int:id>', methods=['POST'])
def edit_polling(id):
    pilihan = request.form.get('pilihan', '').strip()
    status  = request.form.get('status', '').strip()
    rating  = request.form.get('rating', '0').strip()
    aktif   = request.form.get('aktif', 'N').strip()

    try:
        rating_int = int(rating)
    except ValueError:
        rating_int = 0

    db = get_db()
    cur = db.cursor()
    cur.execute(
        "UPDATE jejak_pendapat SET pilihan=%s, status=%s, rating=%s, aktif=%s WHERE id=%s",
        (pilihan, status, rating_int, aktif, id)
    )
    db.commit()
    cur.close()
    db.close()
    return redirect(url_for('admin.jajak_pendapat'))

@admin.route('/hapus_polling/<int:id>')
def hapus_polling(id):
    db = get_db()
    cur = db.cursor()
    cur.execute("DELETE FROM jejak_pendapat WHERE id=%s", (id,))
    db.commit()
    cur.close()
    db.close()
    return redirect(url_for('admin.jajak_pendapat'))


# ---------------- MANAGEMEN USERS ----------------
@admin.route('/manajemen_users')
def manajemen_users():
    if 'user' not in session:  # pastikan login dulu
        return redirect(url_for('admin.login'))

    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users ORDER BY created_at DESC")
    users = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('admin/manajemen_users.html', users=users)


# Tambah User
@admin.route('/tambah_user', methods=['POST'])
def tambah_user():
    if 'user' not in session:
        return redirect(url_for('admin.login'))

    Username = request.form['username']
    Nama_Lengkap = request.form['nama_lengkap']
    Email = request.form['email']
    level = request.form['level']
    Blokir = request.form['status']

    Foto = request.files.get('foto')
    Foto_filename = None
    if Foto and Foto.filename:
        Foto_filename = secure_filename(Foto.filename)
        Foto.save(os.path.join('static', 'img', Foto_filename))

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO users (Username, Nama_Lengkap, Email, level, Blokir, Foto)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (Username, Nama_Lengkap, Email, level, Blokir, Foto_filename))
    conn.commit()
    cursor.close()
    conn.close()

    flash('User berhasil ditambahkan!', 'success')
    return redirect(url_for('admin.manajemen_users'))
# Edit User
@admin.route('/edit_user/<int:id>', methods=['POST'])
def edit_user(id):
    if 'user' not in session:
        return redirect(url_for('admin.login'))


    Username = request.form['username']
    Nama_Lengkap = request.form['nama_lengkap']
    Email = request.form['email']
    level = request.form['level']
    Blokir = request.form['status']

    Foto = request.files.get('foto')
    Foto_filename = None
    if Foto and Foto.filename:
        Foto_filename = secure_filename(Foto.filename)
        Foto.save(os.path.join('static', 'img', Foto_filename))

    conn = get_db()
    cursor = conn.cursor()

    if Foto_filename:
        cursor.execute("""
            UPDATE users 
            SET Username=%s, Nama_Lengkap=%s, Email=%s, level=%s, Blokir=%s, Foto=%s 
            WHERE id=%s
        """, (Username, Nama_Lengkap, Email, level, Blokir, Foto_filename, id))
    else:
        cursor.execute("""
            UPDATE users 
            SET Username=%s, Nama_Lengkap=%s, Email=%s, level=%s, Blokir=%s 
            WHERE id=%s
        """, (Username, Nama_Lengkap, Email, level, Blokir, id))
    
    conn.commit()
    cursor.close()
    conn.close()

    flash('User berhasil diupdate!', 'success')
    return redirect(url_for('admin.manajemen_users'))



# Hapus User
@admin.route('/hapus_user/<id>')
def hapus_user(id):
    if 'user' not in session:
        return redirect(url_for('admin.login'))

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE Username=%s", (id,))
    conn.commit()
    cursor.close()
    conn.close()

    flash('User berhasil dihapus!', 'success')
    return redirect(url_for('admin.manajemen_users'))


# ---------------- TAG VIDEO----------------

@admin.route('/tag_video')
def tag_video():
    if 'user' not in session:
        return redirect(url_for('admin.login'))

    db = get_db()
    cur = db.cursor(dictionary=True)
    cur.execute("SELECT id, nama_tag, link_video, posisi, aktif FROM tag_video ORDER BY posisi, id")
    data = cur.fetchall()
    cur.close()
    db.close()
    return render_template('admin/tag_video.html', data=data)


@admin.route('/tambah_tag_video', methods=['POST'])
def tambah_tag_video():
    nama   = request.form.get('nama_tag', '').strip()
    link   = request.form.get('link_video', '').strip()
    posisi = request.form.get('posisi', '0').strip()
    aktif  = 1 if request.form.get('aktif') == '1' else 0

    try:
        posisi_int = int(posisi)
    except ValueError:
        posisi_int = 0

    db = get_db()
    cur = db.cursor()
    cur.execute(
        "INSERT INTO tag_video (nama_tag, link_video, posisi, aktif) VALUES (%s, %s, %s, %s)",
        (nama, link, posisi_int, aktif)
    )
    db.commit()
    cur.close()
    db.close()
    return redirect(url_for('admin.tag_video'))


@admin.route('/edit_tag_video/<int:id>', methods=['POST'])
def edit_tag_video(id):
    nama   = request.form.get('nama_tag', '').strip()
    link   = request.form.get('link_video', '').strip()
    posisi = request.form.get('posisi', '0').strip()
    aktif  = 1 if request.form.get('aktif') == '1' else 0

    try:
        posisi_int = int(posisi)
    except ValueError:
        posisi_int = 0

    db = get_db()
    cur = db.cursor()
    cur.execute(
        "UPDATE tag_video SET nama_tag=%s, link_video=%s, posisi=%s, aktif=%s WHERE id=%s",
        (nama, link, posisi_int, aktif, id)
    )
    db.commit()
    cur.close()
    db.close()
    return redirect(url_for('admin.tag_video'))


@admin.route('/hapus_tag_video/<int:id>', methods=['POST'])
def hapus_tag_video(id):
    db = get_db()
    cur = db.cursor()
    cur.execute("DELETE FROM tag_video WHERE id=%s", (id,))
    db.commit()
    cur.close()
    db.close()
    return redirect(url_for('admin.tag_video'))

# ---------------- DOWNLOAD AREA----------------
@admin.route('/download_area')
def download_area():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM download ORDER BY Tanggal DESC")
    daftar_file = cursor.fetchall()
    cursor.close()
    db.close()
    return render_template("admin/download_area.html", daftar_file=daftar_file)


@admin.route('/tambah_download', methods=['POST'])
def tambah_download():
    judul = request.form['judul']
    link = request.form['link']
    hits = request.form['hits']
    tanggal = request.form['tanggal']
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO download_area (Judul, Link, Hits, Tanggal) VALUES (%s, %s, %s, %s)', (judul, link, hits, tanggal))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('admin.download_area'))

@admin.route('/edit_download/<int:no>', methods=['POST'])
def edit_download(no):
    judul = request.form['judul']
    link = request.form['link']
    tanggal = request.form['tanggal']
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('UPDATE download_area SET Judul=%s, Link=%s, Tanggal=%s WHERE No=%s', (judul, link, tanggal, no))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('admin.download_area'))

@admin.route('/hapus_download/<int:no>', methods=['GET'])
def hapus_download(no):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM download WHERE No = %s", (no,))
    db.commit()
    cursor.close()
    db.close()
    flash("Data berhasil dihapus", "success")
    return redirect(url_for('admin.download_area'))


# ---------------- AGENDA----------------
@admin.route('/agenda_admin', endpoint='agenda_admin')
def agenda_admin():
    if 'user' not in session:
        return redirect(url_for('admin.login'))

    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM agenda_admin ORDER BY tgl_mulai DESC')
    data = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('admin/agenda_admin.html', data=data)

@admin.route('/tambah_agenda', methods=['POST'])
def tambah_agenda():
    if 'user' not in session:
        return redirect(url_for('admin.login'))

    tema = request.form.get('tema', '').strip()
    tgl_mulai = request.form.get('tgl_mulai', '')
    tgl_selesai = request.form.get('tgl_selesai', '')
    jam = request.form.get('jam', '').strip()

    if not all([tema, tgl_mulai, tgl_selesai, jam]):
        flash('Semua field harus diisi!', 'danger')
        return redirect(url_for('admin.agenda_admin'))

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO agenda_admin (tema, tgl_mulai, tgl_selesai, jam) VALUES (%s, %s, %s, %s)',
        (tema, tgl_mulai, tgl_selesai, jam)
    )
    conn.commit()
    cursor.close()
    conn.close()
    flash('Agenda berhasil ditambahkan!', 'success')
    return redirect(url_for('admin.agenda_admin'))

@admin.route('/edit_agenda/<int:id>', methods=['POST'])
def edit_agenda(id):
    if 'user' not in session:
        return redirect(url_for('admin.login'))

    tema = request.form.get('tema', '').strip()
    tgl_mulai = request.form.get('tgl_mulai', '')
    tgl_selesai = request.form.get('tgl_selesai', '')
    jam = request.form.get('jam', '').strip()

    if not all([tema, tgl_mulai, tgl_selesai, jam]):
        flash('Semua field harus diisi!', 'danger')
        return redirect(url_for('admin.agenda_admin'))

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        'UPDATE agenda_admin SET tema=%s, tgl_mulai=%s, tgl_selesai=%s, jam=%s WHERE id=%s',
        (tema, tgl_mulai, tgl_selesai, jam, id)
    )
    conn.commit()
    cursor.close()
    conn.close()
    flash('Agenda berhasil diubah!', 'success')
    return redirect(url_for('admin.agenda_admin'))

@admin.route('/hapus_agenda/<int:id>')
def hapus_agenda(id):
    if 'user' not in session:
        return redirect(url_for('admin.login'))

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM agenda_admin WHERE id=%s', (id,))
    conn.commit()
    cursor.close()
    conn.close()
    flash('Agenda berhasil dihapus!', 'success')
    return redirect(url_for('admin.agenda_admin'))

# ---------------- IDENTITAS WEBSITE----------------
@admin.route('/identitas_website', methods=['GET', 'POST'])
def identitas_website():
    if 'user' not in session:
        return redirect(url_for('admin.login'))

    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        # Ambil data form
        nama_website   = request.form.get('nama_website', '').strip()
        email          = request.form.get('email', '').strip()
        domain         = request.form.get('domain', '').strip()
        sosial_network = request.form.get('sosial_network', '').strip()
        no_rekening    = request.form.get('no_rekening', '').strip()
        no_telpon      = request.form.get('no_telpon', '').strip()
        meta_deskripsi = request.form.get('meta_deskripsi', '').strip()
        meta_keyword   = request.form.get('meta_keyword', '').strip()
        google_maps    = request.form.get('google_maps', '').strip()

        # Upload favicon jika ada
        favicon_file = request.files.get('favicon')
        favicon_filename = None
        if favicon_file and favicon_file.filename:
            from werkzeug.utils import secure_filename
            import os
            UPLOAD_FOLDER = 'static/uploads'
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)
            favicon_filename = secure_filename(favicon_file.filename)
            favicon_file.save(os.path.join(UPLOAD_FOLDER, favicon_filename))

        # Validasi minimal nama website dan email
        if not nama_website or not email:
            flash('Nama website dan email wajib diisi!', 'danger')
            cursor.close()
            conn.close()
            return redirect(url_for('admin.identitas_website'))

        # Cek apakah sudah ada data
        cursor.execute("SELECT * FROM identitas_website LIMIT 1")
        existing = cursor.fetchone()

        if existing:
            # Update data
            if favicon_filename:
                cursor.execute("""
                    UPDATE identitas_website
                    SET nama_website=%s, email=%s, domain=%s, sosial_network=%s,
                        no_rekening=%s, no_telpon=%s, meta_deskripsi=%s, meta_keyword=%s,
                        google_maps=%s, favicon=%s
                    WHERE id=%s
                """, (nama_website, email, domain, sosial_network, no_rekening, no_telpon,
                      meta_deskripsi, meta_keyword, google_maps, favicon_filename, existing['id']))
            else:
                cursor.execute("""
                    UPDATE identitas_website
                    SET nama_website=%s, email=%s, domain=%s, sosial_network=%s,
                        no_rekening=%s, no_telpon=%s, meta_deskripsi=%s, meta_keyword=%s,
                        google_maps=%s
                    WHERE id=%s
                """, (nama_website, email, domain, sosial_network, no_rekening, no_telpon,
                      meta_deskripsi, meta_keyword, google_maps, existing['id']))
            flash('Data identitas website berhasil diupdate!', 'success')
        else:
            # Insert data baru
            cursor.execute("""
                INSERT INTO identitas_website
                (nama_website, email, domain, sosial_network, no_rekening, no_telpon,
                meta_deskripsi, meta_keyword, google_maps, favicon)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """, (nama_website, email, domain, sosial_network, no_rekening, no_telpon,
                  meta_deskripsi, meta_keyword, google_maps, favicon_filename))
            flash('Data identitas website berhasil ditambahkan!', 'success')

        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('admin.identitas_website'))

    # GET → tampilkan data
    cursor.execute("SELECT * FROM identitas_website LIMIT 1")
    data = cursor.fetchone()
    cursor.close()
    conn.close()

    return render_template('admin/identitas_website.html', data=data)

# ---------------- BERITA---------------

# Halaman daftar berita
@admin.route('/berita')
def berita():
    if 'user' not in session:
        return redirect(url_for('admin.login'))

    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM berita ORDER BY tanggal DESC")
    daftar_berita = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('admin/berita.html', daftar_berita=daftar_berita)


# Tambah berita
@admin.route('/berita/tambah', methods=['POST'])
def tambah_berita():
    if 'user' not in session:
        return redirect(url_for('admin.login'))

    judul = request.form['judul']
    sub_judul = request.form.get('sub_judul')
    video_youtube = request.form.get('video_youtube')
    kategori = request.form.get('kategori')
    headline = request.form.get('headline')
    berita_utama = request.form.get('berita_utama')
    isi_berita = request.form.get('isi_berita')
    tag = request.form.get('tag')
    tanggal = request.form['tanggal']
    waktu_posting = request.form['waktu_posting']
    status = request.form['status']

    # Upload gambar
    gambar = None
    if 'gambar' in request.files:
        file = request.files['gambar']
        if file and file.filename != "":
            filename = secure_filename(file.filename)
            upload_path = os.path.join("static/uploads", filename)
            file.save(upload_path)
            gambar = filename

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO berita (judul, sub_judul, video_youtube, kategori, headline, berita_utama, isi_berita, gambar, tag, tanggal, waktu_posting, status)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """, (judul, sub_judul, video_youtube, kategori, headline, berita_utama, isi_berita, gambar, tag, tanggal, waktu_posting, status))
    conn.commit()
    cursor.close()
    conn.close()

    flash("Berita berhasil ditambahkan!", "success")
    return redirect(url_for('admin.berita'))


# Edit berita
@admin.route('/berita/edit/<int:id>', methods=['POST'])
def edit_berita(id):
    if 'user' not in session:
        return redirect(url_for('admin.login'))

    judul = request.form['judul']
    sub_judul = request.form.get('sub_judul')
    video_youtube = request.form.get('video_youtube')
    kategori = request.form.get('kategori')
    headline = request.form.get('headline')
    berita_utama = request.form.get('berita_utama')
    isi_berita = request.form.get('isi_berita')
    tag = request.form.get('tag')
    tanggal = request.form['tanggal']
    waktu_posting = request.form['waktu_posting']
    status = request.form['status']

    # Upload gambar baru (opsional)
    gambar = None
    if 'gambar' in request.files:
        file = request.files['gambar']
        if file and file.filename != "":
            filename = secure_filename(file.filename)
            upload_path = os.path.join("static/uploads", filename)
            file.save(upload_path)
            gambar = filename

    conn = get_db()
    cursor = conn.cursor()

    if gambar:
        cursor.execute("""
            UPDATE berita SET judul=%s, sub_judul=%s, video_youtube=%s, kategori=%s, headline=%s,
            berita_utama=%s, isi_berita=%s, gambar=%s, tag=%s, tanggal=%s, waktu_posting=%s, status=%s
            WHERE id=%s
        """, (judul, sub_judul, video_youtube, kategori, headline, berita_utama, isi_berita, gambar, tag, tanggal, waktu_posting, status, id))
    else:
        cursor.execute("""
            UPDATE berita SET judul=%s, sub_judul=%s, video_youtube=%s, kategori=%s, headline=%s,
            berita_utama=%s, isi_berita=%s, tag=%s, tanggal=%s, waktu_posting=%s, status=%s
            WHERE id=%s
        """, (judul, sub_judul, video_youtube, kategori, headline, berita_utama, isi_berita, tag, tanggal, waktu_posting, status, id))

    conn.commit()
    cursor.close()
    conn.close()

    flash("Berita berhasil diperbarui!", "success")
    return redirect(url_for('admin.berita'))
    return redirect(url_for('admin.berita'))
# ---------------- HALAMAN BARU ----------------
# Route untuk menampilkan halaman_baru
@admin.route('/halaman_baru')
def halaman_baru():
    if 'user' not in session:
        return redirect(url_for('admin.login'))
    
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT id, judul, link, tanggal_posting FROM halaman_baru ORDER BY tanggal_posting DESC')
    daftar_halaman = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('admin/halaman_baru.html', daftar_halaman=daftar_halaman)


# Tambah halaman baru
@admin.route('/tambah_halaman', methods=['POST'])
def tambah_halaman():
    if 'user' not in session:
        return redirect(url_for('admin.login'))

    judul = request.form.get('judul')
    link = request.form.get('link')
    tanggal_posting = request.form.get('tanggal_posting')

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO halaman_baru (judul, link, tanggal_posting)
        VALUES (%s, %s, %s)
    """, (judul, link, tanggal_posting))
    conn.commit()
    cursor.close()
    conn.close()

    flash("Halaman berhasil ditambahkan!", "success")
    return redirect(url_for('admin.halaman_baru'))


# Edit halaman
@admin.route('/edit_halaman/<int:id>', methods=['POST'])
def edit_halaman(id):
    if 'user' not in session:
        return redirect(url_for('admin.login'))

    judul = request.form.get('judul')
    link = request.form.get('link')
    tanggal_posting = request.form.get('tanggal_posting')

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE halaman_baru SET 
        judul=%s, link=%s, tanggal_posting=%s
        WHERE id=%s
    """, (judul, link, tanggal_posting, id))
    conn.commit()
    cursor.close()
    conn.close()

    flash("Halaman berhasil diperbarui!", "success")
    return redirect(url_for('admin.halaman_baru'))


# Hapus halaman
@admin.route('/hapus_halaman/<int:id>', methods=['POST'])
def hapus_halaman(id):
    if 'user' not in session:
        return redirect(url_for('admin.login'))

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM halaman_baru WHERE id=%s', (id,))
    conn.commit()
    cursor.close()
    conn.close()

    flash("Halaman berhasil dihapus!", "success")
    return redirect(url_for('admin.halaman_baru'))

# ---------------- ALAMAT KONTAK  ----------------
@admin.route('/alamat_kontak')
def alamat_kontak():
    if 'user' not in session:
        return redirect(url_for('admin.login'))

    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM alamat_kontak ORDER BY id DESC")
    daftar_kontak = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('admin/alamat_kontak.html', daftar_kontak=daftar_kontak)

@admin.route('/tambah_kontak', methods=['POST'])
def tambah_kontak():
    if 'user' not in session:
        return redirect(url_for('admin.login'))

    nama_kantor = request.form.get('nama_kantor')
    alamat = request.form.get('alamat')
    telepon = request.form.get('telepon')
    email = request.form.get('email')

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO alamat_kontak (nama_kantor, alamat, telepon, email)
        VALUES (%s, %s, %s, %s)
    """, (nama_kantor, alamat, telepon, email))
    conn.commit()
    cursor.close()
    conn.close()

    flash("Alamat kontak berhasil ditambahkan!", "success")
    return redirect(url_for('admin.alamat_kontak'))

@admin.route('/edit_kontak/<int:id>', methods=['POST'])
def edit_kontak(id):
    if 'user' not in session:
        return redirect(url_for('admin.login'))

    nama_kantor = request.form.get('nama_kantor')
    alamat = request.form.get('alamat')
    telepon = request.form.get('telepon')
    email = request.form.get('email')

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE alamat_kontak SET nama_kantor=%s, alamat=%s, telepon=%s, email=%s WHERE id=%s
    """, (nama_kantor, alamat, telepon, email, id))
    conn.commit()
    cursor.close()
    conn.close()

    flash("Alamat kontak berhasil diperbarui!", "success")
    return redirect(url_for('admin.alamat_kontak'))

@admin.route('/hapus_kontak/<int:id>', methods=['POST'])
def hapus_kontak(id):
    if 'user' not in session:
        return redirect(url_for('admin.login'))

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM alamat_kontak WHERE id=%s", (id,))
    conn.commit()
    cursor.close()
    conn.close()

    flash("Alamat kontak berhasil dihapus!", "success")
    return redirect(url_for('admin.alamat_kontak'))

# ---------------- KOMENTAR BERITA  ----------------
@admin.route('/komentar_berita')
def komentar_berita():
    if 'user' not in session:
        return redirect(url_for('admin.login'))

    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM komentar_berita ORDER BY tanggal_komentar DESC")
    daftar_komentar = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('admin/komentar_berita.html', daftar_komentar=daftar_komentar)

@admin.route('/tambah_komentar', methods=['POST'])
def tambah_komentar():
    if 'user' not in session:
        return redirect(url_for('admin.login'))

    nama = request.form['nama_komentator']
    isi = request.form['isi_komentar']
    tanggal = request.form['tanggal_komentar']

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO komentar_berita (nama_komentator, isi_komentar, tanggal_komentar) VALUES (%s, %s, %s)",
        (nama, isi, tanggal)
    )
    conn.commit()
    cursor.close()
    conn.close()

    return redirect(url_for('admin.komentar_berita'))

@admin.route('/edit_komentar/<int:id>', methods=['POST'])
def edit_komentar(id):
    if 'user' not in session:
        return redirect(url_for('admin.login'))

    nama = request.form['nama_komentator']
    isi = request.form['isi_komentar']
    tanggal = request.form['tanggal_komentar']

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE komentar_berita SET nama_komentator=%s, isi_komentar=%s, tanggal_komentar=%s WHERE id=%s",
        (nama, isi, tanggal, id)
    )
    conn.commit()
    cursor.close()
    conn.close()

    return redirect(url_for('admin.komentar_berita'))

@admin.route('/hapus_komentar/<int:id>', methods=['POST'])
def hapus_komentar(id):
    if 'user' not in session:
        return redirect(url_for('admin.login'))

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM komentar_berita WHERE id=%s", (id,))
    conn.commit()
    cursor.close()
    conn.close()

    return redirect(url_for('admin.komentar_berita'))

# ---------------- PLAYLIST VIDEO  ----------------

UPLOAD_FOLDER = os.path.join(os.getcwd(), "app", "static", "uploads", "playlist")
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# ================================
# ROUTE: Daftar Playlist Video
# ================================
@admin.route('/playlist_video')
def playlist_video():
    if 'user' not in session:
        return redirect(url_for('admin.login'))

    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT id, judul_playlist, cover,
               CASE WHEN aktif = '1' THEN 'Aktif' ELSE 'Nonaktif' END AS status,
               aktif
        FROM playlist_video
        ORDER BY id DESC
    """)
    daftar_playlist = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('admin/playlist_video.html', daftar_playlist=daftar_playlist)

# ================================
# ROUTE: Tambah Playlist
# ================================
@admin.route('/tambah_playlist', methods=['POST'])
def tambah_playlist():
    if 'user' not in session:
        return redirect(url_for('admin.login'))

    judul = request.form['judul']
    aktif = request.form['aktif']
    cover_file = request.files.get('cover')

    cover_filename = None
    if cover_file and cover_file.filename != '':
        cover_filename = secure_filename(cover_file.filename)
        cover_file.save(os.path.join(UPLOAD_FOLDER, cover_filename))

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
    "INSERT INTO playlist_video (judul_playlist, cover, aktif) VALUES (%s, %s, %s)",
    (judul, cover_filename, aktif)
)
    conn.commit()
    cursor.close()
    conn.close()

    flash("Playlist berhasil ditambahkan!", "success")
    return redirect(url_for('admin.playlist_video'))


# ================================
# ROUTE: Edit Playlist
# ================================
@admin.route('/edit_playlist/<int:id>', methods=['POST'])
def edit_playlist(id):
    if 'user' not in session:
        return redirect(url_for('admin.login'))

    judul = request.form.get('judul')
    aktif = request.form.get('aktif', '0')  # default 0 kalau checkbox tidak dicentang
    cover_file = request.files.get('cover')

    conn = get_db()
    cursor = conn.cursor()

    if cover_file and cover_file.filename.strip() != '':
        cover_filename = secure_filename(cover_file.filename)
        cover_path = os.path.join(UPLOAD_FOLDER, cover_filename)
        cover_file.save(cover_path)

        cursor.execute(
            "UPDATE playlist_video SET judul_playlist=%s, cover=%s, aktif=%s WHERE id=%s",
            (judul, cover_filename, aktif, id)
        )
    else:
        cursor.execute(
            "UPDATE playlist_video SET judul_playlist=%s, aktif=%s WHERE id=%s",
            (judul, aktif, id)
        )

    conn.commit()
    cursor.close()
    conn.close()

    flash("Playlist berhasil diperbarui!", "success")
    return redirect(url_for('admin.playlist_video'))


# ================================
# ROUTE: Hapus Playlist
# ================================
@admin.route('/hapus_playlist/<int:id>', methods=['POST'])
def playlist_delete(id):
    if 'user' not in session:
        return redirect(url_for('admin.login'))

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM playlist WHERE id=%s", (id,))
    conn.commit()
    cursor.close()
    conn.close()

    flash("Playlist berhasil dihapus!", "success")
    return redirect(url_for('admin.playlist_video'))
@admin.route('/komentar_video')
def komentar_video():
    if 'user' not in session:
        return redirect(url_for('admin.login'))

    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT kv.id, kv.isi_komentar, kv.tanggal, v.judul AS judul_video
        FROM komentar_video kv
        JOIN video v ON kv.video_id = v.id
        ORDER BY kv.id DESC
    """)
    daftar_komentar = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('admin/komentar_video.html', daftar_komentar=daftar_komentar)
# ---------------- HALAMAN BARU ----------------
# ---------------- HALAMAN BARU ----------------
# ---------------- HALAMAN BARU ----------------
# ---------------- HALAMAN BARU ----------------
# ---------------- HALAMAN BARU ----------------
