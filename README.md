# Challenge Técnico: AI Specialist - SQL Agent Design

Este repositorio contiene la solución al desafío técnico para el rol de AI Specialist en Atom. El objetivo principal es el diseño de un **System Prompt Maestro** capaz de transformar lenguaje natural en consultas SQL precisas, seguras y robustas.

## 🎬 Demo en Video

Puedes ver una demostración técnica de la robustez y seguridad del agente aquí:

https://github.com/jonnathanypg/robust-sql-prompt-engineering/video-demo-prueba.mp4

---

## 1. Entregable Principal: System Prompt
El corazón de esta solución se encuentra en el archivo **`Prompt.md`**.

Este prompt ha sido diseñado bajo principios de ingeniería de instrucciones para garantizar:
* **Formato Estricto**: Salida exclusiva en JSON para integración directa con APIs (Headless Mode).
* **Seguridad de Producción**: Protección contra Inyección SQL y restricciones de acceso de solo lectura (Read-Only).
* **Manejo de Ambigüedad**: Reglas claras para conceptos como "económico", "nuevo", "el mejor" o distinguir entre "Auto" (Sedan/Hatchback) y "Camioneta" (Truck).
* **Robustez Técnica**: Implementación de `LOWER()` para asegurar compatibilidad universal entre motores SQL (PostgreSQL, MySQL, SQLite).

---

## 2. Arquitectura de la Solución (Pensamiento Sistémico)
Aunque el desafío se centra en el prompt, he implementado un entorno de validación para asegurar la viabilidad del diseño en un sistema real:

1.  **Etapa de Razonamiento (Agente)**: El LLM procesa la solicitud y genera un contrato JSON estricto.
2.  **Etapa de Ejecución (Consumidor)**: Un sistema independiente recibe el JSON, valida la existencia de la consulta y la ejecuta de forma segura.

---

## 3. Guía de Ejecución (Entorno de Pruebas)

### Paso 1: Configurar la Base de Datos
Importa el archivo `seed_data.sql` en tu base de datos MySQL para crear la tabla `inventory` con datos de prueba:

```bash
mysql -u tu_usuario -p tu_base_de_datos < seed_data.sql
```

### Paso 2: Configurar Variables de Entorno
Copia el archivo de ejemplo y configura tus credenciales:

```bash
cp .env.example .env
```

Edita `.env` con tus valores reales:
```
DB_HOST=tu_host_de_base_de_datos
DB_PORT=3306
DB_NAME=tu_nombre_de_base_de_datos
DB_USER=tu_usuario
DB_PASSWORD=tu_contraseña
OPENAI_API_KEY=tu_api_key_de_openai
OPENAI_MODEL=gpt-4o-mini
```

### Paso 3: Instalar Dependencias
```bash
pip install -r requirements.txt
```

### Paso 4: Ejecutar la Demo
```bash
python3 demo.py
```

---

## 4. Scripts Incluidos

| Script | Descripción |
|--------|-------------|
| `agent.py` | Simula el comportamiento del LLM devolviendo el JSON estructurado. |
| `consumer.py` | Recibe el JSON, ejecuta la consulta y formatea la respuesta para el usuario. |
| `demo.py` | Ejecuta el flujo completo de punta a punta (End-to-End). |
| `seed_data.sql` | Script SQL para crear la tabla `inventory` con datos de prueba. |

---

## 5. Decisiones de Diseño Clave

* **Prevención de Alucinaciones**: El prompt define explícitamente las columnas inexistentes (como fechas de venta, colores o datos de clientes) para evitar que el modelo invente datos que no están en el esquema `inventory`.
* **Mapeo Estricto de Categorías**: Se han definido reglas para que términos regionales como "Auto", "Carro", "Camioneta" y "Todoterreno" filtren correctamente las categorías `Sedan`, `Hatchback`, `Truck` y `SUV`.
* **JSON Solo (Headless)**: El prompt está blindado para que el LLM actúe como una API silenciosa, retornando únicamente JSON válido sin texto conversacional adicional.


---

## 6. Guía de Ejecución (Entorno de Pruebas)

### Paso 1: Configurar la Base de Datos
Importa el archivo `seed_data.sql` en tu base de datos MySQL para crear la tabla `inventory` con datos de prueba:

```bash
mysql -u tu_usuario -p tu_base_de_datos < seed_data.sql
```

### Paso 2: Configurar Variables de Entorno
Copia el archivo de ejemplo y configura tus credenciales:

```bash
cp .env.example .env
```

Edita `.env` con tus valores reales:
```
DB_HOST=tu_host_de_base_de_datos
DB_PORT=3306
DB_NAME=tu_nombre_de_base_de_datos
DB_USER=tu_usuario
DB_PASSWORD=tu_contraseña
OPENAI_API_KEY=tu_api_key_de_openai
OPENAI_MODEL=gpt-5-nano
```

### Paso 3: Instalar Dependencias
```bash
pip install -r requirements.txt
```

### Paso 4: Ejecutar la Demo
```bash
python3 demo.py
```

---
