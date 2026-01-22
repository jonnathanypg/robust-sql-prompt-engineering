"""
AGENTE SQL - Generador de JSON
==============================
Este agente SOLO genera el JSON estructurado.
NO ejecuta SQL. El JSON es consumido por otro sistema.

Según el PDF:
- Input: Lenguaje natural del usuario
- Output: JSON {sql, intent, reasoning}
"""

import os
import sys
import json
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-5-nano")


def main():
    print("=" * 60)
    print("  🤖 AGENTE SQL - Generador de JSON")
    print("=" * 60)
    print(f"  Modelo: {OPENAI_MODEL}")
    print("  Este agente NO ejecuta SQL, solo genera el JSON.")
    print("=" * 60)
    
    # Initialize LLM
    try:
        llm = ChatOpenAI(
            model_name=OPENAI_MODEL,
            openai_api_key=OPENAI_API_KEY,
            temperature=0
        )
        print("\n✅ LLM inicializado")
    except Exception as e:
        print(f"❌ Error inicializando LLM: {e}")
        sys.exit(1)

    # Read System Prompt
    try:
        with open("Prompt.md", "r") as f:
            system_prompt_text = f.read()
        print("✅ Prompt.md cargado")
    except FileNotFoundError:
        print("❌ Error: Prompt.md no encontrado.")
        sys.exit(1)

    system_message = SystemMessage(content=system_prompt_text)

    print("\n" + "-" * 60)
    print("  Escribe tu consulta. El agente devolverá JSON.")
    print("  Comandos: 'salir' para terminar")
    print("-" * 60)

    while True:
        try:
            user_input = input("\n👤 Usuario: ").strip()
            
            if user_input.lower() in ["exit", "quit", "salir"]:
                print("\n👋 ¡Hasta luego!")
                break
            
            if not user_input:
                continue

            # Generate JSON response
            messages = [system_message, HumanMessage(content=user_input)]
            ai_response = llm.invoke(messages)
            content = ai_response.content
            
            # NO cleanup - the Prompt.md must be authoritative enough to produce raw JSON
            # If this fails, the prompt needs to be stronger, not the code.
            try:
                response_json = json.loads(content.strip())
            except json.JSONDecodeError:
                print(f"\n⚠️ Error: El LLM no devolvió JSON válido.")
                print(f"   Esto indica que el Prompt.md necesita ser más estricto.")
                print(f"   Raw output:")
                print(f"   {content}")
                continue

            # Display JSON output
            print("\n📤 OUTPUT DEL AGENTE (JSON para sistema consumidor):")
            print("-" * 60)
            print(json.dumps(response_json, indent=2, ensure_ascii=False))
            print("-" * 60)

        except KeyboardInterrupt:
            print("\n\n👋 ¡Hasta luego!")
            break
        except Exception as e:
            print(f"\n⚠️ Error: {e}")


if __name__ == "__main__":
    main()
