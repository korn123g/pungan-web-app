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
    """สร้างตาราง 'needs_v2' หากยังไม่มี (แก้ไข: ลบคอมเมนต์ # ใน SQL ออก)"""
    conn = get_db_connection()
    # ใช้คำสั่ง SQL โดยไม่มีคอมเมนต์ # ในบล็อกคำสั่ง เพื่อให้ Render Deploy สำเร็จ
    conn.execute("""
        CREATE TABLE IF NOT EXISTS needs_v2 (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            type TEXT NOT NULL,          -- 'Item' หรือ 'Volunteer'
            description TEXT NOT NULL,
            
            -- คอลัมน์ใหม่สำหรับการติดต่อตามแบบฟอร์ม
            contact_name TEXT, 
            contact_lastname TEXT,
            contact_email TEXT NOT NULL,
            contact_phone TEXT,
            
            status TEXT DEFAULT 'Open'   -- 'Open' หรือ 'Fulfilled'
        );
    """)
    conn.commit()
    conn.close()

# เรียกฟังก์ชันสร้างฐานข้อมูลเมื่อเริ่มต้น
init_db()

# กำหนดชื่อตารางใหม่ที่จะใช้งาน
TABLE_NAME = 'needs_v2'

# --- Routing (เส้นทาง) ---

@app.route('/')
def index():
    """หน้าหลัก: แสดงรายการความต้องการทั้งหมด"""
    conn = get_db_connection()
    # ดึงข้อมูลจากตารางใหม่ needs_v2
    needs = conn.execute(f'SELECT * FROM {TABLE_NAME} WHERE status = "Open" ORDER BY id DESC').fetchall()
    conn.close()
    
    # ดึงคอลัมน์ใหม่ทั้งหมดเพื่อให้แสดงผลได้
    return render_template('index.html', needs=needs)

@app.route('/create', methods=('GET', 'POST'))
def create():
    """หน้าสำหรับสร้างความต้องการใหม่"""
    if request.method == 'POST':
        # ดึงข้อมูลจากฟอร์มใหม่ (ตาม create.html ที่ปรับปรุงแล้ว)
        title = request.form['title']
        type = request.form['type']
        description = request.form['description']
        contact_name = request.form.get('name', '')
        contact_lastname = request.form.get('lastname', '')
        contact_email = request.form['contact_email']
        contact_phone = request.form.get('contact_phone', '')
        
        if not title or not description or not contact_email:
            # การตรวจสอบขั้นต่ำ
            return redirect(url_for('create'))

        conn = get_db_connection()
        
        # INSERT ข้อมูลทั้งหมดลงในตาราง needs_v2
        conn.execute(f'''
            INSERT INTO {TABLE_NAME} 
            (title, type, description, contact_name, contact_lastname, contact_email, contact_phone) 
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (title, type, description, contact_name, contact_lastname, contact_email, contact_phone))
        
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    
    return render_template('create.html')

@app.route('/fulfill/<int:need_id>')
def fulfill(need_id):
    """ฟังก์ชันสำหรับเปลี่ยนสถานะเป็น 'Fulfilled' (สำเร็จแล้ว)"""
    conn = get_db_connection()
    conn.execute(f'UPDATE {TABLE_NAME} SET status = "Fulfilled" WHERE id = ?', (need_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

if __name__ == '__main__':
    # เมื่อรันบนเครื่องตัวเอง ให้ใช้ host='0.0.0.0' เพื่อเปิดให้เข้าถึงจากภายนอกได้ (เช่น โทรศัพท์มือถือ)
    app.run(host='0.0.0.0', debug=True)
