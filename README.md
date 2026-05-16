# ZZP Administratie Pro - Next.js 16

Deze iteratie voert de **volgende 10 stappen** uit richting een professioneel pakket:

1. Dashboard route-groep en layout volledig gemaakt
2. KPI dashboardpagina toegevoegd
3. Inkomstenmodule pagina toegevoegd
4. Uitgavenmodule pagina toegevoegd
5. Offertemodule + offerte→factuur conversie API toegevoegd
6. Urenregistratie overzichtspagina toegevoegd
7. Factuur printpagina (`/dashboard/facturen/[id]/print`) toegevoegd
8. Categorie API toegevoegd
9. Upload API toegevoegd voor bonnetjesbestanden
10. Bankimport + herinneringen API endpoints toegevoegd

## Setup
```bash
npm install
cp .env.example .env.local
npx prisma migrate dev --name init
npx prisma generate
npm run dev
```

## Belangrijkste routes
- `/login`
- `/dashboard`
- `/dashboard/klanten`
- `/dashboard/facturen`
- `/dashboard/facturen/nieuw`
- `/dashboard/facturen/[id]/print`
- `/dashboard/offertes`
- `/dashboard/agenda`
- `/dashboard/inkomen`
- `/dashboard/uitgaven`
- `/dashboard/uren`
- `/dashboard/rapporten`

## Belangrijkste API's
- `GET/POST /api/klanten`
- `GET/POST /api/facturen`
- `POST /api/facturen/verstuur`
- `GET/POST /api/offertes` (+ `?convert=<id>`)
- `GET/POST /api/agenda`
- `GET/POST /api/inkomen`
- `GET/POST /api/uitgaven`
- `GET/POST /api/categorieen`
- `POST /api/upload`
- `POST /api/bankimport`
- `GET /api/herinneringen`
