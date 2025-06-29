# Compatibilidad Python 3.7.16

## Cambios Realizados para Python 3.7.16

### 1. Dependencias Actualizadas
```pip
Flask==2.0.3          # Compatible con Python 3.7.16
Flask-Login==0.5.0    # Compatible con Python 3.7.16  
Werkzeug==2.0.3       # Compatible con Python 3.7.16
```

### 2. Código SQL Modernizado
- **Problema**: `ON CONFLICT` no disponible en SQLite antiguo
- **Solución**: Implementación manual con `SELECT` + `UPDATE`/`INSERT`

**Antes:**
```sql
INSERT INTO monedas (tipo, stock, precio_compra, precio_venta)
VALUES (?, ?, ?, ?)
ON CONFLICT(tipo) DO UPDATE SET
    stock = stock + excluded.stock,
    precio_compra = excluded.precio_compra,
    precio_venta = excluded.precio_venta
```

**Después:**
```python
# Verificar si la moneda ya existe
cursor.execute("SELECT id FROM monedas WHERE tipo = ?", (tipo_moneda,))
moneda_existente = cursor.fetchone()

if moneda_existente:
    # Actualizar moneda existente
    cursor.execute('''
        UPDATE monedas 
        SET stock = stock + ?, precio_compra = ?, precio_venta = ?
        WHERE tipo = ?
    ''', (cantidad, precio_compra, precio_venta, tipo_moneda))
else:
    # Insertar nueva moneda
    cursor.execute('''
        INSERT INTO monedas (tipo, stock, precio_compra, precio_venta)
        VALUES (?, ?, ?, ?)
    ''', (tipo_moneda, cantidad, precio_compra, precio_venta))
```

### 3. Características Utilizadas Compatibles con Python 3.7.16
- ✅ f-strings (disponible desde Python 3.6)
- ✅ Type hints básicos (disponible desde Python 3.5)
- ✅ SQLite3 (incluido en Python estándar)
- ✅ Flask 2.2.x (compatible con Python 3.7+)

### 4. Configuración de Servidor
```python
# Configurado para EC2
app.run(debug=True, host='0.0.0.0', port=8080)
```

### 5. Prueba de Compatibilidad
Ejecutar el script de prueba:
```bash
python3 test_compatibility.py
```

## Instalación en EC2 con Python 3.7.16

### Amazon Linux 2
```bash
sudo yum update -y
sudo yum install python3 python3-pip -y
python3 --version  # Verificar que sea 3.7.x
pip3 install -r requirements.txt
python3 app.py
```

### Ubuntu 18.04/20.04
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install python3.7 python3.7-pip -y
python3.7 --version
python3.7 -m pip install -r requirements.txt
python3.7 app.py
```

## Verificación Post-Instalación
1. ✅ Aplicación accesible en `http://IP:8080`
2. ✅ Login funcional (admin/admin123)
3. ✅ Base de datos SQLite creada automáticamente
4. ✅ Todas las funcionalidades operativas

## Solución de Problemas Comunes

### Error: "ImportError: No module named 'flask'"
```bash
pip3 install --upgrade pip
pip3 install -r requirements.txt
```

### Error: "Permission denied"
```bash
sudo ufw allow 8080  # Ubuntu
sudo firewall-cmd --add-port=8080/tcp --permanent  # CentOS/RHEL
```

### Error: "Database is locked"
```bash
# Verificar permisos del archivo de base de datos
chmod 664 sistema_monedas.db
```

## Notas Importantes
- ✅ El código ha sido probado y es compatible con Python 3.7.16
- ✅ No se utilizan características de Python 3.8+ 
- ✅ SQLite queries son compatibles con versiones antiguas
- ✅ Flask 2.0.3 es una versión estable compatible con Python 3.7.16
