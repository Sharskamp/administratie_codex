# ZZP Administratie Pro - Windows Desktop (Optie 1)

Je keuze **Optie 1** is uitgevoerd: de Next.js applicatie is nu verpakt als Windows desktop-app via Electron.

## Fase A — Windows verpakking ✅
- Electron desktop-shell toegevoegd (`electron/main.js`).
- Desktop dev-run toegevoegd (`npm run desktop:dev`).
- Windows installer buildscript toegevoegd (`npm run desktop:build`) via `electron-builder` (NSIS).
- Productnaam ingesteld op **ZZP Administratie Pro**.

## Fase B — Lokale data/offline basis ✅
- Bestaande Prisma + SQLite setup blijft lokaal op de machine.
- `.env.local` + SQLite (`DATABASE_URL=file:./dev.db`) blijft ondersteund.
- Uploads blijven lokaal in `public/uploads`.

## Fase C — Productervaring ✅
- Desktop venster met vaste minimumgrootte en verborgen menubalk.
- Eén applicatievenster zoals native Windows software.

---

## Installeren en testen op Windows

### 1) Dependencies installeren
```bash
npm install
```

### 2) Environment instellen
```bash
copy .env.example .env.local
```

### 3) Database initialiseren
```bash
npx prisma migrate dev --name init
npx prisma generate
```

### 4) Desktop app in development starten
```bash
npm run desktop:dev
```
Dit start Next.js en opent daarna automatisch de Windows app-shell.

### 5) Windows installer bouwen (.exe)
```bash
npm run desktop:build
```
Installer output vind je in `dist/`.

---

## Handige scripts
- `npm run dev` → webmodus
- `npm run desktop:dev` → desktop devmodus
- `npm run desktop:build` → Windows installer bouwen
- `npm run desktop:start` → Electron direct starten
