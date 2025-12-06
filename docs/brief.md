# Project Brief: Optimización de Memoria para LLMs Pequeños

## Executive Summary

**Product Concept:**
Un sistema avanzado de memoria y recuperación para LLMs pequeños (<4B parámetros) diseñado para maximizar el rendimiento en el benchmark LongMemEval (versión S). El sistema implementará dos arquitecturas principales: un baseline sólido utilizando GraphRAG con búsqueda híbrida (Vector + Grafo) y un modelo avanzado que integra un pipeline agéntico de evaluación interna (con modelo <4B) y re-búsqueda para mejorar iterativamente la calidad de las respuestas antes de la evaluación final.

**Primary Problem:**
Los LLMs pequeños ("edge models") carecen de la capacidad nativa para manejar contextos extensos (~115k tokens) y realizar razonamientos complejos sobre historiales largos, limitando su utilidad en aplicaciones de asistentes conversacionales que requieren persistencia y síntesis de información a largo plazo.

**Target Market:**
Investigadores de IA y desarrolladores de aplicaciones en el borde (edge computing) que necesitan maximizar la eficiencia y precisión de modelos ligeros sin depender de LLMs masivos en la nube.

**Key Value Proposition:**
Lograr un rendimiento de memoria a largo plazo competitivo con modelos grandes, manteniendo la eficiencia de inferencia y privacidad de los modelos pequeños (<4B), mediante el uso estratégico de grafos de conocimiento y validación agéntica.

## Problem Statement

**Current State & Pain Points:**
Los modelos de lenguaje pequeños (como Phi 3.5 Mini) tienen ventanas de contexto limitadas y capacidad de razonamiento restringida en comparación con modelos SOTA. En el contexto de **LongMemEval** (sesiones de ~115k tokens), estos modelos fallan en:
1.  **Extracción de Información (IE):** Olvidan detalles antiguos dispersos.
2.  **Razonamiento Multi-Sesión (MR):** No pueden conectar puntos entre conversaciones distantes.
3.  **Actualización de Conocimiento (KU):** Alucinan con información obsoleta en lugar de usar la más reciente.
4.  **Razonamiento Temporal (TR):** Confunden la secuencia de eventos.

**Why Existing Solutions Fall Short:**
El enfoque de "RAG trivial" (búsqueda vectorial simple) recupera fragmentos aislados sin contexto relacional. Esto es insuficiente para preguntas que requieren síntesis o comprensión de la evolución temporal de los datos. Además, sin un mecanismo de evaluación (loop agéntico), el modelo no tiene oportunidad de corregir respuestas incompletas o erróneas.

**Impact:**
Sin una solución robusta, el sistema obtendrá puntajes bajos en las 5 métricas clave del benchmark, fallando especialmente en preguntas complejas de abstracción y actualización, lo que resulta en una penalización severa por parte del "Judge LLM".

**Urgency:**
Este proyecto es crítico para competir en el track de Investigathon, donde la eficiencia (<4B params) y la precisión de memoria son los únicos criterios de victoria.

## Proposed Solution

**Core Concept:**
Implementar una arquitectura dual para evaluación comparativa y mejora progresiva:

1.  **Baseline (GraphRAG Híbrido):**
    *   **Modelo:** Phi 3.5 Mini.
    *   **Mecanismo:** Búsqueda Híbrida que combina *Vector Search* (similitud semántica) con *Graph Search* (relaciones explícitas entre entidades).
    *   **Objetivo:** Capturar tanto el contexto global como los detalles específicos relacionales que el vector search pierde.

2.  **Modelo Avanzado (Agentic Loop):**
    *   **Pipeline:** Recuperación (Baseline) -> Generación -> Evaluación Agéntica -> (Re-intento).
    *   **Mecanismo:** Un agente "Juez" evalúa la respuesta preliminar del LLM contra la pregunta original. Si la respuesta es incompleta o insatisfactoria, activa una búsqueda secundaria con parámetros expandidos (más profundidad en el grafo o ventanas de tiempo diferentes).
    *   **Objetivo:** Corregir errores de "Abstention" y "Knowledge Update" mediante iteración.

**Key Differentiators:**
*   **Eficiencia Extrema:** Todo se ejecuta con modelos <4B, evitando la latencia y costos de modelos mayores.
*   **Grafo de Conocimiento:** Estructura las sesiones de chat como un grafo temporal, permitiendo "saltos" lógicos entre sesiones distantes (MR).
*   **Auto-corrección:** El loop agéntico mitiga las alucinaciones típicas de los modelos pequeños.

**High-Level Vision:**
Demostrar que la *arquitectura de recuperación* (Graph + Agent) es más determinante que el *tamaño del modelo* para tareas de memoria a largo plazo.

## Target Users

1.  **Primary Segment: Investigathon Evaluators**
    *   **Profile:** Jueces técnicos del evento YHat Investigathon.
    *   **Needs:** Verificar que la solución cumple con la restricción de <4B parámetros y supera al baseline en el benchmark.
    *   **Goal:** Encontrar enfoques novedosos y eficientes para memoria en LLMs.

2.  **Secondary Segment: Edge AI Researchers**
    *   **Profile:** Investigadores trabajando en IA on-device (móviles/IoT).
    *   **Needs:** Arquitecturas que maximicen la inteligencia con recursos limitados.

## Goals & Success Metrics

**Business Objectives:**
*   Ganar el track de Investigathon superando el desempeño del baseline y de otros competidores.
*   Validar la hipótesis de que el grafos + agentes pueden suplir la falta de parámetros.

**Key Performance Indicators (KPIs) - Defined by LongMemEval:**
*   **Accuracy Score (Primary):** Exactitud promedio evaluada por el Juez LLM (GPT-5-mini) en el set de *held-out* (250 preguntas ocultas). **Target:** > Baseline RAG.
*   **Latency:** Tiempo promedio de respuesta por pregunta. **Constraint:** Debe ser viable para inferencia (evitar loops infinitos en el agente).
*   **Variance:** Estabilidad en tiempos de respuesta.
*   **AVG Context Length:** Eficiencia en la recuperación (menor contexto = mayor eficiencia/velocidad).

**MVP Success Criteria:**
*   Implementación funcional del GraphRAG (Baseline).
*   Implementación funcional del Agentic Loop.
*   Ejecución completa del benchmark sin errores (500 preguntas).
*   Superar el score del "RAG trivial" proporcionado por la organización.

## MVP Scope

**Core Features (Must Have):**
*   **GraphRAG Baseline (Phi 3.5 Mini):**
    *   Pipeline de ingesta optimizado para no cargar todo en memoria (procesamiento por lotes de la carpeta `data`).
    *   Construcción de Grafo de Conocimiento (Entidades: Personas, Eventos, Fechas).
    *   Búsqueda Híbrida: Similitud vectorial + Navegación de grafo (1-hop/2-hop).
*   **Agentic Evaluation Pipeline (Internal Loop):**
    *   **Internal Evaluator (<4B - Phi 3.5 Mini):** Un agente "Crítico" que evalúa si la respuesta generada satisface la pregunta del usuario (Self-Reflection), SIN acceso al Ground Truth.
    *   **Lógica de Re-búsqueda:** Si el Evaluador Interno detecta alucinación o falta de información -> Ampliar query o profundidad de grafo.
*   **External Benchmark Judge:**
    *   **ChatGPT 5 Mini:** Usado ÚNICAMENTE como métrica final (JudgeAgent) para comparar la respuesta final del sistema contra el Ground Truth. Es el único componente >4B permitido.
*   **Integration Wrapper:**
    *   Modificación de `main.py` para inyectar estos pipelines manteniendo la interfaz de evaluación original.
    *   Sistema de configuración (`config`) para switch fácil entre Baseline y Agentic Mode.

**Out of Scope for MVP:**
*   Fine-tuning de modelos (usaremos Phi 3.5 Mini "out of the box" con buen prompting).
*   Interfaz Gráfica de Usuario (UI) compleja (todo es CLI/Script).
*   Soporte para modelos >4B parámetros.
*   Procesamiento de imágenes/multimodal (solo texto según benchmark).

## Post-MVP Vision

**Phase 2 Features:**
*   **Re-ranking Avanzado:** Implementar un modelo cross-encoder pequeño para filtrar mejor los resultados del grafo.
*   **Memoria Dinámica:** Sistema para actualizar el grafo en tiempo real durante la conversación (para producción, no solo benchmark estático).

**Long-term Vision:**
Convertirse en el estándar de facto para "Small Language Model Memory", permitiendo asistentes personales verdaderamente inteligentes en dispositivos móviles sin dependencia de la nube.

## Technical Considerations

**Platform Requirements:**
*   **Target:** Linux Environment (Ubuntu).
*   **Hardware:** GPU modesta (para correr modelos <4B).
*   **Performance:** El script `main.py` debe manejar la carga de datos sin OOM (Out Of Memory).

**Technology Preferences:**
*   **Language:** Python (integración con `main.py`).
*   **LLM Framework:** **LlamaIndex** (Seleccionado por sus capacidades nativas de `KnowledgeGraphIndex` y mejor abstracción para RAG avanzado vs LangChain).
*   **Graph Database:** **NetworkX** (Seleccionado por simplicidad, compatibilidad "Edge" y cero dependencias externas para el MVP).
*   **Vector DB:** `FAISS` o `ChromaDB` (ligeros, locales).
*   **Judge Model API:** OpenAI API (para ChatGPT 5 Mini).

**Architecture Considerations:**
*   **Modularidad:** Separar claramente `Ingestion`, `Retrieval (Graph/Vector)`, `Generation`, y `Evaluation`.
*   **Data Handling:** La carpeta `data` es grande. Usar generadores/iteradores para no cargar todo en RAM.
*   **Dependency Injection:** Inyectar los nuevos componentes en `main.py` sin reescribir la lógica de evaluación existente.

**Data Strategy:**
*   **Development/Graph Build:** `data/longmemeval` (Usado como "Training Data" para probar la ingesta y construcción del grafo).
*   **Internal Validation:** `data/investigathon/Investigathon_LLMTranck_Evaluation_s_cleaned.json` (Tiene respuestas. Usado para medir Accuracy durante el desarrollo).
*   **Final Submission:** `data/investigathon/Investigathon_LLMTrack_HeldOut_s_cleaned.json` (Sin respuestas. Generar JSON de salida para enviar al Jurado).

## Constraints & Assumptions

**Constraints:**
*   **Model Size:** Estrictamente <4B parámetros para TODO el proceso de generación (incluyendo el Evaluador Interno).
*   **External Judge:** ChatGPT 5 Mini SOLO permitido para el cálculo del score final (no en el loop de inferencia).
*   **Data Volume:** No cargar todo el dataset en memoria.
*   **Budget/Time:** Entrega rápida para el Hackathon.

**Key Assumptions:**
*   Tenemos acceso a la API de ChatGPT 5 Mini para el juez.
*   El script `main.py` existente es extensible.
*   Los datos en `benchmark_explanation.md` son consistentes con los archivos reales.

## Risks & Open Questions

**Key Risks:**
*   **Latencia Excesiva:** Que el loop agéntico tarde demasiado y el benchmark penalice por tiempo. *Mitigación: Limitar el número máximo de reintentos (max_retries=1).*
*   **Alucinaciones del Grafo:** Que el modelo extraiga relaciones falsas al construir el grafo. *Mitigación: Prompt engineering estricto en la fase de extracción.*
*   **Complejidad de Integración:** Que `main.py` sea difícil de modificar. *Mitigación: Usar el patrón Adapter/Wrapper.*

## Next Steps

**Immediate Actions:**
1.  **Exploración de Datos:** Inspeccionar la estructura real de la carpeta `data` y correr el "RAG trivial" para tener un baseline real.
2.  **Configuración de Entorno:** Instalar librerías (`networkx`, `faiss-cpu`, `langchain`).
3.  **Prototipo de Grafo:** Crear un script de prueba para procesar UNA sola sesión y visualizar el grafo generado.
4.  **Integration Wrapper:** Crear el esqueleto en `src/graph_rag.py` (o similar) que imite la interfaz esperada por `main.py`.

**PM Handoff:**
This Project Brief provides the full context for **Optimización de Memoria para LLMs Pequeños**. Please start in 'PRD Generation Mode', review the brief thoroughly to work with the user to create the PRD section by section as the template indicates, asking for any necessary clarification or suggesting improvements.



