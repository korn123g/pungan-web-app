import sqlite3
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)
DATABASE = 'pungan_db.db'

# --- ฐานข้อมูล (Database Functions) ---

def get_db_connection():
    """เชื่อมต่อและสร้างฐานข้อมูล (ถ้ายังไม่มี)"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # ทำให้สามารถเข้าถึงคอลัมน์เหมือน dict
    return conn

def init_db():
    """สร้างตาราง 'needs' หากยังไม่มี"""
    conn = get_db_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS needs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            type TEXT NOT NULL,  -- 'Item' หรือ 'Volunteer'
            description TEXT NOT NULL,
            contact TEXT NOT NULL,
            status TEXT DEFAULT 'Open' -- 'Open' หรือ 'Fulfilled'
        );
    """)
    conn.commit()
    conn.close()

# เรียกฟังก์ชันสร้างฐานข้อมูลเมื่อเริ่มต้น
init_db()

# --- Routing (เส้นทาง) ---

@app.route('/')
def index():
    """หน้าหลัก: แสดงรายการความต้องการทั้งหมด"""
    conn = get_db_connection()
    # ดึงเฉพาะรายการที่สถานะเป็น 'Open'
    needs = conn.execute('SELECT * FROM needs WHERE status = "Open" ORDER BY id DESC').fetchall()
    conn.close()
    return render_template('index.html', needs=needs)

@app.route('/create', methods=('GET', 'POST'))
def create():
    """หน้าสำหรับสร้างความต้องการใหม่"""
    if request.method == 'POST':
        title = request.form['title']
        type = request.form['type']
        description = request.form['description']
        contact = request.form['contact']
        
        if not title or not description:
            # เพิ่มการจัดการ Error ง่ายๆ
            # ในการพัฒนาจริง ควรแสดงข้อความ Error บนหน้าเว็บ
            return redirect(url_for('create'))

        conn = get_db_connection()
        conn.execute('INSERT INTO needs (title, type, description, contact) VALUES (?, ?, ?, ?)',
                     (title, type, description, contact))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    
    return render_template('create.html')

@app.route('/fulfill/<int:need_id>')
def fulfill(need_id):
    """ฟังก์ชันสำหรับเปลี่ยนสถานะเป็น 'Fulfilled' (สำเร็จแล้ว)"""
    conn = get_db_connection()
    conn.execute('UPDATE needs SET status = "Fulfilled" WHERE id = ?', (need_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)