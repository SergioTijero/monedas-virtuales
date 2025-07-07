#!/usr/bin/env python3
"""
Script para quitar la validación obligatoria de 'categoria' en registrar_moneda
"""

import os

def fix_categoria_validation():
    """Quitar validación obligatoria de categoria"""
    print("🔧 Corrigiendo validación de categoría...")
    
    if not os.path.exists('app.py'):
        print("❌ No se encontró app.py")
        return False
    
    try:
        # Leer el archivo
        with open('app.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Cambio 1: Quitar 'categoria' de campos_requeridos
        old_text1 = "campos_requeridos = ['tipo', 'stock', 'precio_compra', 'precio_venta', 'categoria']"
        new_text1 = "campos_requeridos = ['tipo', 'stock', 'precio_compra', 'precio_venta']"
        
        if old_text1 in content:
            content = content.replace(old_text1, new_text1)
            print("✅ Removida 'categoria' de campos obligatorios")
        
        # Cambio 2: Hacer categoria opcional con valor por defecto
        old_text2 = "categoria = request.form['categoria']"
        new_text2 = "categoria = request.form.get('categoria', 'Otros')  # Valor por defecto si no existe"
        
        if old_text2 in content:
            content = content.replace(old_text2, new_text2)
            print("✅ Categoria ahora es opcional con valor por defecto 'Otros'")
        
        # Escribir el archivo actualizado
        with open('app.py', 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("\n🎉 ¡Problema solucionado!")
        print("📝 Ahora puedes registrar monedas sin el campo categoría")
        print("\n🚀 Reinicia la aplicación: python3 app.py")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("=== Fix Validación Categoría ===\n")
    fix_categoria_validation()
