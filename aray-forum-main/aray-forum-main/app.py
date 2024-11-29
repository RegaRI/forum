from flask import Flask, render_template, request, redirect, url_for, session, flash
import MySQLdb

app = Flask(__name__)
app.secret_key = 'secret'

db_config = {
    "host": "localhost",
    "user": "root",
    "passwd": "kalitengah",
    "db": "users_db"
}

def get_db_connection():
    return MySQLdb.connect(**db_config)

# Membuat tabel
def create_table():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                password VARCHAR(200) NOT NULL
            );
        """)
        conn.commit()
    except Exception as e:
        print(f"Error creating table: {e}")
    finally:
        cursor.close()
        conn.close()

create_table()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register', methods=['POST'])
def register():
    name = request.form.get('name')
    email = request.form.get('email')
    password = request.form.get('password')

    if not name or not email or not password:
        flash('Semua kolom harus diisi!')
        return redirect(url_for('home'))

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Periksa apakah email sudah terdaftar
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        if cursor.fetchone():
            flash('Email sudah terdaftar!')
            return redirect(url_for('home'))

        # Insert user baru
        cursor.execute(
            "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)",
            (name, email, password)
        )
        conn.commit()
        flash('Registrasi berhasil!')
    except Exception as e:
        flash(f'Error: {e}')
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('home'))

@app.route('/login', methods=['POST'])
def login():
    email = request.form.get('email')
    password = request.form.get('password')

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Periksa apakah email dan password cocok
        cursor.execute("SELECT id, name FROM users WHERE email = %s AND password = %s", (email, password))
        user = cursor.fetchone()
        if user:
            session['user_id'] = user[0]
            flash(f'Selamat datang, {user[1]}!')
            return redirect(url_for('user_home'))
        else:
            flash('Email atau password salah!')
    except Exception as e:
        flash(f'Error: {e}')
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('home'))

@app.route('/home')
def user_home():
    user_id = session.get('user_id')
    if user_id:
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            # Ambil data user
            cursor.execute("SELECT name FROM users WHERE id = %s", (user_id,))
            user = cursor.fetchone()
            return render_template('home.html', user=user[0] if user else None)
        except Exception as e:
            flash(f'Error: {e}')
        finally:
            cursor.close()
            conn.close()
    return redirect(url_for('home'))

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Berhasil logout!')
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
