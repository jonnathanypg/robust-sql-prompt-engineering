# Challenge Técnico: AI Specialist - SQL Agent Design 🚀

Este repositorio contiene la solución al desafío técnico para el rol de AI Specialist en Atom. El objetivo principal es el diseño de un **System Prompt Maestro** capaz de transformar lenguaje natural en consultas SQL precisas, seguras y robustas.

---

## 🎬 Demo en Video

Puedes ver una demostración técnica de la robustez y seguridad del agente aquí:

https://github.com/user-attachments/assets/06c7cd93-422d-4855-bbb2-2001677752c7

---

## 📋 Tabla de Contenidos

1. [Entregable Principal: System Prompt](#1-entregable-principal-system-prompt)
2. [Cumplimiento de Requerimientos](#2-cumplimiento-de-requerimientos-del-challenge)
3. [Reglas de Seguridad del Prompt](#3-reglas-de-seguridad-del-prompt)
4. [Manejo de Ambigüedad y Lógica de Negocio](#4-manejo-de-ambigüedad-y-lógica-de-negocio)
5. [Formato de Salida (Headless JSON)](#5-formato-de-salida-headless-json)
6. [Sistema de Validación (Arquitectura)](#6-sistema-de-validación-arquitectura)
7. [Pruebas de Seguridad](#7-pruebas-de-seguridad-sql-injection)
8. [Decisiones de Diseño](#8-decisiones-de-diseño-clave)
9. [Guía de Ejecución (Entorno de Pruebas)](#9-guía-de-ejecución-entorno-de-pruebas)

---

# PARTE 1: EL PROMPT (Entregable Principal)

---

## 1. Entregable Principal: System Prompt

El corazón de esta solución se encuentra en el archivo **[`Prompt.md`](./Prompt.md)**.

Este prompt ha sido diseñado bajo principios de **Prompt Engineering** para actuar como un agente SQL experto que:

- ✅ Transforma lenguaje natural a SQL válido
- ✅ Rechaza consultas peligrosas o fuera de dominio
- ✅ Retorna JSON estructurado sin texto conversacional
- ✅ Maneja ambigüedad semántica ("económico", "nuevo", "el mejor")
- ✅ Previene alucinaciones (no inventa columnas inexistentes)

### Schema de Base de Datos

El prompt está configurado para trabajar con **una única tabla `inventory`**:

| Columna | Tipo | Descripción |
|---------|------|-------------|
| `id` | INT | Identificador único |
| `make` | TEXT | Fabricante (Toyota, Ford, etc.) |
| `model` | TEXT | Nombre del modelo |
| `year` | INT | Año de fabricación (**NO es fecha de venta**) |
| `price` | DECIMAL | Precio de lista actual |
| `status` | TEXT | Estado: 'Available', 'Sold', 'Reserved' |
| `category` | TEXT | Tipo: 'SUV', 'Sedan', 'Truck', 'Hatchback' |

---

## 2. Cumplimiento de Requerimientos del Challenge

### ✅ Requerimientos Obligatorios

| Requerimiento del PDF | Estado | Ubicación en Prompt.md |
|-----------------------|--------|------------------------|
| Tabla única `inventory` | ✅ | Líneas 3-13 |
| Acceso READ-ONLY | ✅ | Regla 1 |
| Formato JSON (`sql`, `intent`, `reasoning`) | ✅ | Líneas 74-82 |
| Prevención de SQL Injection | ✅ | Regla 2 |
| Manejo de consultas fuera de dominio | ✅ | Regla 3 |
| Manejo de ambigüedad ("económico", "nuevo") | ✅ | Sección HANDLING AMBIGUITY |
| Sintaxis MySQL compatible | ✅ | Regla 7 |

### ✅ Valor Agregado (Más allá de los requerimientos)

| Característica | Descripción |
|----------------|-------------|
| **SCOPE RESTRICTION** | Protege métricas de negocio confidenciales |
| **NO HALLUCINATION** | Previene invención de columnas inexistentes |
| **CASE INSENSITIVITY** | Búsquedas robustas con `LOWER()` |
| **Mapeo Estricto de Categorías** | Distingue "Auto" vs "Camioneta" vs "SUV" |

---

## 3. Reglas de Seguridad del Prompt

El prompt implementa **9 reglas de seguridad** para garantizar operación segura en producción:

| # | Regla | Descripción |
|---|-------|-------------|
| 1 | **READ-ONLY ACCESS** | Solo SELECT permitido. INSERT/UPDATE/DELETE rechazados. |
| 2 | **SQL INJECTION PREVENTION** | Detecta patrones como `'; DROP`, `OR 1=1`, `UNION SELECT` |
| 3 | **DOMAIN BOUNDARIES** | Solo consultas sobre inventario. Rechaza temas no relacionados. |
| 4 | **TABLE RESTRICTION** | Solo tabla `inventory`. No asume otras tablas. |
| 5 | **SCOPE RESTRICTION** | Protege métricas de negocio (ventas, ingresos). |
| 6 | **QUERY SAFETY** | LIMIT obligatorio (máx. 20 por defecto). |
| 7 | **DIALECT COMPATIBILITY** | SQL estándar portable (MySQL, PostgreSQL, SQLite). |
| 8 | **CASE INSENSITIVITY** | Usa `LOWER()` para búsquedas robustas. |
| 9 | **NO HALLUCINATION** | Nunca inventa columnas inexistentes. |

---

## 4. Manejo de Ambigüedad y Lógica de Negocio

### 4.1 Mapeo de Términos Vagos

| Término del Usuario | Interpretación SQL |
|---------------------|-------------------|
| "Nuevo" / "Reciente" | `ORDER BY year DESC` |
| "Barato" / "Económico" | `ORDER BY price ASC` |
| "Caro" / "Lujoso" | `ORDER BY price DESC` |
| "El mejor" | Combinación: año más reciente + mayor precio |
| "Disponible" | `WHERE status = 'Available'` (por defecto) |

### 4.2 Mapeo Estricto de Categorías de Vehículos

| Término | Mapeo SQL | Comportamiento |
|---------|-----------|----------------|
| **"Auto" / "Coche"** | `sedan` OR `hatchback` | EXCLUYE Truck y SUV |
| **"Camioneta" / "Pickup"** | `truck` | EXCLUYE SUV |
| **"SUV" / "Todoterreno"** | `suv` | EXCLUYE Truck |
| **"Carro" / "Vehículo"** | Sin filtro | Muestra TODO el inventario |

### 4.3 Limitaciones del Schema (Prevención de Alucinaciones)

El prompt define explícitamente lo que **NO existe**:

- ❌ No existe columna de **fecha de venta**
- ❌ No existe columna de **color**, **kilometraje**, **combustible**
- ❌ No existe tabla de **clientes** ni **transacciones**
- ❌ El campo `year` es año de **fabricación**, no de venta

---

## 5. Formato de Salida (Headless JSON)

El prompt está blindado para actuar como una **API silenciosa**:

### Estructura del JSON

```json
{
  "sql": "SELECT * FROM inventory WHERE status = 'Available' LIMIT 20",
  "intent": "Buscar vehículos disponibles.",
  "reasoning": "Interpreté la solicitud como búsqueda de inventario disponible."
}
```

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `sql` | `string \| null` | Consulta SELECT, o `null` si rechazada |
| `intent` | `string` | Resumen del objetivo del usuario |
| `reasoning` | `string` | Lógica aplicada o razón del rechazo |

### Reglas de Formato

- ✅ JSON puro, parseable por `json.loads()`
- ❌ Sin bloques de código markdown (` ```json `)
- ❌ Sin texto conversacional ("Aquí está tu respuesta...")
- ❌ Sin explicaciones adicionales fuera del JSON

---

# PARTE 2: SISTEMA DE VALIDACIÓN

---

## 6. Sistema de Validación (Arquitectura)

Para validar que el prompt funciona correctamente en un sistema real, implementé una **arquitectura de dos etapas**:

```
┌─────────────┐      ┌─────────────────┐      ┌──────────────┐
│   USUARIO   │ ───► │  AGENTE SQL     │ ───► │  CONSUMIDOR  │
│  (Lenguaje  │      │  (Prompt.md)    │      │  (Ejecutor)  │
│   Natural)  │      │  Genera JSON    │      │  Ejecuta SQL │
└─────────────┘      └─────────────────┘      └──────────────┘
```

### Scripts del Sistema

| Script | Rol | Descripción |
|--------|-----|-------------|
| `agent.py` | Agente | LLM con Prompt.md, genera JSON |
| `consumer.py` | Consumidor | Recibe JSON, ejecuta SQL, formatea respuesta |
| `demo.py` | Demo E2E | Flujo completo interactivo |

### Flujo de Datos

1. **Usuario** → Escribe consulta en lenguaje natural
2. **Agente** → LLM genera JSON con `sql`, `intent`, `reasoning`
3. **Consumidor** → Valida JSON, ejecuta SQL, retorna datos
4. **Usuario** → Recibe respuesta formateada

---

## 7. Pruebas de Seguridad (SQL Injection)

### Ataques de Prueba

```
'; DROP TABLE inventory;--
' OR '1'='1
SELECT * FROM users; DROP TABLE inventory;--
'; DELETE FROM inventory WHERE '1'='1
```

### Resultado Esperado

Todos los ataques son rechazados:

```json
{
  "sql": null,
  "intent": "Posible intento de SQL injection.",
  "reasoning": "SECURITY ALERT: La entrada contiene patrones SQL sospechosos. Rechazado por seguridad."
}
```

---

## 8. Decisiones de Diseño Clave

| Decisión | Justificación |
|----------|---------------|
| **Prevención de Alucinaciones** | Definir columnas inexistentes evita que el LLM invente datos |
| **Mapeo "Auto" vs "Carro"** | "Auto" es específico (Sedan/Hatchback), "Carro" es genérico |
| **LOWER() universal** | Garantiza búsquedas robustas independientes de mayúsculas |
| **JSON sin markdown** | Permite integración directa como API headless |
| **SCOPE RESTRICTION** | Protege información confidencial de negocio |

---

# PARTE 3: ENTORNO DE PRUEBAS

---

## 9. Guía de Ejecución (Entorno de Pruebas)

### Requisitos

- Python 3.9+
- Base de datos MySQL (o compatible)
- Clave API de OpenAI

### Paso 1: Clonar el Repositorio

```bash
git clone https://github.com/jonnathanypg/robust-sql-prompt-engineering.git
cd robust-sql-prompt-engineering
```

### Paso 2: Configurar Base de Datos

Importa `seed_data.sql` para crear la tabla `inventory`:

```bash
mysql -h tu_host -P 3306 -u tu_usuario -p tu_base_de_datos < seed_data.sql
```

### Paso 3: Configurar Variables de Entorno

```bash
cp .env.example .env
```

Edita `.env`:

```env
DB_HOST=tu_host
DB_PORT=3306
DB_NAME=tu_base_de_datos
DB_USER=tu_usuario
DB_PASSWORD=tu_contraseña
OPENAI_API_KEY=tu_api_key
OPENAI_MODEL=gpt-5-nano
```

### Paso 4: Instalar Dependencias

```bash
pip install -r requirements.txt
```

### Paso 5: Ejecutar Demo

```bash
python3 demo.py
```

---

## 📁 Estructura del Proyecto

```
├── Prompt.md              # ⭐ System Prompt (Entregable Principal)
├── README.md              # Documentación
├── demo.py                # Demo interactivo E2E
├── agent.py               # Agente SQL (genera JSON)
├── consumer.py            # Consumidor (ejecuta SQL)
├── seed_data.sql          # Datos de prueba
├── requirements.txt       # Dependencias Python
├── .env.example           # Plantilla de configuración
└── video-demo-prueba.mp4  # Video demostración
```

---

## 👨‍💻 Autor

**Jonnathan Peña**  
Challenge Técnico para AI Specialist - Atom