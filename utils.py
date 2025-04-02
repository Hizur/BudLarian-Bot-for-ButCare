# utils.py
import discord
import asyncio
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import os

async def send_long_message(channel, text, chunk_size=1900, ephemeral=False):
    """Breaks a long message into chunks and sends them."""
    chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
    for chunk in chunks:
        if hasattr(channel, 'followup') and hasattr(channel.followup, 'send'):
            # This is an Interaction
            await channel.followup.send(chunk, ephemeral=ephemeral)
        else:
            # This is a regular channel
            await channel.send(chunk)

def get_best_match(user_input, valid_options, threshold=0.8):
    """
    Finds the best match for the user input from a list of valid options using fuzzy matching.
    
    Args:
        user_input (str): The input provided by the user.
        valid_options (list): A list of valid strings to match against.
        threshold (float): The minimum similarity ratio to consider a match.
    
    Returns:
        tuple: (best_match, similarity) - The best matching option and its similarity score if a match is found, 
               otherwise (None, 0)
    """
    if not user_input or not valid_options:
        return None, 0.0
        
    user_input = user_input.lower()
    
    # First check for exact matches (case-insensitive)
    for option in valid_options:
        if user_input == option.lower():
            return option, 1.0
    
    # Use fuzzywuzzy for more robust matching
    best_match, score = process.extractOne(
        user_input, 
        valid_options,
        scorer=lambda x, y: max(
            fuzz.token_set_ratio(x, y),  # Handles word order differences
            fuzz.partial_ratio(x, y)     # Handles substring matches
        )
    )
    
    # Normalize score to 0-1 range
    similarity = score / 100.0
    
    return (best_match, similarity) if similarity >= threshold else (None, 0.0)

def ensure_file_exists(filepath, default_content="[]"):
    """
    Ensures that a file exists. If it doesn't, creates it with default content.
    
    Args:
        filepath (str): The path to the file.
        default_content (str): The default content to write if the file is missing.
    """
    if not os.path.exists(filepath):
        print(f"WARNING: File {filepath} does not exist. Creating it with default content.")
        with open(filepath, 'w') as f:
            f.write(default_content)