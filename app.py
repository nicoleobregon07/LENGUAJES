from flask import Flask, render_template, request, redirect, url_for, send_file, make_response
import cx_Oracle
import os
import io

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

@app.route('/')
def index():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT ID_Cliente, Nombre, Telefono, Cedula, Correo, Pais, Provincia, Canton, Distrito, Estado_ID FROM FIDE_CLIENTES_TB')
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('index.html', rows=rows)

@app.route('/inventario', methods=['GET', 'POST'])
def inventario():
    conn = get_db_connection()
    cursor = conn.cursor()
    if request.method == 'POST':
        try:
            nombre = request.form['nombre']
            precio = request.form['precio']
            detalle = request.form['detalle']
            cantidad = request.form['cantidad']
            categoria = request.form['categoria']
            proveedor_id = request.form['proveedor_id']
            casillero_id = request.form['casillero_id']
            imagen = request.files['imagen']
            imagen_blob = imagen.read()
            
            print("Datos recibidos:")
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
        except Exception as e:
            print("Error al insertar el producto:", str(e))
        finally:
            cursor.close()
            conn.close()
        return redirect(url_for('inventario'))

    cursor.execute('SELECT ID_Producto, Nombre, Imagen, Precio, Detalle, Cantidad, Categoria, Proveedor_ID, Casillero_ID, Estado_ID, Fecha_Entrada FROM FIDE_INVENTARIO_TB')
    productos = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('inventario.html', productos=productos)

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
        response.headers.set('Content-Type', 'image/jpeg')  # Asume que todas las imágenes son JPEG
        return response
    return 'No image found', 404

if __name__ == '__main__':
    app.run(debug=True)
