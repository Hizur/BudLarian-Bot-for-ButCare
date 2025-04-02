# Bud-Larian Discord Bot

Bot to narzędzie stworzone do zarządzania informacjami o klinikach konopnych oraz odmianach medycznej marihuany. Bot umożliwia użytkownikom wyszukiwanie informacji o klinikach, odmianach oraz ich dostępności.

## Funkcje

- **Informacje o klinikach**: Wyświetlanie szczegółowych informacji o klinikach konopnych w Polsce.
- **Lista klinik**: Grupowanie klinik według miast lub sieci.
- **Informacje o odmianach**: Wyświetlanie szczegółowych informacji o odmianach medycznej marihuany, takich jak zawartość THC/CBD, typ odmiany i dostępność.
- **Lista odmian**: Grupowanie odmian według producentów z możliwością filtrowania.

## Wymagania

- Python 3.8 lub nowszy
- Zainstalowane zależności z pliku `requirements.txt`

## Instalacja

1. Sklonuj repozytorium:
   ```bash
   git clone https://github.com/your-repo/CannabisClinicBot.git
   cd CannabisClinicBot
   ```

2. Zainstaluj wymagane zależności:
   ```bash
   pip install -r requirements.txt
   ```

3. Utwórz własny plik konfiguracyjny:
   ```bash
   cp config_example.py config.py
   ```

4. Skonfiguruj plik `config.py`:
   - Wprowadź swój token bota Discord w zmiennej `BOT_TOKEN`.
   - Opcjonalnie skonfiguruj inne ustawienia, takie jak `TEST_GUILD_ID` czy `LOG_LEVEL`.

5. Utwórz pliki danych (jeśli nie istnieją):
   - Stwórz puste pliki JSON lub użyj przykładowych plików:
   ```bash
   echo "[]" > strains_alt.json
   echo "[]" > clinic_data.json
   ```

6. Uruchom bota:
   ```bash
   python bot.py
   ```

## Pliki

- **`bot.py`**: Główny plik uruchamiający bota.
- **`config.py`**: Plik konfiguracyjny zawierający ustawienia bota.
- **`clinic_commands.py`**: Komendy związane z klinikami.
- **`strains_commands.py`**: Komendy związane z odmianami.
- **`utils.py`**: Funkcje pomocnicze.
- **`clinic_data.json`**: Dane o klinikach.
- **`strains_alt.json`**: Dane o odmianach.

## Komendy

### Komendy tekstowe (prefix `!`)

- `!klinika [lokalizacja]`: Wyświetla informacje o klinikach w podanej lokalizacji.
- `!listaklinik`: Wyświetla listę wszystkich dostępnych klinik.
- `!odmiana [nazwa odmiany]`: Wyświetla informacje o danej odmianie.
- `!listaodmian`: Wyświetla listę wszystkich dostępnych odmian.

### Komendy slash (`/`)

- `/klinika [lokalizacja]`: Wyświetla informacje o klinikach w podanej lokalizacji.
- `/listaklinik`: Wyświetla listę wszystkich dostępnych klinik.
- `/odmiana [nazwa odmiany]`: Wyświetla informacje o danej odmianie.
- `/listaodmian`: Wyświetla listę wszystkich dostępnych odmian.

## Logowanie

Logi bota są zapisywane w katalogu `logs` w pliku `bot.log`.

## Rozwój projektu

1. Sklonuj repozytorium
2. Stwórz własny plik konfiguracyjny oparty o `config_example.py`
3. Zaimplementuj swoje zmiany
4. Przetestuj funkcjonalność na swoim serwerze testowym
5. Wyślij Pull Request z opisem zmian

## Uwagi

- Przed uruchomieniem bota upewnij się, że pliki `clinic_data.json` i `strains_alt.json` istnieją i zawierają poprawne dane.
- W przypadku problemów z synchronizacją komend, upewnij się, że bot ma odpowiednie uprawnienia na serwerze Discord.

## Licencja

Projekt jest dostępny na licencji MIT.
