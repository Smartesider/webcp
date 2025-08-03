# webcp
Simple FastAPI/HTML based WebCP

Her kommer den fullstendige, kompromissløse og grundige programbeskrivelsen for ditt hosting-dashboard-prosjekt — inkludert **alle funksjoner, låser, sikkerhetskrav og detaljer** vi har diskutert i denne chatten. Dette er skrevet med tanke på at GitHub Copilot i VS Code skal kunne generere koden helt identisk, uten problemer eller unntak.

---

# FULLSTENDIG PROGRAMBESKRIVELSE FOR HOSTING-DASHBOARD

---

## 1. OVERORDNET FORMÅL

Et sikkert, robust og modulært webhosting-administrasjonsdashboard med:

* **Frontend:** Utelukkende statiske HTML- og JS-filer i `/home/skycode.no/public_html/cp/` (med separate områder for admin, bruker, login)
* **Backend:** FastAPI-applikasjon som kjører på port **8098**, eksponert via Nginx som proxy på `https://cp.skycode.no/api/v1`
* **Sikkerhet:** Strenge låser og valideringer som sikrer at kun angitte porter, kataloger, API-endepunkter og formater brukes
* **Funksjoner:** Full kontroll over Nginx vhosts, MariaDB-databaser, e-postkontoer, portvakt, firewall, certbot SSL-håndtering, GitHub-integrasjon, systemovervåkning, statistikk og mer
* **Automatisering:** Robust backup, rollback, testing og varsling i alle kritiske operasjoner
* **Brukerroller:** Admin og bruker med tydelig rollebasert tilgangskontroll
* **Utviklingsverktøy:** Integrert med moderne VS Code extensions og CI/CD pipelines for kvalitetssikring

---

## 2. KATALOGSTRUKTUR OG FILPLACERING

```
/home/skycode.no/public_html/cp/
├── index.html                   # Felles login-side (brukere og admin)
/home/skycode.no/public_html/cp/admin/
├── index.html                   # Admin-dashboard
├── vhost.html                  # Admin vhost-oppsett
├── db.html                     # Admin databasebrukeroppsett
├── mail.html                   # E-postadministrasjon
├── portvakt.html               # Port- og tjenesteoversikt
├── firewall.html               # UFW firewall-kontroll
├── certbot.html                # SSL-sertifikat administrasjon
├── github.html                 # GitHub repo management
├── overvaking.html             # Systemovervåkning og statistikk
└── ...                        # Flere adminsider med relevante funksjoner
/home/skycode.no/public_html/cp/bruker/
├── index.html                   # Kunde-login og brukerpanel
```

---

## 3. FRONTEND-KRAV

* **Statisk HTML + JS som KUN kommuniserer med `https://cp.skycode.no/api/v1` via port 8098**
* **Ingen kall til andre porter, domener eller IP-adresser tillatt** (låses hardt i backend og frontend)
* **Streng CORS-policy backend:** Kun tillatt origin `https://cp.skycode.no`
* **Alle API-kall forventer og håndterer utelukkende JSON-svar**
* **Frontend må validere brukerrolle før sensitive sider vises** (f.eks. admin vs bruker)
* **Frontend håndterer feilmeldinger ved feil responsformat** — logg og vis feilmelding, ikke fallback til andre kall
* **Alle sensitive handlinger i frontend krever gyldig JWT-token med riktige rettigheter**
* **Frontend UI skal være responsiv og brukervennlig** med sidepanel, søkefelt, varslinger og grafiske dataoversikter (se GUI-detaljer lenger ned)

---

## 4. BACKEND - FASTAPI SPESIFIKASJONER

### API BASE URL:

* `https://cp.skycode.no:8098/api/v1`

### VIKTIGE LÅSER I KODE:

* **Kun port 8098 skal brukes for all API-trafikk.**
* **Streng validering av `Host` header og CORS for kun `cp.skycode.no` tillatelse.**
* **API-endepunkter SKAL bare svare i JSON.**
* **Alle filoperasjoner må kun skje innenfor `/home/skycode.no/public_html/cp/` og underliggende kataloger.**
* **Alle systemendringer (vhost, DB, mail, firewall, certbot) må utføres med eksklusiv fil- eller DB-lås.**
* **Rollback må alltid trigges ved feil i destruktive operasjoner.**
* **Autentisering må være på plass på alle endepunkter — admin og brukerroller separert.**
* **Inputvalidering på alle parametere for å hindre injection og sikkerhetshull.**
* **Portkontroll skal nekte bruk av porter utenfor 8000-8099, spesielt reservert port 8098.**

### MODULER OG FUNKSJONER:

* **vhost\_admin:** Opprettelse, redigering, sletting, syntaksvalidasjon, reload av Nginx
* **mariadb\_admin:** DB og brukeropprettelse, passordendring, sletting, ressursovervåking
* **mail\_admin:** Kontoopprettelse, sletting, IMAP/SMTP verifisering, kvoter, spamfilter
* **portvakt:** Oversikt over aktive porter (8000-8099), tjenestestatus, varsler, konfliktdeteksjon
* **firewall\_admin:** UFW-regler opprettelse, sletting, logging, Fail2Ban-integrasjon
* **certbot\_admin:** SSL-sertifikat opprettelse, fornyelse, wildcard-støtte, rollback, varsling
* **github\_admin:** Repo-opprettelse, status, webhook, pull request-overvåking
* **systemovervaking:** CPU, RAM, disk, nettverk, logganalyse, varsler
* **auth:** JWT/OAuth2 med rollebasert kontroll og 2FA (valgfritt)
* **logging:** Detaljert logging av alle endringer, rollback og varslinger

### KOMMENTARER OG INSTRUKSJONER I KODE:

* Hver funksjon skal ha kommentarer som tydeliggjør krav til port, katalog og format.
* Eksempelkommentar i funksjon som starter server:

  ```python
  # LOCK: Server must only listen on port 8098.
  # DO NOT open any other ports for API access.
  # API responses must be JSON only.
  ```
* Ved filoperasjoner:

  ```python
  # LOCK: File operations must be limited to /home/skycode.no/public_html/cp/ hierarchy only.
  # Backup must be created before any destructive change.
  ```
* Ved API kall:

  ```python
  # LOCK: Validate request origin is https://cp.skycode.no only.
  # Validate JWT and user roles.
  ```

---

## 5. NGINX-KONFIGURASJON (KORT UTDYPNING FOR KOPILOT)

```nginx
server {
    listen 8098 ssl http2;
    server_name cp.skycode.no;

    ssl_certificate /etc/letsencrypt/live/cp.skycode.no/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/cp.skycode.no/privkey.pem;

    location /api/v1/ {
        proxy_pass http://127.0.0.1:8098/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /cp/ {
        root /home/skycode.no/public_html/;
        try_files $uri $uri/ =404;
    }
}
```

---

## 6. FRONTEND-UTVIKLING (KRAV)

* Bruk kun statisk HTML + JavaScript (ES6+) uten server-side rendering.
* API-kall skal alltid gå til `https://cp.skycode.no/api/v1/...` med fetch/Axios.
* Inkluder funksjonalitet for login, token-lagring (f.eks. localStorage), rollebasert sidevisning.
* GUI skal være responsivt og brukervennlig (se GUI-detaljer nedenfor).
* Alle sensitive handlinger skal kreve gyldig JWT-token.
* Frontend må validere alle input før sending til backend.

---

## 7. GUI - MODERNE BRUKERVENNLIG DESIGN (INNKLUDERT I PROGRAM)

* Dashboard med statuskort for server, tjenester, SSL, firewall, ressursbruk, varsler
* Responsivt design for desktop og mobil
* Sidepanel med kategorier: Vhost, Database, Mail, Portvakt, Firewall, Certbot, GitHub, Overvåking
* Søkefunksjon for rask filtrering
* Interaktive grafer for ressursbruk
* Trinnvise veivisere for komplekse operasjoner (f.eks. ny vhost)
* Varslingspanel for system- og feilvarsler
* Integrert API Explorer (Swagger UI)
* Inline validering og popup-varsler ved feil

---

## 8. AUTENTISERING OG ROLLESTYRING

* Bruk JWT-tokens med tilgangsroller (admin, bruker)
* Mulighet for to-faktor-autentisering (valgfritt)
* Token valideres ved hvert API-kall
* Ugyldige eller utløpte tokens avvises med klar JSON-feilmelding

---

## 9. BACKUP, ROLLBACK OG FEILHÅNDTERING

* Backup tas alltid før destruktive endringer på filer og DB
* Maks 5 backup-versjoner lagres
* Ved feil i operasjon, automatisk rollback til siste backup
* Feil returneres som JSON med struktur `{ "error": "...", "rollback": true }`
* Logging av alle operasjoner, feil og rollback med tidsstempel

---

## 10. CI/CD, TEST OG KVALITETSSIKRING

* Automatisert testing av låser på port, kataloger, JSON-respons
* Statisk kodeanalyse i pipeline (f.eks. flake8, mypy, bandit)
* PR-blokkering ved brudd på låser eller feil
* Automatisk generering og lukking av bugs i GitHub via pre-commit hooks og workflows
* Automatisk testkjøring og rapportering av testresultater via GitHub Actions

---

## 11. LISTE OVER ALLE FUNKSJONER (FULLT)

**Nginx vhost:** Opprett, endre, slett, syntaks-test, reload, SSL-validasjon, redirect-sjekk, portkonfliktkontroll, gzip/brotli, caching, logging, rate-limiting.

**MariaDB:** Opprett DB og bruker, endre passord, slett, brukertilganger, overvåk ressursbruk, sikkerhetskopiering, indekser, logging.

**E-post:** Opprett konto, rediger passord, slett, IMAP/SMTP verifisering, alias, spamfiltrering, kø-status, kvoter, logging.

**Portvakt:** Liste porter (8000-8099), tjenestestatus, konfliktdeteksjon, trafikklogging, healthchecks, varsler.

**Firewall:** UFW-regler, legg til/slett, logging, fail2ban-integrasjon, geo-IP blokkering, varsling, historikk.

**Certbot:** SSL-sertifikat opprettelse, fornyelse, wildcard, rollback, varsling, kjede-sjekk, https-tester.

**GitHub:** Repo opprettelse, status, webhook, pull request overvåking, git-kommandoer, logging.

**Systemovervåking:** CPU, minne, disk, nettverk, logganalyse, varsler, statistikk.

**Bruker og roller:** Autentisering, JWT, 2FA, rollebasert tilgang.

**Backup og rollback:** Automatisk backup, versjonskontroll, automatisk rollback.

**Frontend:** Login, token-håndtering, rollebasert UI, statiske filer, API-kall til fast endpoint.

---

## 12. INSTRUKSJONER TIL COPILOT FOR FILER OG STRUKTUR

* Alle sensitive data (porter, kataloger, API URL) skal leses fra en sentral `config.py` med **kommentar om at disse IKKE skal endres uten godkjenning**.
* All koding skal følge strenge inline-kommentarer som minner om låser (port 8098, katalog `/home/skycode.no/public_html/cp/`, JSON-respons, kun FastAPI backend).
* Backupfunksjoner må være modulære og brukes i alle destruktive operasjoner.
* En låsemodul (`lock_enforcer.py`) skal importeres og brukes i alle moduler som gjør systemendringer.
* API må aldri akseptere kall fra andre domener eller porter, og returnere klart feilsvar i JSON ved brudd.
* Alle filendringer skal først ta backup, og rollback trigges ved feil.
* Logger skrives med tidsstempel og lagres i tilgjengelig katalog for visning i dashboard.
* Nginx-konfigurasjon og certbot håndteres via dedikerte moduler som implementerer sikkerhets- og rollbackrutiner.
* Frontend må kun kalle API via fast URL, og all kommunikasjon skal validere token og user role.

---

## 13. MANGELSVURDERING

Etter gjennomgang er **ingen funksjoner utelatt**. Alle tidligere diskusjoner, funksjoner og sikkerhetskrav er innarbeidet.

---

# Oppsummering

Dette dokumentet er en komplett guide, med alle nødvendige regler, låser, funksjoner og detaljer, utformet for at Copilot eller hvilken som helst AI-kodegenerator skal kunne implementere prosjektet nøyaktig som planlagt — med full sikkerhet og robusthet.

---


# SKYCODE.NO HOSTING DASHBOARD

## VIKTIGE SIKKERHETSREGLER OG LÅSER

- ALLE nettverksservere MÅ KUN bruke port **8098** for API-trafikk.  
- API-baseurl skal alltid være: `https://cp.skycode.no/api/v1`  
- Alle API-responser SKAL være i JSON-format.  
- Alle filoperasjoner må begrenses til `/home/skycode.no/public_html/cp/`.  
- Alle endringer i kritiske filer skal ta backup FØR modifikasjon.  
- Operasjoner som påvirker systemet SKAL ha eksklusiv låsing og rollback ved feil.  
- Endringer som bryter disse reglene vil kunne føre til øyeblikkelig rollback og potensielt blokkering av commit.  
- Enhver omgåelse eller endring av disse reglene uten godkjenning anses som kritisk sikkerhetsbrudd.

**Dette er ikke et valg. Det er krav.**

---

## KODEKVALITET

- Kommenter all kode med `# LOCK:` kommentarer for å minne om regler.  
- Følg strenge PEP8, typehint og sikkerhetsstandarder.  
- Test alt via CI før merge.

---

Les og forstå disse før du bidrar i prosjektet.
