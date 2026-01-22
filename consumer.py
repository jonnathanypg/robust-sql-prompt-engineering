"""
SISTEMA CONSUMIDOR - Ejecutor de SQL
=====================================
Este sistema recibe el JSON del Agente SQL y:
1. Ejecuta la consulta SQL en la base de datos
2. Formatea una respuesta amigable para el usuario final
"""

import os
import sys
import json
from decimal import Decimal
from dotenv import load_dotenv
from langchain_community.utilities import SQLDatabase
from sqlalchemy import create_engine

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")


def format_vehicle(row):
    """Formatea un vehículo de forma amigable."""
    id, make, model, year, price, status, category = row
    return f"  • {year} {make} {model} ({category}) - ${float(price):,.2f} [{status}]"


def process_agent_json(agent_json: dict, db) -> str:
    """
    Recibe el JSON del agente, ejecuta SQL, retorna respuesta formateada.
    """
    sql = agent_json.get("sql")
    intent = agent_json.get("intent", "")
    reasoning = agent_json.get("reasoning", "")
    
    if sql is None:
        return f"❌ Solicitud rechazada.\n   Razón: {reasoning}"
    
    # Execute SQL
    try:
        result = db.run(sql)
        if isinstance(result, str):
            result = eval(result)
    except Exception as e:
        return f"⚠️ Error ejecutando SQL: {e}"
    
    # Format response
    if not result:
        return f"📭 No encontré resultados para: {intent}"
    
    if "COUNT" in sql.upper():
        count = result[0][0] if result else 0
        return f"📊 {intent}\n   Resultado: {count} vehículos"
    
    lines = [f"🚗 {intent}", f"   Encontré {len(result)} resultado(s):", ""]
    for row in result[:10]:
        lines.append(format_vehicle(row))
    if len(result) > 10:
        lines.append(f"\n   ... y {len(result) - 10} más")
    
    return "\n".join(lines)


def main():
    print("=" * 60)
    print("  📥 SISTEMA CONSUMIDOR - Ejecutor de SQL")
    print("=" * 60)
    print("  Este sistema recibe JSON del agente y ejecuta el SQL.")
    print("=" * 60)
    
    # Connect to database
    try:
        db_uri = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        engine = create_engine(db_uri, pool_pre_ping=True, pool_recycle=3600)
        db = SQLDatabase(engine)
        db.run("SELECT 1")
        print(f"\n✅ Conectado a {DB_NAME}@{DB_HOST}")
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        sys.exit(1)

    print("\n" + "-" * 60)
    print("  Pega el JSON del agente (una sola línea).")
    print("  Comandos: 'salir' para terminar")
    print("-" * 60)

    while True:
        try:
            json_input = input("\n📥 JSON del agente: ").strip()
            
            if json_input.lower() in ["exit", "quit", "salir"]:
                print("\n👋 ¡Hasta luego!")
                break
            
            if not json_input:
                continue

            try:
                agent_json = json.loads(json_input)
            except json.JSONDecodeError:
                print("⚠️ JSON inválido. Intenta de nuevo.")
                continue

            print("\n⚙️ Procesando...")
            if agent_json.get("sql"):
                print(f"   Ejecutando: {agent_json.get('sql')[:50]}...")
            
            response = process_agent_json(agent_json, db)
            
            print("\n💬 RESPUESTA FINAL AL USUARIO:")
            print("-" * 60)
            print(response)
            print("-" * 60)

        except KeyboardInterrupt:
            print("\n\n👋 ¡Hasta luego!")
            break
        except Exception as e:
            print(f"\n⚠️ Error: {e}")


if __name__ == "__main__":
    main()
