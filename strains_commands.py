# strains_commands.py
import discord
from discord import app_commands
from strains_utils import get_strain_info, list_strains, parse_producer_filters, parse_producer_includes

def register_strain_commands(client, tree, strains_data):
    """Registers strain-related commands."""

    @client.command(name="odmiana", help="Wyświetla informacje o danej odmianie.")
    async def odmiana_prefix(ctx, *, nazwa_odmiany: str = None):
        if nazwa_odmiany is None:
            await ctx.send("Proszę podać nazwę odmiany. Użyj: `!odmiana [nazwa odmiany]`")
            return
            
        # Clean up the input a bit
        nazwa_odmiany = nazwa_odmiany.strip()
        if not nazwa_odmiany:
            await ctx.send("Proszę podać poprawną nazwę odmiany. Użyj: `!odmiana [nazwa odmiany]`")
            return
            
        await get_strain_info(ctx, nazwa_odmiany, strains_data, ephemeral=False)

    @client.command(name="listaodmian", help="Wyświetla listę wszystkich dostępnych odmian. Użyj: -producent (aby wykluczyć), +producent (aby pokazać tylko określonych producentów).")
    async def listaodmian_prefix(ctx, *args):
        # Parse args to extract producers to exclude or include
        excluded_producers = parse_producer_filters(args)
        included_producers = parse_producer_includes(args)
        
        # Only one filtering mode can be active at once
        if excluded_producers and included_producers:
            await ctx.send("Błąd: Nie możesz używać filtrów wykluczających (-) i włączających (+) jednocześnie. Wybierz jeden rodzaj filtrowania.")
            return
        
        await list_strains(ctx, strains_data, ephemeral=False, 
                          excluded_producers=excluded_producers, 
                          included_producers=included_producers)

    @tree.command(name="odmiana", description="Wyświetla informacje o danej odmianie.")
    async def odmiana_command(interaction: discord.Interaction, nazwa_odmiany: str):
        try:
            await interaction.response.defer(ephemeral=True)
            nazwa_odmiany = nazwa_odmiany.strip()
            if not nazwa_odmiany:
                await interaction.followup.send("Proszę podać poprawną nazwę odmiany.", ephemeral=True)
                return
                
            await get_strain_info(interaction, nazwa_odmiany, strains_data, ephemeral=True)
        except Exception as e:
            print(f"Error in /odmiana: {e}")
            # Try to recover if possible
            try:
                await interaction.followup.send("Wystąpił błąd podczas przetwarzania komendy. Spróbuj ponownie.", ephemeral=True)
            except:
                print("Failed to send error message")

    @tree.command(name="listaodmian", description="Wyświetla listę dostępnych odmian.")
    @discord.app_commands.describe(
        wyklucz="Opcjonalnie: Lista producentów do wykluczenia (np. 'tilray slab')",
        pokaz="Opcjonalnie: Lista producentów do pokazania (np. 'four20 cantourage')"
    )
    async def listaodmian_command(interaction: discord.Interaction, wyklucz: str = None, pokaz: str = None):
        try:
            await interaction.response.defer(ephemeral=True)
            
            excluded_producers = []
            included_producers = []
            
            if wyklucz and pokaz:
                await interaction.followup.send("Błąd: Nie możesz używać parametrów 'wyklucz' i 'pokaz' jednocześnie. Wybierz jeden rodzaj filtrowania.", ephemeral=True)
                return
                
            if wyklucz:
                # Split by spaces and add '-' prefix to match the parse_producer_filters format
                args = [f"-{producer.strip()}" for producer in wyklucz.split() if producer.strip()]
                excluded_producers = parse_producer_filters(args)
            
            if pokaz:
                # Split by spaces and add '+' prefix to match the parse_producer_includes format
                args = [f"+{producer.strip()}" for producer in pokaz.split() if producer.strip()]
                included_producers = parse_producer_includes(args)
                
            await list_strains(interaction, strains_data, ephemeral=True,
                              excluded_producers=excluded_producers,
                              included_producers=included_producers)
        except Exception as e:
            print(f"Error in /listaodmian: {e}")
            try:
                await interaction.followup.send("Wystąpił błąd podczas przetwarzania komendy. Spróbuj ponownie.", ephemeral=True)
            except:
                print("Failed to send error message")

    @tree.command(name="odmiany", description="Wyświetla listę wszystkich dostępnych odmian.")
    async def odmiany_command(interaction: discord.Interaction):
        try:
            await interaction.response.defer(ephemeral=True)
            await list_strains(interaction, strains_data, ephemeral=True)
        except Exception as e:
            print(f"Error in /odmiany: {e}")
            try:
                await interaction.followup.send("Wystąpił błąd podczas przetwarzania komendy. Spróbuj ponownie.", ephemeral=True)
            except:
                print("Failed to send error message")