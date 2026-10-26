#!/usr/bin/env python3
"""
Supabase Database Setup for Ultron Agent
This script sets up the database schema and initializes the connection
"""

import os
import json
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Supabase configuration - get from environment variables
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

def get_supabase_client() -> Client:
    """Get Supabase client instance"""
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise ValueError("Please set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY environment variables")
    return create_client(SUPABASE_URL, SUPABASE_KEY)

def test_connection():
    """Test the Supabase connection"""
    try:
        client = get_supabase_client()
        # Try a simple query
        result = client.table("conversations").select("*").limit(1).execute()
        print("✓ Supabase connection successful!")
        return True
    except Exception as e:
        print(f"✗ Connection failed: {e}")
        return False

if __name__ == "__main__":
    print("Ultron Agent - Supabase Setup")
    print("=" * 40)

    # Test connection first
    test_connection()

    print("\nNext steps:")
    print("1. Go to your Supabase Dashboard")
    print("2. Navigate to SQL Editor")
    print("3. Copy and paste the contents of supabase/schema.sql")
    print("4. Run the SQL to create all tables")
    print("\nThen update your ultron_config.json with Supabase credentials!")
