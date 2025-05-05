import tkinter as tk
from tkinter import ttk, scrolledtext
import sqlite3
import pandas as pd
import requests
import json
import os
import re
from threading import Thread

class TextToSQLApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Text-to-SQL Assistant")
        self.root.geometry("1200x800")
        
        # Database path
        self.db_path = "company_database.db"
        
        # Create sample database if it doesn't exist
        if not os.path.exists(self.db_path):
            self.create_sample_database()
        
        # Frame for database schema display
        self.schema_frame = ttk.LabelFrame(root, text="Database Schema")
        self.schema_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        self.schema_text = scrolledtext.ScrolledText(self.schema_frame, width=40, height=25)
        self.schema_text.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)
        
        # Load and display schema
        self.load_schema()
        
        # Frame for natural language query input
        self.query_frame = ttk.LabelFrame(root, text="Ask Your Question")
        self.query_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        
        self.query_entry = scrolledtext.ScrolledText(self.query_frame, width=40, height=5)
        self.query_entry.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)
        
        # Submit button
        self.submit_button = ttk.Button(self.query_frame, text="Generate SQL & Run Query", command=self.process_query)
        self.submit_button.pack(pady=5)
        
        # Example queries button
        self.example_button = ttk.Button(self.query_frame, text="Show Example Queries", command=self.show_examples)
        self.example_button.pack(pady=5)
        
        # Frame for SQL display
        self.sql_frame = ttk.LabelFrame(root, text="Generated SQL")
        self.sql_frame.grid(row=0, column=1, rowspan=2, padx=10, pady=10, sticky="nsew")
        
        self.sql_text = scrolledtext.ScrolledText(self.sql_frame, width=50, height=10)
        self.sql_text.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)
        
        # Frame for results
        self.results_frame = ttk.LabelFrame(root, text="Query Results")
        self.results_frame.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        
        self.results_text = scrolledtext.ScrolledText(self.results_frame, width=90, height=15)
        self.results_text.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)
        
        # Configure grid weights
        root.grid_columnconfigure(0, weight=1)
        root.grid_columnconfigure(1, weight=2)
        root.grid_rowconfigure(0, weight=3)
        root.grid_rowconfigure(1, weight=1)
        root.grid_rowconfigure(2, weight=2)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        self.status_bar = ttk.Label(root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.grid(row=3, column=0, columnspan=2, sticky="ew")
    
    def create_sample_database(self):
        """Create a sample database for demonstration"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create tables
        cursor.execute('''
        CREATE TABLE Customers (
            CustomerID INTEGER PRIMARY KEY,
            Name TEXT NOT NULL,
            Email TEXT,
            Phone TEXT,
            JoinDate DATE
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE Products (
            ProductID INTEGER PRIMARY KEY,
            Name TEXT NOT NULL,
            Category TEXT,
            Price DECIMAL(10,2),
            Stock INTEGER
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE Employees (
            EmployeeID INTEGER PRIMARY KEY,
            Name TEXT NOT NULL,
            Position TEXT,
            Salary DECIMAL(10,2),
            HireDate DATE
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE Orders (
            OrderID INTEGER PRIMARY KEY,
            CustomerID INTEGER,
            OrderDate DATE,
            TotalAmount DECIMAL(10,2),
            FOREIGN KEY (CustomerID) REFERENCES Customers(CustomerID)
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE OrderDetails (
            OrderDetailID INTEGER PRIMARY KEY,
            OrderID INTEGER,
            ProductID INTEGER,
            Quantity INTEGER,
            UnitPrice DECIMAL(10,2),
            FOREIGN KEY (OrderID) REFERENCES Orders(OrderID),
            FOREIGN KEY (ProductID) REFERENCES Products(ProductID)
        )
        ''')
        
        # Insert sample data
        # Customers
        customers = [
            (1, 'John Smith', 'john@example.com', '555-1234', '2020-01-15'),
            (2, 'Jane Doe', 'jane@example.com', '555-5678', '2019-06-22'),
            (3, 'Bob Johnson', 'bob@example.com', '555-9012', '2021-03-10'),
            (4, 'Alice Brown', 'alice@example.com', '555-3456', '2018-11-05'),
            (5, 'Charlie Wilson', 'charlie@example.com', '555-7890', '2022-02-28')
        ]
        cursor.executemany('INSERT INTO Customers VALUES (?,?,?,?,?)', customers)
        
        # Products
        products = [
            (1, 'Laptop', 'Electronics', 999.99, 50),
            (2, 'Smartphone', 'Electronics', 699.99, 100),
            (3, 'Desk Chair', 'Furniture', 199.99, 30),
            (4, 'Coffee Table', 'Furniture', 149.99, 25),
            (5, 'Headphones', 'Electronics', 89.99, 75),
            (6, 'Bookshelf', 'Furniture', 129.99, 20),
            (7, 'Tablet', 'Electronics', 399.99, 60),
            (8, 'Monitor', 'Electronics', 299.99, 40)
        ]
        cursor.executemany('INSERT INTO Products VALUES (?,?,?,?,?)', products)
        
        # Employees
        employees = [
            (1, 'Michael Scott', 'Manager', 75000.00, '2018-05-10'),
            (2, 'Jim Halpert', 'Sales', 65000.00, '2019-03-15'),
            (3, 'Pam Beesly', 'Reception', 48000.00, '2019-04-20'),
            (4, 'Dwight Schrute', 'Sales', 67000.00, '2018-09-30'),
            (5, 'Angela Martin', 'Accounting', 59000.00, '2018-07-25'),
            (6, 'Kevin Malone', 'Accounting', 52000.00, '2020-01-15'),
            (7, 'Stanley Hudson', 'Sales', 63000.00, '2021-11-05'),
            (8, 'Phyllis Vance', 'Sales', 61000.00, '2022-02-10')
        ]
        cursor.executemany('INSERT INTO Employees VALUES (?,?,?,?,?)', employees)
        
        # Orders
        orders = [
            (1, 1, '2023-01-15', 1699.98),
            (2, 2, '2023-02-20', 699.99),
            (3, 3, '2023-03-10', 349.98),
            (4, 4, '2023-04-05', 129.99),
            (5, 5, '2023-05-12', 1299.97),
            (6, 1, '2023-06-18', 199.99),
            (7, 2, '2023-07-22', 89.99),
            (8, 3, '2022-08-30', 399.99),
            (9, 4, '2022-09-15', 299.99),
            (10, 5, '2022-10-20', 129.99)
        ]
        cursor.executemany('INSERT INTO Orders VALUES (?,?,?,?)', orders)
        
        # OrderDetails
        order_details = [
            (1, 1, 1, 1, 999.99),
            (2, 1, 5, 1, 699.99),
            (3, 2, 2, 1, 699.99),
            (4, 3, 3, 1, 199.99),
            (5, 3, 5, 1, 149.99),
            (6, 4, 6, 1, 129.99),
            (7, 5, 1, 1, 999.99),
            (8, 5, 7, 1, 299.99),
            (9, 6, 3, 1, 199.99),
            (10, 7, 5, 1, 89.99),
            (11, 8, 7, 1, 399.99),
            (12, 9, 8, 1, 299.99),
            (13, 10, 6, 1, 129.99)
        ]
        cursor.executemany('INSERT INTO OrderDetails VALUES (?,?,?,?,?)', order_details)
        
        conn.commit()
        conn.close()
    
    def load_schema(self):
        """Load and display database schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get table names
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        schema_text = "DATABASE SCHEMA:\n\n"
        
        for table in tables:
            table_name = table[0]
            schema_text += f"TABLE: {table_name}\n"
            
            # Get column info
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            
            for col in columns:
                col_name = col[1]
                col_type = col[2]
                is_pk = "PRIMARY KEY" if col[5] == 1 else ""
                schema_text += f"  - {col_name} ({col_type}) {is_pk}\n"
            
            schema_text += "\n"
        
        conn.close()
        
        self.schema_text.delete(1.0, tk.END)
        self.schema_text.insert(tk.END, schema_text)
    
    def show_examples(self):
        """Show example queries"""
        examples = [
            "Top 5 Customers by Total Purchase Amount",
            "Products with No Sales in the Last 6 Months",
            "List Employees Hired in the Last 5 Years",
            "Identify Products with No Sales in the Past Year",
            "Average Order Quantity by Product Category",
            "Employees with Above-Average Salaries"
        ]
        
        example_text = "Example Questions:\n\n"
        for i, example in enumerate(examples, 1):
            example_text += f"{i}. {example}\n"
        
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, example_text)
    
    def fix_common_sql_issues(self, sql):
        """Fix common SQL issues like ambiguous column names"""
        # Fix ambiguous column names in SELECT and GROUP BY
        if "JOIN" in sql or "join" in sql:
            # Replace unqualified column names with qualified ones in SELECT
            lines = sql.split('\n')
            for i, line in enumerate(lines):
                if any(keyword in line.upper() for keyword in ["SELECT", "GROUP BY", "ORDER BY"]):
                    # Look for unqualified column names that might be ambiguous
                    if "CustomerID" in line and not ("Customers.CustomerID" in line or "Orders.CustomerID" in line):
                        line = line.replace("CustomerID", "Customers.CustomerID")
                    if "ProductID" in line and not ("Products.ProductID" in line or "OrderDetails.ProductID" in line):
                        line = line.replace("ProductID", "Products.ProductID")
                    # Add more common column fixes as needed
                    lines[i] = line
            
            sql = '\n'.join(lines)
        
        return sql
        
    def extract_sql_query(self, text):
        """Extract SQL query from LLM response, handling various formats"""
        # First try to find SQL between code blocks
        sql_pattern = re.compile(r"```sql\s*(.*?)\s*```", re.DOTALL)
        match = sql_pattern.search(text)
        if match:
            return match.group(1).strip()
        
        # Try other code block format
        code_pattern = re.compile(r"```\s*(.*?)\s*```", re.DOTALL)
        match = code_pattern.search(text)
        if match:
            return match.group(1).strip()
        
        # If we reach here, try to extract SQL directly
        
        # Check for common explanation markers and truncate
        explanation_markers = [
            "### Explain", 
            "# Explanation", 
            "-- Explanation",
            "/* Explanation",
            "-- This query",
            "-- The query",
            "-- First",
            "-- Here",
            "# This"
        ]
        
        for marker in explanation_markers:
            if marker in text:
                text = text.split(marker)[0].strip()
        
        # Remove common prefixes LLMs add
        lines = text.split('\n')
        cleaned_lines = []
        skip_prefixes = [
            "Sure!", "Here is", "Here's", "The SQL", "SQL query",
            "I'll", "Let me", "To answer", "For this", "This query"
        ]
        
        for line in lines:
            # Skip lines that are likely explanatory text
            should_skip = False
            line_lower = line.lower().strip()
            for prefix in skip_prefixes:
                if line_lower.startswith(prefix.lower()):
                    should_skip = True
                    break
            
            if not should_skip and line.strip():
                cleaned_lines.append(line)
        
        # Join remaining lines which should be mostly SQL
        return '\n'.join(cleaned_lines).strip()
    
    def generate_sql(self, natural_language_query):
        """Generate SQL from natural language using local LLM (via Ollama)"""
        try:
            # Create prompt with schema and query
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get table info
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            
            schema_info = ""
            for table in tables:
                table_name = table[0]
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns = cursor.fetchall()
                
                schema_info += f"Table: {table_name}\n"
                schema_info += "Columns:\n"
                for col in columns:
                    schema_info += f"  - {col[1]} ({col[2]})\n"
                schema_info += "\n"
            
            conn.close()
            
            prompt = f"""
            ### Write only the SQL query without any explanations or additional text.
            SQLite database tables, with their properties:
            
            {schema_info}
            
            ### A user asks the following question:
            {natural_language_query}
            
            ### Important instructions:
            1. Generate ONLY the SQLite SQL query that answers the user's question.
            2. DO NOT include any explanations, comments, or markdown formatting.
            3. Always use fully qualified column names (table_name.column_name) when joining tables and full table's name.
            4. Your response should contain NOTHING except the SQL code itself.
            5. Double check that the column you write is exist!
            
            
            SQL query:
            """

            # Call Ollama API
            url = "http://localhost:11434/api/generate"
            data = {
                "model": "sqlcoder:15b",  # Make sure you've pulled this model in Ollama
                "prompt": prompt,
                "stream": False
            }
            
            self.status_var.set("Generating SQL with local LLM...")
            response = requests.post(url, json=data)
            response_data = json.loads(response.text)
            
            # Extract SQL from response
            generated_text = response_data.get("response", "")
            
            # Extract just the SQL query
            sql = self.extract_sql_query(generated_text)
            
            # Additional cleanup for common SQL ambiguity issues
            sql = self.fix_common_sql_issues(sql)
            
            # Debug info
            self.status_var.set("SQL extracted successfully")
            return sql
            
        except Exception as e:
            self.status_var.set(f"Error generating SQL: {str(e)}")
            return None
    
    def process_query(self):
        """Process natural language query to SQL and execute it"""
        def worker():
            query = self.query_entry.get("1.0", tk.END).strip()
            if not query:
                self.status_var.set("Please enter a query")
                return
            
            # Generate SQL
            sql = self.generate_sql(query)
            if not sql:
                return
            
            # Display raw SQL before execution
            self.sql_text.delete(1.0, tk.END)
            self.sql_text.insert(tk.END, sql)
            
            # Execute SQL
            try:
                conn = sqlite3.connect(self.db_path)
                df = pd.read_sql_query(sql, conn)
                conn.close()
                
                # Display results
                if df.empty:
                    result_text = "No results found."
                else:
                    result_text = df.to_string(index=False)
                
                self.results_text.delete(1.0, tk.END)
                self.results_text.insert(tk.END, result_text)
                
                self.status_var.set("Query executed successfully")
                
            except Exception as e:
                self.results_text.delete(1.0, tk.END)
                self.results_text.insert(tk.END, f"Error executing SQL: {str(e)}\n\nSQL query attempted:\n{sql}")
                self.status_var.set("SQL execution failed")
        
        # Run in separate thread to keep UI responsive
        Thread(target=worker).start()

if __name__ == "__main__":
    # Check if Ollama is running
    try:
        response = requests.get("http://localhost:11434/api/tags")
        
        # Check if required model is available
        models = json.loads(response.text).get("models", [])
        llama_available = any("llama2" in model.get("name", "").lower() for model in models)
        
        if not llama_available:
            print("Warning: llama2 model not found in Ollama. Please run: ollama pull llama2")
            print("Continuing anyway, but the application may not work properly until you've pulled the model.")
    
    except Exception as e:
        print(f"Warning: Could not connect to Ollama server. Make sure Ollama is running.")
        print("You can install Ollama from: https://ollama.ai/download")
        print(f"Error details: {str(e)}")
    
    root = tk.Tk()
    app = TextToSQLApp(root)
    root.mainloop()