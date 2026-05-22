from flask import Flask, render_template, redirect, url_for, request, session
import sqlite3

app = Flask(__name__)
# Llave secreta obligatoria en Flask para encriptar las sesiones de usuario
app.secret_key = 'llave_secreta_super_segura_para_mauricio'

def init_db():
    conn = sqlite3.connect('erp_motos.db')
    cursor = conn.cursor()
    
    # Área 1: Inventario (Compras y Ventas)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS productos (
            id_producto INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            marca TEXT,
            precio_costo REAL,
            precio_venta REAL,
            stock INTEGER,
            stock_minimo INTEGER
        )
    ''')
    
    # Área 2: Logística (Colas FIFO)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS colas_atencion (
            id_cola INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente TEXT,
            estado TEXT,
            hora_ingreso TEXT
        )
    ''')
    
    # Datos base si está vacía
    cursor.execute("SELECT COUNT(*) FROM productos")
    if cursor.fetchone()[0] == 0:
        cursor.executemany("INSERT INTO productos (nombre, marca, precio_costo, precio_venta, stock, stock_minimo) VALUES (?,?,?,?,?,?)", [
            ('Pastillas de Freno FZ16', 'Brembo', 45.00, 110.00, 5, 5),
            ('Llanta Delantera 90/90-17', 'Michelin', 180.00, 325.00, 12, 3),
            ('Aceite de Motor 4T 10W40', 'Motul', 35.00, 75.00, 20, 5)
        ])
        cursor.executemany("INSERT INTO colas_atencion (cliente, estado, hora_ingreso) VALUES (?,?,?)", [
            ('Taller El Esfuerzo (Mayorista)', 'En Espera de Delivery', '22:15'),
            ('Carlos Gómez (Particular)', 'Preparando Repuesto', '22:20')
        ])
    conn.commit()
    conn.close()

# --- CONTROL DE ACCESO (LOGIN) ---

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Validación estricta solicitada
        if username == 'jaroche' and password == 'tatan2026':
            session['user'] = username  # Guardamos la sesión activa
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error='Credenciales incorrectas. Intente de nuevo.')
            
    return render_template('login.html', error=None)

@app.route('/logout')
def logout():
    session.pop('user', None)  # Destruye la sesión del usuario
    return redirect(url_for('login'))

# --- DASHBOARD PRINCIPAL (PROTEGIDO) ---

@app.route('/')
def dashboard():
    # Si el usuario no ha iniciado sesión, lo redirige de inmediato al Login
    if 'user' not in session:
        return redirect(url_for('login'))
        
    conn = sqlite3.connect('erp_motos.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM productos")
    productos = cursor.fetchall()
    
    cursor.execute("SELECT * FROM colas_atencion")
    cola = cursor.fetchall()
    
    cursor.execute("SELECT COUNT(*) FROM productos WHERE stock <= stock_minimo")
    alertas_desabastecimiento = cursor.fetchone()[0]
    
    conn.close()
    return render_template('dashboard.html', productos=productos, cola=cola, alertas=alertas_desabastecimiento)

# --- ACCIONES INTERACTIVAS (COMPRAS, VENTAS Y DELIVERIES) ---

@app.route('/vender/<int:id_producto>')
def vender_producto(id_producto):
    if 'user' not in session: return redirect(url_for('login'))
    conn = sqlite3.connect('erp_motos.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE productos SET stock = MAX(0, stock - 1) WHERE id_producto = ?", (id_producto,))
    conn.commit()
    conn.close()
    return redirect(url_for('dashboard'))

@app.route('/comprar/<int:id_producto>')
def comprar_producto(id_producto):
    if 'user' not in session: return redirect(url_for('login'))
    conn = sqlite3.connect('erp_motos.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE productos SET stock = stock + 5 WHERE id_producto = ?", (id_producto,))
    conn.commit()
    conn.close()
    return redirect(url_for('dashboard'))

@app.route('/despachar/<int:id_cola>')
def despachar_cola(id_cola):
    if 'user' not in session: return redirect(url_for('login'))
    conn = sqlite3.connect('erp_motos.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM colas_atencion WHERE id_cola = ?", (id_cola,))
    conn.commit()
    conn.close()
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)