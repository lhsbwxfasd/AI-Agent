"""
SQLite3 replacement for ChromaDB compatibility
ChromaDB requires sqlite3 >= 3.35.0, but Windows Python 3.8 may have older version.
This module checks sqlite3 version and provides guidance.
"""
import sys

try:
    # Try to import pysqlite3
    from pysqlite3 import dbapi2 as sqlite3
    
    # Replace the system sqlite3 module
    sys.modules["sqlite3"] = sqlite3
    
    print(f"Using pysqlite3 (sqlite3 version: {sqlite3.sqlite_version})")
except ImportError:
    # Fall back to system sqlite3
    import sqlite3
    
    # Check version
    version = sqlite3.sqlite_version
    version_tuple = tuple(map(int, version.split('.')))
    
    if version_tuple < (3, 35, 0):
        print(f"WARNING: sqlite3 version {version} is below 3.35.0")
        print("ChromaDB 0.4.x requires sqlite3 >= 3.35.0")
        print("SOLUTION: Using chromadb 0.3.21 which is compatible with older sqlite3")
    else:
        print(f"Using system sqlite3 (version: {version})")
