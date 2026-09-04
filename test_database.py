#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tools.database_integration_tool import DatabaseIntegrationTool

def test_database():
    print("Testing PostgreSQL/Supabase Database Integration")
    print("=" * 50)
    
    tool = DatabaseIntegrationTool()
    
    # Test connection
    print("Testing connection...")
    if tool.connect():
        print("[OK] Database connected successfully")
    else:
        print("[FAIL] Database connection failed")
        return
    
    # Test show tables
    print("\nTesting show tables...")
    result = tool.execute("show tables")
    print(f"Result: {result}")
    
    # Test create table
    print("\nTesting create table...")
    create_sql = """
    CREATE TABLE IF NOT EXISTS ultron_logs (
        id SERIAL PRIMARY KEY,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        component VARCHAR(100),
        message TEXT,
        level VARCHAR(20)
    )
    """
    result = tool.execute(create_sql)
    print(f"Result: {result}")
    
    # Test insert
    print("\nTesting insert...")
    insert_sql = "INSERT INTO ultron_logs (component, message, level) VALUES ('test', 'Database integration test', 'INFO')"
    result = tool.execute(insert_sql)
    print(f"Result: {result}")
    
    # Test select
    print("\nTesting select...")
    select_sql = "SELECT * FROM ultron_logs ORDER BY timestamp DESC LIMIT 5"
    result = tool.execute(select_sql)
    print(f"Result: {result}")
    
    tool.close()
    print("\nDatabase integration test completed!")

if __name__ == "__main__":
    test_database()