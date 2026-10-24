"""SCRUM-27: retriever de la base vectorial para cadenas de LangChain.

Prueba rapida (desde Backend):  python -m rag.retriever "tu pregunta"
"""
import sys
from typing import List

from langchain_core.callbacks import CallbackManagerForRetrieverRun
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever

from rag.clientes import get_embeddings, get_supabase


class SupabaseRetriever(BaseRetriever):
    """Busca los k chunks mas parecidos a la pregunta en Supabase."""

    k: int = 3
    umbral: float = 0.0  # similitud minima (0 a 1) para aceptar un chunk

    def _get_relevant_documents(
        self, query: str, *, run_manager: CallbackManagerForRetrieverRun
    ) -> List[Document]:
        vector = get_embeddings().embed_query(query, task_type="RETRIEVAL_QUERY")
        respuesta = get_supabase().rpc(
            "match_conocimiento",
            {"query_embedding": vector, "match_count": self.k},
        ).execute()
        return [
            Document(
                page_content=fila["contenido"],
                metadata={"fuente": fila["fuente"], "similitud": fila["similitud"]},
            )
            for fila in (respuesta.data or [])
            if fila["similitud"] >= self.umbral
        ]


def formatear_contexto(documentos: List[Document]) -> str:
    """Une los chunks recuperados en un solo texto para el prompt."""
    return "\n\n".join(d.page_content for d in documentos)


if __name__ == "__main__":
    pregunta = " ".join(sys.argv[1:]) or "¿Cómo apago los servicios?"
    for doc in SupabaseRetriever(k=3).invoke(pregunta):
        print(f"[{doc.metadata['similitud']:.3f}] ({doc.metadata['fuente']})")
        print(doc.page_content[:300], "\n")
