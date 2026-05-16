# ZZP Administratie Pro (Windows MVP+)

Deze versie is een veel bruikbaardere basis voor een zzp'er op Windows.

## Wat zit erin
- Klantbeheer met uitgebreidere klantdata.
- Agenda/afspraken met uren en tarief.
- Facturen met:
  - Jaar-gebaseerde factuurnummers (`INV-YYYY-00001`)
  - Meerdere factuurregels vanuit geselecteerde afspraken
  - BTW-berekening
  - Statusflow (`concept`, `bevestigd`, `verzonden`, `betaald`)
  - E-mail (`mailto`) en WhatsApp (`wa.me`) verzending
  - CSV-export per factuur
- Inkomstenregistratie met handmatige koppeling + auto-match op factuurnummer in omschrijving.
- Uitgavenregistratie met categorieën, leverancier, BTW en bonbestand.
- Dashboard met omzet, uitgaven, resultaat, betaald/openstaand.
- Instellingen met bedrijfsgegevens en Google OAuth pad (voorbereid op Calendar-koppeling).

## Starten op Windows
1. Installeer Python 3.11+
2. Open terminal in de projectmap
3. Start:

```bash
python admin_windows_app.py
```

## Data en backup
- Data staat lokaal in `admin_data.db`.
- Maak regelmatig backup van dit bestand.

## Volgende stap (fase 2)
- Echte Google Calendar OAuth en events ophalen.
- Event->factuur wizard met bevestig/plan verzendmoment.
- PDF-facturen met layout + automatische e-mail bijlage.
- Bank CSV import met slimmere matching op bedrag + referentie.

## Naar .exe bouwen
Met PyInstaller (later):
```bash
pip install pyinstaller
pyinstaller --noconsole --onefile --name ZZPAdministratie admin_windows_app.py
```
