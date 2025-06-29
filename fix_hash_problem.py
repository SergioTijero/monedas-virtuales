#!/usr/bin/env python3
"""
Script para solucionar el problema de hash scrypt en Python 3.7
Resetea la contraseña del admin con un hash compatible
"""

import sqlite3
from werkzeug.security import generate_password_hash

DATABASE = 'sistema_monedas.db'

def solucionar_problema_hash():
    """Solucionar problema de hash scrypt no compatible con Python 3.7"""
    print("🔧 Solucionando problema de hash scrypt...")
    
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        # Generar hash compatible con Python 3.7 (pbkdf2:sha256)
        nueva_password = generate_password_hash("admin123", method='pbkdf2:sha256')
        print(f"✅ Nuevo hash generado: {nueva_password[:50]}...")
        
        # Actualizar contraseña del admin
        cursor.execute('''
            UPDATE usuarios SET password = ? WHERE username = ?
        ''', (nueva_password, "admin"))
        
        # Si no existe el usuario, crearlo
        if cursor.rowcount == 0:
            cursor.execute('''
                INSERT INTO usuarios (username, password)
                VALUES (?, ?)
            ''', ("admin", nueva_password))
            print("✅ Usuario admin creado")
        else:
            print("✅ Contraseña admin actualizada")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("\n🎉 PROBLEMA SOLUCIONADO")
        print("📝 Credenciales:")
        print("   Usuario: admin")
        print("   Contraseña: admin123")
        print("\n🚀 Ahora puedes ejecutar: python3 app.py")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    solucionar_problema_hash()
