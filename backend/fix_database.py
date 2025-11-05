#!/usr/bin/env python3
"""
Database schema fix script to add missing OCR fields to SQLite database.
This script adds the columns that were created in the 002_ocr_fields migration.
"""
import sqlite3
import sys
from pathlib import Path

def fix_database_schema():
    """Add missing OCR fields to the claims table."""
    
    db_path = Path("claims_dev.db")
    if not db_path.exists():
        print(f"❌ Database file not found: {db_path}")
        return False
    
    try:
        # Connect to SQLite database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if the columns already exist
        cursor.execute("PRAGMA table_info(claims)")
        columns = [column[1] for column in cursor.fetchall()]
        
        print(f"📋 Current columns in claims table: {columns}")
        
        # Add missing columns if they don't exist
        columns_to_add = [
            ("ocr_confidence_score", "FLOAT"),
            ("ocr_processed_at", "DATETIME"),
            ("requires_human_review", "BOOLEAN NOT NULL DEFAULT 0")
        ]
        
        for column_name, column_type in columns_to_add:
            if column_name not in columns:
                try:
                    sql = f"ALTER TABLE claims ADD COLUMN {column_name} {column_type}"
                    cursor.execute(sql)
                    print(f"✅ Added column: {column_name}")
                except sqlite3.Error as e:
                    print(f"⚠️  Error adding column {column_name}: {e}")
        
        # Create index for requires_human_review if it doesn't exist
        try:
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS ix_claims_requires_human_review 
                ON claims (requires_human_review)
            """)
            print("✅ Created index: ix_claims_requires_human_review")
        except sqlite3.Error as e:
            print(f"⚠️  Error creating index: {e}")
        
        # Commit changes
        conn.commit()
        
        # Verify the changes
        cursor.execute("PRAGMA table_info(claims)")
        new_columns = [column[1] for column in cursor.fetchall()]
        print(f"📋 Updated columns in claims table: {new_columns}")
        
        conn.close()
        print("✅ Database schema updated successfully!")
        return True
        
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Fixing database schema...")
    success = fix_database_schema()
    sys.exit(0 if success else 1)