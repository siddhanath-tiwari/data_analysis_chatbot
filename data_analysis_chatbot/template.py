import os

def create_structure(base_path, structure):
    for key, value in structure.items():
        path = os.path.join(base_path, key)
        if isinstance(value, dict):
            os.makedirs(path, exist_ok=True)
            create_structure(path, value)
        else:
            with open(path, "w") as f:
                f.write(value)

project_structure = {
    "data_analysis_chatbot": {
        "setup.py": "# Package setup and installation",
        "requirements.txt": "# Dependencies",
        "README.md": "# Project documentation",
        ".env.example": "# Example environment variables",
        "data_analysis_chatbot": {
            "__init__.py": "",
            "config.py": "# Configuration management",
            "main.py": "# Main entry point",
            "database": {
                "__init__.py": "",
                "db_manager.py": "# Database connection and operations",
                "models.py": "# Database models"
            },
            "rag": {
                "__init__.py": "",
                "document_store.py": "# Document storage and retrieval",
                "embeddings.py": "# Embedding models",
                "retriever.py": "# Document retrieval logic",
                "vectordb.py": "# Vector database integration"
            },
            "data_analysis": {
                "__init__.py": "",
                "analyzer.py": "# Data analysis functions",
                "visualization.py": "# Data visualization functions",
                "processors.py": "# Data preprocessing functions"
            },
            "llm": {
                "__init__.py": "",
                "llm_manager.py": "# LLM client and operations",
                "prompt_templates.py": "# Prompt engineering templates"
            },
            "api": {
                "__init__.py": "",
                "routes.py": "# API endpoints",
                "middlewares.py": "# API middlewares"
            },
            "ui": {
                "__init__.py": "",
                "app.py": "# Streamlit/Gradio app",
                "components.py": "# UI components"
            }
        },
        "tests": {
            "__init__.py": "",
            "test_database.py": "",
            "test_rag.py": "",
            "test_data_analysis.py": "",
            "test_api.py": ""
        }
    }
}

if __name__ == "__main__":
    base_path = os.getcwd()
    create_structure(base_path, project_structure)
    print("Project structure created successfully.")
