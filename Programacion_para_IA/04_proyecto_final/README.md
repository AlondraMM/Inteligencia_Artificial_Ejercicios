# Búsqueda y análisis de productos Amazon con MCP

Aplicación local para buscar productos de Electronics por similitud semántica y
analizar las valoraciones de la selección proporcionada: **600 productos y
6 992 reseñas**. El servidor utiliza el SDK oficial de MCP v2 mediante Streamable
HTTP en `http://127.0.0.1:8000/mcp`.

## Preparación y ejecución

Se necesitan Python 3.12 y `uv`. Desde esta carpeta, se instalan las versiones fijadas:

```bash
uv sync --locked
```

En una primera terminal, iniciar el servidor y esperar a que termine de preparar los
embeddings:

```bash
uv run --locked python server.py
```

La primera carga de `sentence-transformers/all-MiniLM-L6-v2` necesita conexión a Internet para descargar el modelo; las siguientes aprovechan su caché local.
`config.json` permite configurar `model_name`, `batch_size` y `device` (`cpu` por
defecto).

En una segunda terminal, ejecutar el cliente:

```bash
uv run --locked python main.py
```

El cliente utiliza las tres herramientas, muestra sus respuestas JSON y verifica
análisis, comparaciones, productos desconocidos y entradas inválidas. La última
búsqueda válida comprueba que la misma sesión se recupera de los errores. Si no
conecta, confirma que el servidor está listo y que la URL termina en `/mcp`.
Una demostración con respuestas inesperadas termina con un código distinto de cero.

Para comprobar los tipos de todos los módulos de la aplicación:

```bash
uv run --locked mypy --strict server.py client.py main.py support tests
```

Para ejecutar las pruebas automatizadas:

```bash
uv run --locked python -m unittest discover -s tests -v
```

Verificación realizada: instalación con `uv sync --locked` desde una copia sin
`.venv`, 12 pruebas aprobadas y `mypy --strict` sin errores en los 10 archivos
Python. El arranque con los datos completos construyó una matriz `(600, 384)`.
La demostración HTTP descubrió las tres herramientas y completó sus 10 llamadas,
incluida una búsqueda válida después de cuatro errores de entrada en la misma sesión.

## Herramientas y cálculo

- `search_products(query, top_k=5)`: devuelve ID, título, similitud y cantidad de
  reseñas seleccionadas, en orden descendente. `top_k` debe ser un entero entre 1 y 20.
- `analyze_product(product_id)`: devuelve cantidad, conteos y proporciones de 1 a 5
  estrellas, media y mediana.
- `compare_products(product_ids)`: compara al menos dos IDs distintos e informa
  las diferencias de media respecto al primero.

Las consultas y los IDs vacíos producen un error claro. Un producto desconocido
tiene conteo, conteos y proporciones en cero, media y mediana `null`; una diferencia
sin ambas medias también es `null`.

El catálogo se representa con título, características y descripción disponible.
Cada reseña con texto se codifica por separado y se conserva su ID estable
`Electronics:<source_line>`. Para cada producto se normaliza el promedio de sus
embeddings de reseñas, se combina con el vector normalizado del catálogo con
**50 % de cada fuente** y se normaliza el resultado. El mismo modelo codifica las
consultas; un producto matricial calcula las similitudes coseno.

Los vectores y el modelo se preparan una vez al iniciar el servidor y se mantienen
en memoria. No se guardan vectores en disco: reiniciar el servidor los regenera a
partir de `datasets/` y `config.json`.

## Ejemplos de consultas e interpretación

Resultados obtenidos con la selección completa, `config.json` y el modelo en CPU.
Las similitudes están redondeadas a cuatro decimales.

| Consulta | Producto recuperado | ID | Similitud | Reseñas seleccionadas |
|---|---|---|---:|---:|
| `A portable waterproof Bluetooth speaker` | Altec Lansing Mini H2O | `B0B786PFYJ` | 0.7942 | 11 |
| Misma consulta | EDUPLINK Waterproof Portable Bluetooth Speaker | `B0BNY1L4JP` | 0.7896 | 13 |
| Misma consulta | Bose SoundLink Micro | `B09WWG19YS` | 0.7580 | 27 |
| `Comfortable headphones with good sound` | Sony MDR7506 | `B07CQMZVZ6` | 0.7294 | 30 |
| Misma consulta | OneOdio Over Ear Headphone | `B091K4WYD1` | 0.7166 | 30 |

La primera consulta recupera bocinas cuyos títulos coinciden con portabilidad,
Bluetooth y resistencia al agua. El orden expresa cercanía semántica del catálogo
y sus reseñas; no certifica esas prestaciones ni indica cuál suena mejor.

La segunda recupera audífonos ante una consulta sobre comodidad y sonido. Sus
puntajes permiten ordenar coincidencias, pero no demostrar comodidad para una
persona ni comparar calidad de audio. Solo se usaron hasta 30 reseñas por producto
y los textos largos pueden perder información por el límite de 256 tokens.

Como ejemplo de análisis, `B0BCTJMN63` tiene 7 reseñas seleccionadas: tres de
4 estrellas y cuatro de 5, media 4.5714 y mediana 5. Al compararlo con
`B09MMWM2Y8` (20 reseñas, media 4.35), la diferencia del segundo respecto al
primero es -0.2214 estrellas. Estos tamaños de muestra no permiten generalizar
la diferencia a todas las valoraciones de Amazon.

## Alcance y limitaciones

Las estadísticas describen únicamente las reseñas seleccionadas, entre 5 y 30 por
producto. La selección es por conveniencia, no aleatoria ni representativa de
Amazon. Su conteo no mide popularidad y una media con pocas reseñas requiere cautela.

El modelo está orientado a inglés y trunca los textos que superan 256 tokens de su
tokenizador. Conviene consultar en inglés; información al final de textos largos
puede quedar fuera. La búsqueda siempre devuelve los productos más cercanos,
incluso ante consultas poco relevantes: la similitud no es una probabilidad ni una
medida de calidad del producto.

