import os
from pathlib import Path
from typing import Dict, Any, Optional

from sqlalchemy import create_engine, Column, Integer, String, Text, text
from sqlalchemy.orm import declarative_base, sessionmaker

import chromadb
from chromadb.config import Settings

from .config import get_config_dir

Base = declarative_base()

class UserProfile(Base):
    """SQLAlchemy model for global user profile."""
    __tablename__ = 'user_profile'
    id = Column(Integer, primary_key=True)
    name = Column(String, default="Developer")
    email = Column(String, default="developer@example.com")
    style_prompt = Column(Text, default="")
    theme = Column(String, default="dark")
    api_provider = Column(String, default="openai")  # openai, anthropic, gemini, ollama
    api_key = Column(String, default="")
    fallback_api_provider = Column(String, default="gemini")
    fallback_api_key = Column(String, default="")
    tech_stack = Column(Text, default="Python")
    tokens_saved = Column(Integer, default=0)
    comments_minimized = Column(Integer, default=0)

class MemoryManager:
    """Manages SQLite structured data and ChromaDB semantic memory."""
    
    def __init__(self):
        # Setup SQLite for Global Profile
        self.global_db_path = get_config_dir() / "flowstate.db"
        self.engine = create_engine(f"sqlite:///{self.global_db_path}")
        Base.metadata.create_all(self.engine)
        
        # Safely migrate existing DB
        try:
            with self.engine.begin() as conn:
                conn.execute(text("ALTER TABLE user_profile ADD COLUMN fallback_api_provider TEXT DEFAULT 'gemini'"))
                conn.execute(text("ALTER TABLE user_profile ADD COLUMN fallback_api_key TEXT DEFAULT ''"))
        except Exception:
            pass
            
        self.Session = sessionmaker(bind=self.engine)
        
        # Setup ChromaDB for Per-Project semantic memory (Centralized safely in ~/.flowstate)
        self.project_chroma_path = get_config_dir() / "chroma_db"
        self.chroma_client = chromadb.PersistentClient(path=str(self.project_chroma_path))
        self.collection = self.chroma_client.get_or_create_collection(name="project_memory")

    def get_profile(self) -> UserProfile:
        with self.Session() as session:
            profile = session.query(UserProfile).first()
            if not profile:
                profile = UserProfile()
                session.add(profile)
                session.commit()
                # Need to refresh or just return the new one
                profile = session.query(UserProfile).first()
            return profile

    def update_profile(self, name: str=None, email: str=None, style_prompt: str=None, 
                       api_provider: str=None, api_key: str=None, 
                       fallback_api_provider: str=None, fallback_api_key: str=None,
                       tech_stack: str=None) -> None:
        with self.Session() as session:
            profile = session.query(UserProfile).first()
            if not profile:
                profile = UserProfile()
                session.add(profile)
            if name is not None: profile.name = name
            if email is not None: profile.email = email
            if style_prompt is not None: profile.style_prompt = style_prompt
            if api_provider is not None: profile.api_provider = api_provider
            if api_key is not None: profile.api_key = api_key
            if fallback_api_provider is not None: profile.fallback_api_provider = fallback_api_provider
            if fallback_api_key is not None: profile.fallback_api_key = fallback_api_key
            if tech_stack is not None: profile.tech_stack = tech_stack
            session.commit()
            
    def increment_stat(self, stat_name: str, amount: int = 1):
        with self.Session() as session:
            profile = session.query(UserProfile).first()
            if profile:
                current = getattr(profile, stat_name, 0)
                setattr(profile, stat_name, current + amount)
                session.commit()

    def add_project_memory(self, doc_id: str, content: str, metadata: Optional[Dict[str, Any]] = None):
        """Add context/memory specific to this project."""
        if metadata is None:
            metadata = {}
        self.collection.upsert(
            documents=[content],
            metadatas=[metadata],
            ids=[doc_id]
        )

    def query_project_memory(self, query: str, n_results: int = 3) -> list:
        """Query project context."""
        if self.collection.count() == 0:
            return []
        
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )
        return results.get('documents', [[]])[0]

    def query_project_memory_full(self, query: str, n_results: int = 3, where: dict = None) -> dict:
        """Query project context and return full dictionary (documents, metadatas)."""
        if self.collection.count() == 0:
            return {'documents': [[]], 'metadatas': [[]]}
        
        kwargs = {
            "query_texts": [query],
            "n_results": n_results
        }
        if where:
            kwargs["where"] = where
            
        results = self.collection.query(**kwargs)
        return results

    def get_learned_projects(self) -> list:
        """Returns a list of all unique project paths learned in ChromaDB."""
        if self.collection.count() == 0:
            return []
            
        # Get all metadatas
        data = self.collection.get(include=['metadatas'])
        projects = set()
        for metas in data.get('metadatas', []):
            if metas and 'project_path' in metas:
                projects.add(metas['project_path'])
                
        return sorted(list(projects))
