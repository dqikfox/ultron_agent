#!/usr/bin/env python3
"""
Ultron Agent Database Module
Provides database operations for conversations, avatars, and agent sessions
Using Supabase as the backend
"""

import os
import json
import uuid
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from supabase import create_client, Client

class UltronDB:
    """Main database class for Ultron Agent"""

    def __init__(self, supabase_url: str = None, supabase_key: str = None):
        """Initialize the database connection"""
        self.supabase_url = supabase_url or os.getenv("SUPABASE_URL")
        self.supabase_key = supabase_key or os.getenv("SUPABASE_SERVICE_ROLE_KEY")

        if not self.supabase_url or not self.supabase_key:
            raise ValueError("Supabase URL and key are required. Please set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY environment variables.")

        self.client: Client = create_client(self.supabase_url, self.supabase_key)

    # ==================== Conversations ====================

    def create_conversation(self, user_id: str = None, title: str = "New Conversation") -> Dict[str, Any]:
        """Create a new conversation"""
        data = {
            "user_id": user_id,
            "title": title,
            "metadata": {}
        }
        result = self.client.table("conversations").insert(data).execute()
        return result.data[0] if result.data else {}

    def get_conversation(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """Get a conversation by ID"""
        result = self.client.table("conversations").select("*").eq("id", conversation_id).execute()
        return result.data[0] if result.data else None

    def list_conversations(self, user_id: str = None, limit: int = 50) -> List[Dict[str, Any]]:
        """List conversations, optionally filtered by user"""
        query = self.client.table("conversations").select("*").order("updated_at", desc=True).limit(limit)
        if user_id:
            query = query.eq("user_id", user_id)
        result = query.execute()
        return result.data

    def update_conversation(self, conversation_id: str, title: str = None, metadata: Dict = None) -> Dict[str, Any]:
        """Update a conversation"""
        update_data = {}
        if title:
            update_data["title"] = title
        if metadata:
            update_data["metadata"] = json.dumps(metadata)

        result = self.client.table("conversations").update(update_data).eq("id", conversation_id).execute()
        return result.data[0] if result.data else {}

    def delete_conversation(self, conversation_id: str) -> bool:
        """Delete a conversation (cascades to messages)"""
        result = self.client.table("conversations").delete().eq("id", conversation_id).execute()
        return len(result.data) > 0

    # ==================== Messages ====================

    def add_message(
        self,
        conversation_id: str,
        role: str,
        content: str,
        model: str = None,
        tokens: int = None,
        metadata: Dict = None
    ) -> Dict[str, Any]:
        """Add a message to a conversation"""
        data = {
            "conversation_id": conversation_id,
            "role": role,
            "content": content,
            "model": model,
            "tokens": tokens,
            "metadata": metadata or {}
        }
        result = self.client.table("messages").insert(data).execute()

        # Update conversation's updated_at
        self.client.table("conversations").update({"updated_at": datetime.now().isoformat()}).eq("id", conversation_id).execute()

        return result.data[0] if result.data else {}

    def get_messages(self, conversation_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get messages for a conversation"""
        result = self.client.table("messages").select("*").eq("conversation_id", conversation_id).order("created_at", asc=True).limit(limit).execute()
        return result.data

    def delete_message(self, message_id: str) -> bool:
        """Delete a message"""
        result = self.client.table("messages").delete().eq("id", message_id).execute()
        return len(result.data) > 0

    # ==================== Avatars ====================

    def create_avatar(
        self,
        user_id: str,
        name: str,
        race: str = "Human",
        char_class: str = "Warrior",
        alignment: str = "Neutral",
        stats: Dict = None
    ) -> Dict[str, Any]:
        """Create a new avatar"""
        data = {
            "user_id": user_id,
            "name": name,
            "race": race,
            "class": char_class,
            "alignment": alignment,
            "stats": stats or {}
        }
        result = self.client.table("avatars").insert(data).execute()
        return result.data[0] if result.data else {}

    def get_avatar(self, avatar_id: str) -> Optional[Dict[str, Any]]:
        """Get an avatar by ID"""
        result = self.client.table("avatars").select("*").eq("id", avatar_id).execute()
        return result.data[0] if result.data else None

    def get_user_avatars(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all avatars for a user"""
        result = self.client.table("avatars").select("*").eq("user_id", user_id).execute()
        return result.data

    def update_avatar(self, avatar_id: str, **kwargs) -> Dict[str, Any]:
        """Update avatar attributes"""
        # Handle special JSON fields
        for key in ["inventory", "stats", "relationship_scores"]:
            if key in kwargs:
                kwargs[key] = json.dumps(kwargs[key])

        result = self.client.table("avatars").update(kwargs).eq("id", avatar_id).execute()
        return result.data[0] if result.data else {}

    def delete_avatar(self, avatar_id: str) -> bool:
        """Delete an avatar"""
        result = self.client.table("avatars").delete().eq("id", avatar_id).execute()
        return len(result.data) > 0

    # ==================== Agent Sessions ====================

    def create_session(
        self,
        session_id: str,
        user_id: str = None,
        context: Dict = None,
        expires_in_hours: int = 24
    ) -> Dict[str, Any]:
        """Create or update an agent session"""
        expires_at = (datetime.now() + timedelta(hours=expires_in_hours)).isoformat()

        data = {
            "session_id": session_id,
            "user_id": user_id,
            "context": context or {},
            "expires_at": expires_at
        }

        # Try to insert, if exists then update
        try:
            result = self.client.table("agent_sessions").insert(data).execute()
        except Exception:
            result = self.client.table("agent_sessions").update({
                "context": context or {},
                "updated_at": datetime.now().isoformat(),
                "expires_at": expires_at
            }).eq("session_id", session_id).execute()

        return result.data[0] if result.data else {}

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get an agent session"""
        result = self.client.table("agent_sessions").select("*").eq("session_id", session_id).execute()
        session = result.data[0] if result.data else None

        if session and session.get("expires_at"):
            expires_at = datetime.fromisoformat(session["expires_at"].replace("Z", "+00:00"))
            if expires_at < datetime.now(expires_at.tzinfo):
                # Session expired, delete it
                self.delete_session(session_id)
                return None

        return session

    def update_session(self, session_id: str, state: Dict = None, context: Dict = None, memory: Dict = None) -> Dict[str, Any]:
        """Update session state"""
        update_data = {}
        if state:
            update_data["state"] = json.dumps(state)
        if context:
            update_data["context"] = json.dumps(context)
        if memory:
            update_data["memory"] = json.dumps(memory)

        result = self.client.table("agent_sessions").update(update_data).eq("session_id", session_id).execute()
        return result.data[0] if result.data else {}

    def delete_session(self, session_id: str) -> bool:
        """Delete a session"""
        result = self.client.table("agent_sessions").delete().eq("session_id", session_id).execute()
        return len(result.data) > 0

    def cleanup_expired_sessions(self) -> int:
        """Clean up expired sessions"""
        result = self.client.table("agent_sessions").delete().lt("expires_at", datetime.now().isoformat()).execute()
        return len(result.data)

    # ==================== Workflows ====================

    def create_workflow(
        self,
        name: str,
        definition: Dict,
        user_id: str = None,
        description: str = None,
        is_public: bool = False
    ) -> Dict[str, Any]:
        """Create a workflow"""
        data = {
            "name": name,
            "description": description,
            "definition": json.dumps(definition),
            "user_id": user_id,
            "is_public": is_public
        }
        result = self.client.table("workflows").insert(data).execute()
        return result.data[0] if result.data else {}

    def get_workflow(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get a workflow"""
        result = self.client.table("workflows").select("*").eq("id", workflow_id).execute()
        return result.data[0] if result.data else None

    def list_workflows(self, user_id: str = None, include_public: bool = True) -> List[Dict[str, Any]]:
        """List workflows"""
        query = self.client.table("workflows").select("*")

        if user_id and include_public:
            query = query.or_(f"user_id.eq.{user_id},is_public.eq.true")
        elif user_id:
            query = query.eq("user_id", user_id)
        elif not include_public:
            query = query.eq("is_public", True)

        result = query.execute()
        return result.data

    def update_workflow(self, workflow_id: str, **kwargs) -> Dict[str, Any]:
        """Update a workflow"""
        for key in ["definition", "stats"]:
            if key in kwargs:
                kwargs[key] = json.dumps(kwargs[key])

        result = self.client.table("workflows").update(kwargs).eq("id", workflow_id).execute()
        return result.data[0] if result.data else {}

    def delete_workflow(self, workflow_id: str) -> bool:
        """Delete a workflow"""
        result = self.client.table("workflows").delete().eq("id", workflow_id).execute()
        return len(result.data) > 0

    # ==================== User Preferences ====================

    def get_preferences(self, user_id: str) -> Dict[str, Any]:
        """Get user preferences"""
        result = self.client.table("user_preferences").select("*").eq("user_id", user_id).execute()
        if result.data:
            return result.data[0]

        # Create default preferences
        return self.update_preferences(user_id, {})

    def update_preferences(self, user_id: str, preferences: Dict) -> Dict[str, Any]:
        """Update user preferences"""
        data = {
            "user_id": user_id,
            "preferences": json.dumps(preferences)
        }

        # Try to update first
        result = self.client.table("user_preferences").update(data).eq("user_id", user_id).execute()

        if not result.data:
            # Insert if not exists
            result = self.client.table("user_preferences").insert(data).execute()

        return result.data[0] if result.data else {}

    # ==================== Audit Logging ====================

    def log_action(
        self,
        action: str,
        user_id: str = None,
        entity_type: str = None,
        entity_id: str = None,
        details: Dict = None,
        ip_address: str = None
    ) -> Dict[str, Any]:
        """Log an action for audit purposes"""
        data = {
            "action": action,
            "user_id": user_id,
            "entity_type": entity_type,
            "entity_id": entity_id,
            "details": details or {},
            "ip_address": ip_address
        }
        result = self.client.table("audit_logs").insert(data).execute()
        return result.data[0] if result.data else {}

    def get_audit_logs(self, user_id: str = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Get audit logs"""
        query = self.client.table("audit_logs").select("*").order("created_at", desc=True).limit(limit)
        if user_id:
            query = query.eq("user_id", user_id)
        result = query.execute()
        return result.data


# Convenience function to get database instance
def get_ultron_db() -> UltronDB:
    """Get a UltronDB instance using environment variables"""
    return UltronDB()


if __name__ == "__main__":
    # Test the database connection
    print("Testing Supabase connection...")
    db = get_ultron_db()

    # Test creating a conversation
    print("\n1. Creating test conversation...")
    conv = db.create_conversation(user_id="test_user", title="Test Conversation")
    print(f"   Created: {conv['id']}")

    # Test adding messages
    print("\n2. Adding messages...")
    msg1 = db.add_message(conv["id"], "user", "Hello Ultron!")
    msg2 = db.add_message(conv["id"], "assistant", "Greetings! How may I assist you?")
    print(f"   Added {len([msg1, msg2])} messages")

    # Test retrieving messages
    print("\n3. Retrieving messages...")
    messages = db.get_messages(conv["id"])
    print(f"   Found {len(messages)} messages")

    # Test creating an avatar
    print("\n4. Creating test avatar...")
    avatar = db.create_avatar("test_user", "UltronBot", "Robot", "AI", "Lawful Good")
    print(f"   Created: {avatar['name']}")

    # Test creating a session
    print("\n5. Creating test session...")
    session = db.create_session("test_session_001", "test_user", {"mode": "assistant"})
    print(f"   Created session: {session['session_id']}")

    print("\n✓ All tests passed!")
