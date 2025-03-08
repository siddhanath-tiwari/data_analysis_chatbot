"""
Prompt engineering templates.
"""
from typing import Dict, Any

# System message for data analysis chatbot
SYSTEM_PROMPT = """You are an intelligent data analysis assistant with expertise in analyzing various types of data. 
Your goal is to help the user understand their data, extract insights, and visualize results.
You can assist with:
- Data analysis and interpretation
- Statistical testing
- Data visualization recommendations
- Answering questions based on data
- Explaining data patterns and trends

When the user provides data, analyze it thoroughly before responding.
When answering questions, use the provided context and data.
Be clear, concise, and helpful.
"""

# Template for data analysis with context
DATA_ANALYSIS_TEMPLATE = """
I need to analyze the following data:

{data_summary}

Based on this data, please answer the following question:
{question}

Additional context:
{context}

Analyze the data thoroughly and provide a detailed explanation of your findings.
If relevant, suggest visualizations or further analyses that could help understand the data better.
"""

# Template for generating Python code for data analysis
DATA_ANALYSIS_CODE_TEMPLATE = """
I need Python code to analyze the following data:

{data_summary}

The analysis should help answer this question:
{question}

The data is available in a pandas DataFrame called `df`.
Include comments explaining your approach and key parts of the code.
Ensure the code is efficient, well-structured, and follows best practices.
"""

# Template for data visualization code
DATA_VISUALIZATION_TEMPLATE = """
I need Python code to create visualizations for the following data:

{data_summary}

Visualization requirements:
{visualization_requirements}

The data is available in a pandas DataFrame called `df`.
Provide code using matplotlib, seaborn, or plotly that creates clear, informative, and professionally styled visualizations.
Include comments explaining the visualization choices.
"""

# Template for RAG-based QA
RAG_QA_TEMPLATE = """
I need to answer a question based on the following retrieved information:

RETRIEVED INFORMATION:
{context}

QUESTION:
{question}

Please provide a comprehensive answer based on the retrieved information above.
If the information is insufficient to fully answer the question, clearly state what is unknown.
"""

# Template for summarizing data analysis results
DATA_SUMMARY_TEMPLATE = """
I need a clear summary of the following data analysis results:

{analysis_results}

Please provide:
1. A concise summary of the key findings (3-5 bullet points)
2. Any important patterns or trends
3. Limitations of the analysis
4. Potential next steps or further analyses

The summary should be accessible to someone without a strong background in data analysis.
"""

# Template for analyzing database query results
DB_ANALYSIS_TEMPLATE = """
I've run the following SQL query:

```sql
{sql_query}
```

This query returned the following results:

{query_results}

Please analyze these results and help me understand:
1. What these results mean
2. Key insights from the data
3. Any patterns or anomalies
4. Suggestions for follow-up queries or analyses
"""

# Dictionary mapping template names to templates
TEMPLATES = {
    "system_prompt": SYSTEM_PROMPT,
    "data_analysis": DATA_ANALYSIS_TEMPLATE,
    "data_analysis_code": DATA_ANALYSIS_CODE_TEMPLATE,
    "data_visualization": DATA_VISUALIZATION_TEMPLATE,
    "rag_qa": RAG_QA_TEMPLATE,
    "data_summary": DATA_SUMMARY_TEMPLATE,
    "db_analysis": DB_ANALYSIS_TEMPLATE,
}

def get_template(template_name: str) -> str:
    """
    Get a prompt template by name.
    
    Args:
        template_name: Name of the template
        
    Returns:
        Template string
    """
    return TEMPLATES.get(template_name, "")

def format_template(template_name: str, variables: Dict[str, Any]) -> str:
    """
    Format a template with the provided variables.
    
    Args:
        template_name: Name of the template
        variables: Variables to substitute in the template
        
    Returns:
        Formatted template string
    """
    template = get_template(template_name)
    return template.format(**variables)