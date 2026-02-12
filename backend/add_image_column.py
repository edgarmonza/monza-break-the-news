"""
Script para añadir la columna image_url a la tabla threads
"""
from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()

print("🔧 Añadiendo columna image_url a threads...")

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

# La forma más sencilla es usar postgrest directamente
# Pero para DDL necesitamos acceso directo a PostgreSQL o usar el Dashboard

sql_command = """
ALTER TABLE threads ADD COLUMN IF NOT EXISTS image_url TEXT;
"""

print("\n📋 SQL a ejecutar en Supabase Dashboard (SQL Editor):")
print("=" * 60)
print(sql_command)
print("=" * 60)
print("\n💡 Pasos:")
print("1. Ve a: https://pekgooxiykqaltgtunjq.supabase.co/project/_/sql")
print("2. Pega el SQL de arriba")
print("3. Click en 'Run'")
print("\nO alternativamente, el seed script continuará sin imagen_url si no existe.")
