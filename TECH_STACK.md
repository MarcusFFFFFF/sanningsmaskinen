# Sanningsmaskinen — Tech Stack

> Epistemiskt analysverktyg för journalister och myndigheter.  
> Testar konkurrerande hypoteser mot evidens. Falsifierar svagare förklaringar.  
> Sanningen favoriserar ingen sida.

---

## Nuvarande stack — Lokal prototyp (v8.18)

### Översikt

```
Användare → Streamlit UI (localhost:8501)
                ↓
           engine.py (pipeline)
          ↙         ↘
   Claude Opus    GPT-4o
   (Anthropic)    (OpenAI)
          ↘         ↙
        normalizer.py
             ↓
        pdf_export.py
             ↓
      Lokal JSON-historik
```

### Komponenter

| Lager | Teknologi | Version | Syfte |
|-------|-----------|---------|-------|
| Frontend | Streamlit | 1.x | UI, inputhantering, resultatvisning |
| Primäranalys | Claude Opus 4 (Anthropic) | claude-opus-4-6 | Hypotesgenerering, auto-rewrite, layers |
| Reality Check | Claude Sonnet 4 (Anthropic) | claude-sonnet-4-6 | Faktaverifiering |
| Kritiker | GPT-4o search preview (OpenAI) | gpt-4o-search-preview | Adversariell kritik, Red Team |
| Pipeline | Python | 3.9 | engine.py, normalizer.py |
| PDF-export | ReportLab | 4.x | Premiumdokument med canvas-rendering |
| Lagring | Lokala JSON-filer | — | Analyshistorik, ingen databas |
| Konfiguration | python-dotenv | — | API-nyckelhantering |
| OS/Plattform | macOS | — | MacBook Air, lokal körning |

### Filstruktur

```
sanningsmaskinen/
├── app.py              # Streamlit UI — rendering, interaktion
├── engine.py           # Analysmotor — pipeline, API-anrop
├── normalizer.py       # Dataparser — strukturerar råsvar
├── pdf_export.py       # PDF-generering — ReportLab
├── history.py          # Lokal JSON-historik
├── .env                # API-nycklar (ej i repo)
└── requirements.txt    # Beroenden
```

### Analysmodell — fem steg

```
Steg 0  Reality Check        Claude Sonnet  Faktaverifiering, E-nivåklassificering
Steg 1  Primäranalys         Claude Opus    Tre hypoteser (H1/H2/H3), ACH-metodik
Steg 2  GPT-4 Kritiker       GPT-4o         Adversariell granskning, källdisciplin
Steg 3  Konfliktanalys       Claude Sonnet  Epistemiska meningsskiljaktigheter
Steg 4  Red Team             GPT-4o         Konkurrerande modell, VERDICT
Steg 5  Auto-rewrite         Claude Opus    Revidering vid KOLLAPSAR/MODIFIERAS
```

### Metodologi

- **ACH** — Analysis of Competing Hypotheses
- **Tre linser** — H1 Strukturell (Waltz), H2 Domestic Politics (Allison), H3 Aktörpsykologi (Jervis)
- **Evidensskala** — E1 (rykten) till E5 (primärkälla)
- **Confidence** — evidensstyrka × log(bevisantal+1) × källkvalitet, normaliserat 0–1
- **Epistemisk prioritering** — mönster före enskilda påståenden, domslut är E5

### Begränsningar i nuvarande setup

- **En användare åt gången** — Streamlit hanterar inte parallella sessioner
- **Lokal körning** — ingen hosting, ingen autentisering
- **Ingen databas** — JSON-filer, ingen sökning eller aggregering
- **Ingen API** — kan inte integreras med externa system
- **Skaltak** — praktiskt omöjligt att nå fler än 2–3 simultana användare

---

## Skalad stack — Produktionsscenario (10 000+ användare)

### Förutsättningar

- Kommersiell produkt, prenumerationsmodell
- Flera simultana användare (journalister, myndigheter, redaktioner)
- Krav på autentisering, datalagring, audit trails
- Möjlighet att anpassa per kund (white label, egna källhierarkier)
- Dataanalytiker som behöver tillgång till aggregerad analysdata

---

### Arkitekturöversikt

```
                    ┌─────────────────────────────┐
                    │         CDN / Edge           │
                    │    (Cloudflare / Vercel)     │
                    └────────────┬────────────────┘
                                 │
                    ┌────────────▼────────────────┐
                    │       React Frontend         │
                    │   (Next.js, Tailwind CSS)    │
                    │   Replaces Streamlit         │
                    └────────────┬────────────────┘
                                 │ HTTPS / WebSocket
                    ┌────────────▼────────────────┐
                    │       API Gateway            │
                    │    (FastAPI / Python)        │
                    │  Auth, rate limiting,        │
                    │  request routing             │
                    └──┬──────────────────┬───────┘
                       │                  │
          ┌────────────▼──┐    ┌──────────▼────────┐
          │  Analysis      │    │  Background       │
          │  Workers       │    │  Job Queue        │
          │  (Ray / Celery)│    │  (Redis / BullMQ) │
          └────────────┬──┘    └──────────┬────────┘
                       │                  │
          ┌────────────▼──────────────────▼────────┐
          │              AI Tier                    │
          │   Claude Opus  │  GPT-4o  │  Fallbacks  │
          │   (Anthropic)  │  (OpenAI)│  (Gemini?)  │
          └────────────────────────────────────────┘
                       │
          ┌────────────▼──────────────────────────┐
          │            Data Layer                  │
          │  PostgreSQL (strukturerad data)        │
          │  Redis (cache, sessions, queues)       │
          │  S3/R2 (PDF-export, bilagor)           │
          │  Elasticsearch (sökbart analysarkiv)  │
          └───────────────────────────────────────┘
                       │
          ┌────────────▼──────────────────────────┐
          │         Analytics / BI                 │
          │  dbt + BigQuery / Snowflake            │
          │  Metabase / Superset (dashboards)      │
          │  för datateam och investerarrapporter  │
          └───────────────────────────────────────┘
```

---

### Komponentval

#### Frontend

| Teknologi | Motivering |
|-----------|------------|
| **Next.js** (React) | SSR/SSG, snabb rendering, bra för SEO och delning av analyser |
| **Tailwind CSS** | Matchar nuvarande design-tokens direkt |
| **WebSocket** | Realtids-streaming av analyspipeline steg-för-steg |
| **Vercel** | Deployment, CDN, edge-funktioner |

#### Backend

| Teknologi | Motivering |
|-----------|------------|
| **FastAPI** (Python) | Behåller Python-ekosystemet, async, automatisk API-dokumentation |
| **Celery + Redis** | Asynkrona jobb — en analys tar 60–120 sek, får inte blockera UI |
| **JWT + OAuth2** | Autentisering, organisationsinloggning (SSO för myndigheter) |

#### Databas

| Teknologi | Användning |
|-----------|-----------|
| **PostgreSQL** | Användare, organisationer, analyser, källgranskningar |
| **Redis** | Sessions, cache för återkommande frågor, jobbkö |
| **S3 / Cloudflare R2** | PDF-export, råtexter, bilagor |
| **Elasticsearch** | Sökbart arkiv — "hitta alla analyser om Iran" |

#### AI-infrastruktur

| Teknologi | Motivering |
|-----------|------------|
| **Anthropic API** | Primär — Claude Opus för analys, Sonnet för snabbare steg |
| **OpenAI API** | GPT-4o för kritiker/Red Team — adversariell mångfald |
| **LLM-router** | Automatisk fallback vid API-avbrott (LiteLLM eller liknande) |
| **Prompt-versionshantering** | LangSmith eller eget system — spåra promptförändringar |

#### Datateam / Analytics

| Teknologi | Användning |
|-----------|-----------|
| **dbt** | Transformationer av analysdata |
| **BigQuery / Snowflake** | Data warehouse — beteende, källkvalitet, frågemönster |
| **Metabase** | Interna dashboards för produkt- och affärsteam |
| **Segment** | Händelsetracking (utan att kompromissa med användarintegritet) |

#### DevOps

| Teknologi | Användning |
|-----------|-----------|
| **GitHub Actions** | CI/CD — tester, deployment |
| **Docker + Kubernetes** | Container-orchestrering vid hög last |
| **Railway / Fly.io** | Enklare hosting-alternativ i tidig skala |
| **Sentry** | Felspårning och prestandaövervakning |

---

### Migrationsväg — Steg för steg

```
Nu          Streamlit lokal → Demo, proof of concept
Fas 1       FastAPI backend + Next.js frontend (ersätter Streamlit)
            PostgreSQL ersätter JSON-filer
            Enkel autentisering (e-post/lösenord)
            Hosting på Railway eller Fly.io

Fas 2       Celery + Redis för asynkrona jobb
            Organisationskonton (redaktioner, myndigheter)
            SSO / SAML för myndighetsintegration
            S3 för PDF-arkiv

Fas 3       Elasticsearch för sökbart analysarkiv
            Analytics-pipeline (dbt + BigQuery)
            White label / API-access för kunder
            Kubernetes för auto-scaling

Fas 4       LLM-router med fallback
            Finjusterade modeller på domänspecifik data
            Realtids-collaboration (flera analytiker per analys)
```

---

### Kostnadsuppskattning vid skala

| Post | Månadskostnad (10k användare) |
|------|-------------------------------|
| Anthropic API (Claude Opus) | ~15 000–40 000 kr |
| OpenAI API (GPT-4o) | ~5 000–15 000 kr |
| Hosting (Fly.io/Railway) | ~3 000–8 000 kr |
| Databas (PostgreSQL + Redis) | ~2 000–5 000 kr |
| S3/R2-lagring | ~500–2 000 kr |
| Totalt | ~25 000–70 000 kr/mån |

> API-kostnaderna dominerar. Caching av återkommande frågor och
> val av rätt modell per steg (Sonnet istället för Opus där möjligt)
> är de viktigaste kostnadsdrivarna att optimera.

---

### Säkerhet och integritet

- Analyser lagras krypterade
- Användare äger sin data — exportmöjlighet och radering
- Ingen träning på kunddata
- Audit trail för myndighetsanvändning (vem körde vad, när)
- GDPR-kompatibel arkitektur från dag ett
- Separata tenant-miljöer vid behov (white label)

---

### Vad som inte förändras vid skalning

Kärnmekaniken förblir oförändrad:

- ACH-metodiken (tre linser, falsifieringstest)
- Evidensskalan E1–E5
- Red Team-strukturen
- Den epistemiska prioriteringsregeln (mönster före enskilda påståenden)
- Källhierarkin med geografisk anpassning

Det är metodologin som är produkten — tekniken är bäraren.

---

*Sanningsmaskinen — sanningen favoriserar ingen sida.*
