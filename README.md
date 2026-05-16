# Administratie Software voor Windows (MVP)

Lokale desktopapp (Python + Tkinter + SQLite) voor administratie.

## Functionaliteiten
- Klantbeheer
- Afspraken registreren
- Facturen opstellen op basis van afspraken
- Facturen versturen via e-mail (`mailto:`) of WhatsApp (`wa.me`)
- Inkomsten registreren en koppelen aan facturen
- Uitgaven registreren met categorie en bon-pad
- Rapportage van inkomsten, uitgaven en saldo
- Basis-instellingen voor Google account-koppeling (voorbereid op latere OAuth/sync)

## Starten op Windows
1. Installeer Python 3.11 of nieuwer.
2. Open Command Prompt in deze map.
3. Start de applicatie:

```bash
python admin_windows_app.py
```

## Notities
- De Google Calendar synchronisatie is voorbereid in instellingen en database, maar in deze MVP nog handmatig via afspraken.
- WhatsApp verzending gebruikt de gratis `wa.me` deep-link fallback.
- Data wordt lokaal opgeslagen in `admin_data.db`.

## Volgende iteratie (aanbevolen)
- Google OAuth + echte Calendar event sync
- PDF factuurgeneratie
- SMTP verzending met bijlage
- Bank CSV import + automatische matching
- Build naar `.exe` met PyInstaller
