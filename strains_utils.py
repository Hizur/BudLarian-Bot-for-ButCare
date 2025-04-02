# strains_utils.py
import discord
from discord.ext import commands
from utils import get_best_match
from difflib import SequenceMatcher
from fuzzywuzzy import fuzz

# Mapa producentów i ich słów kluczowych (małe litery, bez spacji do porównania)
PRODUCER_KEYWORDS = {
    "Four20 Pharma": ["four20pharma", "four20", "four 20 pharma"],
    "S-LAB": ["s-lab", "slab"],
    "Tilray": ["tilray"],
    "Aurora": ["aurora"],
    "Canopy Growth": ["canopygrowth", "canopy"],
    "CanPoland": ["canpoland"],
    "COSMA": ["cosma"],
    "Polfarmex": ["polfarmex"],
    "ODI Pharma": ["odipharma", "odi pharma", "odi"],
    "Cantourage": ["cantourage"],
    "Medezin": ["medezin"],
    "Spectrum Therapeutics": ["spectrum", "spectrum therapeutics" , "Spectrum Therapeutics"],
}

DEFAULT_PRODUCER = "Inni Producenci"

def detect_producer(product_name):
    """Wykrywa nazwę producenta na podstawie nazwy produktu, używając PRODUCER_KEYWORDS."""
    if not product_name:
        return DEFAULT_PRODUCER

    # Normalizacja nazwy produktu dla łatwiejszego porównania
    normalized_product_name = ''.join(filter(str.isalnum, product_name.lower()))

    for producer_name, keywords in PRODUCER_KEYWORDS.items():
        if any(keyword in normalized_product_name for keyword in keywords):
            return producer_name

    return DEFAULT_PRODUCER

def get_similarity(a, b):
    """Calculate the similarity ratio between two strings."""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def normalize_strain_name(name):
    """
    Normalize strain names to handle common variations in capitalization,
    spacing, and special characters.
    """
    if not name:
        return ""
    
    # Convert to lowercase
    normalized = name.lower()
    
    # Replace special characters with standard format
    normalized = normalized.replace("#", " # ")
    
    # Handle various separators
    normalized = normalized.replace("-", " ")
    normalized = normalized.replace("_", " ")
    
    # Normalize spaces
    normalized = " ".join(normalized.split())
    
    # Specific known variations
    replacements = {
        "gg4": "gorilla glue # 4",
        "gg #4": "gorilla glue # 4",
        "gorilla glue": "gorilla glue # 4",  # If this is always the same strain
    }
    
    for key, value in replacements.items():
        if normalized == key:
            normalized = value
    
    return normalized

def find_matching_strains(query, strains_data, threshold=0.8):
    """Find strains that match the query with fuzzy matching."""
    if not query or not strains_data:
        return [], False
        
    # Normalize the query
    query = normalize_strain_name(query)
    
    # First try exact match (case insensitive)
    exact_matches = [strain for strain in strains_data if normalize_strain_name(strain["strain_name"]) == query]
    if exact_matches:
        return exact_matches, True  # Return exact matches and a flag indicating exact match

    # Get all strain names for fuzzy matching
    strain_names = [normalize_strain_name(strain["strain_name"]) for strain in strains_data]
    
    # Try fuzzy matching with all strain names
    best_match, similarity = get_best_match(query, strain_names, threshold=threshold)
    
    if best_match:
        # If we found a good match, return all strains with that exact name
        matched_strains = [strain for strain in strains_data if normalize_strain_name(strain["strain_name"]) == best_match]
        return matched_strains, False
    
    # If still no match, try advanced fuzzy matching approach
    fuzzy_matches = []
    for strain in strains_data:
        strain_name = normalize_strain_name(strain["strain_name"])
        
        # Calculate multiple types of fuzzy matches
        token_set_ratio = fuzz.token_set_ratio(query, strain_name) / 100.0
        partial_ratio = fuzz.partial_ratio(query, strain_name) / 100.0
        
        # Use the best match score
        best_similarity = max(token_set_ratio, partial_ratio)
        
        if best_similarity >= threshold:
            # Add similarity score to strain for sorting
            strain_copy = strain.copy()
            strain_copy["similarity"] = best_similarity
            fuzzy_matches.append(strain_copy)
    
    if fuzzy_matches:
        # Sort fuzzy matches by similarity score, highest first
        fuzzy_matches.sort(key=lambda x: x.get("similarity", 0), reverse=True)
        return fuzzy_matches[:10], False  # Limit results to avoid overwhelming the user
    
    # No matches found
    return [], False

async def get_strain_info(ctx_or_interaction, nazwa_odmiany, strains_data, ephemeral=False):
    """Pobiera i wyświetla informacje o odmianie (lub odmianach)."""
    matching_strains, is_exact = find_matching_strains(nazwa_odmiany, strains_data)

    if matching_strains:
        if len(matching_strains) == 1:
            strain = matching_strains[0]
            strain_info_embed = discord.Embed(
                title=f"Informacje o Odmianie: {strain['strain_name']}",
                color=discord.Color.green()
            )
            
            if not is_exact:
                strain_info_embed.description = f"*Pokazuję najbliższe dopasowanie do '{nazwa_odmiany}'*"
            
            # Format availability with emoji like in list_strains
            availability = strain['availability']
            availability_emoji = "🟢" if availability.lower() == "wysoka" else "🔴" if availability.lower() in ["brak", "wycofany"] else "⚪"
            
            strain_info_embed.add_field(name="Nazwa Produktu", value=strain['product_name'], inline=False)
            strain_info_embed.add_field(name="Typ", value=strain['strain_type'], inline=True)
            strain_info_embed.add_field(name="Zawartość THC", value=strain['thc_content'], inline=True)
            strain_info_embed.add_field(name="Zawartość CBD", value=strain['cbd_content'], inline=True)
            strain_info_embed.add_field(name="Dostępność", value=f"{availability_emoji} {availability}", inline=False)
            strain_info_embed.add_field(name="Dowiedz się więcej", value=f"[Kliknij Tutaj]({strain['strain_url']})", inline=False)
            
            # Add legend like in list_strains
            strain_info_embed.add_field(
                name="Legenda",
                value="🟢 Wysoka dostępność | ⚪ Brak informacji | 🔴 Brak/Wycofany",
                inline=False
            )

            if isinstance(ctx_or_interaction, commands.Context):
                await ctx_or_interaction.send(embed=strain_info_embed)
            else:
                await ctx_or_interaction.followup.send(embed=strain_info_embed, ephemeral=ephemeral)
        else:
            # Create embed for multiple strain results
            matches_embed = discord.Embed(
                title=f"Znalezione Odmiany dla: '{nazwa_odmiany}'",
                color=discord.Color.green()
            )
            
            if not is_exact:
                matches_embed.description = f"Nie znaleziono dokładnego dopasowania dla '{nazwa_odmiany}'. Czy chodziło Ci o jedną z tych odmian?"
            else:
                matches_embed.description = f"Znaleziono wiele odmian o nazwie '{nazwa_odmiany}'. Wybierz jedną z poniższych:"
            
            # Group by producer using the centralized helper function
            producers = {}
            for strain in matching_strains:
                # Use the new helper function to detect producer
                producer = detect_producer(strain['product_name'])
                    
                if producer not in producers:
                    producers[producer] = []
                    
                availability = strain.get('availability', 'Brak informacji')
                availability_emoji = "🟢" if availability.lower() == "wysoka" else "🔴" if availability.lower() in ["brak", "wycofany"] else "⚪"
                
                producers[producer].append({
                    'strain': strain,
                    'availability_emoji': availability_emoji
                })
            
            # Add fields for each producer
            for producer, strains in sorted(producers.items()):
                strain_list = ""
                for strain_info in strains:
                    strain = strain_info['strain']
                    emoji = strain_info['availability_emoji']
                    strain_list += f"{emoji} **{strain['strain_name']}** - {strain['product_name']} (THC: {strain['thc_content']}, CBD: {strain['cbd_content']})\n"
                    strain_list += f"   [Więcej info]({strain['strain_url']})\n"
                
                matches_embed.add_field(name=f"__{producer}__", value=strain_list, inline=False)
            
            # Add legend
            matches_embed.set_footer(text="🟢 Wysoka dostępność | ⚪ Brak informacji | 🔴 Brak/Wycofany")

            if isinstance(ctx_or_interaction, commands.Context):
                await ctx_or_interaction.send(embed=matches_embed)
            else:
                await ctx_or_interaction.followup.send(embed=matches_embed, ephemeral=ephemeral)
    else:
        # Create embed for no results
        not_found_embed = discord.Embed(
            title=f"Brak wyników dla: '{nazwa_odmiany}'",
            description=f"Nie znaleziono odmiany '{nazwa_odmiany}' w bazie danych. Spróbuj innej nazwy lub sprawdź pisownię.",
            color=discord.Color.red()
        )
        
        if isinstance(ctx_or_interaction, commands.Context):
            await ctx_or_interaction.send(embed=not_found_embed)
        else:
            await ctx_or_interaction.followup.send(embed=not_found_embed, ephemeral=ephemeral)

def parse_producer_filters(args):
    """
    Parse command arguments to extract producer filters.
    Arguments starting with '-' will be treated as producers to exclude.
    
    Example: ['-tilray', '-slab'] will exclude Tilray and S-LAB producers.
    
    Returns a list of producer names to exclude.
    """
    excluded_producers = []
    
    for arg in args:
        if arg.startswith('-'):
            # Remove the '-' prefix
            producer_key = arg[1:].lower()
            
            # Match with known producers
            for producer_name, keywords in PRODUCER_KEYWORDS.items():
                if producer_key in keywords or producer_key == producer_name.lower().replace(' ', ''):
                    excluded_producers.append(producer_name)
                    break
    
    return excluded_producers

def parse_producer_includes(args):
    """
    Parse command arguments to extract producers to include.
    Arguments starting with '+' will be treated as producers to include (showing only these).
    
    Example: ['+tilray', '+four20'] will show only Tilray and Four20 Pharma producers.
    
    Returns a list of producer names to include.
    """
    included_producers = []
    
    for arg in args:
        if arg.startswith('+'):
            # Remove the '+' prefix
            producer_key = arg[1:].lower()
            
            # Match with known producers
            for producer_name, keywords in PRODUCER_KEYWORDS.items():
                if producer_key in keywords or producer_key == producer_name.lower().replace(' ', ''):
                    included_producers.append(producer_name)
                    break
    
    return included_producers

async def list_strains(ctx_or_interaction, strains_data, ephemeral=False, excluded_producers=None, included_producers=None):
    """Wyświetla listę dostępnych odmian, pogrupowanych według producenta."""
    if not strains_data:
        if isinstance(ctx_or_interaction, commands.Context):
            await ctx_or_interaction.send("Brak dostępnych danych odmian.")
        else:
            await ctx_or_interaction.followup.send("Brak dostępnych danych odmian.", ephemeral=ephemeral)
        return

    # Initialize filter lists if not provided
    if excluded_producers is None:
        excluded_producers = []
    if included_producers is None:
        included_producers = []

    # Group strains by producer using the centralized function
    producers = {}
    for strain in strains_data:
        # Use the helper function to detect producer
        producer = detect_producer(strain['product_name'])
        
        # Skip if producer is in the excluded list
        if producer in excluded_producers:
            continue
            
        # Skip if we're only including specific producers and this one isn't in the list
        if included_producers and producer not in included_producers:
            continue
            
        strain_name = strain.get("strain_name", "Nieznana Odmiana")
        strain_url = strain.get("strain_url", "#")

        if producer not in producers:
            producers[producer] = []

        thc_content = strain.get("thc_content", "N/A")
        cbd_content = strain.get("cbd_content", "N/A")
        availability = strain.get("availability", "Brak informacji")

        # Add strain information
        producers[producer].append({
            'name': strain_name,
            'thc': thc_content,
            'cbd': cbd_content,
            'url': strain_url,
            'availability': availability
        })

    # Create list of embeds with improved logic
    embeds = []
    current_embed = None
    current_size = 0
    MAX_EMBED_SIZE = 5900

    # Helper function to create a new embed
    def create_new_embed(title="Dostępne Odmiany"):
        embed = discord.Embed(
            title=title,
            color=discord.Color.green()
        )
        embed.set_footer(text="🟢 Wysoka dostępność | ⚪ Brak informacji | 🔴 Brak/Wycofany")
        
        description = "Lista odmian pogrupowana według producentów:"
        if included_producers:
            description += f"\n*Pokazani producenci: {', '.join(included_producers)}*"
        if excluded_producers:
            description += f"\n*Wykluczeni producenci: {', '.join(excluded_producers)}*"
        
        embed.description = description
        return embed

    current_embed = create_new_embed()
    current_size += len(current_embed.title) + (len(current_embed.description) if current_embed.description else 0) + 50

    sorted_producer_names = sorted(producers.keys(), key=lambda p: (p == DEFAULT_PRODUCER, p))

    for producer_name in sorted_producer_names:
        strains = producers[producer_name]
        producer_strains_parts = []
        current_field_part = ""

        for strain in sorted(strains, key=lambda x: x['name']):
            availability_emoji = "🟢" if strain['availability'].lower() == "wysoka" else "🔴" if strain['availability'].lower() in ["brak", "wycofany"] else "⚪"

            link_md = f" - [Info]({strain['url']})" if strain['url'] and strain['url'] != "#" else ""

            strain_entry = f"{availability_emoji} **{strain['name']}** (THC: {strain['thc']}, CBD: {strain['cbd']}){link_md}\n"

            if len(current_field_part + strain_entry) > 1024:
                producer_strains_parts.append(current_field_part)
                current_field_part = strain_entry
            else:
                current_field_part += strain_entry

        if current_field_part:
            producer_strains_parts.append(current_field_part)

        for i, field_content in enumerate(producer_strains_parts):
            field_name = f"{producer_name}" if i == 0 else f"{producer_name} (cz. {i+1})"
            field_size = len(field_name) + len(field_content)

            if current_size + field_size > MAX_EMBED_SIZE:
                embeds.append(current_embed)
                current_embed = create_new_embed("Dostępne Odmiany (kontynuacja)")
                current_size = len(current_embed.title) + (len(current_embed.description) if current_embed.description else 0) + 50

            current_embed.add_field(name=field_name, value=field_content, inline=False)
            current_size += field_size

    if current_embed.fields or not embeds:
        embeds.append(current_embed)

    if isinstance(ctx_or_interaction, commands.Context):
        for embed in embeds:
            await ctx_or_interaction.send(embed=embed)
    else:
        first_message = True
        for embed in embeds:
            if first_message and not ctx_or_interaction.response.is_done():
                try:
                    await ctx_or_interaction.response.send_message(embed=embed, ephemeral=ephemeral)
                except discord.InteractionResponded:
                    await ctx_or_interaction.followup.send(embed=embed, ephemeral=ephemeral)
                first_message = False
            else:
                await ctx_or_interaction.followup.send(embed=embed, ephemeral=ephemeral)