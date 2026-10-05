"""Cliente HTTP de AstroBot: carga, consulta y evidencias del RAG."""

import base64
import json
import os
from pathlib import Path
from urllib.parse import quote

import httpx
import streamlit as st

API_URL = os.getenv("RAG_API_URL", "http://localhost:8000").rstrip("/")
TIMEOUT = 180.0
INGEST_TIMEOUT = 1800.0

@st.cache_data(show_spinner=False)
def background_image(filename: str) -> str:
    """Cargar los fondos locales desde la carpeta de esta interfaz."""
    image_path = Path(__file__).resolve().with_name(filename)
    return base64.b64encode(image_path.read_bytes()).decode("ascii")


def api_error(response: httpx.Response) -> str:
    """Mostrar el detalle de FastAPI, incluso en errores de validación."""
    try:
        body = response.json()
        detail = body.get("detail", body) if isinstance(body, dict) else body
    except ValueError:
        detail = response.text.strip()
    if isinstance(detail, list):
        messages = []
        for item in detail:
            if isinstance(item, dict) and "msg" in item:
                location = ".".join(str(part) for part in item.get("loc", []))
                messages.append(f"{location}: {item['msg']}" if location else str(item["msg"]))
            else:
                messages.append(json.dumps(item, ensure_ascii=False))
        detail = "; ".join(messages)
    elif isinstance(detail, dict):
        detail = json.dumps(detail, ensure_ascii=False)
    return f"Error de la API ({response.status_code}): {detail or response.reason_phrase}"


def index_files(files: list, *, reindex_source: str | None = None) -> None:
    """La carga y la reindexación utilizan el mismo endpoint de ingestión."""
    if reindex_source is not None and (len(files) != 1 or files[0].name != reindex_source):
        st.error("El archivo debe tener exactamente el mismo nombre que el documento seleccionado.")
        return
    payload = [("files", (file.name, file.getvalue())) for file in files]
    with st.spinner("Partiendo, incrustando e indexando..."):
        try:
            with httpx.Client(timeout=INGEST_TIMEOUT) as client:
                response = client.post(f"{API_URL}/ingest", files=payload)
                response.raise_for_status()
            result = response.json()
            if reindex_source is None:
                confirmation = (
                    f"{result['documents_indexed']} documentos y "
                    f"{result['chunks_indexed']} chunks indexados."
                )
            else:
                confirmation = f"{reindex_source} reindexado: {result['chunks_indexed']} chunks."
            st.session_state.ingest_success = confirmation
            st.rerun()
        except httpx.HTTPStatusError as exc:
            st.error(api_error(exc.response))
        except httpx.HTTPError:
            st.error("No se pudo conectar con la API durante la indexación.")
        except (ValueError, KeyError, TypeError):
            st.error("La API devolvió una respuesta de indexación inválida.")


def show_message(message: dict) -> None:
    """Renderizar también las evidencias al recuperar el historial."""
    with st.chat_message(message["role"]):
        if message.get("error"):
            st.error(message["content"])
            return
        st.write(message["content"])
        if message["role"] == "user" and "source" in message:
            st.caption(f"Consultar en: {message['source'] or 'Todos los documentos'}")
        if message.get("abstained"):
            st.info("El sistema se abstuvo por falta de evidencia suficiente.")
        for position, citation in enumerate(message.get("citations", []), 1):
            number = citation.get("number", position)
            label = f"[{number}] {citation['source']} · score: {citation['score']:.4f}"
            with st.expander(label):
                if citation.get("page") is not None:
                    st.caption(f"Página: {citation['page']}")
                if citation.get("chunk_index") is not None:
                    st.caption(f"Índice del chunk: {citation['chunk_index']}")
                st.text(citation["text"])


st.set_page_config(page_title="AstroBot", page_icon="☄️", initial_sidebar_state="expanded")
st.markdown(
    f"""
    <style>
    [data-testid="stAppViewContainer"] {{
        --main-overlay: light-dark(rgba(255, 255, 255, 0.86), rgba(14, 17, 23, 0.86));
        background-image:
            linear-gradient(var(--main-overlay), var(--main-overlay)),
            url("data:image/jpeg;base64,{background_image('universo.jpg')}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}
    [data-testid="stSidebar"] {{
        --sidebar-overlay: light-dark(rgba(255, 255, 255, 0.72), rgba(14, 17, 23, 0.58));
        background-image:
            linear-gradient(var(--sidebar-overlay), var(--sidebar-overlay)),
            url("data:image/jpeg;base64,{background_image('luna.jpg')}");
        background-size: cover;
        background-position: center top;
        background-repeat: no-repeat;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)
st.title(" ☄️ AstroBot")
st.subheader("🧑🏻‍🚀 Tu guía del cosmos de confianza 🪐")

st.write(
    "🌌 El universo es enorme y está lleno de preguntas. "
    "Por suerte, AstroBot tiene algunas respuestas."
)

health = None
health_error = None
try:
    with httpx.Client(timeout=10) as client:
        health_response = client.get(f"{API_URL}/health")
        health_response.raise_for_status()
        health = health_response.json()
except httpx.HTTPStatusError as exc:
    health_error = api_error(exc.response)
except httpx.HTTPError:
    health_error = f"La API no responde en {API_URL}. Iníciala con Uvicorn."
except ValueError:
    health_error = "La API devolvió un estado que no es JSON válido."

api_available = health is not None
key_configured = api_available and health["key_configured"]

# Un único historial se conserva incluso cuando la API deja de responder.
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "¿Qué quieres descubrir sobre el universo?"}
    ]

inventory = None
inventory_error = None
if api_available:
    try:
        with httpx.Client(timeout=10) as client:
            response = client.get(f"{API_URL}/documents")
            response.raise_for_status()
        inventory = response.json()
        documents = inventory["documents"]
        if not isinstance(documents, list) or any(
            not isinstance(item, dict) or not isinstance(item.get("source"), str)
            or not isinstance(item.get("chunks"), int) for item in documents
        ):
            raise ValueError("Inventario inválido")
        document_names = [item["source"] for item in documents]
        documents_count = int(inventory["documents_count"])
    except httpx.HTTPStatusError as exc:
        inventory_error = api_error(exc.response)
        inventory = None
    except httpx.HTTPError:
        inventory_error = "No se pudo consultar la lista de documentos de la API."
        inventory = None
    except (ValueError, KeyError, TypeError):
        inventory_error = "La API devolvió una lista de documentos inválida."
        inventory = None
if inventory is None:
    documents = []
    document_names = []
documents_available = inventory is not None

with st.sidebar:
    st.subheader("🛸 Estado")
    if api_available:
        st.write(f"Chunks en el índice: **{health['index_chunks']}**")
        st.caption(f"Embeddings: {health['embedding_model']}")
    else:
        st.warning("API no disponible")
    st.caption(f"API: {API_URL}")
    if st.button("Reintentar conexión"):
        st.rerun()
    top_k = st.number_input(
        "Chunks a recuperar (top_k)", min_value=1, max_value=10, value=4,
        step=1, disabled=not api_available,
    )
    if api_available and not key_configured:
        st.error("Falta GOOGLE_API_KEY en el .env de la API.")
    st.divider()
    st.subheader("Documentos indexados 📡")
    if inventory_error:
        st.error(inventory_error)
    elif documents_available:
        st.caption(f"Documentos: {documents_count}")
        for document in documents:
            st.write(f"{document['source']} — {document['chunks']} chunks")
        if not documents:
            st.info("Todavía no hay documentos indexados.")
    else:
        st.caption("La lista estará disponible al conectar con la API.")
    if documents_available and st.session_state.get("query_source") not in document_names:
        st.session_state.query_source = None
    query_options = document_names if documents_available else [
        source for source in [st.session_state.get("query_source")] if source is not None
    ]
    query_options = [None, *query_options]
    query_source = st.selectbox(
        "Consultar en", query_options, key="query_source",
        index=query_options.index(st.session_state.get("query_source")),
        format_func=lambda source: source or "Todos los documentos",
        disabled=not documents_available,
    )
    st.divider()
    st.subheader("Cargar documentos  🚀")
    files = st.file_uploader(
        "Archivos .txt, .md o .pdf", type=["txt", "md", "pdf"], accept_multiple_files=True
    )
    if "ingest_success" in st.session_state:
        st.success(st.session_state.pop("ingest_success"))
    if st.button("Indexar", disabled=not files or not key_configured):
        index_files(files)
    st.divider()
    st.subheader("Gestionar documentos 🛰️")
    if documents_available and st.session_state.get("managed_source") not in document_names:
        st.session_state.managed_source = None
    management_options = document_names if documents_available else [
        source for source in [st.session_state.get("managed_source")] if source is not None
    ]
    management_options = [None, *management_options]
    managed_source = st.selectbox(
        "Documento a gestionar", management_options, key="managed_source",
        index=management_options.index(st.session_state.get("managed_source")),
        format_func=lambda source: source or "Selecciona un documento",
        disabled=not documents_available or not document_names,
    )
    if "document_success" in st.session_state:
        st.success(st.session_state.pop("document_success"))
    can_delete = bool(managed_source) and documents_available
    if st.button("Borrar documento", disabled=not can_delete) and can_delete:
        try:
            with httpx.Client(timeout=10) as client:
                response = client.delete(f"{API_URL}/documents/{quote(managed_source, safe='')}")
                response.raise_for_status()
            result = response.json()
            st.session_state.document_success = (
                f"{result['source']} borrado: {result['chunks_deleted']} chunks eliminados."
            )
            st.rerun()
        except httpx.HTTPStatusError as exc:
            st.error(api_error(exc.response))
        except httpx.HTTPError:
            st.error("No se pudo conectar con la API durante el borrado.")
        except (ValueError, KeyError, TypeError):
            st.error("La API devolvió una respuesta de borrado inválida.")
    if managed_source:
        st.caption(f"Para reindexar, carga un archivo con el mismo nombre: {managed_source}")
    replacement = st.file_uploader(
        "Archivo para reindexar", type=["txt", "md", "pdf"], key="reindex_file",
        disabled=not documents_available or not managed_source or not key_configured,
    )
    replacement_matches = replacement is not None and replacement.name == managed_source
    if replacement is not None and not replacement_matches:
        st.warning("El archivo debe tener exactamente el mismo nombre que el documento seleccionado.")
    can_reindex = documents_available and replacement_matches and key_configured
    if st.button("Reindexar documento", disabled=not can_reindex) and can_reindex:
        index_files([replacement], reindex_source=managed_source)
    st.divider()
    if st.button("Limpiar historial"):
        st.session_state.messages = [
            {"role": "assistant", "content": "¿Qué quieres descubrir sobre el universo?"}
        ]
        st.rerun()

if not api_available:
    st.error(health_error)
    st.caption("Ejecuta este comando desde rag-app/ y vuelve a intentar la conexión:")
    st.code(".venv/bin/python -m uvicorn app.main:app --reload --port 8000", language="bash")

if api_available and not key_configured:
    st.info("Configura la clave de Google AI para indexar y preguntar.")
if api_available and health["index_chunks"] == 0:
    st.info("El índice está vacío. Carga documentos desde la barra lateral.")

# Mostrar historial del chat
for message in st.session_state.messages:
    show_message(message)

can_query = api_available and documents_available and key_configured and health["index_chunks"] > 0
question = st.chat_input(
    "Pregunta sobre el universo...",
    disabled=not can_query,
)
if question is not None and can_query:
    question = question.strip()
    if not question:
        st.warning("La pregunta no puede estar en blanco.")
    else:
        user_message = {"role": "user", "content": question, "source": query_source}
        st.session_state.messages.append(user_message)
        show_message(user_message)
        with st.spinner("Recuperando evidencia y consultando a Gemini..."):
            try:
                query_payload = {"question": question, "top_k": int(top_k)}
                if query_source is not None:
                    query_payload["source"] = query_source
                with httpx.Client(timeout=TIMEOUT) as client:
                    response = client.post(
                        f"{API_URL}/query", json=query_payload
                    )
                    response.raise_for_status()
                result = response.json()
                assistant_message = {
                    "role": "assistant",
                    "content": result["answer"],
                    "citations": result["citations"],
                    "abstained": result["abstained"],
                }
            except httpx.HTTPStatusError as exc:
                assistant_message = {"role": "assistant", "content": api_error(exc.response), "error": True}
            except httpx.HTTPError:
                assistant_message = {
                    "role": "assistant",
                    "content": "No se pudo conectar con la API durante la consulta.",
                    "error": True,
                }
            except (ValueError, KeyError, TypeError):
                assistant_message = {
                    "role": "assistant",
                    "content": "La API devolvió una respuesta de consulta inválida.",
                    "error": True,
                }
        st.session_state.messages.append(assistant_message)
        show_message(assistant_message)
