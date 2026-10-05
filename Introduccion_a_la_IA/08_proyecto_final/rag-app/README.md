# AstroBot: RAG sobre astronomía y cosmología

Proyecto final de un sistema RAG. Streamlit es un cliente HTTP de FastAPI; la API extrae y parte los documentos, obtiene embeddings de Google AI, los persiste en ChromaDB y recupera evidencia antes de pedir la respuesta a Gemini.

## Instalación y configuración

Ejecuta los comandos desde esta carpeta `rag-app/`, con Python 3.12. En una instalación nueva, crea un entorno propio; si ya tienes un `.venv` funcional, actívalo e instala las dependencias sin recrearlo:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

No se necesita descargar un modelo de embeddings local.

Obtén una clave propia en [Google AI Studio](https://aistudio.google.com/apikey). Si todavía no tienes `.env`, crea uno:

```bash
cp .env.example .env
```

Edita `.env` y completa `GOOGLE_API_KEY=tu_clave`. Conserva tu `.env` existente si ya estaba configurado. La API carga ese archivo desde la raíz del proyecto, independientemente del directorio de persistencia. También puedes proporcionar la clave mediante el entorno; las variables ya exportadas tienen prioridad:

```bash
export GOOGLE_API_KEY='tu_clave'
```

No publiques la clave. `.gitignore` excluye `.env`, `.venv/` y `chroma/` de nuevas incorporaciones.

## Iniciar API y UI

Después de instalar las dependencias y configurar `.env`, abre dos terminales en la carpeta `rag-app/`.

En la primera terminal, activa el entorno virtual e inicia FastAPI:

```bash
source .venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

En la segunda terminal, activa el mismo entorno e inicia Streamlit:

```bash
source .venv/bin/activate
streamlit run ui/streamlit_app.py
```

Mantén ambas terminales abiertas mientras usas la aplicación. Para detener cada servidor, pulsa `Ctrl+C` en su terminal.

Abre [Streamlit](http://localhost:8501) y la [documentación interactiva de FastAPI](http://localhost:8000/docs). Las solicitudes de Streamlit salen de su proceso de servidor mediante `httpx`, por lo que la comunicación local entre los puertos 8501 y 8000 no depende de CORS del navegador. Streamlit no importa Chroma ni el SDK de Google.

La UI utiliza `http://localhost:8000` como dirección predeterminada de la API. Si cambias `RAG_API_URL`, expórtala antes de iniciar Streamlit: la UI lee el entorno de su proceso. Reinicia la API después de cambiar su configuración.

## Corpus e indexación

`data/` contiene seis documentos distintos sobre astronomía, cosmología, agujeros negros y origen del universo.

**Documentos utilizados:**

* `Agujeros_negros.md`
* `Origen_del_universo_y_la_vida.md`
* `Hawkin_historia_del_tiempo.md`
* `Misterios_del_universo.md`
* `Panorama_del_universo.md`
* `Galaxias_Haro_pdf`

En la barra lateral de Streamlit, selecciona los archivos y pulsa **Indexar**. La UI envía un multipart HTTP a `/ingest` y muestra el número de documentos y chunks. Se admiten `.md`, `.txt` UTF-8 y PDF con texto extraíble, hasta 10 MB por archivo. Los PDF escaneados sin texto se rechazan; no se cuentan como documentos ingeridos.

Para hacer la misma ingestión desde una terminal:

```bash
curl --fail-with-body -X POST http://localhost:8000/ingest \
  -F 'files=@data/Agujeros_negros.md' \
  -F 'files=@data/Origen_del_universo_y_la_vida.md' \
  -F 'files=@data/Hawkin_historia_del_tiempo.md' \
  -F 'files=@data/Misterios_del_universo.md' \
  -F 'files=@data/Panorama_del_universo.md' \
  -F 'files=@data/Big_bang_fisica_y_cosmos.md'
```

Volver a cargar un archivo con el mismo nombre reemplaza sus chunks en la colección; los otros documentos se conservan. La API calcula los embeddings antes de escribir. Chroma incorpora los nuevos chunks antes de eliminar los que hayan quedado obsoletos, para conservar la versión previa si rechaza los nuevos vectores. El nombre del archivo identifica el origen, por lo que los archivos de una misma carga deben tener nombres distintos.

## Inventario y gestión de documentos

La barra lateral muestra los documentos indexados y la cantidad de chunks de cada uno. **Consultar en** permite elegir todos los documentos o limitar las siguientes preguntas a un archivo. En la sección de gestión, selecciona un documento y usa el botón de borrado para eliminar sus chunks del índice; los demás documentos y los archivos locales se conservan.

Para listar el inventario por HTTP:

```bash
curl --fail-with-body http://localhost:8000/documents
```

`GET /documents` devuelve `documents` (lista de objetos con `source` y `chunks`), `documents_count` e `index_chunks`. Usa el valor exacto de `source` devuelto por ese inventario para filtrar o borrar. Renombrar un archivo en `data/` no cambia el nombre que ya tienen sus chunks en Chroma.

Para borrar únicamente un documento con `DELETE /documents/{source}`, codifica su nombre como un segmento de URL; así también se admiten espacios y caracteres acentuados:

```bash
documento='Agujeros_negros.md'
documento_url=$(python -c 'import sys; from urllib.parse import quote; print(quote(sys.argv[1], safe=""))' "$documento")
curl --fail-with-body -X DELETE "http://localhost:8000/documents/${documento_url}"
```

La respuesta indica `source`, `chunks_deleted` e `index_chunks`. Si el nombre no está indexado, la API devuelve 404. Listar y borrar no requieren `GOOGLE_API_KEY` ni consumen cuota de Google: actúan sobre el índice local.

Para reindexar desde Streamlit, en **Gestionar documentos** elige la fuente, carga la versión actualizada **con el mismo nombre** y pulsa **Reindexar documento**. También puedes enviar ese único archivo a `/ingest`:

```bash
curl --fail-with-body -X POST http://localhost:8000/ingest \
  -F 'files=@data/Agujeros_negros.md'
```

Esta operación genera nuevos embeddings y requiere clave y cuota de Google AI. Reemplaza ese documento sin reconstruir la colección ni alterar las otras fuentes. Subirlo con un nombre distinto crea otra fuente en el índice.

## Consultas y abstención

Prueba en Streamlit estas tres preguntas del dominio y revisa que cada respuesta factual cite fuentes visibles:

1. ¿Qué es un agujero negro y qué es su horizonte de sucesos?
2. ¿Cómo está compuesto el sol?
3. ¿Cómo está compuesto el universo?

En cada respuesta se deben poder abrir los fragmentos recuperados y ver su texto, origen, número `[n]` y score. El historial conserva preguntas, respuestas, citas y el filtro utilizado originalmente en `session_state` durante la sesión de Streamlit. Cambiar **Consultar en** afecta las nuevas preguntas; las anteriores mantienen su filtro y evidencia. **Limpiar historial** borra el chat de la sesión y no altera el índice. El historial no se guarda en disco y una nueva sesión comienza con un chat nuevo.

Para reproducir la primera pregunta contra FastAPI:

```bash
curl --fail-with-body http://localhost:8000/query \
  -H 'Content-Type: application/json' \
  -d '{"question":"¿Qué es un agujero negro y qué es su horizonte de sucesos?","top_k":4}'
```

En `/docs`, expande `POST /query`, pulsa **Try it out**, pega el mismo JSON y ejecuta la solicitud. La respuesta contiene `answer`, `citations` y `abstained`. Cada cita incluye `id`, `number`, `source`, `text`, `score`, `chunk_index` y, para PDF, `page`.

`POST /query` también admite `source` opcional para recuperar evidencia únicamente de ese archivo. Si omites `source` o envías `null`, se consulta todo el índice. Un nombre que no está indexado devuelve 404; consulta primero `/documents`. En el JSON, el nombre se envía como texto normal, sin codificación de URL:

```bash
curl --fail-with-body http://localhost:8000/query \
  -H 'Content-Type: application/json' \
  -d '{"question":"¿Qué es un agujero negro y qué es su horizonte de sucesos?","top_k":4,"source":"Agujeros_negros.md"}'
```

Pregunta imposible incluida para comprobar la abstención:

```bash
curl --fail-with-body http://localhost:8000/query \
  -H 'Content-Type: application/json' \
  -d '{"question":"¿Quién es Taylor Swift?","top_k":4}'
```

Esa contraseña y esa biblioteca no aparecen en el corpus. El resultado esperado es `abstained: true` con un mensaje explícito de falta de evidencia, sin inventar una contraseña. Ejecuta también esta pregunta en Streamlit.

La API aplica dos criterios: se abstiene si el índice está vacío o el mejor score es menor que `MIN_SCORE` (0.55); si hay evidencia candidata, Gemini debe devolver `NO_EVIDENCIA` cuando los fragmentos no cubran la pregunta. Las citas agrupadas, como `[1, 3]`, se normalizan a `[1][3]` y todos sus números se validan. Se descartan respuestas vacías, sin citas numéricas o con números que no corresponden a los chunks recuperados. El mensaje de abstención es «No tengo evidencia suficiente en el corpus para responder esa pregunta». Este control comprueba la existencia de las citas, no demuestra automáticamente que cada afirmación esté sustentada; hay que revisar los fragmentos en las pruebas de aceptación.

## Componentes y parámetros

| Archivo | Responsabilidad |
|---|---|
| `app/main.py` | API `/health`, `/ingest`, `/query`, `/documents` y borrado por fuente; configuración y coordinación del RAG |
| `app/chunk.py` | Extraer texto y dividirlo en ventanas por palabras; conservar página de PDF |
| `app/embed.py` | Google AI, lotes de 16, tareas `RETRIEVAL_DOCUMENT` y `RETRIEVAL_QUERY` |
| `app/store.py` | Chroma persistente, inventario, borrado y reindexación por fuente, recuperación por vector con filtro opcional |
| `app/generate.py` | Prompt con evidencia numerada, español, citas y abstención |
| `ui/streamlit_app.py` | Carga, inventario, filtro, gestión de documentos, historial y fragmentos visibles mediante HTTP |

El mismo `EMBEDDING_MODEL=gemini-embedding-001` vectoriza documentos y preguntas. Gemini `GENERATION_MODEL=gemini-3.6-flash` genera el texto final después de recuperar los chunks. Chroma recibe los vectores calculados por Google y usa distancia coseno; no se utiliza FastText, BERT ni bolsa de palabras. El score mostrado es `1 - distancia`, limitado al intervalo `[0,1]`, y no es una probabilidad.

`CHUNK_WORDS=250` y `CHUNK_OVERLAP=50` producen ventanas de 250 palabras con avance de 200. El solape conserva contexto entre ventanas; los PDF se parten por página. `top_k` tiene valor predeterminado 4 y acepta de 1 a 10 mediante el JSON de consulta o el selector de Streamlit. `CHROMA_PATH=chroma` es relativo a la raíz del proyecto y se puede configurar también con una ruta absoluta. Cada chunk conserva `source`, `chunk_index` y página cuando corresponde.
