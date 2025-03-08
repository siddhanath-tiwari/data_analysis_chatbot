"""
Database manager for handling database connections and operations.
"""



import os
from typing import Dict, Any, Optional, List, Tuple
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker, scoped_session, Session
from sqlalchemy.ext.declarative import declarative_base
from loguru import logger

Base = declarative_base()

class DatabaseManager:
    """
    Manages database connections and operations.
    Supports SQLite, PostgreSQL, and MongoDB.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the database manager.
        
        Args:
            config: Database configuration
        """
        self.config = config
        self.engine = None
        self.session_factory = None
        self.session = None
        self.db_type = config.get("type", "sqlite").lower()
        self.connection_string = config.get("connection_string", "sqlite:///data/chatbot.db")
        
        # Ensure data directory exists for SQLite
        if self.db_type == "sqlite" and "sqlite:///" in self.connection_string:
            db_path = self.connection_string.split("sqlite:///")[1]
            os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    def initialize(self) -> None:
        """
        Initialize the database connection.
        """
        if self.db_type in ["sqlite", "postgresql"]:
            self._init_sql_database()
        elif self.db_type == "mongodb":
            self._init_mongodb()
        else:
            raise ValueError(f"Unsupported database type: {self.db_type}")
        
        logger.info(f"Database initialized: {self.db_type}")
    
    def _init_sql_database(self) -> None:
        """
        Initialize SQL database (SQLite or PostgreSQL).
        """
        self.engine = create_engine(
            self.connection_string,
            pool_size=self.config.get("pool_size", 5),
            max_overflow=self.config.get("max_overflow", 10),
            echo=self.config.get("echo", False),
        )
        
        self.session_factory = sessionmaker(bind=self.engine)
        self.session = scoped_session(self.session_factory)
        
        # Create tables if they don't exist
        Base.metadata.create_all(self.engine)
    
    def _init_mongodb(self) -> None:
        """
        Initialize MongoDB connection.
        """
        from pymongo import MongoClient
        
        client = MongoClient(self.connection_string)
        db_name = self.config.get("database_name", "data_analysis_chatbot")
        self.db = client[db_name]
        logger.info(f"Connected to MongoDB: {db_name}")
    
    def get_session(self) -> Session:
        """
        Get a database session.
        
        Returns:
            Database session
        """
        if self.db_type in ["sqlite", "postgresql"]:
            return self.session()
        raise ValueError(f"Sessions not supported for database type: {self.db_type}")
    
    def close_session(self, session: Session) -> None:
        """
        Close a database session.
        
        Args:
            session: Database session to close
        """
        if session:
            session.close()
    
    def commit_session(self, session: Session) -> None:
        """
        Commit changes in a database session.
        
        Args:
            session: Database session to commit
        """
        if session:
            try:
                session.commit()
            except Exception as e:
                session.rollback()
                logger.error(f"Error committing session: {e}")
                raise
    
    def execute_query(self, query: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Execute a raw SQL query.
        
        Args:
            query: SQL query string
            params: Query parameters
            
        Returns:
            List of dictionaries containing query results
        """
        if self.db_type not in ["sqlite", "postgresql"]:
            raise ValueError(f"Raw queries not supported for database type: {self.db_type}")
        
        result = []
        with self.engine.connect() as connection:
            cursor = connection.execute(query, params or {})
            if cursor.returns_rows:
                for row in cursor:
                    result.append(dict(row))
        
        return result
    
    def create_tables(self) -> None:
        """
        Create all database tables.
        """
        if self.db_type in ["sqlite", "postgresql"]:
            Base.metadata.create_all(self.engine)
            logger.info("Database tables created")
        else:
            logger.warning(f"Creating tables not supported for database type: {self.db_type}")
    
    def drop_tables(self) -> None:
        """
        Drop all database tables.
        """
        if self.db_type in ["sqlite", "postgresql"]:
            Base.metadata.drop_all(self.engine)
            logger.info("Database tables dropped")
        else:
            logger.warning(f"Dropping tables not supported for database type: {self.db_type}")