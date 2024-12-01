import sys
import os

# Add the parent directory to Python path so we can import from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.scripts.sync_users import main
import asyncio

if __name__ == '__main__':
    asyncio.run(main()) 