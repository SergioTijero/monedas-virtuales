# Instrucciones para EC2 - Python 3.7.16

## Comandos para instalar en EC2 (Amazon Linux/Ubuntu):

```bash
# Actualizar el sistema
sudo yum update -y  # Para Amazon Linux
# sudo apt update && sudo apt upgrade -y  # Para Ubuntu

# Instalar Python 3.7 específicamente y pip
sudo yum install python3 python3-pip -y  # Amazon Linux
# sudo apt install python3.7 python3.7-pip -y  # Ubuntu

# Verificar la versión de Python (debe ser 3.7.x)
python3 --version

# Clonar o subir tu proyecto
# Navegar a la carpeta del proyecto

# Instalar dependencias compatibles con Python 3.7.16
pip3 install -r requirements.txt

# IMPORTANTE: Si tienes problemas con hash scrypt, ejecuta:
python3 fix_hash_problem.py

# Ejecutar la aplicación
python3 app.py
```

## Versiones de dependencias compatibles con Python 3.7.16:
- Flask==1.1.4
- Flask-Login==0.5.0
- Werkzeug==1.0.1

## Solución al problema de hash scrypt:
Si ves el error "ValueError: unsupported hash type scrypt", ejecuta:
```bash
python3 fix_hash_problem.py
```

## Acceder a la aplicación:
- Desde EC2: `http://IP_PUBLICA_DE_TU_EC2:8080`
- Usuario: `admin`
- Contraseña: `admin123`

## Notas importantes:
1. Asegúrate de que el Security Group de EC2 permita tráfico en el puerto 8080
2. Si usas firewall, abre el puerto 8080: `sudo ufw allow 8080`
3. Para detener la aplicación: `Ctrl+C`
4. Para ejecutar en background: `nohup python3 app.py &`
5. **Importante**: El código ha sido optimizado para ser compatible con Python 3.7.16 y SQLite versiones anteriores
6. **Hash scrypt**: Se usa pbkdf2:sha256 para compatibilidad con Python 3.7
