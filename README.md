# Text-to-SQL Assistant

A desktop application that converts natural language questions into SQL queries and automatically runs them against a SQLite database.

## Overview

This Text-to-SQL Assistant uses a local LLM to translate natural language questions into SQL queries. It provides an interface to interact with a database to non-technical users.

## Architecture

The application architecture:

1. **UI Layer** - Built with Tkinter:
   - Natural language query input
   - SQL query display
   - Query results display

2. **Database Layer** - SQLite database with sample company data:
   - Customers
   - Products
   - Employees
   - Orders
   - OrderDetails

3. **AI Translation Layer** - Uses Ollama to host a SQLCoder model that:
   - Receives the database schema and natural language query
   - Generates appropriate SQL code
   - Handles query parsing and SQL extraction


## Key Features

- Natural language to SQL translation
- SQL execution
- Result display in tabular format
- Example queries to help users get started
- SQL extraction from LLM responses
- Common SQL issue correction
- Threaded query processing to keep UI responsive

## Assumptions

1. **Local LLM Usage**: The application assumes you have Ollama installed and running locally.
2. **SQLCoder Model**: The app expects the "sqlcoder:15b" model to be available in Ollama.
3. **English Language Queries**: The NL-to-SQL translation works best with English language queries.
4. **SQLite Compatibility**: All queries are designed for SQLite syntax compatibility.
5. **Single User/Desktop Usage**: The application is designed for single-user desktop use, not as a web application or multi-user system.

Trade-offs
1. This is the only model that was making sense. Other models was generated false SQL query and couldn't execute it.
models tested: qwen3:14b, llama3:13b, llama3:8b, sqlcoder:7b, codellama:7b, mistral:7b-instruct

2. Other System Trade-offs
Local LLM vs. API Services:
 
Pro: Privacy, no API costs, works offline
Con: Requires local resources, depends on locally installed software
## Installation Requirements

### Prerequisites

1. **Python 3.7+**
2. **Ollama** - Local LLM server (https://ollama.ai/download)

### Required Python Packages

```
pip install tkinter
pip install pandas
pip install requests
```

### Installing the SQLCoder Model

After installing Ollama, run:

```
ollama pull sqlcoder:15b
```

## Usage Instructions

1. **Starting the Application**:
   ```
   python text_to_sql_app.py
   ```

2. **Viewing Database Schema**:
   - The left panel shows the structure of the sample database

3. **Asking Questions**:
   - Type your question in natural language in the input box
   - Click "Generate SQL & Run Query"
   - Example: "Show me the top 3 customers by total order amount"

4. **Viewing Results**:
   - Generated SQL appears in the middle panel
   - Query results appear in the bottom panel

5. **Using Example Queries**:
   - Click "Show Example Queries" to see sample questions you can ask

## Customizing the Database

To use your own database instead of the sample one:

1. Modify the `db_path` variable in the `__init__` method
2. Remove the `create_sample_database` method call if you already have a database
3. Adjust the schema display code if needed
