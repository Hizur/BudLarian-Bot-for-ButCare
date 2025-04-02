# clinic_utils.py
import discord
from discord.ext import commands
from difflib import SequenceMatcher
from utils import get_best_match

async def list_clinics(ctx_or_interaction, clinics_data):
    """Wyświetla listę dostępnych klinik."""
    if not clinics_data:
        if isinstance(ctx_or_interaction, discord.Interaction):
            await ctx_or_interaction.followup.send("Brak dostępnych danych klinik.", ephemeral=True)
        else:
            await ctx_or_interaction.send("Brak dostępnych danych klinik.")
        return

    # Grupujemy kliniki według sieci/sieci
    networks = {}
    for clinic in clinics_data:
        title = clinic.get("title", "Nieznana Klinika")
        
        # Wyciągamy nazwę sieci z tytułu (część przed myślnikiem)
        if " – " in title:
            network_name = title.split(" – ")[0].strip()
        elif " - " in title:
            network_name = title.split(" - ")[0].strip()
        else:
            network_name = "Inne Kliniki"

        if network_name not in networks:
            networks[network_name] = []

        networks[network_name].append(clinic)

    # Tworzymy listę embedów
    embeds = []
    current_embed = None
    current_size = 0
    MAX_EMBED_SIZE = 5800  # Zostawiamy margines bezpieczeństwa

    # Funkcja pomocnicza do tworzenia nowego embeda
    def create_new_embed(title="Dostępne Kliniki Konopne"):
        embed = discord.Embed(
            title=title,
            color=discord.Color.green()
        )
        if title == "Dostępne Kliniki Konopne":
            embed.description = "Lista wszystkich dostępnych klinik konopnych pogrupowana według sieci:"
        return embed

    current_embed = create_new_embed()

    # Dodajemy pola dla każdej sieci klinik
    for network_name, clinics in sorted(networks.items()):
        network_clinics = []
        current_field = ""

        for clinic in clinics:
            address = clinic.get("address", "Brak adresu")
            phone = clinic.get("phone", "Brak telefonu")
            clinic_url = clinic.get("clinic_url", "#")
            
            # Przygotuj wpis dla kliniki
            if address == "N/A":
                address = "Brak informacji o adresie"
                
            city_part = ""
            if " – " in clinic.get("title", ""):
                city_part = clinic.get("title", "").split(" – ")[1].strip()
            elif " - " in clinic.get("title", ""):
                city_part = clinic.get("title", "").split(" - ")[1].strip()
            
            clinic_entry = f"**{city_part}**\n"
            clinic_entry += f"📍 {address}\n"
            clinic_entry += f"📞 {phone}\n"
            clinic_entry += f"🔗 [Link do strony]({clinic_url})\n\n"

            if len(current_field + clinic_entry) > 1000:
                network_clinics.append(current_field)
                current_field = clinic_entry
            else:
                current_field += clinic_entry

        if current_field:
            network_clinics.append(current_field)

        # Dodajemy pola dla sieci klinik
        for i, field_content in enumerate(network_clinics):
            field_name = f"__{network_name}__" if i == 0 else f"__{network_name} (część {i+1})__"
            field_size = len(field_name) + len(field_content)

            # Sprawdzamy, czy dodanie nowego pola nie przekroczy limitu
            if current_size + field_size > MAX_EMBED_SIZE:
                embeds.append(current_embed)
                current_embed = create_new_embed("Dostępne Kliniki Konopne (kontynuacja)")
                current_size = 0

            current_embed.add_field(name=field_name, value=field_content, inline=False)
            current_size += field_size

    embeds.append(current_embed)

    # Dodajemy stopkę do ostatniego embeda
    embeds[-1].set_footer(text="Dane klinik mogą ulec zmianie. Przed wizytą zaleca się kontakt telefoniczny w celu potwierdzenia dostępności i cen.")

    # Wysyłamy wszystkie embedy
    if isinstance(ctx_or_interaction, discord.Interaction):
        for embed in embeds:
            await ctx_or_interaction.followup.send(embed=embed, ephemeral=True)
    else:
        for embed in embeds:
            await ctx_or_interaction.send(embed=embed)

def get_similarity(a, b):
    """Calculate the similarity ratio between two strings."""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def extract_city_from_address(address):
    """Extract city name from address string."""
    if not address or address == "N/A":
        return ""
    
    # Common format: "City, street details"
    if "," in address:
        # Extract the part before the first comma (likely the city)
        parts = address.split(",", 1)
        return parts[0].strip()
    
    # If no comma, try to find city based on common prefixes in Polish addresses
    prefixes = ["ul.", "ul ", "al.", "al ", "os.", "os "]
    for prefix in prefixes:
        if prefix in address.lower():
            # Assume city is before the prefix
            parts = address.lower().split(prefix, 1)
            if parts[0].strip():
                return parts[0].strip().capitalize()
    
    # If no comma or prefix, just return the whole address as we can't reliably extract the city
    return address.strip()

def find_matching_clinics(location_query, clinics_data, threshold=0.65):
    """Find clinics that match the location query with fuzzy matching."""
    if not location_query or not clinics_data:
        return [], False
    
    # Normalize the query
    location_query = location_query.strip().lower()
    
    # Process each clinic to extract city info
    cities = set()
    for clinic in clinics_data:
        # Extract city from address if not already present
        if "city" not in clinic and "address" in clinic:
            city = extract_city_from_address(clinic["address"])
            clinic["city"] = city
            if city:
                cities.add(city)
    
    # First try exact match (case insensitive)
    exact_matches = []
    for clinic in clinics_data:
        address = clinic.get("address", "").lower()
        city = clinic.get("city", "").lower()
        
        # Check if location query is in city name or at the beginning of address
        if (city and location_query in city) or \
           (address.startswith(location_query + ",")) or \
           (address and location_query in address.split(",")[0].strip()):
            exact_matches.append(clinic)
    
    if exact_matches:
        return exact_matches, True  # Return exact matches and flag
    
    # If no exact match, try fuzzy matching with the cities list
    city_list = list(cities)  # Convert set to list for get_best_match
    best_city_match, similarity = get_best_match(location_query, city_list, threshold=threshold)
    
    if best_city_match:
        # Found a fuzzy match for the city
        fuzzy_matches = [clinic for clinic in clinics_data 
                        if clinic.get("city", "").lower() == best_city_match.lower()]
        return fuzzy_matches, False
    
    # If still no match, try direct fuzzy matching on addresses
    fuzzy_matches = []
    for clinic in clinics_data:
        address = clinic.get("address", "")
        city = clinic.get("city", "")
            
        # Only check similarity if we have data to compare
        if city or address:
            # Check similarity with city
            city_similarity = get_best_match(location_query, [city])[1] if city else 0
            
            # Also check first part of address (likely contains city)
            address_part = address.split(",")[0] if address and "," in address else ""
            address_similarity = get_best_match(location_query, [address_part])[1] if address_part else 0
            
            # Use the better match
            best_similarity = max(city_similarity, address_similarity)
            
            if best_similarity >= threshold:
                # Add similarity score to clinic for sorting
                clinic_copy = clinic.copy()
                clinic_copy["similarity"] = best_similarity
                fuzzy_matches.append(clinic_copy)
    
    # Sort fuzzy matches by similarity score, highest first
    fuzzy_matches.sort(key=lambda x: x.get("similarity", 0), reverse=True)
    return fuzzy_matches[:10], False  # Limit results to avoid overwhelming the user

async def get_clinic_info(ctx_or_interaction, location_query, clinics_data, ephemeral=True):
    """Wyświetla informacje o klinikach w danej lokalizacji."""
    matching_clinics, is_exact = find_matching_clinics(location_query, clinics_data)

    if matching_clinics:
        if len(matching_clinics) == 1:
            # Tylko jedna klinika znaleziona
            clinic = matching_clinics[0]
            
            # Get name from title or create a name from address
            clinic_name = clinic.get('title', None)
            if not clinic_name:
                address = clinic.get('address', 'Nieznana lokalizacja')
                clinic_name = f"Klinika - {address}"
                
            embed = discord.Embed(
                title=f"Klinika: {clinic_name}",
                color=discord.Color.green()
            )
            
            # Add a notice if this was a fuzzy match
            if not is_exact:
                embed.description = f"*Pokazuję najbliższe dopasowanie do zapytania '{location_query}'*"
            
            if "city" in clinic and clinic["city"]:
                embed.add_field(name="Miasto", value=clinic["city"], inline=True)
                
            if clinic.get("address"):
                embed.add_field(name="Adres", value=clinic["address"], inline=True)
                
            if clinic.get("phone"):
                embed.add_field(name="Telefon", value=clinic["phone"], inline=True)
                
            if clinic.get("email"):
                embed.add_field(name="Email", value=clinic["email"], inline=True)
                
            if clinic.get("website") or clinic.get("clinic_url"):
                website_url = clinic.get("website") or clinic.get("clinic_url", "#")
                embed.add_field(name="Strona WWW", value=f"[Kliknij tutaj]({website_url})", inline=True)
                
            if clinic.get("description"):
                embed.add_field(name="Opis", value=clinic["description"], inline=False)
                
            if clinic.get("doctors"):
                doctors_text = "\n".join([f"• {doctor}" for doctor in clinic["doctors"]])
                embed.add_field(name="Lekarze", value=doctors_text, inline=False)
                
            if isinstance(ctx_or_interaction, commands.Context):
                await ctx_or_interaction.send(embed=embed)
            else:
                await ctx_or_interaction.followup.send(embed=embed, ephemeral=ephemeral)
        else:
            # Wiele klinik znalezionych
            if is_exact:
                response_text = f"Znaleziono {len(matching_clinics)} klinik w '{location_query}':\n\n"
            else:
                response_text = f"Znaleziono {len(matching_clinics)} klinik podobnych do '{location_query}':\n\n"
                
            for i, clinic in enumerate(matching_clinics):
                # Get name from title or create a name from address
                clinic_name = clinic.get('title', None)
                if not clinic_name:
                    address = clinic.get('address', 'Nieznana lokalizacja')
                    city = extract_city_from_address(address)
                    clinic_name = f"Klinika w {city}" if city else f"Klinika - {address}"
                
                response_text += f"**{i + 1}. {clinic_name}**\n"
                
                if clinic.get("address"):
                    response_text += f"   📍 {clinic['address']}\n"
                    
                if clinic.get("phone"):
                    response_text += f"   📞 {clinic['phone']}\n"
                    
                website_url = clinic.get("website") or clinic.get("clinic_url")
                if website_url:
                    response_text += f"   🔗 [Strona WWW]({website_url})\n"
                    
                response_text += "\n"
                
            if isinstance(ctx_or_interaction, commands.Context):
                await ctx_or_interaction.send(response_text)
            else:
                await ctx_or_interaction.followup.send(response_text, ephemeral=ephemeral)
    else:
        message = f"Nie znaleziono klinik w lokalizacji '{location_query}'. Spróbuj wpisać nazwę miasta lub sprawdź pisownię."
        if isinstance(ctx_or_interaction, commands.Context):
            await ctx_or_interaction.send(message)
        else:
            await ctx_or_interaction.followup.send(message, ephemeral=ephemeral)

async def list_all_clinics(ctx_or_interaction, clinics_data, ephemeral=True):
    """Wyświetla listę wszystkich dostępnych klinik."""
    if not clinics_data:
        message = "Brak dostępnych danych o klinikach."
        if isinstance(ctx_or_interaction, commands.Context):
            await ctx_or_interaction.send(message)
        else:
            await ctx_or_interaction.followup.send(message, ephemeral=True)
        return

    # Process and organize clinics by city
    cities = {}
    for clinic in clinics_data:
        # Extract city from address if not already present
        address = clinic.get("address", "")
        
        # Get city either from title or from address
        city = None
        title = clinic.get("title", "")
        if title:
            # Try to extract city from title (often in format "Network - City")
            if " - " in title:
                city = title.split(" - ")[1].strip()
            elif " – " in title:
                city = title.split(" – ")[1].strip()
        
        # If city not found in title, extract from address
        if not city and address:
            city = extract_city_from_address(address)
            
        # If still no city, try to parse first part of address
        if not city and address and "," in address:
            city = address.split(",")[0].strip()
        
        # Default if we couldn't extract a city
        if not city:
            city = "Inna lokalizacja"
        
        # Add to cities dictionary
        if city not in cities:
            cities[city] = []
        cities[city].append(clinic)

    # Create embeds for the grouped clinics
    embeds = []
    current_embed = None
    current_size = 0
    MAX_EMBED_SIZE = 5800  # Leave safety margin

    # Helper function to create a new embed
    def create_new_embed(title="Dostępne Kliniki Konopne"):
        embed = discord.Embed(
            title=title,
            color=discord.Color.green()
        )
        if title == "Dostępne Kliniki Konopne":
            embed.description = "Lista dostępnych klinik pogrupowana według miast:"
        return embed

    current_embed = create_new_embed()

    # Add fields for each city
    for city, clinics in sorted(cities.items()):
        city_clinics = []
        current_field = ""

        for clinic in clinics:
            # Get clinic name from title or network name
            clinic_name = None
            title = clinic.get('title', '')
            
            if title:
                if " – " in title:
                    network = title.split(" – ")[0].strip()
                    clinic_name = f"{network} ({city})"
                elif " - " in title:
                    network = title.split(" - ")[0].strip()
                    clinic_name = f"{network} ({city})"
                else:
                    clinic_name = title
            
            # If still no name, create one from address
            if not clinic_name:
                address = clinic.get('address', 'Nieznany adres')
                if address != "N/A":
                    # Get the street part if possible
                    if "," in address:
                        street = address.split(",", 1)[1].strip()
                        clinic_name = f"Klinika - {street}"
                    else:
                        clinic_name = f"Klinika - {address}"
                else:
                    clinic_name = "Klinika (brak adresu)"
            
            # Format clinic entry
            clinic_entry = f"**{clinic_name}**\n"
            
            if clinic.get("address") and clinic.get("address") != "N/A":
                clinic_entry += f"📍 {clinic['address']}\n"
            
            if clinic.get("phone") and clinic.get("phone") != "N/A":
                clinic_entry += f"📞 {clinic['phone']}\n"
            
            website_url = clinic.get("website") or clinic.get("clinic_url")
            if website_url:
                clinic_entry += f"🔗 [Strona WWW]({website_url})\n"
                
            clinic_entry += "\n"

            # Check if adding this clinic would exceed field size
            if len(current_field + clinic_entry) > 1000:
                city_clinics.append(current_field)
                current_field = clinic_entry
            else:
                current_field += clinic_entry

        if current_field:
            city_clinics.append(current_field)

        # Add fields for the city
        for i, field_content in enumerate(city_clinics):
            field_name = f"__{city}__" if i == 0 else f"__{city} (część {i+1})__"
            field_size = len(field_name) + len(field_content)

            # Check if adding the new field would exceed the limit
            if current_size + field_size > MAX_EMBED_SIZE:
                embeds.append(current_embed)
                current_embed = create_new_embed("Dostępne Kliniki Konopne (kontynuacja)")
                current_size = 0

            current_embed.add_field(name=field_name, value=field_content, inline=False)
            current_size += field_size

    # Add footer to the last embed
    if embeds or current_embed:
        if current_embed:
            current_embed.set_footer(text="Dane klinik mogą ulec zmianie. Przed wizytą zaleca się kontakt telefoniczny.")
            embeds.append(current_embed)

    # Send all embeds
    if isinstance(ctx_or_interaction, commands.Context):
        for embed in embeds:
            await ctx_or_interaction.send(embed=embed)
    else:
        for embed in embeds:
            await ctx_or_interaction.followup.send(embed=embed, ephemeral=ephemeral)
