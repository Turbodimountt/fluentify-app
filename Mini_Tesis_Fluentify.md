# **TÍTULO DEL PROYECTO**

**"Desarrollo de una solución tecnológica multiplataforma para el aprendizaje de lenguas extranjeras basada en modelos de lenguaje de gran escala (LLM) y visión artificial para la reducción de la ansiedad lingüística"**

---

## **RESUMEN EXECUTIVO**
El presente proyecto propone el desarrollo de **Fluentify**, una plataforma integral diseñada para abordar uno de los mayores obstáculos en el aprendizaje de idiomas: la ansiedad lingüística y la brecha entre el conocimiento teórico y la fluidez verbal. Mediante la integración de Modelos de Lenguaje de Gran Escala (LLM) para diálogos naturales, sistemas de procesamiento de voz (STT/TTS) para feedback fonético y algoritmos de visión artificial para la validación de escritura manual, Fluentify ofrece un entorno seguro, adaptativo y altamente personalizado. La solución se orienta a estudiantes que, a pesar de dominar reglas gramaticales, enfrentan parálisis comunicativa en contextos reales, especialmente en entornos profesionales específicos.

---

## **1. INTRODUCCIÓN**
El aprendizaje de una segunda lengua en la era digital ha evolucionado de métodos puramente gramaticales a enfoques comunicativos. Sin embargo, persiste el fenómeno conocido como "Foreign Language Anxiety" (FLA), donde el miedo al juicio social impide la práctica efectiva del habla. Fluentify utiliza la Inteligencia Artificial Generativa no solo como una herramienta de enseñanza, sino como un compañero de práctica no intimidante que permite al usuario cometer errores y recibir feedback pedagógico en tiempo real sin la presión de un interlocutor humano.

---

## **2. EL PROBLEMA**

### **2.1 Planteamiento del Problema**
Los métodos tradicionales de aprendizaje digital suelen basarse en la repetición mecánica de frases descontextualizadas, lo que genera una "fluidez incompleta": el estudiante puede decodificar textos, pero es incapaz de producir discurso coherente en una conversación fluida. A esto se suma la falta de personalización, donde los cursos generales no cubren las necesidades técnicas de profesionales en áreas como medicina, ingeniería o finanzas.

### **2.2 Análisis de Causas, Efectos y Consecuencias**
A continuación, se presenta la matriz de análisis que fundamenta la necesidad del presente proyecto:

| **Causas (¿Por qué pasa?)** | **Efectos (¿Qué sucede hoy?)** | **Consecuencias (Impacto a futuro)** |
| :--- | :--- | :--- |
| **Métodos pasivos:** Aplicaciones basadas en la repetición de frases sueltas o gramática pura. | El alumno sabe leer y escribir, pero es incapaz de mantener una conversación real. | Frustración crónica y abandono del estudio por falta de progreso tangible. |
| **Ansiedad Social:** Miedo al juicio humano al pronunciar mal o cometer errores. | El estudiante evita practicar el habla ("Silencio defensivo"). | Desarrollo de una "fluidez incompleta" que limita oportunidades laborales. |
| **Contenido Genérico:** Lecciones iguales para todos los perfiles (médicos, gamers, etc.). | Falta de interés y desmotivación al estudiar temas no útiles para el usuario. | Pérdida de tiempo y recursos en cursos que no se adaptan al mercado real. |

---

## **3. OBJETIVOS DEL PROYECTO**

### **3.1 Objetivo General**
Desarrollar una plataforma multiplataforma (móvil y escritorio) de aprendizaje de idiomas que utilice Inteligencia Artificial Generativa para eliminar la brecha entre el conocimiento teórico y la fluidez verbal mediante entornos de práctica seguros y adaptativos.

### **3.2 Objetivos Específicos**
*   **Implementar un motor de IA conversacional** capaz de simular escenarios de la vida real (Roleplay) que evalúe gramática, coherencia y tono.
*   **Diseñar una interfaz de usuario (UI) de alta retención** basada en gamificación y "nodos de conocimiento" (Constelaciones).
*   **Desarrollar el "Modo Susurro"**, una funcionalidad de reconocimiento de voz de baja presión para practicar fonética sin ansiedad social.
*   **Integrar un sistema de reconocimiento de trazo** para el aprendizaje de alfabetos no latinos (Kanjis, Cirílico) mediante visión artificial.

---

## **4. JUSTIFICACIÓN: NECESIDADES A CUBRIR**
El proyecto Fluentify se justifica en la necesidad de resolver tres carencias críticas del mercado educativo tecnológico:

1.  **Personalización Masiva:** Adaptar el vocabulario y los escenarios de práctica a los intereses profesionales específicos (ingeniería, turismo, salud, etc.).
2.  **Feedback Inmediato:** Proporcionar corrección en tiempo real de errores gramaticales y de pronunciación mediante la estructura: *texto_original → corrección → explicación*.
3.  **Alfabetización Visual:** Solucionar la carencia de enseñanza de escritura manual en idiomas asiáticos o eslavos, validando no solo la forma sino el orden correcto de los trazos.

---

## **5. PROPUESTA TÉCNICA**

### **5.1 Arquitectura del Sistema**
La solución utiliza una arquitectura desacoplada para garantizar escalabilidad y rendimiento:
*   **Backend (FastAPI):** Encargado de la lógica de negocio, gestión de sesiones WebSocket para streaming y persistencia en PostgreSQL.
*   **Frontend (React/Vite & Flutter):** Interfaces responsivas diseñadas para una experiencia de usuario premium, con micro-animaciones y soporte multiplataforma.
*   **Motor de IA (OpenAI GPT-4o):** Orquestación de prompts dinámicos para los diferentes modos de práctica.
*   **Visión Artificial (MediaPipe):** Procesamiento de trazos en el cliente para feedback instantáneo (< 500ms).

---

## **6. CONCLUSIONES PRELIMINARES**
La integración de LLMs y visión artificial representa un cambio de paradigma en la enseñanza de idiomas. Fluentify no solo enseña un lenguaje, sino que construye la confianza necesaria para usarlo, reduciendo activamente la ansiedad del estudiante y optimizando el tiempo de retención mediante algoritmos de repetición espaciada (SM-2).
