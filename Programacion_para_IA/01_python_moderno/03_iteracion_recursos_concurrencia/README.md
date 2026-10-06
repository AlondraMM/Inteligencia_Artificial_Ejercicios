# Sesión 3: Iteración, recursos y concurrencia

La [presentación de la sesión](https://drive.google.com/file/d/1gMZ1HGejLwIAsZf80W7OjOz9Ktkw5Arz/view?usp=drivesdk)
introduce los conceptos que después se prueban en la
[notebook](./u1_n4_iteracion_recursos_concurrencia.ipynb).

## Entrega de prácticas

La fecha límite para entregar las prácticas de la Unidad 1 es el **7 de octubre de 2026**.
Envía los entregables mediante el [formulario de entrega](https://docs.google.com/forms/d/e/1FAIpQLSdTJ2vU04VfIpw1Tst_T_0g0tlbE-n6ZI81nrG0RQJMReAtaQ/viewform?usp=publish-editor).

## Recorrido

1. Generadores y consumo bajo demanda.
2. Uso de `with`, una introducción breve a decoradores y `@contextmanager`.
3. Funciones síncronas y corrutinas, `to_thread`, `create_task`, `gather`,
   `TaskGroup` y tiempos límite con `asyncio`.

La notebook contiene cuatro ejercicios para el estudiante: uno sobre
generadores, uno sobre cierre de archivos y dos sobre concurrencia.
Consulta los [entregables en PRACTICA.md](./PRACTICA.md).

Los ejemplos se ejecutan con la biblioteca estándar y crean archivos solo en
directorios temporales.

## Abrir la notebook

[![Abrir en Google Colab](https://img.shields.io/badge/Abrir_en-Google_Colab-F9AB00?logo=googlecolab&logoColor=F9AB00&labelColor=333333)](https://colab.research.google.com/drive/1HKRCn91Q5ZGxFq--79Xwow3G692LyyuM)

Ejecuta las celdas en orden. Jupyter y Colab permiten usar `await` directamente
en una celda. En un archivo `.py`, el punto de entrada habitual sería
`asyncio.run(main())`.

Las [fuentes oficiales](./FUENTES.md) permiten ampliar cualquiera de los temas.
También recomendamos la [guía de concurrencia y async/await](https://fastapi.tiangolo.com/async/),
comenzando por «In a hurry?».
