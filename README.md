# ZZP Administratie Pro - Next.js 16

Uitvoering van je gevraagde 5 vervolgstappen:
1. NextAuth credentials login basis
2. Factuur aanmaak met regels + BTW 21/9/0
3. E-mail verzending (nodemailer) + WhatsApp deeplink endpoint
4. Google Calendar integratie foundation (OAuth client helper + agenda API)
5. BTW kwartaalrapportage pagina

## Snelle setup
```bash
npm install
cp .env.example .env.local
npx prisma migrate dev --name init
npx prisma generate
npm run dev
```

## Nieuwe kernroutes
- `/login`
- `/dashboard`
- `/dashboard/klanten`
- `/dashboard/facturen`
- `/dashboard/facturen/nieuw`
- `/dashboard/agenda`
- `/dashboard/rapporten`

## API
- `POST /api/facturen` (aanmaken)
- `POST /api/facturen/verstuur` (email/whatsapp)
- `GET/POST /api/agenda`
- `GET/POST /api/inkomen`
- `GET/POST /api/uitgaven`

## Let op
Google OAuth callback + tokenopslag en volledige NextAuth sessiebeveiliging over alle routes zijn voorbereid maar nog niet volledig afgemaakt.
