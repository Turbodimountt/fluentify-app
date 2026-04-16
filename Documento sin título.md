

**Especificación de Requerimientos**

**de Software (SRS)**

Fluentify — Plataforma de Aprendizaje de Idiomas con IA

| Versión | 1.0 |
| :---- | :---- |
| **Fecha** | Marzo 2026 |
| **Estado** | Borrador para revisión |
| **Plataforma base** | FastAPI · Flutter · PostgreSQL · OpenAI |

 

Equipo de Producto · Fluentify Inc.

 

| Resumen del Documento |
| ----- |
| Este documento constituye la Especificación de Requerimientos de Software (SRS) para Fluentify, una plataforma multiplataforma de aprendizaje de idiomas basada en Inteligencia Artificial. Describe de forma completa y sin ambigüedades los requerimientos funcionales, no funcionales, el modelo de datos, la arquitectura técnica y los criterios de aceptación que guiarán el desarrollo del sistema. |

 

**Tabla de Contenidos**

 

 

1\. Introducción...................................................................................................................................... 1

1.1 Propósito del Documento........................................................................................................... 1

1.2 Alcance del Sistema................................................................................................................... 1

1.3 Definiciones, Acrónimos y Abreviaturas.................................................................................... 1

1.4 Referencias................................................................................................................................ 1

1.5 Descripción General del Documento......................................................................................... 1

2\. Descripción General del Sistema.................................................................................................... 1

2.1 Perspectiva del Producto........................................................................................................... 1

2.2 Objetivos del Producto............................................................................................................... 1

2.3 Funciones Principales del Sistema............................................................................................ 1

2.4 Roles de Usuario........................................................................................................................ 1

2.5 Entorno Operativo...................................................................................................................... 1

3\. Requerimientos Funcionales........................................................................................................... 1

3.1 Módulo de Autenticación............................................................................................................ 1

3.2 Módulo de Onboarding y Perfil.................................................................................................. 1

3.3 Módulo de Conversación con IA................................................................................................ 1

3.4 Módulo de Feedback y Correcciones........................................................................................ 1

3.5 Módulo de Voz (Speech)........................................................................................................... 1

3.6 Módulo de Visión Artificial.......................................................................................................... 1

3.7 Módulo de Gamificación............................................................................................................. 1

3.8 Módulo de Reportes y Estadísticas........................................................................................... 1

4\. Requerimientos No Funcionales..................................................................................................... 1

5\. Modelo de Datos.............................................................................................................................. 1

5.1 Tablas Principales...................................................................................................................... 1

5.2 Políticas de Seguridad a Nivel de Fila (RLS)............................................................................ 1

6\. Arquitectura Técnica y Restricciones.............................................................................................. 1

6.1 Stack Tecnológico...................................................................................................................... 1

6.2 Restricciones del Proyecto........................................................................................................ 1

6.3 Dependencias Externas............................................................................................................. 1

7\. Interfaces del Sistema..................................................................................................................... 1

7.1 Interfaces de Usuario — Vistas Principales.............................................................................. 1

7.2 Interfaces de la API Backend..................................................................................................... 1

8\. Criterios de Aceptación.................................................................................................................... 1

8.1 Criterios Generales.................................................................................................................... 1

8.2 Criterios por Módulo................................................................................................................... 1

8.3 Matriz de Trazabilidad................................................................................................................ 1

9\. Control de Cambios del Documento................................................................................................ 1

Próximas versiones previstas.......................................................................................................... 1

 

 

# **1\. Introducción**

 

## **1.1 Propósito del Documento**

Este documento constituye la Especificación de Requerimientos de Software (SRS) para Fluentify, una plataforma multiplataforma de aprendizaje de idiomas basada en Inteligencia Artificial. Su objetivo es describir de manera clara, completa y sin ambigüedades todos los requerimientos que deberá satisfacer el sistema a desarrollar, sirviendo como acuerdo entre las partes interesadas y guía técnica para el equipo de desarrollo.

 

## **1.2 Alcance del Sistema**

Fluentify tendrá el siguiente alcance en su versión 1.0:

•  Motor de IA conversacional con tres modos: Libre, Roleplay Profesional y Modo Susurro.

•  Personalización del vocabulario y escenarios según el Contexto Profesional del usuario.

•  Análisis de pronunciación y feedback fonético mediante STT y TTS.

•  Reconocimiento de trazos para escritura manual en Kanji (N5) y alfabeto Cirílico.

•  Sistema de gamificación: XP, nodos de conocimiento (SM-2), rachas, logros y niveles.

•  App multiplataforma: iOS, Android, Web y Desktop (Flutter).

•  API RESTful y WebSocket en tiempo real (FastAPI \+ PostgreSQL).

 

Quedan fuera del alcance de esta versión:

•  Panel de administración B2B para gestión de equipos empresariales.

•  Integración con plataformas LMS externas (Moodle, Canvas).

•  Evaluación formal CEFR con emisión de certificados.

•  Soporte para escrituras RTL (Árabe) o Devanagari (Hindi).

•  Módulo de pagos y suscripciones (gestionado externamente).

 

## **1.3 Definiciones, Acrónimos y Abreviaturas**

 

| Término | Definición |
| ----- | ----- |
| **SRS** | Software Requirements Specification — Especificación de Requerimientos de Software |
| **RF** | Requerimiento Funcional |
| **RNF** | Requerimiento No Funcional |
| **LLM** | Large Language Model — Modelo de Lenguaje de Gran Escala (ej. GPT-4o) |
| **STT** | Speech-to-Text — Conversión de voz a texto |
| **TTS** | Text-to-Speech — Conversión de texto a voz |
| **CEFR** | Common European Framework of Reference for Languages — Marco europeo de referencia para idiomas (A1–C2) |
| **JWT** | JSON Web Token — Estándar para transmisión segura de autenticación entre partes |
| **SM-2** | SuperMemo 2 — Algoritmo de repetición espaciada para optimizar la retención de conocimiento |
| **XP** | Experience Points — Puntos de Experiencia del sistema de gamificación |
| **Modo Susurro** | Modo de práctica de fonética de baja presión diseñado para reducir la ansiedad lingüística |
| **Roleplay** | Juego de roles inmersivo donde la IA adopta un personaje de un escenario profesional |
| **Nodo de Conocimiento** | Unidad de habilidad lingüística con nivel de maestría y próxima fecha de repaso |
| **WER** | Word Error Rate — Tasa de error de palabras en transcripción de voz (métrica de calidad STT) |
| **CNN** | Convolutional Neural Network — Red Neuronal Convolucional para clasificación de imágenes (trazos) |
| **API** | Application Programming Interface — Interfaz de Programación de Aplicaciones |
| **WebSocket** | Protocolo de comunicación bidireccional y persistente para streaming de tokens en tiempo real |

 

## **1.4 Referencias**

 

•  OpenAI API Reference: https://platform.openai.com/docs

•  Google Cloud Speech-to-Text: https://cloud.google.com/speech-to-text/docs

•  ElevenLabs API Documentation: https://docs.elevenlabs.io

•  MediaPipe Hands: https://developers.google.com/mediapipe/solutions/vision/hand\_landmarker

•  Flutter Documentation: https://docs.flutter.dev

•  FastAPI Documentation: https://fastapi.tiangolo.com

•  WCAG 2.1 — Web Content Accessibility Guidelines: https://www.w3.org/TR/WCAG21/

•  OWASP Top 10: https://owasp.org/www-project-top-ten/

•  SM-2 Algorithm: https://www.supermemo.com/en/blog/application-of-a-computer-to-improve-the-results-obtained-in-working-with-the-supermemo-method

 

## **1.5 Descripción General del Documento**

El resto del documento se organiza de la siguiente manera: la Sección 2 describe la visión general del producto y sus objetivos; la Sección 3 detalla los requerimientos funcionales agrupados por módulo; la Sección 4 expone los requerimientos no funcionales; la Sección 5 describe el modelo de datos; la Sección 6 incluye el stack tecnológico, restricciones y dependencias; la Sección 7 presenta las interfaces del sistema; la Sección 8 define los criterios de aceptación y la matriz de trazabilidad; y la Sección 9 registra el control de cambios del documento.

 

# **2\. Descripción General del Sistema**

 

## **2.1 Perspectiva del Producto**

Fluentify es una plataforma de aprendizaje de idiomas de nueva generación que cierra la brecha entre el conocimiento gramatical teórico y la fluidez verbal. A diferencia de aplicaciones basadas en repetición mecánica (Duolingo, Babbel), Fluentify propone aprendizaje situado: el error es parte del juego, no una penalización.

El sistema se construirá como una aplicación multiplataforma (Flutter) que se comunica con un backend propio en FastAPI, integrando modelos LLM de última generación (GPT-4o) para el motor conversacional, visión artificial para el reconocimiento de escritura manual, y servicios de voz para práctica fonética.

 

## **2.2 Objetivos del Producto**

 

| ID | Objetivo | Indicador de Éxito |
| ----- | ----- | ----- |
| **OBJ-01** | **Reducir la ansiedad lingüística** | El 80% de los usuarios reportan menos miedo a hablar tras 4 semanas de uso (encuesta in-app) |
| **OBJ-02** | **Fluidez verbal contextualizada** | El usuario completa una sesión de roleplay de 10 minutos sin abandonar antes del turno 5 |
| **OBJ-03** | **Vocabulario profesional activo** | El usuario incorpora ≥ 20 términos de su contexto profesional en 30 días |
| **OBJ-04** | **Escritura de sistemas no latinos** | El usuario reconoce y traza correctamente ≥ 50 Kanji N5 en el primer mes |
| **OBJ-05** | **Retención y hábito** | Retención D7 \> 40%, retención D30 \> 25% medida en cohortes mensuales |

 

## **2.3 Funciones Principales del Sistema**

 

| Módulo | Descripción | Usuarios |
| ----- | ----- | :---: |
| **Motor de IA Conversacional** | Diálogos fluidos en tiempo real con evaluación de gramática, coherencia y tono | Todos |
| **Modo Roleplay Profesional** | Escenarios inmersivos adaptados al contexto profesional del usuario | Todos |
| **Modo Susurro** | Práctica de fonética de baja presión con feedback no intimidante | Todos |
| **Análisis de Voz (STT/TTS)** | Transcripción en tiempo real y reproducción de pronunciación modelo | Todos |
| **Visión Artificial** | Reconocimiento y validación de trazos para escrituras Kanji y Cirílico | Todos |
| **Sistema de Gamificación** | XP, nodos de conocimiento, rachas, logros y niveles de usuario | Todos |
| **Reportes de Progreso** | Estadísticas, historial de sesiones y exportación de datos de aprendizaje | Todos |

 

## **2.4 Roles de Usuario**

 

| Rol | Descripción | Permisos Principales |
| ----- | ----- | ----- |
| **Estudiante** | Usuario estándar del sistema | Acceso a todos los modos de práctica, historial personal, estadísticas y logros propios |
| **Administrador** | Gestor del sistema (futura versión B2B) | Todo lo del estudiante \+ gestión de usuarios, configuración de contextos y reportes globales |

 

## **2.5 Entorno Operativo**

 

•  Plataformas: iOS 15+, Android 8+, Web (Chrome 90+ / Firefox 88+ / Safari 14+), macOS, Windows.

•  Dispositivos: Smartphone, tablet y desktop (diseño responsive desde 320px).

•  Conectividad: Requiere conexión a internet. La latencia del WebSocket es crítica para la UX conversacional.

•  Backend: Propio en FastAPI (Python 3.12+) con PostgreSQL 16 y Redis 7\.

•  IA: OpenAI API (GPT-4o), Google Cloud Speech-to-Text, ElevenLabs TTS.

 

# **3\. Requerimientos Funcionales**

 

## **3.1 Módulo de Autenticación**

 

| ID | Nombre | Descripción | Prioridad |
| ----- | ----- | ----- | :---: |
| **RF-01** | **Registro de Usuario** | El sistema permitirá que nuevos usuarios se registren con nombre, correo electrónico y contraseña. Se validará el correo mediante enlace de confirmación. | Alta |
| **RF-02** | **Inicio de Sesión** | El usuario podrá autenticarse con correo y contraseña. Se generará un JWT válido almacenado de forma segura en el cliente. | Alta |
| **RF-03** | **Cierre de Sesión** | El usuario podrá cerrar sesión en cualquier momento, invalidando el token activo y limpiando el historial de sesión. | Alta |
| **RF-04** | **Recuperación de Contraseña** | El usuario podrá solicitar un enlace de recuperación de contraseña enviado a su correo registrado. | Media |
| **RF-05** | **Persistencia de Sesión** | La sesión persistirá entre cierres de la app durante un período configurable (máximo 7 días). | Media |
| **RF-06** | **OAuth Social** | El sistema soportará inicio de sesión con Google como proveedor OAuth adicional. | Baja |

 

## **3.2 Módulo de Onboarding y Perfil**

 

| ID | Nombre | Descripción | Prioridad |
| ----- | ----- | ----- | :---: |
| **RF-07** | **Selección de Idioma** | En el onboarding, el usuario seleccionará su idioma objetivo (Inglés, Japonés, Ruso, Francés, Mandarín) y su nivel CEFR inicial. | Alta |
| **RF-08** | **Contexto Profesional** | El usuario elegirá un Contexto Profesional (Medicina, Ingeniería, Videojuegos, Finanzas, General) que adaptará el vocabulario y los escenarios. | Alta |
| **RF-09** | **Configuración de Preferencias** | El usuario podrá configurar: idioma de la interfaz, nivel de correcciones (bajo/medio/alto) y activación del Modo Susurro por defecto. | Media |

 

## **3.3 Módulo de Conversación con IA**

 

| ID | Nombre | Descripción | Prioridad |
| ----- | ----- | ----- | :---: |
| **RF-10** | **Chat con IA (Modo Libre)** | El sistema permitirá conversaciones libres con el motor de IA, evaluando gramática, coherencia y tono en tiempo real. | Alta |
| **RF-11** | **Modo Roleplay Profesional** | El usuario podrá seleccionar un escenario de roleplay contextualizado a su perfil profesional. La IA permanecerá en personaje durante la sesión. | Alta |
| **RF-12** | **Modo Susurro** | Modo de práctica de fonética de baja presión: máximo 2 correcciones por turno, tono cálido y refuerzo positivo. Diseñado para reducir la ansiedad lingüística. | Alta |
| **RF-13** | **Streaming en Tiempo Real** | Las respuestas de la IA se transmitirán token-a-token vía WebSocket para minimizar la latencia percibida y no romper el flujo conversacional. | Alta |
| **RF-14** | **Historial de Conversación** | El sistema mantendrá el historial de los últimos 10 turnos activos y persistirá la sesión completa en base de datos al finalizarla. | Alta |
| **RF-15** | **Selección de Escenarios** | El usuario podrá seleccionar entre mínimo 5 escenarios de roleplay por contexto profesional, con descripción previa del rol que asumirá la IA. | Media |

 

## **3.4 Módulo de Feedback y Correcciones**

 

| ID | Nombre | Descripción | Prioridad |
| ----- | ----- | ----- | :---: |
| **RF-16** | **Correcciones en Tiempo Real** | Al finalizar cada turno, el sistema proveerá correcciones instantáneas con tres campos: texto original → corrección → explicación pedagógica. | Alta |
| **RF-17** | **Niveles de Severidad** | Cada corrección tendrá un nivel: Baja (sugerencia de estilo), Media (error notable) o Alta (error que impide la comprensión). | Alta |
| **RF-18** | **Vocabulario Destacado** | El sistema resaltará 1–3 términos especializados del contexto profesional en cada respuesta de la IA, con su traducción y ejemplo de uso. | Media |
| **RF-19** | **Rating de Feedback** | El usuario podrá marcar una corrección como 'no útil' para mejorar la personalización del modelo a lo largo del tiempo. | Baja |
| **RF-20** | **Sugerencia de Continuación** | Al finalizar cada turno, el sistema sugerirá una pregunta o acción para continuar el flujo conversacional. | Baja |

 

## **3.5 Módulo de Voz (Speech)**

 

| ID | Nombre | Descripción | Prioridad |
| ----- | ----- | ----- | :---: |
| **RF-21** | **Entrada de Voz (STT)** | En Modo Susurro, el usuario podrá enviar mensajes de voz que serán transcritos en tiempo real mediante Google Cloud Speech-to-Text. | Alta |
| **RF-22** | **Pronunciación Modelo (TTS)** | El sistema podrá reproducir la pronunciación correcta de palabras o frases a petición del usuario, usando ElevenLabs TTS. | Media |
| **RF-23** | **Análisis de Pronunciación** | El sistema analizará la pronunciación del usuario y ofrecerá feedback sobre fonemas específicos, comparando con el modelo nativo. | Media |

 

## **3.6 Módulo de Visión Artificial**

 

| ID | Nombre | Descripción | Prioridad |
| ----- | ----- | ----- | :---: |
| **RF-24** | **Reconocimiento de Trazos** | El sistema validará el orden y forma de trazos para escrituras manuales de Kanji (N5, 80 caracteres) y alfabeto Cirílico (66 caracteres). | Alta |
| **RF-25** | **Guía Animada de Trazos** | Para cada carácter, el sistema mostrará una animación del orden correcto de trazos antes de la práctica del usuario. | Alta |
| **RF-26** | **Feedback Visual de Trazo** | El sistema mostrará en tiempo real si el trazo es correcto (verde) o incorrecto (rojo con flecha guía de corrección). | Alta |
| **RF-27** | **Latencia de Análisis** | El análisis del trazo debe completarse en menos de 500ms desde que el usuario levanta el dedo/lápiz del canvas. | Alta |

 

## **3.7 Módulo de Gamificación**

 

| ID | Nombre | Descripción | Prioridad |
| ----- | ----- | ----- | :---: |
| **RF-28** | **Sistema de XP** | El usuario acumulará puntos de experiencia (XP) al finalizar cada sesión, calculados en función de la duración, el modo y la tasa de corrección. | Alta |
| **RF-29** | **Nodos de Conocimiento** | El progreso se visualizará como una constelación de nodos de conocimiento, cada uno representando una habilidad lingüística con su nivel de maestría. | Alta |
| **RF-30** | **Repetición Espaciada (SM-2)** | El sistema aplicará el algoritmo SM-2 para determinar cuándo el usuario debe repasar cada nodo de conocimiento. | Alta |
| **RF-31** | **Sistema de Rachas** | El sistema registrará rachas de días consecutivos de práctica y enviará notificación push si el usuario no practica en 20 horas. | Media |
| **RF-32** | **Logros y Badges** | El sistema otorgará logros desbloqueables (ej. 'Primera Sesión', 'Racha de 7 días', 'Sin Errores') con animación de celebración. | Media |
| **RF-33** | **Niveles de Usuario** | El sistema definirá 7 rangos progresivos (Explorador → Maestro) basados en el XP acumulado total. | Media |

 

## **3.8 Módulo de Reportes y Estadísticas**

 

| ID | Nombre | Descripción | Prioridad |
| ----- | ----- | ----- | :---: |
| **RF-34** | **Estadísticas de Progreso** | El usuario podrá consultar sus estadísticas: XP total, racha actual, nodos dominados, tasa de corrección histórica y tiempo practicado. | Alta |
| **RF-35** | **Historial de Sesiones** | El usuario accederá al historial completo de sesiones pasadas, con detalle de correcciones, vocabulario y XP ganado por sesión. | Media |
| **RF-36** | **Exportación de Progreso** | El usuario podrá exportar su historial de correcciones y vocabulario aprendido en formato CSV. | Baja |

 

# **4\. Requerimientos No Funcionales**

 

| ID | Categoría | Descripción | Prioridad |
| ----- | ----- | ----- | :---: |
| **RNF-01** | **Rendimiento — Latencia** | El primer token de respuesta del motor de IA debe llegar al cliente en menos de 800ms desde que el usuario envía su mensaje. | Alta |
| **RNF-02** | **Rendimiento — Análisis de Voz** | La transcripción de voz (STT) debe estar disponible en menos de 1.5 segundos para sesiones de hasta 60 segundos de audio. | Alta |
| **RNF-03** | **Rendimiento — Análisis de Trazo** | El análisis de trazo de escritura manual debe completarse en menos de 500ms. | Alta |
| **RNF-04** | **Disponibilidad** | La API debe tener una disponibilidad mínima del 99.5% mensual. El frontend debe mostrar un estado offline elegante ante fallas de conectividad. | Alta |
| **RNF-05** | **Escalabilidad** | La arquitectura debe soportar hasta 1,000 usuarios concurrentes con WebSocket activo sin degradación de rendimiento perceptible. | Media |
| **RNF-06** | **Seguridad — Autenticación** | Todos los endpoints protegidos requieren JWT válido. Los tokens de acceso expiran en 15 minutos; los refresh tokens, en 7 días. | Alta |
| **RNF-07** | **Seguridad — Almacenamiento** | Las contraseñas se almacenarán exclusivamente como hash bcrypt (cost factor ≥ 12). Nunca en texto plano ni con MD5/SHA1. | Alta |
| **RNF-08** | **Seguridad — API Keys** | Las claves de API de OpenAI, ElevenLabs y Google Cloud nunca se expondrán al cliente. Solo se utilizarán en el entorno de servidor. | Alta |
| **RNF-09** | **Seguridad — Rate Limiting** | La API aplicará rate limiting de 60 req/min por IP globalmente y 20 req/min en endpoints de autenticación para prevenir fuerza bruta. | Alta |
| **RNF-10** | **Privacidad — Datos de Voz** | El audio capturado en Modo Susurro se procesará en memoria y no se almacenará de forma persistente. Solo se guarda la transcripción. | Alta |
| **RNF-11** | **Privacidad — RGPD/GDPR** | El usuario podrá solicitar la exportación completa de sus datos o la eliminación total de su cuenta en cualquier momento. | Alta |
| **RNF-12** | **Multiplataforma** | La app Flutter debe funcionar en iOS 15+, Android 8+, Web (Chrome/Firefox/Safari) y macOS/Windows como app de escritorio. | Alta |
| **RNF-13** | **Responsive / Accesibilidad** | La interfaz debe ser funcional en pantallas desde 320px. Se cumplirán los criterios de contraste WCAG 2.1 nivel AA. | Alta |
| **RNF-14** | **Seguridad Psicológica** | El Modo Susurro debe estar diseñado para ser percibido como un espacio seguro: sin puntuaciones agresivas, sin sonidos de error, con refuerzo positivo. | Alta |
| **RNF-15** | **Localización** | La interfaz del sistema debe estar disponible en Español e Inglés como idiomas de la aplicación (no del aprendizaje). | Media |
| **RNF-16** | **Mantenibilidad** | El código del backend debe mantener una cobertura de tests ≥ 70%. El frontend debe tener widget tests para las pantallas críticas. | Media |

 

# **5\. Modelo de Datos**

 

## **5.1 Tablas Principales**

 

| Tabla | Descripción | Campos Principales |
| ----- | ----- | ----- |
| **users** | Cuentas de usuario | id (UUID PK), email, hashed\_password, display\_name, is\_active, created\_at, updated\_at |
| **user\_profiles** | Perfil lingüístico y gamificación | id (UUID PK), user\_id (FK), target\_language, native\_language, cefr\_level, professional\_context\_id (FK), total\_xp, current\_streak, last\_session\_at |
| **professional\_contexts** | Contextos profesionales disponibles | id (UUID PK), name, slug, vocabulary\_tags (TEXT\[\]), scenario\_templates (JSONB), icon\_slug |
| **sessions** | Registro de sesiones de práctica | id (UUID PK), user\_id (FK), session\_type, professional\_ctx, target\_language, scenario\_name, duration\_seconds, xp\_earned, messages\_count, errors\_detected, started\_at, ended\_at |
| **conversation\_logs** | Mensajes individuales por sesión | id (UUID PK), user\_id (FK), session\_id (FK), turn\_number, user\_message (TEXT), ai\_response (TEXT), detected\_errors (JSONB), confidence\_score, created\_at |
| **feedback\_entries** | Correcciones detalladas por turno | id (UUID PK), conversation\_log\_id (FK), feedback\_type, original\_text, corrected\_text, explanation, severity ('low'|'medium'|'high'), was\_helpful |
| **knowledge\_nodes** | Nodos de la constelación de aprendizaje | id (UUID PK), user\_id (FK), category\_id (FK), node\_key, display\_label, mastery\_score (0.0–1.0), repetitions, easiness\_factor, interval\_days, next\_review\_at |
| **node\_categories** | Taxonomía de habilidades | id (UUID PK), name, parent\_id (FK), skill\_area ('grammar'|'vocabulary'|'phonetics'|'writing'|'culture'), color\_hex |
| **achievements** | Catálogo de logros | id (UUID PK), slug, name, description, xp\_reward, condition (JSONB) |
| **user\_achievements** | Logros desbloqueados por usuario | user\_id (FK), achievement\_id (FK), earned\_at — PK compuesta |

 

## **5.2 Políticas de Seguridad a Nivel de Fila (RLS)**

 

| Tabla | Operaciones | Política |
| ----- | :---: | ----- |
| **users** | SELECT / UPDATE | El usuario puede leer y actualizar únicamente su propio registro. |
| **user\_profiles** | ALL | El usuario accede solo a su propio perfil. El administrador puede leer todos. |
| **sessions** | SELECT / INSERT | El usuario solo puede insertar sesiones con su propio user\_id y leer las propias. |
| **conversation\_logs** | SELECT / INSERT | El usuario puede operar únicamente sobre logs de sus propias sesiones. |
| **feedback\_entries** | ALL | El usuario puede operar solo sobre feedback de sus propios conversation\_logs. |
| **knowledge\_nodes** | ALL | El usuario puede operar únicamente sobre sus propios nodos de conocimiento. |

 

# **6\. Arquitectura Técnica y Restricciones**

 

## **6.1 Stack Tecnológico**

 

| Capa | Tecnología | Justificación |
| ----- | ----- | ----- |
| **App Frontend** | Flutter 3.x | Multiplataforma (iOS, Android, Web, Desktop). BLoC para gestión de estado, Dio para HTTP, WebSocket nativo. |
| **API Backend** | FastAPI (Python 3.12+) | API REST \+ WebSocket. Async con SQLAlchemy 2.0. Rate limiting, autenticación JWT, streaming de tokens. |
| **Base de Datos** | PostgreSQL 16 \+ Redis 7 | PostgreSQL para persistencia principal. Redis para caché de sesiones activas y rate limiting. |
| **Cola de Tareas** | Celery \+ RabbitMQ | Procesamiento asíncrono de: actualización de nodos SM-2, cálculo de logros y envío de notificaciones push. |
| **Motor de IA** | OpenAI GPT-4o | Motor conversacional principal. Prompts dinámicos por modo (Roleplay, Susurro, Libre) y contexto profesional. |
| **Voz (STT)** | Google Cloud Speech-to-Text | Transcripción de audio en tiempo real para el Modo Susurro. Soporte multiidioma. |
| **Voz (TTS)** | ElevenLabs API | Síntesis de voz de alta calidad para reproducción de pronunciación modelo. |
| **Visión Artificial** | MediaPipe \+ TensorFlow Lite | Detección de landmarks de la mano (MediaPipe) y clasificación de caracteres escritos (CNN TFLite). |
| **Despliegue** | Docker \+ AWS ECS / Cloud Run | Contenedores Docker. CI/CD con GitHub Actions. CDN para assets estáticos. RDS para PostgreSQL gestionado. |
| **Monitoreo** | Sentry \+ Prometheus \+ Grafana | Error tracking (Sentry), métricas de rendimiento (Prometheus) y dashboards operativos (Grafana). |

 

## **6.2 Restricciones del Proyecto**

 

•  El sistema de autenticación DEBE implementarse mediante JWT propio generado por el backend FastAPI.

•  Las claves de API de servicios externos (OpenAI, ElevenLabs, Google) DEBEN residir exclusivamente en variables de entorno del servidor.

•  El audio capturado en Modo Susurro NO DEBE almacenarse persistentemente. Solo se guardará la transcripción resultante.

•  Las políticas RLS DEBEN implementarse en PostgreSQL para todas las tablas que contengan datos de usuario.

•  El sistema NO procesará datos de pago ni información de nómina en esta versión.

•  Los registros de sesiones y conversaciones solo podrán desactivarse (soft delete), no eliminarse permanentemente.

•  El acceso a la base de datos con rol de administrador está prohibido desde el cliente Flutter.

 

## **6.3 Dependencias Externas**

 

| Dependencia | Versión | Propósito | Riesgo |
| ----- | :---: | ----- | ----- |
| **OpenAI API** | GPT-4o (latest) | Motor conversacional principal | Crítico — sin alternativa directa en calidad |
| **Google Cloud Speech** | v2 (latest) | Transcripción de voz en tiempo real | Alto — puede sustituirse por Whisper API |
| **ElevenLabs API** | v1 (latest) | Síntesis de voz modelo | Medio — alternativa: Google TTS |
| **Flutter SDK** | 3.x (stable) | Framework multiplataforma del frontend | Bajo — ecosistema estable |
| **FastAPI** | 0.111+ | Framework del backend Python | Bajo — ecosistema maduro |
| **PostgreSQL** | 16+ | Base de datos relacional principal | Bajo — estándar de la industria |

 

# **7\. Interfaces del Sistema**

 

## **7.1 Interfaces de Usuario — Vistas Principales**

 

| Vista | Ruta | Descripción | Usuarios |
| ----- | ----- | ----- | :---: |
| **Pantalla de Bienvenida** | /login | Inicio de sesión, registro y onboarding para nuevos usuarios. | Público |
| **Dashboard Principal** | /dashboard | Estado de la racha, XP acumulado, acceso rápido a los 3 modos y nodos pendientes de repaso. | Estudiante |
| **Selección de Modo** | /practice | Selección del modo de práctica (Libre, Roleplay, Susurro) y del contexto profesional. | Estudiante |
| **Selección de Escenario** | /practice/scenario | Lista de escenarios disponibles para el contexto seleccionado con descripción de cada rol. | Estudiante |
| **Pantalla de Chat** | /practice/session | Interfaz de conversación con streaming de tokens, panel deslizable de correcciones y contador de XP. | Estudiante |
| **Modo Susurro** | /practice/whisper | Interfaz de grabación de voz con onda de audio animada y transcripción en tiempo real. | Estudiante |
| **Práctica de Escritura** | /practice/writing | Canvas táctil para trazos, guía animada del orden correcto y feedback visual en tiempo real. | Estudiante |
| **Constelación de Nodos** | /progress | Visualización en grafo de los nodos de conocimiento con nivel de maestría y próxima revisión. | Estudiante |
| **Historial de Sesiones** | /history | Lista de sesiones pasadas con filtros por fecha, modo y correcciones recibidas. | Estudiante |
| **Logros** | /achievements | Catálogo de logros obtenidos y disponibles, con animación de desbloqueo. | Estudiante |
| **Perfil de Usuario** | /profile | Edición de datos personales, idioma objetivo, contexto profesional y preferencias de feedback. | Todos |

 

## **7.2 Interfaces de la API Backend**

 

•  POST /auth/register — Registro de nuevo usuario con email y contraseña.

•  POST /auth/login — Autenticación y generación de tokens JWT.

•  POST /auth/refresh — Renovación de access token usando refresh token.

•  GET | PUT /users/me/profile — Lectura y actualización del perfil lingüístico.

•  GET /professional-contexts — Listado de contextos profesionales disponibles.

•  POST /api/v1/conversation — Turno de conversación vía HTTP (fallback).

•  WS /ws/conversation — Streaming de tokens de la IA vía WebSocket en tiempo real.

•  GET /api/v1/scenarios/{context} — Escenarios disponibles para un contexto.

•  GET /progress/nodes — Nodos de conocimiento del usuario con estado de maestría.

•  GET /progress/stats — XP total, racha, nivel y nodos pendientes de repaso.

•  POST /vision/analyze-stroke — Análisis de trazo (imagen base64) → validación.

•  GET /vision/stroke-guide/{char} — Secuencia animada de trazos del carácter.

•  GET /achievements — Logros desbloqueados y disponibles del usuario.

 

# **8\. Criterios de Aceptación**

 

## **8.1 Criterios Generales**

 

•  Todos los requerimientos funcionales con prioridad Alta deben estar implementados y validados antes del lanzamiento de beta cerrada.

•  Todos los requerimientos no funcionales de seguridad (RNF-06 al RNF-11) deben cumplirse sin excepción.

•  La aplicación debe funcionar correctamente en los dispositivos y navegadores objetivo definidos en la sección 6\.

•  No deben existir vulnerabilidades críticas (OWASP Top 10\) en el análisis de seguridad previo al lanzamiento.

•  La cobertura de tests del backend debe ser ≥ 70% antes de la fase de beta cerrada.

 

## **8.2 Criterios por Módulo**

 

| Módulo | Criterio de Aceptación |
| ----- | ----- |
| **Autenticación** | El usuario puede registrarse, confirmar su cuenta, iniciar sesión, recuperar contraseña y cerrar sesión sin errores en todos los dispositivos objetivo. |
| **Onboarding** | El flujo de onboarding (idioma → nivel → contexto) se completa en menos de 2 minutos y los datos se persisten correctamente en el perfil. |
| **Motor de IA — Libre** | El usuario puede mantener una conversación de 10 turnos en Modo Libre con feedback de correcciones en cada turno. |
| **Motor de IA — Roleplay** | El usuario puede completar un roleplay de 5 turnos sin que la IA abandone el personaje salvo para correcciones explícitas marcadas como \[Coach:\]. |
| **Modo Susurro** | El Modo Susurro muestra máximo 2 correcciones por turno, ningún sonido de error, y el usuario no ve puntuaciones numéricas durante la sesión. |
| **Modo Voz (STT)** | La transcripción de un mensaje de 30 segundos está disponible en menos de 1.5 segundos con una tasa de error de palabras (WER) menor al 10%. |
| **Análisis de Trazo** | El sistema valida correctamente el trazo del Kanji 日 en menos de 500ms e indica qué trazo es incorrecto si el orden no es correcto. |
| **Gamificación — XP** | El XP ganado al finalizar una sesión se refleja en el perfil en menos de 3 segundos y los nodos afectados actualizan su mastery\_score. |
| **Gamificación — Rachas** | El sistema detecta correctamente una racha rota si el usuario no practica en más de 24 horas y la reinicia a 0\. |
| **Seguridad RLS** | Un usuario autenticado no puede leer, modificar ni eliminar datos de otro usuario mediante llamadas directas a la API. |
| **Multiplataforma** | La app funciona correctamente en iOS 15, Android 8, Chrome 90 y como app de escritorio en macOS sin errores visuales ni funcionales. |
| **Responsive** | La interfaz es completamente usable en pantalla de 375px (iPhone SE) y en 1920px sin scroll horizontal en ninguna vista. |

 

## **8.3 Matriz de Trazabilidad**

 

| Objetivo | Requerimientos Relacionados | Criterio de Éxito |
| ----- | ----- | ----- |
| **OBJ-01: Reducir ansiedad** | RF-12 (Modo Susurro), RNF-14 (Seguridad Psicológica) | 80% usuarios reportan menos ansiedad a las 4 semanas |
| **OBJ-02: Fluidez verbal** | RF-10, RF-11, RF-13, RF-14, RF-15 | Sesión de roleplay de 10 min completada sin abandonar |
| **OBJ-03: Vocabulario profesional** | RF-07, RF-08, RF-18 | ≥ 20 términos incorporados en 30 días |
| **OBJ-04: Escritura no latina** | RF-24, RF-25, RF-26, RF-27 | ≥ 50 Kanji reconocidos y trazados en el primer mes |
| **OBJ-05: Retención y hábito** | RF-28, RF-29, RF-30, RF-31, RF-32, RF-33 | D7 \> 40%, D30 \> 25% en cohortes mensuales |

 

# **9\. Control de Cambios del Documento**

 

| Versión | Fecha | Autor | Descripción del Cambio |
| :---: | :---: | ----- | ----- |
| 1.0 | Marzo 2026 | Equipo de Producto | Versión inicial del documento SRS. |

 

## **Próximas versiones previstas**

 

•  v1.1 — Integración con módulo de notificaciones push personalizadas.

•  v1.2 — Panel de administración B2B para empresas con múltiples empleados.

•  v2.0 — Módulo de evaluación formal CEFR con certificado exportable.

•  v2.1 — Soporte para Árabe (escritura RTL) y Hindi (Devanagari).

 

— Fin del Documento —

