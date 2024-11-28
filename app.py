from flask import Flask, render_template, request, redirect, url_for, send_file, make_response
import cx_Oracle
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def get_db_connection():
    connection = cx_Oracle.connect(
        user='Proyecto1',
        password='Proyecto1',
        dsn='localhost:1521/XE',
        encoding='UTF-8'
    )
    return connection

# Ruta principal: Índice
@app.route('/')
def index():
    return render_template('index.html')

# Ruta: Inventario
@app.route('/inventario', methods=['GET', 'POST'])
def inventario():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        if request.method == 'POST':
            nombre = request.form['nombre']
            precio = request.form['precio']
            detalle = request.form['detalle']
            cantidad = request.form['cantidad']
            categoria = request.form['categoria']
            proveedor_id = request.form['proveedor_id']
            casillero_id = request.form['casillero_id']
            imagen = request.files['imagen']
            imagen_blob = imagen.read()
            
            # Datos de depuración
            print("Datos recibidos para insertar:")
            print(f"Nombre: {nombre}, Precio: {precio}, Detalle: {detalle}, Cantidad: {cantidad}, Categoría: {categoria}, Proveedor ID: {proveedor_id}, Casillero ID: {casillero_id}, Imagen: {len(imagen_blob)} bytes")

            cursor.execute("""
                INSERT INTO FIDE_INVENTARIO_TB 
                (Nombre, Imagen, Precio, Detalle, Cantidad, Categoria, Proveedor_ID, Casillero_ID, Fecha_Entrada)
                VALUES (:nombre, :imagen_blob, :precio, :detalle, :cantidad, :categoria, :proveedor_id, :casillero_id, SYSTIMESTAMP)
            """, {
                'nombre': nombre,
                'imagen_blob': imagen_blob,
                'precio': precio,
                'detalle': detalle,
                'cantidad': cantidad,
                'categoria': categoria,
                'proveedor_id': proveedor_id,
                'casillero_id': casillero_id
            })
            conn.commit()
            print("Producto insertado correctamente")
        cursor.execute('SELECT ID_Producto, Nombre, Imagen, Precio, Detalle, Cantidad, Categoria, Proveedor_ID, Casillero_ID, Estado_ID, Fecha_Entrada FROM FIDE_INVENTARIO_TB')
        productos = cursor.fetchall()
        print("Productos obtenidos:", productos)
        return render_template('inventario.html', productos=productos)
    except Exception as e:
        print("Error en la operación:", str(e))
    finally:
        cursor.close()
        conn.close()

# Ruta para cargar imagen del inventario
@app.route('/imagen/<int:producto_id>')
def imagen(producto_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT Imagen FROM FIDE_INVENTARIO_TB WHERE ID_Producto = :producto_id', {'producto_id': producto_id})
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    if row and row[0]:
        response = make_response(row[0].read())
        response.headers.set('Content-Type', 'image/jpeg')
        return response
    return 'No image found', 404

# Ruta: Clientes
@app.route('/clientes', methods=['GET', 'POST'])
def clientes():
    conn = get_db_connection()
    cursor = conn.cursor()
    if request.method == 'POST':
        # Si hay datos enviados por un formulario, procesarlos aquí
        nombre = request.form['nombre']
        telefono = request.form['telefono']
        cedula = request.form['cedula']
        correo = request.form['correo']
        pais = request.form['pais']
        provincia = request.form['provincia']
        canton = request.form['canton']
        distrito = request.form['distrito']
        
        cursor.execute("""
            INSERT INTO FIDE_CLIENTES_TB 
            (Nombre, Telefono, Cedula, Correo, Pais, Provincia, Canton, Distrito, Estado_ID)
            VALUES (:nombre, :telefono, :cedula, :correo, :pais, :provincia, :canton, :distrito, 1)
        """, {
            'nombre': nombre,
            'telefono': telefono,
            'cedula': cedula,
            'correo': correo,
            'pais': pais,
            'provincia': provincia,
            'canton': canton,
            'distrito': distrito
        })
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('clientes'))

    # Obtener todos los clientes de la base de datos
    cursor.execute('SELECT ID_Cliente, Nombre, Telefono, Cedula, Correo, Pais, Provincia, Canton, Distrito, Estado_ID FROM FIDE_CLIENTES_TB')
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('clientes.html', rows=rows)

# Ruta: Proveedores
@app.route('/proveedores', methods=['GET', 'POST'])
def proveedores():
    conn = get_db_connection()
    cursor = conn.cursor()
    if request.method == 'POST':
        nombre = request.form['nombre']
        contacto = request.form['contacto']
        telefono = request.form['telefono']
        correo = request.form['correo']
        direccion = request.form['direccion']
        
        cursor.execute("""
            INSERT INTO FIDE_PROVEEDORES_TB 
            (Nombre, Contacto, Telefono, Correo, Direccion)
            VALUES (:nombre, :contacto, :telefono, :correo, :direccion)
        """, {
            'nombre': nombre,
            'contacto': contacto,
            'telefono': telefono,
            'correo': correo,
            'direccion': direccion
        })
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('proveedores'))

    cursor.execute('SELECT ID_Proveedor, Nombre, Contacto, Telefono, Correo, Direccion FROM FIDE_PROVEEDORES_TB')
    proveedores = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('proveedores.html', proveedores=proveedores)

# Agregar más rutas aquí según los requerimientos...

if __name__ == '__main__':
    app.run(debug=True)
