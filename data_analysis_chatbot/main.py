"""
Main entry point for the Data Analysis Chatbot application.
"""
import argparse
import os
from loguru import logger

from data_analysis_chatbot.config import load_config
from data_analysis_chatbot.database.db_manager import DatabaseManager
from data_analysis_chatbot.rag.document_store import DocumentStore
from data_analysis_chatbot.llm.llm_manager import LLMManager
from data_analysis_chatbot.api.routes import start_api_server
from data_analysis_chatbot.ui.app import start_ui

def setup_logger():
    """Configure the application logger."""
    log_level = os.getenv("LOG_LEVEL", "INFO")
    logger.remove()
    logger.add(
        "logs/app.log",
        rotation="100 MB",
        retention="10 days",
        level=log_level,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
    )
    logger.add(
        lambda msg: print(msg),
        level=log_level,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
    )

def init_application():
    """Initialize all components of the application."""
    # Load configuration
    config = load_config()
    
    # Initialize database
    db_manager = DatabaseManager(config["database"])
    db_manager.initialize()
    
    # Initialize RAG components
    document_store = DocumentStore(config["rag"])
    
    # Initialize LLM
    llm_manager = LLMManager(config["llm"])
    
    logger.info("Application initialized successfully")
    
    return {
        "config": config,
        "db_manager": db_manager,
        "document_store": document_store,
        "llm_manager": llm_manager,
    }

def main():
    """Main entry point for the application."""
    parser = argparse.ArgumentParser(description="Data Analysis Chatbot")
    parser.add_argument(
        "--mode",
        type=str,
        choices=["api", "ui", "both"],
        default="both",
        help="Run mode (api, ui, or both)",
    )
    parser.add_argument(
        "--port", type=int, default=8000, help="Port for the API server"
    )
    parser.add_argument(
        "--ui-port", type=int, default=8501, help="Port for the UI server"
    )
    parser.add_argument(
        "--debug", action="store_true", help="Enable debug mode"
    )
    
    args = parser.parse_args()
    
    # Setup logger
    setup_logger()
    
    if args.debug:
        os.environ["LOG_LEVEL"] = "DEBUG"
        logger.info("Debug mode enabled")
    
    logger.info(f"Starting application in {args.mode} mode")
    
    # Initialize application components
    app_components = init_application()
    
    # Start servers based on the selected mode
    if args.mode in ["api", "both"]:
        start_api_server(app_components, port=args.port)
    
    if args.mode in ["ui", "both"]:
        start_ui(app_components, port=args.ui_port)

if __name__ == "__main__":
    main()