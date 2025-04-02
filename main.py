import asyncio
import os
import shutil
from bot import client
import logging

logger = logging.getLogger('budcare_bot.main')

async def main():
    # Delete the problematic basic_commands.py file if it exists
    commands_dir = os.path.join(os.path.dirname(__file__), 'commands')
    basic_commands_path = os.path.join(commands_dir, 'basic_commands.py')
    
    if os.path.exists(basic_commands_path):
        try:
            # Create backup first
            backup_path = basic_commands_path + '.bak'
            shutil.copy2(basic_commands_path, backup_path)
            os.remove(basic_commands_path)
            print(f"Removed problematic file {basic_commands_path} (backup at {backup_path})")
        except Exception as e:
            print(f"Warning: Could not remove {basic_commands_path}: {e}")
    
    # Run the bot
    async with client:
        await client.start('TWÓJ_TOKEN_BOTA')  # This will be overridden by the actual token in config.py

if __name__ == '__main__':
    asyncio.run(main())
