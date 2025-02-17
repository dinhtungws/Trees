from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

# Kết nối và tạo bảng nếu chưa có
def connect_db():
    conn = sqlite3.connect("trees.db")
    return conn

def init_db():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS trees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tree_name TEXT NOT NULL,
            species TEXT NOT NULL,
            location TEXT NOT NULL,
            age INTEGER NOT NULL,
            status TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

# Route hiển thị danh sách cây
@app.route('/')
def index():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM trees")
    trees = cursor.fetchall()
    conn.close()
    return render_template('index.html', trees=trees)

# Thêm / Sửa cây
@app.route('/add_edit', methods=['GET', 'POST'])
def add_edit():
    if request.method == 'POST':
        tree_id = request.form.get('tree_id')
        tree_name = request.form['tree_name']
        species = request.form['species']
        location = request.form['location']
        age = request.form['age']
        status = request.form['status']

        conn = connect_db()
        cursor = conn.cursor()
        
        if tree_id:  # Nếu có ID, cập nhật cây
            cursor.execute("""
                UPDATE trees SET tree_name=?, species=?, location=?, age=?, status=? WHERE id=?
            """, (tree_name, species, location, age, status, tree_id))
        else:  # Nếu không có ID, thêm cây mới
            cursor.execute("""
                INSERT INTO trees (tree_name, species, location, age, status) VALUES (?, ?, ?, ?, ?)
            """, (tree_name, species, location, age, status))
        
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    
    tree_id = request.args.get('id')
    tree = None
    if tree_id:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM trees WHERE id=?", (tree_id,))
        tree = cursor.fetchone()
        conn.close()
    
    return render_template('add_edit.html', tree=tree)

# Xóa cây
@app.route('/delete/<int:tree_id>')
def delete(tree_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM trees WHERE id=?", (tree_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

# Tìm kiếm cây
@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query', '')
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM trees WHERE tree_name LIKE ? OR species LIKE ? OR location LIKE ?", 
                   ('%' + query + '%', '%' + query + '%', '%' + query + '%'))
    trees = cursor.fetchall()
    conn.close()
    return render_template('index.html', trees=trees)

if __name__ == '__main__':
    init_db()  # Khởi tạo database nếu chưa có
    app.run(debug=True)
