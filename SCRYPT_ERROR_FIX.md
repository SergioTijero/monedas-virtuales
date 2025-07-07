# 🚨 ERRORES COMUNES - SOLUCIONES INMEDIATAS

## Error 1: Hash scrypt no soportado
```
ValueError: unsupported hash type scrypt:32768:8:1
```

## Error 2: Template multiply filter
```
TemplateAssertionError: no filter named 'multiply'
```

## Error 3: Formulario registrar moneda (400)
```
Bad Request - Los campos requeridos faltan o son inválidos
```

## ⚡ SOLUCIÓN COMPLETA (En tu EC2):

### Paso 1: Actualizar archivos problemáticos
```bash
python3 update_ec2.py
```

### Paso 2: Corregir hash de contraseña
```bash
python3 fix_hash_problem.py
```

### Paso 3: Iniciar aplicación
```bash
python3 app.py
```

## 🔧 ¿Qué solucionan estos scripts?

### `update_ec2.py`:
- ✅ Corrige el filtro `multiply` en `compras.html`
- ✅ Mejora manejo de errores en formularios
- ✅ Crea backups de seguridad

### `fix_hash_problem.py`:
- ✅ Resetea contraseña admin con hash compatible
- ✅ Usa `pbkdf2:sha256` en lugar de `scrypt`

## 🎯 Credenciales después del fix:
- **Usuario**: `admin`
- **Contraseña**: `admin123`

## 📱 Verificar que funciona:
1. Ve a: `http://TU_IP_EC2:8080`
2. Login con admin/admin123
3. Prueba registrar una nueva moneda
4. Ve la sección "Compras" sin errores

## 🆘 Si sigues teniendo problemas:

### Reinstalar dependencias:
```bash
pip3 uninstall -y Flask Flask-Login Werkzeug
pip3 install -r requirements.txt
```

### Revisar logs:
```bash
tail -f nohup.out  # Si ejecutas con nohup
```

### Verificar puerto:
```bash
sudo netstat -tlnp | grep :8080
```

---
*Scripts de solución automática para despliegue en EC2*
