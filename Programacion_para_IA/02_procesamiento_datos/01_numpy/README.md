# Sesión 1: NumPy y vectorización

[Presentación de la sesión (PDF)](https://drive.google.com/file/d/1nd5-nHeYSDUZgLEwXG9WLvCaIF-c_oPl/view?usp=drivesdk).

Una lista puede guardar mediciones; un arreglo permite expresar su organización
y operar sobre grupos de valores. Trabajaremos con temperaturas de tres salas
para construir selecciones correctas y llevar el análisis a una aplicación.

## Entrega de prácticas

La fecha límite para entregar las prácticas de la Unidad 2 es el **19 de octubre de 2026**.
Envía los entregables mediante el [formulario de entrega](https://docs.google.com/forms/d/e/1FAIpQLScOPQOB1sgjXsZbrealNcJ_U8Aa-bqtds5SozcSsRNSek7FxA/viewform?usp=publish-editor).

## Objetivos

- Interpretar `ndim`, `shape`, `size` y `dtype` a partir del significado de los datos.
- Seleccionar mediciones por posición y por condiciones, conservando las dimensiones necesarias.
- Distinguir una vista de una copia y evitar modificaciones accidentales.
- Aplicar una operación a todo el arreglo y combinar formas compatibles mediante broadcasting.
- Reutilizar operaciones de NumPy en una notebook y en una aplicación ejecutada con `uv`.

Se retoman listas, slicing, funciones, módulos, archivos y los comandos de `uv`
de la unidad anterior.

## Contenido

| Orden | Material | Trabajo |
|---|---|---|
| 1 | [Guía de trabajo](./GUIA.md) | Preparar los proyectos y alternar terminal, notebook y editor |
| 2 | [Proyecto de exploración](./01-exploracion/README.md) | Arreglos, selección, máscaras, vectorización y broadcasting |
| 3 | [Proyecto de reporte](./02-reporte-mediciones/README.md) | Leer datos, seleccionar filas completas y resumir por sala |
| 4 | [Práctica](./PRACTICA.md) | Selección independiente y comprobación de resultados |
| 5 | [Ficha de datos](./datos/README.md) | Columnas, unidades, procedencia y valores no finitos |
| 6 | [Fuentes](./FUENTES.md) | Documentación oficial para consultar cada concepto |

## Estructura

```text
sesion-01-numpy/
├── datos/
│   ├── readings.csv
│   └── readings_quality.csv
├── 01-exploracion/
│   ├── main.py
│   ├── u2_n1_arreglos_numpy.ipynb
│   ├── pyproject.toml
│   └── uv.lock
└── 02-reporte-mediciones/
    ├── main.py
    ├── measurements/processing.py
    ├── tests/
    ├── u2_n2_reporte_mediciones.ipynb
    ├── pyproject.toml
    └── uv.lock
```

Los dos proyectos se ejecutan completos como referencia. La sesión reúne 11 ejercicios: 1–8 en la notebook de exploración,
9 en `PRACTICA.md` y 10–11 en la notebook de reporte. La práctica desarrolla
el mismo ejercicio 11 del proyecto. Los ejercicios se
resuelven en las celdas reservadas o en un módulo nuevo, sin sustituir el código
necesario para continuar la sesión.

Consulta los [entregables en PRACTICA.md](./PRACTICA.md).

La primera notebook introduce y combina los conceptos; la segunda muestra cómo
reutilizar la selección y los resúmenes en una aplicación. Esta sesión se centra
en operaciones por elemento y por eje; los productos matriciales no son necesarios
para el problema de mediciones.
