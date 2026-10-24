"""Clientes compartidos (Supabase y embeddings de Gemini)."""
import os
from functools import lru_cache

from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from supabase import create_client

load_dotenv()  # lee Backend/.env cuando se corre fuera de Docker


@lru_cache
def get_supabase():
    return create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_KEY"])


@lru_cache
def get_embeddings():
    return GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001",
        google_api_key=os.environ["GOOGLE_API_KEY"],
    )
