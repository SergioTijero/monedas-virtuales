from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Necesario para manejar mensajes flash

# Inicializar stock de monedas (en memoria o cargar desde un archivo JSON)
monedas_stock = 1000  # Ejemplo de stock inicial
ventas_registradas = []  # Lista para registrar las ventas


@app.route('/')
def index():
    return render_template('index.html', stock=monedas_stock, ventas=ventas_registradas)


@app.route('/registrar_venta', methods=['POST'])
def registrar_venta():
    global monedas_stock
    usuario = request.form['usuario']
    cantidad = int(request.form['cantidad'])

    if cantidad <= monedas_stock:
        # Registrar la venta
        ventas_registradas.append({'usuario': usuario, 'cantidad': cantidad})
        # Descontar del stock
        monedas_stock -= cantidad
        flash("Venta registrada exitosamente", "success")
    else:
        flash("Stock insuficiente para realizar la venta", "danger")

    return redirect(url_for('index'))


@app.route('/aumentar_stock', methods=['POST'])
def aumentar_stock():
    global monedas_stock
    cantidad = int(request.form['cantidad'])
    monedas_stock += cantidad
    flash("Stock actualizado correctamente", "success")
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
