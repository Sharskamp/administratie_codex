# ZZP Administratie Pro (Windows)

Professionele lokale administratie-app voor zzp'ers op Windows.

## Wat nu is opgeleverd
- Uitgebreide administratie modules: klanten, agenda, facturen, inkomsten, uitgaven en dashboard.
- Facturatie:
  - Factuurnummers per jaar (`INV-YYYY-00001`)
  - Facturen bouwen vanuit meerdere afspraken
  - BTW, subtotaal en totaalberekening
  - Statusflow (`concept`, `bevestigd`, `verzonden`, `betaald`)
  - Verzenden via e-mail (`mailto`) en WhatsApp (`wa.me`)
  - CSV-export van facturen
- Inkomsten:
  - Koppeling aan facturen
  - Auto-match op factuurnummer in omschrijving
- Uitgaven:
  - Categorieën, leverancier, bedragen excl/incl btw, bonbestand
- Instellingen:
  - Bedrijfsgegevens, BTW, Google OAuth pad (voorbereid), SMTP velden
- Beheer & betrouwbaarheid:
  - Database migraties voor oudere lokale databases
  - Backup maken en herstel in de UI
  - Logging naar `app.log`

## Starten op Windows
1. Installeer Python 3.11+
2. Open terminal in de projectmap
3. Start:

```bash
python admin_windows_app.py
```

## Bestanden
- Database: `admin_data.db`
- Backups: `backups/`
- Logs: `app.log`

## Volgende fase (nog te bouwen)
- Echte Google Calendar OAuth + event sync
- PDF-facturen + echte SMTP verzending met bijlagen
- Bank CSV import wizard per bankformaat
- Automatische herinneringen op vervaldatum
- .exe installer met auto-update
