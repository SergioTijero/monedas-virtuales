#!/usr/bin/env python3
"""
Script de prueba de compatibilidad para Python 3.7.16
"""

import sys
import sqlite3

def test_python_version():
    """Verificar versión de Python"""
    print(f"Python version: {sys.version}")
    major, minor = sys.version_info[:2]
    if major == 3 and minor >= 7:
        print("✅ Python version compatible")
        return True
    else:
        print("❌ Python version not compatible - need 3.7+")
        return False

def test_sqlite_compatibility():
    """Verificar compatibilidad de SQLite"""
    try:
        conn = sqlite3.connect(':memory:')
        cursor = conn.cursor()
        
        # Crear tabla de prueba
        cursor.execute('''
            CREATE TABLE test_table (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                value INTEGER
            )
        ''')
        
        # Probar INSERT OR IGNORE (compatible con versiones antiguas)
        cursor.execute("INSERT OR IGNORE INTO test_table (name, value) VALUES (?, ?)", ("test", 1))
        
        # Probar UPDATE
        cursor.execute("UPDATE test_table SET value = ? WHERE name = ?", (2, "test"))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("✅ SQLite operations compatible")
        return True
        
    except Exception as e:
        print(f"❌ SQLite compatibility issue: {e}")
        return False

def test_imports():
    """Verificar imports necesarios"""
    try:
        import flask
        print(f"✅ Flask version: {flask.__version__}")
        
        import flask_login
        print(f"✅ Flask-Login version: {flask_login.__version__}")
        
        import werkzeug
        print(f"✅ Werkzeug version: {werkzeug.__version__}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

if __name__ == "__main__":
    print("=== Prueba de Compatibilidad Python 3.7.16 ===\n")
    
    tests = [
        test_python_version(),
        test_sqlite_compatibility(),
        test_imports()
    ]
    
    if all(tests):
        print("\n🎉 Todas las pruebas pasaron - Sistema compatible con Python 3.7.16")
    else:
        print("\n⚠️ Algunas pruebas fallaron - revisar configuración")
