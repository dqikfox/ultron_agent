#!/usr/bin/env python3

from tools.database_tool import DatabaseTool

def test_database():
    tool = DatabaseTool()

    # Test storing data
    store_command = 'store data table conversations {"user_input": "test message", "ai_response": "test response"}'
    result = tool.execute(store_command)
    print('Database Store Test Result:')
    print(result)
    print()

    # Test querying data
    query_command = 'query data table conversations'
    query_result = tool.execute(query_command)
    print('Database Query Test Result:')
    print(query_result)

if __name__ == "__main__":
    test_database()
