# ZZP Administratie Pro - Next.js 16

Je vroeg expliciet om een professioneel pakket volgens je Next.js/Prisma-plan. Deze repo is daarom omgezet naar een moderne webapp-structuur met visuele dashboardstijl.

## Opgeleverd in deze iteratie
- Next.js 16 + TypeScript projectstructuur
- Prisma schema (User, Klant, Factuur, FactuurRegel, Offerte, Inkomen, Uitgave, Categorie, Afspraak, Uurregistratie)
- Dashboard-layout met visuele cards/gradient UI (niet meer basic)
- Pagina's voor Dashboard, Klanten, Facturen, Agenda, Rapporten, Instellingen
- API-routes basis voor klanten, facturen, inkomen, uitgaven, agenda
- Utility libs (`prisma`, `utils`, `whatsapp`)
- `.env.example` voor lokale setup

## Starten
1. Installeer dependencies
```bash
npm install
```
2. Maak env bestand
```bash
cp .env.example .env.local
```
3. Prisma client/migratie
```bash
npx prisma migrate dev --name init
npx prisma generate
```
4. Start app
```bash
npm run dev
```

## Belangrijk
Dit is de **professionele foundation + visuele upgrade** en niet alleen een kleine patch. Volgende commit kan direct doorpakken op:
- NextAuth login flow
- factuur aanmaak/bewerk scherm met regels + BTW 21/9/0
- email verzending (nodemailer)
- Google Calendar OAuth sync
- BTW kwartaalrapportage en bankimport
