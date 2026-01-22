"""
DEMO COMPLETO - Sistema de Dos Etapas
======================================

Flujo según el PDF Challenge:

  [USUARIO] ──consulta──► [AGENTE SQL] ──JSON──► [CONSUMIDOR] ──respuesta──► [USUARIO]
                              ↑                       ↑
                         Prompt.md              Ejecuta SQL
                         (solo JSON)            + Formatea

Este demo muestra AMBAS etapas en una sola ejecución para validar el sistema.
"""

import os
import sys
import json
from decimal import Decimal
from dotenv import load_dotenv
from langchain_community.utilities import SQLDatabase
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from sqlalchemy import create_engine

load_dotenv()

# Configuration
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-5-nano")


def format_vehicle(row):
    id, make, model, year, price, status, category = row
    return f"    • {year} {make} {model} ({category}) - ${float(price):,.2f} [{status}]"


def format_final_response(intent, reasoning, sql, result):
    if sql is None:
        # Mensajes amigables para usuarios finales (sin tecnicismos)
        if "SECURITY" in reasoning.upper():
            return "  ❌ Lo siento, esa acción no está permitida.\n     Solo puedo ayudarte a buscar vehículos disponibles."
        elif "SCOPE" in reasoning.upper():
            return "  ❌ Esa información no está disponible.\n     ¿Te puedo ayudar a encontrar un vehículo?"
        elif "DOMAIN" in reasoning.upper() or "OUT OF DOMAIN" in reasoning.upper():
            return "  ❌ Solo puedo ayudarte con información sobre vehículos.\n     ¿Buscás algún auto o camioneta en particular?"
        elif "SCHEMA" in reasoning.upper():
            return "  ❌ No tengo acceso a esa información.\n     Puedo mostrarte los vehículos disponibles si querés."
        else:
            return "  ❌ No puedo procesar esa solicitud.\n     ¿Te puedo ayudar a buscar un vehículo?"
    if not result:
        return "  📭 No encontré resultados para esa búsqueda.\n     ¿Querés probar con otros criterios?"
    if "COUNT" in sql.upper():
        count = result[0][0] if result else 0
        return f"  📊 {intent}\n     Resultado: {count} vehículos"
    
    lines = [f"  🚗 {intent}", f"     Encontré {len(result)} resultado(s):", ""]
    for row in result[:8]:
        lines.append(format_vehicle(row))
    if len(result) > 8:
        lines.append(f"\n     ... y {len(result) - 8} más")
    return "\n".join(lines)


def print_box(title, content, char="─"):
    width = 70
    print(f"\n  ┌{char * (width - 4)}┐")
    print(f"  │ {title:<{width - 6}} │")
    print(f"  ├{char * (width - 4)}┤")
    for line in content.split("\n"):
        print(f"  │ {line:<{width - 6}} │")
    print(f"  └{char * (width - 4)}┘")


def main():
    os.system('clear' if os.name == 'posix' else 'cls')
    
    print("═" * 70)
    print("  🚘 DEMO COMPLETO - Sistema SQL Agent (Arquitectura Dos Etapas)")
    print("═" * 70)
    print(f"\n  Modelo: {OPENAI_MODEL}")
    print(f"  DB: {DB_NAME}@{DB_HOST}")
    print("\n  FLUJO:")
    print("  ┌─────────┐      ┌─────────────┐      ┌────────────┐")
    print("  │ USUARIO │ ───► │ AGENTE SQL  │ ───► │ CONSUMIDOR │")
    print("  └─────────┘      └─────────────┘      └────────────┘")
    print("       │             (Prompt.md)          (Ejecuta SQL)")
    print("       │                 │                     │")
    print("       │            Genera JSON           Respuesta")
    print("       └──────────────────────────────────────►│")
    
    # Initialize components
    print("\n" + "─" * 70)
    print("  Inicializando componentes...")
    
    try:
        llm = ChatOpenAI(model_name=OPENAI_MODEL, openai_api_key=OPENAI_API_KEY, temperature=0)
        print("  ✅ LLM listo")
    except Exception as e:
        print(f"  ❌ Error LLM: {e}")
        sys.exit(1)
    
    try:
        with open("Prompt.md", "r") as f:
            system_prompt = f.read()
        system_message = SystemMessage(content=system_prompt)
        print("  ✅ Prompt.md cargado")
    except Exception as e:
        print(f"  ❌ Error Prompt: {e}")
        sys.exit(1)
    
    try:
        db_uri = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        engine = create_engine(db_uri, pool_pre_ping=True, pool_recycle=3600)
        db = SQLDatabase(engine)
        db.run("SELECT 1")
        print("  ✅ Base de datos conectada")
    except Exception as e:
        print(f"  ❌ Error DB: {e}")
        sys.exit(1)
    
    print("─" * 70)
    print("\n  Escribe tu consulta. Comandos: 'salir' para terminar\n")

    while True:
        try:
            user_input = input("  👤 Usuario: ").strip()
            
            if not user_input:
                continue
            if user_input.lower() in ["exit", "quit", "salir"]:
                print("\n  👋 ¡Hasta luego!")
                break
            
            # ══════════════════════════════════════════════════════════════
            # ETAPA 1: AGENTE SQL (genera JSON)
            # ══════════════════════════════════════════════════════════════
            print("\n" + "═" * 70)
            print("  📤 ETAPA 1: AGENTE SQL (Prompt.md)")
            print("     El agente traduce lenguaje natural a JSON...")
            print("═" * 70)
            
            messages = [system_message, HumanMessage(content=user_input)]
            ai_response = llm.invoke(messages)
            content = ai_response.content
            
            # NO cleanup - the Prompt.md must be authoritative enough to produce raw JSON
            # If this fails, the prompt needs strengthening, not code workarounds.
            try:
                agent_json = json.loads(content.strip())
            except json.JSONDecodeError:
                print(f"\n  ⚠️ Error: El LLM no devolvió JSON válido.")
                print(f"     Esto indica que el Prompt.md necesita ser más estricto.")
                print(f"     Raw output: {content}")
                continue
            
            # Show JSON output
            print("\n  📋 JSON generado por el agente:")
            formatted_json = json.dumps(agent_json, indent=2, ensure_ascii=False)
            for line in formatted_json.split("\n"):
                print(f"     {line}")
            
            # ══════════════════════════════════════════════════════════════
            # ETAPA 2: SISTEMA CONSUMIDOR (ejecuta SQL)
            # ══════════════════════════════════════════════════════════════
            print("\n" + "═" * 70)
            print("  📥 ETAPA 2: SISTEMA CONSUMIDOR")
            print("     El consumidor recibe el JSON y ejecuta el SQL...")
            print("═" * 70)
            
            sql = agent_json.get("sql")
            intent = agent_json.get("intent", "")
            reasoning = agent_json.get("reasoning", "")
            
            result = None
            if sql:
                print(f"\n  ⚙️ Ejecutando SQL: {sql[:50]}...")
                try:
                    raw_result = db.run(sql)
                    if isinstance(raw_result, str):
                        result = eval(raw_result)
                    else:
                        result = raw_result
                    print(f"  ✅ Query exitoso. {len(result) if result else 0} registros.")
                except Exception as e:
                    print(f"  ❌ Error SQL: {e}")
            else:
                print("\n  ⚠️ No hay SQL para ejecutar (solicitud rechazada por el agente)")
            
            # Final response
            final_response = format_final_response(intent, reasoning, sql, result)
            print("\n" + "═" * 70)
            print("  💬 RESPUESTA FINAL AL USUARIO")
            print("═" * 70)
            print(final_response)
            print("\n" + "─" * 70)

        except KeyboardInterrupt:
            print("\n\n  👋 ¡Hasta luego!")
            break
        except Exception as e:
            print(f"\n  ⚠️ Error: {e}")


if __name__ == "__main__":
    main()
