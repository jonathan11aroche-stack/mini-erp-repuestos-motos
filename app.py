from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify

app = Flask(__name__)
app.secret_key = 'clave_secreta_mauricio'

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        usuario_ingresado = request.form.get('username')
        password_ingresado = request.form.get('password')
        
        if usuario_ingresado == "jaroche" and password_ingresado == "tatan2026":
            return redirect(url_for('dashboard'))
        else:
            error = "Usuario o contraseña incorrectos, intenta de nuevo."
            
    return render_template('login.html', error=error)

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/agregar_al_carrito', methods=['POST'])
def agregar_al_carrito():
    producto = request.json 
    if 'carrito' not in session:
        session['carrito'] = []
    
    lista_carrito = session['carrito']
    lista_carrito.append(producto)
    session['carrito'] = lista_carrito
    session.modified = True 
    
    return jsonify({"mensaje": "Producto agregado", "total": len(session['carrito'])})

@app.route('/ver_carrito')
def ver_carrito():
    carrito = session.get('carrito', [])
    return render_template('carrito.html', carrito=carrito)

@app.route('/vaciar_carrito')
def vaciar_carrito():
    session.pop('carrito', None)
    return redirect(url_for('ver_carrito'))

# --- RUTA DE REGISTRAR VENTA CON CÁLCULO DE TOTAL ---
@app.route('/registrar_venta', methods=['POST'])
def registrar_venta():
    datos = request.json # Recibe nombre, nit, tel, fecha
    
    carrito_actual = session.get('carrito', [])
    
    # 1. Guardar nombres de los productos
    datos['productos'] = [item['nombre'] for item in carrito_actual]
    
    # 2. Calcular total de la venta (limpiando el formato "Q 00.00")
    total_venta = 0.0
    for item in carrito_actual:
        # Quitamos la 'Q', quitamos espacios y convertimos a float
        precio_limpio = item['precio'].replace('Q', '').strip()
        total_venta += float(precio_limpio)
    
    # Guardamos el total formateado a 2 decimales
    datos['total'] = f"{total_venta:.2f}"
    
    if 'ventas' not in session:
        session['ventas'] = []
    
    session['ventas'].append(datos)
    session.modified = True
    
    # Vaciamos el carrito
    session.pop('carrito', None) 
    
    return jsonify({"mensaje": "Venta registrada con éxito", "total": datos['total']})

@app.route('/ver_ventas')
def ver_ventas():
    ventas = session.get('ventas', [])
    return render_template('ventas.html', ventas=ventas)

if __name__ == '__main__':
    app.run(debug=True)