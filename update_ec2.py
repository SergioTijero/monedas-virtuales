#!/usr/bin/env python3
"""
Script para actualizar los archivos en EC2 y solucionar problemas
"""

import os
import shutil
import sys

def crear_backup():
    """Crear backup de archivos importantes"""
    print("🔧 Creando backup...")
    try:
        if os.path.exists('sistema_monedas.db'):
            shutil.copy2('sistema_monedas.db', 'sistema_monedas.db.backup')
            print("✅ Backup de base de datos creado")
        
        if os.path.exists('app.py'):
            shutil.copy2('app.py', 'app.py.backup')
            print("✅ Backup de app.py creado")
            
    except Exception as e:
        print(f"⚠️ Error creando backup: {e}")

def actualizar_template_compras():
    """Corregir el template compras.html"""
    print("🔧 Actualizando template compras.html...")
    
    template_path = 'templates/compras.html'
    if not os.path.exists(template_path):
        print("❌ No se encontró templates/compras.html")
        return False
    
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Reemplazar el filtro multiply problemático
        old_text = """{% set total_inversion = compras|sum(attribute='precio_compra')|multiply(compras|sum(attribute='cantidad')) %}
                    {% set total_valor = compras|sum(attribute='precio_venta')|multiply(compras|sum(attribute='cantidad')) %}"""
        
        new_text = """{% set total_inversion = 0 %}
                    {% set total_valor = 0 %}
                    {% for compra in compras %}
                        {% set total_inversion = total_inversion + (compra['cantidad'] * compra['precio_compra']) %}
                        {% set total_valor = total_valor + (compra['cantidad'] * compra['precio_venta']) %}
                    {% endfor %}"""
        
        if old_text in content:
            content = content.replace(old_text, new_text)
            
            # Corregir valores duplicados
            content = content.replace(
                '<span class="stat-value sell">$0.00</span>',
                ''
            )
            content = content.replace(
                '<span class="stat-value profit">$0.00</span>',
                '<span class="stat-value profit">${{ "%.2f"|format(total_valor - total_inversion) }}</span>'
            )
            
            with open(template_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print("✅ Template compras.html actualizado")
            return True
        else:
            print("⚠️ No se encontró el texto a reemplazar en compras.html")
            return False
            
    except Exception as e:
        print(f"❌ Error actualizando template: {e}")
        return False

def verificar_dependencias():
    """Verificar que las dependencias estén instaladas"""
    print("🔧 Verificando dependencias...")
    
    try:
        import flask
        import flask_login
        import werkzeug
        print(f"✅ Flask: {flask.__version__}")
        print(f"✅ Flask-Login: {flask_login.__version__}")
        print(f"✅ Werkzeug: {werkzeug.__version__}")
        return True
    except ImportError as e:
        print(f"❌ Error de dependencias: {e}")
        print("Ejecuta: pip3 install -r requirements.txt")
        return False

def actualizar_codigo_app():
    """Corregir validaciones en app.py"""
    print("🔧 Actualizando validaciones en app.py...")
    
    if not os.path.exists('app.py'):
        print("❌ No se encontró app.py")
        return False
    
    try:
        with open('app.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Quitar categoria de campos requeridos
        old_validation = "campos_requeridos = ['tipo', 'stock', 'precio_compra', 'precio_venta', 'categoria']"
        new_validation = "campos_requeridos = ['tipo', 'stock', 'precio_compra', 'precio_venta']"
        
        if old_validation in content:
            content = content.replace(old_validation, new_validation)
            
            # También actualizar la asignación de categoria
            old_categoria = "categoria = request.form['categoria']"
            new_categoria = "categoria = request.form.get('categoria', 'Otros')  # Valor por defecto si no existe"
            
            content = content.replace(old_categoria, new_categoria)
            
            with open('app.py', 'w', encoding='utf-8') as f:
                f.write(content)
            
            print("✅ Validaciones en app.py actualizadas")
            return True
        else:
            print("⚠️ No se encontró el texto a reemplazar en app.py")
            return False
            
    except Exception as e:
        print(f"❌ Error actualizando app.py: {e}")
        return False

def main():
    print("=== Script de Actualización EC2 ===\n")
    
    # Verificar que estamos en el directorio correcto
    if not os.path.exists('app.py'):
        print("❌ No se encontró app.py. Asegúrate de estar en el directorio del proyecto.")
        sys.exit(1)
    
    # Crear backup
    crear_backup()
    
    # Verificar dependencias
    if not verificar_dependencias():
        print("\n⚠️ Instala las dependencias antes de continuar")
        return
    
    # Actualizar template
    template_ok = actualizar_template_compras()
    
    # Actualizar código app.py
    app_ok = actualizar_codigo_app()
    
    if template_ok and app_ok:
        print("\n🎉 Actualización completada exitosamente!")
        print("\nPróximos pasos:")
        print("1. python3 fix_hash_problem.py  # Si aún tienes problemas de login")
        print("2. python3 app.py              # Iniciar la aplicación")
        print("\n📱 Accede a: http://IP_DE_TU_EC2:8080")
    else:
        print("\n⚠️ Algunos problemas durante la actualización")
        print("Puedes subir los archivos manualmente desde tu repositorio local")
    
    # Actualizar código de app.py
    actualizar_codigo_app()

if __name__ == "__main__":
    main()
