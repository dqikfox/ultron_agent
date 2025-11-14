import sqlite3
from datetime import datetime
import json

class AvatarDatabase:
    def __init__(self):
        self.conn = sqlite3.connect('avatars.db')
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        """Create the avatar table if it does not exist."""
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS avatars (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                class TEXT NOT NULL,
                race TEXT NOT NULL,
                level INTEGER NOT NULL,
                stats TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.conn.commit()

    def create_avatar(self, data):
        """Insert a new avatar into the database."""
        try:
            self.cursor.execute('''
                INSERT INTO avatars (name, class, race, level, stats) VALUES (?, ?, ?, ?, ?)
            ''', (data['name'], data['class'], data['race'], data['level'], json.dumps(data['stats'])))
            self.conn.commit()
            return self.get_avatar(self.cursor.lastrowid)
        except Exception as e:
            self.logger.error(f"Failed to create avatar: {e}")
            raise

    def get_avatar(self, id):
        """Retrieve an avatar by its ID."""
        try:
            self.cursor.execute('SELECT * FROM avatars WHERE id = ?', (id,))
            return self.cursor.fetchone()
        except Exception as e:
            self.logger.error(f"Failed to retrieve avatar: {e}")
            raise

    def update_avatar(self, id, data):
        """Update an existing avatar."""
        try:
            # Update stats if provided
            if 'stats' in data:
                data['stats'] = json.dumps(data['stats'])
            self.cursor.execute('''
                UPDATE avatars SET name=?, class=?, race=?, level=?, stats=?, updated_at=? WHERE id=?
            ''', (data['name'], data['class'], data['race'], data['level'], data['stats'], datetime.now(), id))
            self.conn.commit()
            return self.get_avatar(id)
        except Exception as e:
            self.logger.error(f"Failed to update avatar: {e}")
            raise

    def delete_avatar(self, id):
        """Remove an existing avatar."""
        try:
            self.cursor.execute('DELETE FROM avatars WHERE id = ?', (id,))
            self.conn.commit()
            return True
        except Exception as e:
            self.logger.error(f"Failed to delete avatar: {e}")
            raise

    def list_avatars(self, filters):
        """List avatars with optional filters."""
        try:
            # Convert filters dictionary to SQL WHERE clause
            where_clause = ' AND '.join([f"{k} = ?" for k in filters.keys()])
            
            if where_clause:
                self.cursor.execute(f"SELECT * FROM avatars WHERE {where_clause}", list(filters.values()))
            else:
                self.cursor.execute('SELECT * FROM avatars')
            
            return [self._format_avatar(row) for row in self.cursor.fetchall()]
        except Exception as e:
            self.logger.error(f"Failed to list avatars: {e}")
            raise

    def get_leaderboard(self, limit=10):
        """Get the top avatars by level/stats."""
        try:
            # SQL query to order by level and stats in descending order
            self.cursor.execute('SELECT * FROM avatars ORDER BY level DESC, stats DESC LIMIT ?', (limit,))
            return [self._format_avatar(row) for row in self.cursor.fetchall()]
        except Exception as e:
            self.logger.error(f"Failed to get leaderboard: {e}")
            raise

    def _format_avatar(self, row):
        """Format the avatar data for display."""
        stats = json.loads(row[5])
        return {
            'id': row[0],
            'name': row[1],
            'class': row[2],
            'race': row[3],
            'level': row[4],
            'stats': stats,
            'created_at': row[6],
            'updated_at': row[7]
        }

    def __del__(self):
        """Close the database connection."""
        self.conn.close()

# Usage example:
if __name__ == "__main__":
    avatar_db = AvatarDatabase()
    
    # Create a new avatar
    new_avatar = {'name': 'John Doe', 'class': 'Warrior', 'race': 'Human', 'level': 1, 'stats': {'health': 100}}
    created_avatar = avatar_db.create_avatar(new_avatar)
    print(f"Created Avatar: {created_avatar}")

    # Retrieve the avatar by ID
    retrieved_avatar = avatar_db.get_avatar(created_avatar['id'])
    print(f"Retrieved Avatar: {retrieved_avatar}")

    # Update the avatar
    updated_avatar = {'level': 2}
    avatar_db.update_avatar(created_avatar['id'], updated_avatar)
    print(f"Updated Avatar: {avatar_db.get_avatar(created_avatar['id'])}")

    # Delete the avatar
    deleted = avatar_db.delete_avatar(created_avatar['id'])
    print(f"Deleted Avatar: {deleted}")

    # List avatars with filters
    filtered_avatars = avatar_db.list_avatars({'level': 1})
    print("Filtered Avatars:", filtered_avatars)

    # Get leaderboard
    leaderboard = avatar_db.get_leaderboard()
    print("Leaderboard:", leaderboard)