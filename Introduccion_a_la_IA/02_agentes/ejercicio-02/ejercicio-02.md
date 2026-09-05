# Ejercicio 2 — Descripción PEAS de agentes inteligentes

## Contexto

En el capítulo 2 de *Artificial Intelligence: A Modern Approach* (Russell & Norvig),
un agente se entiende mejor cuando se especifica su **entorno de tarea**. Una forma
estándar de hacerlo es la descripción **PEAS**:

| Letra | Significado | Pregunta guía |
|---|---|---|
| **P** | *Performance* (medida de desempeño) | ¿Cómo se evalúa el éxito del agente? |
| **E** | *Environment* (entorno) | ¿En qué mundo opera? ¿Quién más actúa ahí? |
| **A** | *Actuators* (actuadores) | ¿Qué acciones puede ejecutar? |
| **S** | *Sensors* (sensores) | ¿Qué información puede percibir? |

Este ejercicio consiste en analizar distintos tipos de
aplicaciones reales y describir cada una con el esquema PEAS.

## Objetivo

Redactar una descripción PEAS completa y coherent, pensando como diseñador del agente: qué optimiza, dónde actúa, con qué puede mover o modificar el mundo, y qué puede observar.

## Aplicaciones analizadas

### 01. Asistente virtual de voz

- **Performance:** 
Porcentaje de solicitudes del usuario completadas correctamente, precisión del reconocimiento de voz.

- **Environment:**
Suele utilizarce en viviendas y oficinas, ante ruido ambiental. Además interactúa con usuarios, dispositivos inteligentes, aplicaciones, servicios web y conexiones de red.

  - **Propiedades del ambiente:**
    - **Parcialmente observable:** El audio puede ser ambiguo y el agente no conoce por completo la intención, el contexto ni las preferencias del usuario.
    - **Estocástico:** Asigna probabilidades a distintas transcripciones e intenciones.
    - **Secuencial:** Una respuesta o pregunta de aclaración afecta los siguientes turnos del diálogo, aunque una orden aislada podría tratarse como episódica.
    - **Dinámico:** El usuario, los dispositivos y los servicios pueden cambiar mientras procesa la petición.
    - **Mixto:** El audio y el tiempo son continuos, mientras que las intenciones y comandos disponibles son discretos.
    - **Multiagente:** El asistente interactúa con el usuario y con otros servicios para alcanzar una meta común.

- **Actuators:** 
Responder en voz alta, generar imágenes y texto; consultar aplicaciones; crear alarmas y recordatorios.

- **Sensors:** 
Micrófonos; botones o pantalla táctil; historial de conversaciones y preferencias.

### 02. Robot aspirador doméstico

- **Performance:** 
Limpiar el área límitada por fronteras (paredes, barreras) manteniendo el consumo mínimo de energía. Capacidad de regresar correctamente a la base.

- **Environment:**
Opera en pisos con habitaciones, muebles, paredes, escaleras, alfombras, cables, suciedad, personas, mascotas y una base de carga.

  - **Propiedades del ambiente:**
    - **Parcialmente observable:** El robot detecta otros objetos dentro de un radio de distancia.
    - **Estocástico:** El desplazamiento, la detección de suciedad y la eficacia de la succión pueden variar debido al deslizamiento, las superficies o el desgaste.
    - **Secuencial:** Cada movimiento modifica su posición, batería, mapa y opciones futuras.
    - **Dinámico:** Las personas, mascotas y objetos pueden moverse mientras limpia.
    - **Continuo:** En posición, orientación, velocidad y tiempo,

- **Actuators:**
Accionar las ruedas; girar y cambiar de dirección; activar o regular la succión; mover los cepillos; detenerse; rodear obstáculos; regresar a la base; acoplarse para cargar.

- **Sensors:**
sensores de proximidad; detectores de desniveles; codificadores de ruedas; sensor de suciedad; sensor de carga de la batería; detector de la base; y sensores de atasco de ruedas o cepillos.

### 03. Sistema de recomendación de streaming

- **Performance:** 
Tasa de reproducción de los contenidos recomendados; tiempo de visualización o escucha; porcentaje de finalización; reducción de abandonos y saltos; retención del usuario.

- **Environment:** 
Opera en una plataforma con usuarios, perfiles, películas, series, canciones, listas, dispositivos y un catálogo sujeto a licencias y cambios.

- **Propiedades del ambiente:**
    - **Parcialmente observable:** Los gustos, el estado de ánimo y la intención actual del usuario son variables latentes.
    - **Estocástico:** La respuesta a una recomendación se modela como una probabilidad.
    - **Secuencial:** cada contenido mostrado o consumido modifica el historial y puede influir en preferencias y recomendaciones posteriores.
    - **Dinámico:** Cambian los gustos, las tendencias, el catálogo y el contexto.
    - **Mixto:** Los contenidos, clics y posiciones del ranking son discretos, mientras que el tiempo de reproducción, los puntajes y las probabilidades son continuos.

- **Actuators:** 
Seleccionar contenidos; ordenar y mostrar recomendaciones; personalizar listas; crear playlists; decidir el siguiente contenido; ajustar la diversidad del catálogo presentado; y enviar notificaciones autorizadas.

- **Sensors:** 
Historial de reproducciones; búsquedas; abandonos; tiempo consumido; porcentaje de finalización; valoraciones; contenidos guardados u ocultados; metadatos del catálogo; y comportamiento agregado de usuarios similares.

### 04. Vehículo autónomo en ciudad

- **Performance:**
Número de situaciones de riesgo; cumplimiento de las normas de tránsito; llegada al destino correcto; tiempo de viaje; comodidad de los pasajeros; consumo de energía; desgaste del vehículo.

- **Environment:**
Opera en calles, avenidas e intersecciones con automóviles, motocicletas, bicicletas, peatones, animales, semáforos, señales, obras, obstáculos, clima.

- **Propiedades del ambiente:**
    - **Parcialmente observable:** Alcance limitado de sensores y porque no se conoce las intenciones de otros conductores o peatones.
    - **Estocástico:** El comportamiento del tráfico, las condiciones de adherencia y las fallas se modelan probabilísticamente.
    - **Secuencial:** Una maniobra modifica la trayectoria y las posibilidades futuras.
    - **Dinámico:** El tráfico continúa moviéndose mientras el agente decide.
    - **Continuo:** En tiempo, posición, velocidad, aceleración y dirección.
    - **Multiagente:** Parcialmente cooperativo al evitar accidentes y parcialmente competitivo al disputar carriles, cruces o espacios de estacionamiento.

- **Actuators:**
Controlar acelerador, frenos y dirección; cambiar de marcha; activar luces, direccionales, limpiaparabrisas y claxon; abrir o cerrar puertas cuando corresponda.

- **Sensors:**
Cámaras; radar; GPS; mapas digitales; velocímetro; codificadores de ruedas; sensores del motor, batería y frenos.

### 05. Agente de trading algorítmico en bolsa

- **Performance:** Rendimiento neto después de comisiones e impuestos; rentabilidad ajustada por riesgo.

- **Environment:**
Opera en bolsas, plataformas y mercados donde participan inversionistas, instituciones, corredores y reguladores.

- **Propiedades del ambiente:**
    - **Parcialmente observable:** No se conocen todas las estrategias.
    - **Estocástico:** Los movimientos de precios, la ejecución de órdenes y los eventos futuros se representan mediante probabilidades.
    - **Secuencial:** Cada operación cambia el portafolio, el efectivo, el riesgo y las decisiones posteriores.
    - **Dinámico:** Precios y órdenes pueden variar mientras el agente analiza.
    - **Mixto:** los eventos son discretos, mientras que tiempo, precios, indicadores y niveles de riesgo suelen tratarse como continuos.
    - **Multiagente:** Competitivo, ya que las decisiones de otros participantes afectan sus oportunidades y resultados.

- **Actuators:** 
Enviar órdenes de compra o venta; elegir órdenes de mercado; definir precio y volumen; cancelar o modificar órdenes; cerrar posiciones; rebalancear el portafolio.

- **Sensors:** 
Cotizaciones; precios de compra y venta; indicadores técnicos y macroeconómicos; calendario financiero; límites regulatorios o internos.

### 06. Sistema de diagnóstico médico asistido por IA

- **Performance:** 
Precisión diagnóstica; tasas de falsos negativos y falsos positivos; detección temprana de condiciones graves; concordancia con especialistas.

- **Environment:** 
Opera en hospitales o clínicas con pacientes, médicos, expedientes, equipos de laboratorios y protocolos clínicos.

- **Propiedades del ambiente:**
    - **Parcialmente observable:** Los síntomas, imágenes y pruebas ofrecen evidencia incompleta o ruidosa.
    - **Estocástico:** Enfermedades similares pueden producir manifestaciones distintas y las pruebas tienen sensibilidad y especificidad probabilísticas.
    - **Secuencial:** Puede sugerir estudios y actualizar el diagnóstico con nuevos resultados.
    - **Dinámico:** La condición del paciente puede evolucionar durante el proceso.
    - **Mixto:** Diagnósticos y decisiones son discretos, mientras que signos vitales, mediciones e imágenes contienen valores continuos.
    - **Multiagente:** Se coopera con el médico.

- **Actuators:** 
Presentar diagnósticos; resaltar regiones sospechosas en imágenes; emitir alertas clínicas; recomendar pruebas adicionales.

- **Sensors:**
Síntomas reportados; antecedentes médicos y familiares; resultados de laboratorio; notas clínicas.

### 07. Dron de inspección de infraestructura

- **Performance:** Precisión y sensibilidad en la detección de grietas, corrosión o fugas; tasa de falsas alarmas; calidad de imágenes; duración de la misión; consumo de batería; estabilidad de vuelo; cumplimiento de la ruta; y ausencia de colisiones, daños o violaciones de seguridad.

- **Environment:** 
Opera alrededor de puentes, tuberías, torres o líneas eléctricas, con estructuras, cables, vegetación, trabajadores, vehículos, aves, viento, lluvia, cambios de iluminación y posibles interferencias de comunicación.

- **Propiedades del ambiente:**
    - **Parcialmente observable:** Porque existen zonas inaccesibles, defectos internos y limitaciones de resolución.
    - **Estocástico:** El viento, las turbulencias, la señal GPS y el comportamiento de obstáculos móviles son inciertos.
    - **Secuencial:** Cada movimiento afecta la posición, la batería, la cobertura lograda y la ruta restante.
    - **Dinámico:** Por los cambios meteorológicos y la presencia de personas, vehículos o maquinaria.
    - **Continuo:** En posición, orientación, velocidad, tiempo y control de vuelo, aunque los puntos de inspección puedan definirse de forma discreta.

- **Actuators:** 
Variar la velocidad, ascender, descender, avanzar, retroceder y girar; controlar el estabilizador de la cámara; ajustar enfoque y zoom; tomar fotografías o video; encender iluminación; marcar coordenadas.

- **Sensors:**
Cámaras térmicas, magnetómetro; barómetro; sensores de batería y motores; medidores de distancia; sensores de gases o acústicos cuando se buscan fugas.

### 08. Agente jugador de ajedrez

- **Performance:**
Ganar la partida con el menor número de movimientos en el menor tiempo posible.

- **Environment:**
Opera sobre un tablero con piezas, reglas, reloj, historial de movimientos y un oponente.

- **Propiedades del ambiente:**
    - **Totalmente observable:** El estado relevante de la partida (posición, turno, relojes) está disponible.
    - **Determinista:** Cada movimiento legal produce un estado definido y no existen eventos aleatorios.
    - **Secuencial:** Cada movimiento condiciona todas las posiciones futuras.
    - **Semidinámico:** El tablero permanece igual, pero el tiempo disponible y la medida de desempeño sí cambian.
    - **Discreto:** Posee estados, turnos y movimientos diferenciados.
    - **Multiagente:** Competitivo, cada jugador intenta obtener un resultado contrario al del adversario.
- **Actuators:**
Ejecutar un movimiento legal; ofrecer, aceptar o rechazar tablas; abandonar la partida; y accionar el reloj.

- **Sensors:**
Posición completa de las piezas; color asignado; jugador en turno; movimiento del adversario; historial de movimientos; posibilidad de captura al paso; estado de jaque; tiempo restante de ambos jugadores; y ofertas de tablas.
