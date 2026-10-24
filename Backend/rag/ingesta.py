"""SCRUM-20: pipeline de ingesta del RAG.

Carga archivos .txt/.md de rag/documentos, los divide en chunks con
RecursiveCharacterTextSplitter, genera embeddings y los guarda en Supabase.

Uso (desde la carpeta Backend):  python -m rag.ingesta
"""
from pathlib import Path

from langchain_text_splitters import RecursiveCharacterTextSplitter

from rag.clientes import get_embeddings, get_supabase

CARPETA = Path(__file__).parent / "documentos"
TABLA = "conocimiento_chunks"
LOTE = 20  # chunks por peticion a la API de embeddings


def cargar_documentos():
    archivos = sorted(list(CARPETA.glob("*.txt")) + list(CARPETA.glob("*.md")))
    if not archivos:
        raise SystemExit(f"No hay archivos .txt o .md en {CARPETA}")
    return [(a.name, a.read_text(encoding="utf-8")) for a in archivos]


def main():
    splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)
    embeddings = get_embeddings()
    supabase = get_supabase()
    total = 0

    for nombre, texto in cargar_documentos():
        chunks = splitter.split_text(texto)
        print(f"{nombre}: {len(chunks)} chunks")

        # Re-ingestar el mismo archivo no duplica: primero se borran sus chunks viejos.
        supabase.table(TABLA).delete().eq("fuente", nombre).execute()

        for inicio in range(0, len(chunks), LOTE):
            lote = chunks[inicio:inicio + LOTE]
            vectores = embeddings.embed_documents(lote, task_type="RETRIEVAL_DOCUMENT")
            filas = [
                {
                    "fuente": nombre,
                    "chunk_index": inicio + i,
                    "contenido": texto_chunk,
                    "embedding": vector,
                }
                for i, (texto_chunk, vector) in enumerate(zip(lote, vectores))
            ]
            supabase.table(TABLA).insert(filas).execute()
            total += len(filas)

    print(f"Listo: {total} chunks guardados en '{TABLA}'.")


if __name__ == "__main__":
    main()
