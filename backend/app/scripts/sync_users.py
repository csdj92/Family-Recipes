import httpx
import asyncio
from sqlalchemy import create_engine, text
from sqlalchemy.exc import IntegrityError
import logging
from ..config import get_settings
from ..models.user import UserRole  # Import the UserRole enum

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()

async def fetch_supabase_users():
    """Fetch all users from Supabase Auth"""
    headers = {
        'apikey': settings.SUPABASE_KEY,
        'Authorization': f'Bearer {settings.ADMIN_SECRET_KEY}'
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f'{settings.SUPABASE_URL}/auth/v1/admin/users',
            headers=headers
        )
        response.raise_for_status()
        return response.json()

def sync_user(connection, user_data):
    """Sync a single user to the application's users table"""
    try:
        # Extract user information
        user_id = user_data['id']
        email = user_data['email']
        name = user_data.get('raw_user_meta_data', {}).get('name', email)
        is_verified = user_data.get('email_confirmed_at') is not None
        
        # Check if user exists
        result = connection.execute(
            text('SELECT id FROM users WHERE id = :user_id'),
            {'user_id': user_id}
        ).fetchone()
        
        if result is None:
            # Insert new user
            connection.execute(
                text('''
                    INSERT INTO users (id, email, name, role, is_verified)
                    VALUES (:id, :email, :name, :role, :is_verified)
                '''),
                {
                    'id': user_id,
                    'email': email,
                    'name': name,
                    'role': UserRole.MEMBER.value,  # Use the correct enum value
                    'is_verified': is_verified
                }
            )
            logger.info(f'Created new user record for {email}')
        else:
            # Update existing user
            connection.execute(
                text('''
                    UPDATE users
                    SET email = :email,
                        name = :name,
                        is_verified = :is_verified
                    WHERE id = :id
                '''),
                {
                    'id': user_id,
                    'email': email,
                    'name': name,
                    'is_verified': is_verified
                }
            )
            logger.info(f'Updated existing user record for {email}')
            
    except IntegrityError as e:
        logger.error(f'Error syncing user {email}: {str(e)}')
    except Exception as e:
        logger.error(f'Unexpected error syncing user {email}: {str(e)}')

async def main():
    try:
        # Fetch all Supabase users
        logger.info('Fetching users from Supabase...')
        supabase_users = await fetch_supabase_users()
        
        # Create database engine
        engine = create_engine(settings.DATABASE_URL)
        
        # Sync each user
        with engine.connect() as connection:
            with connection.begin():
                for user in supabase_users:
                    sync_user(connection, user)
        
        logger.info('User sync completed successfully')
        
    except Exception as e:
        logger.error(f'Sync failed: {str(e)}')
        raise

if __name__ == '__main__':
    asyncio.run(main()) 