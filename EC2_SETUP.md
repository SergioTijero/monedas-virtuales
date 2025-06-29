# Instrucciones para EC2

## Comandos para instalar en EC2 (Amazon Linux/Ubuntu):

```bash
# Actualizar el sistema
sudo yum update -y  # Para Amazon Linux
# sudo apt update && sudo apt upgrade -y  # Para Ubuntu

# Instalar Python 3.7 y pip (si no está instalado)
sudo yum install python3 python3-pip -y  # Amazon Linux
# sudo apt install python3 python3-pip -y  # Ubuntu

# Clonar o subir tu proyecto
# Navegar a la carpeta del proyecto

# Instalar dependencias
pip3 install -r requirements.txt

# Ejecutar la aplicación
python3 app.py
```

## Acceder a la aplicación:
- Desde EC2: `http://IP_PUBLICA_DE_TU_EC2:8080`
- Usuario: `admin`
- Contraseña: `admin123`

## Notas importantes:
1. Asegúrate de que el Security Group de EC2 permita tráfico en el puerto 8080
2. Si usas firewall, abre el puerto 8080
3. Para detener la aplicación: `Ctrl+C`
4. Para ejecutar en background: `nohup python3 app.py &`
