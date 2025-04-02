# clinic_commands.py
import discord
from discord.ext import commands
from clinic_utils import get_clinic_info, list_all_clinics

def register_clinic_commands(client, tree, clinics_data):
    """Rejestruje komendy związane z klinikami."""

    @client.command(name="klinika", help="Wyświetla informacje o klinikach w podanej lokalizacji.")
    async def klinika_prefix(ctx, *, lokalizacja: str = None):
        if lokalizacja is None:
            await ctx.send("Proszę podać lokalizację kliniki. Użyj: `!klinika [nazwa miasta]`")
            return
            
        # Clean up the input
        lokalizacja = lokalizacja.strip()
        if not lokalizacja:
            await ctx.send("Proszę podać poprawną lokalizację. Użyj: `!klinika [nazwa miasta]`")
            return
            
        await get_clinic_info(ctx, lokalizacja, clinics_data, ephemeral=False)

    @client.command(name="listaklinik", help="Wyświetla listę wszystkich dostępnych klinik.")
    async def listaklinik_prefix(ctx):
        await list_all_clinics(ctx, clinics_data, ephemeral=False)

    @tree.command(name="listaklinik", description="Wyświetla listę wszystkich dostępnych klinik.")
    async def listaklinik_command(interaction: discord.Interaction):
        try:
            await interaction.response.defer(ephemeral=True)
            await list_all_clinics(interaction, clinics_data, ephemeral=True)
        except Exception as e:
            print(f"Error in /listaklinik: {e}")
            try:
                await interaction.followup.send("Wystąpił błąd podczas przetwarzania komendy. Spróbuj ponownie.", ephemeral=True)
            except:
                print("Failed to send error message")

    @tree.command(name="klinika", description="Wyświetla informacje o klinikach w podanej lokalizacji.")
    async def klinika_command(interaction: discord.Interaction, lokalizacja: str):
        try:
            await interaction.response.defer(ephemeral=True)
            await get_clinic_info(interaction, lokalizacja, clinics_data, ephemeral=True)
        except Exception as e:
            print(f"Error in /klinika: {e}")
            try:
                await interaction.followup.send("Wystąpił błąd podczas przetwarzania komendy. Spróbuj ponownie.", ephemeral=True)
            except:
                print("Failed to send error message")

