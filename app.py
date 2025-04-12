from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os

app = Flask(__name__)

# إعدادات الاتصال بقاعدة البيانات SQLite
def get_db_connection():
    conn = sqlite3.connect('employee_db.db')  # اسم قاعدة البيانات SQLite
    conn.row_factory = sqlite3.Row  # لكي نتمكن من الوصول إلى الأعمدة بالاسم
    return conn

# إنشاء قاعدة البيانات وجدول الموظفين إذا لم يكونا موجودين
def init_db():
    if not os.path.exists('employee_db.db'):  # إذا لم تكن قاعدة البيانات موجودة
        conn = sqlite3.connect('employee_db.db')
        cursor = conn.cursor()

        # إنشاء الجدول إذا لم يكن موجودًا
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS employees (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                position TEXT NOT NULL,
                department TEXT,
                phone TEXT,
                address TEXT
            )
        ''')

        conn.commit()
        conn.close()

# تنفيذ التهيئة عند بدء تشغيل التطبيق
init_db()

@app.route('/')
def index():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM employees')  # استعلام للحصول على كل الموظفين
    employees = cursor.fetchall()
    conn.close()
    return render_template('index.html', employees=employees)

@app.route('/add', methods=['GET', 'POST'])
def add_employee():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        position = request.form['position']
        department = request.form['department']
        phone = request.form['phone']
        address = request.form['address']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO employees (name, email, position, department, phone, address) VALUES (?, ?, ?, ?, ?, ?)',
                       (name, email, position, department, phone, address))
        conn.commit()
        conn.close()

        return redirect(url_for('index'))

    return render_template('add_employee.html')

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_employee(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM employees WHERE id = ?', (id,))
    employee = cursor.fetchone()

    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        position = request.form['position']
        department = request.form['department']
        phone = request.form['phone']
        address = request.form['address']

        cursor.execute('UPDATE employees SET name = ?, email = ?, position = ?, department = ?, phone = ?, address = ? WHERE id = ?',
                       (name, email, position, department, phone, address, id))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))

    conn.close()
    return render_template('edit_employee.html', employee=employee)

@app.route('/delete/<int:id>', methods=['POST'])
def delete_employee(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM employees WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/search', methods=['POST'])
def search_employee():
    search_term = request.form['search']
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM employees WHERE name LIKE ? OR position LIKE ?", ('%' + search_term + '%', '%' + search_term + '%'))
    employees = cursor.fetchall()
    conn.close()
    return render_template('index.html', employees=employees)

if __name__ == '__main__':
    app.run(debug=False)
