# CLAUDE.md — Timbre musical de Vedruna Escorial Vic

> Aquest document és el traspàs complet d'una conversa amb Claude (claude.ai) on es va dissenyar i construir aquest projecte del 9 al 18 d'octubre de 2026. Llegeix-lo sencer abans de tocar res: explica el **perquè** de cada decisió, no només el què. Continua la feina com si haguessis estat a la conversa.

---

## 0. Com treballar amb en Pol (llegeix primer)

- **Usuari:** en Pol, mestre de primària a **Vedruna Escorial Vic** (Vic, Catalunya) i responsable de comunicació de l'escola. Té bon nivell tècnic (fa apps amb Claude, Google Sheets + Apps Script, GitHub Pages), però **no és electricista**: tot el que sigui 230 V ho ha de fer l'instal·lador.
- **Idioma:** parla-li en **català**. Totes les interfícies, missatges i textos d'usuari, en català.
- **Git (norma fixa):** a l'inici de cada sessió fes `git pull`. En acabar cada canvi complet, fes `git commit` + `git push` **sense que t'ho demani**.
  - **Fusionar a `main` també ho fas tu (autoritzat per en Pol el 18/10):** si treballes en una branca, en acabar cada canvi provat obre el pull request contra `main` i **fusiona'l tu mateix**, sense esperar-lo. La Raspberry s'actualitza des de `main`. Només ho deixes obert si en Pol demana revisar-lo abans o si les proves no passen.
- **Convencions de desenvolupament:** mobile-first, en català, **sense frameworks pesats** (HTML/CSS/JS pur i Python estàndard).
- **Disseny:** el pes màxim de lletra és **Bold (700)**. **Mai Black/900**: ho ha demanat diverses vegades perquè perjudica la llegibilitat.
- **Colors corporatius** (extrets del logo oficial de l'escola, `docs/logo-vedruna-escorial-vic.png`): granat **`#810023`** i vermell **`#E0003F`**. El logo és un "check" de dos traços (curt vermell + llarg granat) amb el text "**Vedruna** Escorial Vic".
- **Prefereix crítica honesta** a l'afalac. Si una idea seva té un problema, digues-li.
- Vol veure **resultats reals** (captures, proves executades), no descripcions d'arquitectura.
- **Contrasenyes, IP i similars:** no inventis dades de l'escola. Pregunta-les.

---

## 1. El problema original

A l'escola, quan és l'hora d'entrar a l'aula (9 h, pati, 15 h…), sona **una cançó per megafonia a tota l'escola**. El sistema només admet **un pen USB amb una sola cançó**. Això provoca dos problemes:

1. Algú ha d'anar periòdicament a canviar el pen.
2. Sonar sempre la mateixa cançó cansa.

**Objectiu d'en Pol:** un sol suport amb moltes cançons que vagin variant, gestionable fàcilment. Més tard ho va ampliar: una **web** per canviar hores, gestionar cançons i "tota la gestió de la megafonia", i **modes de rotació** (una diferent a cada toc / la mateixa tot el dia / la mateixa tota la setmana). L'estètica ha de seguir els colors corporatius.

---

## 2. L'equip real (fotos a `docs/fotos/`)

Tot és en una prestatgeria de fusta d'una sala de l'escola.

| Foto | Aparell | Notes |
|---|---|---|
| `05-caixa-rellotge-theben.jpg` | **Caixa blanca Merlin Gerin** amb un **relé** (groc), un **contactor Merlin Gerin multi9 CT 16 A 230 V** i un **programador horari digital Theben TR 608 top2 S** (rail DIN, 1 canal, setmanal, 56 memòries, bateria de 10 anys, canvi d'hora automàtic opcional) | És **el cervell actual**: a les hores programades dona corrent. Botons: MENU, OK, ◄, ►. |
| `02-fonestar-fs2900.jpg` | **Fonestar FS-2900** (reproductor MP3 USB/SD de rack) | El reproductor actual, amb un pen. A sobre hi ha l'adhesiu de l'instal·lador: **Llach, tel. 93 850 45 05**. |
| `03-jedia-i-fonestar.jpg` | **JEDIA JPA-1240A** (amplificador de zones amb atenuació) = "**amplificador 1**" | 5 entrades: 1 MICRO (PTT), 2 M. INAL(àmbric) REMOTE, 3 M.EX(terior), 4 i 5 de línia (etiqueta "CD"). 5 zones d'altaveus + ALL CALL. Seccions CHIME, TEL, SIREN, MASTER ("volum general", escrit a mà). LEDs DC / AC / **STAND-BY** (a les fotos, encès en STAND-BY). |
| `04-jedia-i-ampli2-apart-pa240p.jpg` | **Apart PA240P** = "**AMPLI 2**" | **SIRENES D'EMERGÈNCIA. NO TOCAR MAI.** Té cinta adhesiva a l'interruptor de POWER. |
| `01-rack-complet.jpg` | Vista de tot el conjunt | |
| `07-endoll-del-rellotge-fletxa.jpg` | La fletxa vermella assenyala on s'endolla el **transformador del Fonestar**: un endoll que **surt directament de la caixa del rellotge** (només té corrent quan el rellotge activa) | Al costat hi ha una **regleta blanca amb endolls lliures i corrent permanent**. També hi ha una **connexió amb regletes de borns i cables marrons sobre la fusta, sense caixa** (probablement el contacte del relé que engega l'ampli). S'ha recomanat que **no es toqui** i que l'instal·lador la tanqui en una caixeta. |
| `06-protocol-paret.jpg` | Protocol penjat a la paret | Vegeu la transcripció a sota. |
| `08-darrere-fonestar-i-jedia.jpg` (21/10) | **Darrere del Fonestar i del JEDIA** | Fonestar: entrada DC 12 V 0,5 A, **interruptor AUTOPLAY MODE: RANDOM / STANDARD** (ja era a RANDOM; vegeu la nota de la secció 3) i sortides **RCA R/L**. El cable RCA del Fonestar va a la secció **LINE IN** (RCA) del darrere del JEDIA. El JEDIA també té PRE OUT, REC (RCA) i entrades MIC/LINE combo (XLR/jack) amb GAIN. A la foto no es veu clar si queda un parell LINE IN lliure. |

### Transcripció del protocol de la paret

> **PROTOCOL APARELL DE MÚSICA I EMERGÈNCIES SIRENA.**
>
> **VACANCES I DIES ESPORÀDICS DE FESTA:** Desendollar l'interruptor de la pared. Té un rellotge que no perd memòria!
>
> **CAIXA BLANCA DEL RELLOTGE:** Només manipular-la per canviar l'hora d'estiu a hivern i a l'inrevés. Si s'adelanta o retarda amb freqüència caldrà canviar el rellotge intern. Té una vida útil de cinc anys.
>
> **MEGAFONIA: Musica i micros.** Música i Micros van amb l'amplificador 1. Per posar música fora de l'horari programat cal apretar "power" de l'amplificador.
> Tres micros: micro taula (peu blanc), funciona apretant la tecla del micro; micro inal·làmbric, funciona connectant el "jac" que està solt a l'emisora del micro (caixa cartró blanca) que ha d'estar connectada al corrent. El micro s'ha de posar la pila i treure-la abans d'endreçar-lo; micro exterior: per connectar a la farola de les pistes.
>
> **FAROLA:** té una connexió per instal·lar un micro amb fil i també la emisora del micro inal·lambric si tenim un allargis pel corrent. És la primera farola de la rampa al costat de les escales d'entrada a la pista la que té la connexió.
>
> **SINERES EMERGÈNCIA:** Les sirenes interiors i exteriors van amb l'**amplificador 2**.
> **AMPLIFICADOR 2. NO TOCAR-LO MAI!** Sempre ha d'estar encès. Hem posat cinta adhesiva a l'interruptor.

### Com funciona el sistema actual (deduït i comprovat)

1. El **Theben** activa una sortida a les hores programades.
2. Aquesta sortida **alimenta l'endoll del Fonestar** i, segons el protocol, **treu el JEDIA de standby**. Fora d'horari cal prémer POWER del JEDIA per tenir so. Això encara **no està verificat al 100 %**: cal mirar si el LED del JEDIA passa de STAND-BY a encès en un toc real.
3. El Fonestar s'engega en rebre corrent i reprodueix el pen **des de la pista 1**.
4. Quan el rellotge talla, s'apaga tot.

---

## 3. Proves fetes a l'aparell amb en Pol (15/10/2026)

| Prova | Resultat |
|---|---|
| Prémer POWER del Fonestar fora d'horari | **No s'encén.** Només té corrent quan el rellotge activa. |
| Activació manual del Theben: MENU → MANUAL → OVERRIDE | Va servir per donar corrent i fer les proves. **Cal cancel·lar l'override** després, o es queda engegat. |
| Modes del botó REPEAT del Fonestar | Només **REPEAT (una)**, **REPEAT ALBUM** i **REPEAT ALL**. **No té mode aleatori.** |
| Prova de memòria: es posa la pista 02, es talla el corrent amb el rellotge i es torna a donar | **Torna a sonar la pista 1.** No recorda la posició. |

**Conclusió:** amb el Fonestar és impossible fer rotar les cançons. Cal substituir-lo com a font de música.

> **Nota del 21/10:** al darrere del Fonestar hi ha un interruptor **AUTOPLAY MODE (RANDOM / STANDARD)**. En Pol confirma que **ja estava a RANDOM** durant la prova del 15/10, i igualment va tornar a sonar la pista 1 després de tallar el corrent. Per tant, l'aleatori només actua mentre està encès; en engegar-se sempre comença per la mateixa. **La conclusió es manté:** cal la Raspberry.

---

## 4. Història de decisions (per què és com és)

### v1 — Raspberry amb senyal del rellotge per GPIO (descartada) → `versions-anteriors/v1-senyal-gpio/`
- Es posava un carregador USB a l'endoll del rellotge. Un divisor de tensió (**1 kΩ + 2 kΩ**, de 5 V a 3,3 V) anava al **GPIO17 (pin 11)** i, en detectar corrent, la Raspberry tocava una cançó. Les cançons es descarregaven d'una carpeta de Google Drive amb **rclone**.
- **Descartada perquè** en Pol va demanar una cosa més fàcil, "sense resistències i tot plegat".

### v2 — Raspberry amb horari propi en un fitxer de text (substituïda) → `versions-anteriors/v2-horari-txt/`
- La Raspberry sap l'hora per NTP i llegeix `horari.txt` de Drive (amb rclone). Sense cap cablejat.
- **Substituïda per la v3** quan en Pol va demanar una web de gestió. Amb la web, rclone i Drive ja no calien (era el pas més complicat de la instal·lació).

### v3 — ACTUAL: Raspberry amb web de gestió pròpia (arrel del repo)
- La Raspberry serveix la web a la xarxa de l'escola (`http://timbre.local` o la IP, port 80). Tot es configura des d'allà.
- **Decisió clau que s'ha de mantenir: el rellotge Theben NO s'elimina.** És qui engega l'amplificador JEDIA, i la Raspberry no pot fer-ho sense tocar el cablejat de 230 V (cosa que hauria de fer l'instal·lador). Per tant:
  - El Theben continua engegant l'ampli a les seves hores, sense canvis.
  - La Raspberry toca la música a les **mateixes hores**, amb un `RETARD_INICI` de 3 s perquè l'ampli tingui temps d'engegar-se.
  - **Les hores de la web i les del rellotge han de coincidir.** La web ho recorda en un avís fix a la pantalla d'Horari i al toast quan es desa.
- **Pla de tornada:** si la Raspberry falla, es torna a connectar el cable d'àudio al Fonestar i tot funciona com abans.

### Afegits del 18/10
- **Modes de selecció de cançons:** `cada_toc`, `dia`, `setmana` (canvia cada dilluns, segons la setmana ISO) i `fixa` (una cançó concreta). Els tres primers els va demanar en Pol; el mode `fixa` l'he afegit jo pensant en Nadal, Sant Jordi, etc.
- **Disseny amb els colors corporatius** de Vedruna Escorial Vic.

---

## 5. Arquitectura actual (v3)

```
timbre.py         Tot el backend en un sol fitxer:
                    - configuració (config.json) amb lock i escriptura atòmica
                    - programador (fil que revisa cada 0,5 s si toca un toc)
                    - Reproductor (mpv com a subprocés, control de volum per socket IPC → fos final)
                    - selecció de cançó (modes) i "no repetir les últimes"
                    - web Flask + API JSON, servida amb waitress (o el servidor de Flask si no hi és)
web/index.html    Tota la web en un fitxer (CSS + JS vanilla, icones SVG inline, sense dependències externes)
installa.sh       apt (mpv, python3-flask, python3-waitress, python3-mutagen, alsa-utils), servei systemd
GUIA.md           Guia d'instal·lació per a en Pol (no tècnica)
tools/            demo.sh (servidor de proves sense so), proves-api.sh, captures.py (Playwright)
```

### Fitxers de dades (a la Raspberry, a `~/timbre/`; estan al `.gitignore`)
- `config.json`: horari, festius, ajustos, metadades de cançons, mode de selecció i hash de la contrasenya. Es desa amb `escriu_atomic` (fitxer temporal + `fsync` + `replace`) i, just després, una còpia idèntica a **`config.bak`**. En arrencar, si `config.json` falta o està malmès es fa servir `config.bak`. Un fitxer malmès **no se sobreescriu mai**: es reanomena a `config.malmes-AAAAMMDD-HHMMSS(.json|.bak)`. Motiu: amb una SD i talls de llum, un `config.json` buit feia carregar els valors per defecte i la web quedava **sense contrasenya**.
- `mpv.log`: errors de l'última reproducció (mpv amb `--msg-level=all=error`).
- `estat.json` (també amb `escriu_atomic`): `tocades` (les últimes 200 cançons, per no repetir-les) i `periode` (`{mode, clau, canco}`, la cançó del dia o de la setmana).
- `historial.jsonl`: una línia JSON per cada cop que sona o ho intenta (`t`, `canco`, `motiu`, `segons`, `error` si no ha sonat i, si és d'horari, `toc`). Es retalla a 2.000 línies en arrencar.
- `musica/`: les cançons (mp3, m4a, ogg, wav, flac, opus, aac).
- `reserva.mp3`: opcional. Sona si no hi ha cap cançó activa.
- `.clau_sessio`: secret de les cookies de Flask.

### Esquema de `config.json`
```json
{
  "actiu": true,
  "silenci_data": "2026-10-20",            // o null. "Silenci només avui"
  "tocs": [{"nom": "Entrada del matí", "hora": "09:00", "durada": 60, "dies": [0,1,2,3,4], "actiu": true}],
                                            // dies: 0 = dilluns … 6 = diumenge; durada: 5–900 s
  "festius": [{"inici": "2026-12-22", "fi": "2027-01-07", "nom": "Vacances de Nadal"}],
  "cancons": {"Nom.mp3": {"activa": true, "inici": 12}},   // inici = segon on comença (salta intros)
  "seleccio": {"mode": "cada_toc|dia|setmana|fixa", "canco_fixa": null},
  "ajustos": {"volum": 100, "retard_inici": 3, "durada_fos": 3, "normalitza": true, "no_repetir": 20},
  "contrasenya": "sal$hash_pbkdf2_sha256"
}
```
**Les hores per defecte (09:00, 11:00, 11:30, 15:00) són EXEMPLES.** Les reals s'han de copiar del Theben (vegeu Pendents).

### Lògica de l'horari
- `motiu_silenci(dia)`: no sona si `actiu=false`, si `silenci_data` és avui o si el dia cau en un festiu.
- `proper_toc(ara, marge)`: busca fins a 60 dies endavant.
- El programador dispara quan `moment + retard_inici <= ara` i el toc encara no s'ha fet. Té un `MARGE_RETARD` de 30 s: si la Raspberry arrenca a mig toc, encara toca el temps que queda. Toca durant `durada - (ara - moment)` segons i acaba amb un fos.
- `SONATS` i `FALLATS` (en memòria i reconstruïts des de l'historial) marquen a Inici quins tocs d'avui "Ha sonat" o "Ha fallat".

### Detecció d'errors de reproducció (afegit el 18/10, a Claude Code)
- `Reproductor.toca()` engega mpv i espera `COMPROVA_INICI` (1,5 s). Si mpv ja ha acabat, **no ha sonat**: `explica_error_mpv` llegeix `mpv.log` i en treu un missatge en català (sortida d'àudio incorrecta / fitxer malmès / s'ha acabat de seguida). Es registra amb `error`, `segons: 0`, i `toca()` retorna el missatge (si ha anat bé, retorna `None`).
- Comprovat amb mpv 0.37 real: amb un `--audio-device` inexistent surt en 0,2 s amb codi 2. Amb un fitxer malmès, també codi 2 ("Failed to recognize file format").
- `/api/toca` respon 400 `No ha sonat: …`. A `/api/estat`, el toc té `estat: "error"` i `error`. La web mostra el xip "Ha fallat", un avís vermell a Inici i el motiu a l'Historial. `--prova` surt amb error.

### Selecció de cançó (`tria_canco`)
- `cada_toc`: `tria_aleatoria` tria entre les cançons actives i evita les últimes `min(n_actives // 2, no_repetir)`.
- `dia` / `setmana`: `canco_del_periode` reutilitza la cançó guardada a `estat.periode` si la clau (`2026-10-18` o `2026-S42`) coincideix i la cançó encara existeix i està activa. Si no, en tria una de nova i la guarda. `POST /api/periode` la canvia: a l'atzar, o una concreta amb `{"canco": nom}`.
- `fixa`: sempre `canco_fixa`. Si s'esborra aquesta cançó, el mode torna a `cada_toc`.
- El botó "Toca una cançó ara" de la web fa servir la mateixa lògica. En mode dia, doncs, toca la cançó d'avui.

### API (totes requereixen sessió excepte `/`, `/api/sessio`, `/api/configura`, `/api/login`)
| Mètode | Ruta | Funció |
|---|---|---|
| GET | `/api/sessio` | `{configurada, ok}` |
| POST | `/api/configura` | Primer ús: estableix la contrasenya (codi de 4 xifres, `codi_valid`). Si ja n'hi ha una, retorna 403. Normalment no es fa servir, perquè `installa.sh` ja demana la contrasenya. |
| POST | `/api/login` / `/api/logout` | Cookie de sessió de 90 dies (`HttpOnly`, `SameSite=Lax`, sense `Secure` perquè la web va per http). A partir del 5è error seguit des d'una IP, `/api/login` respon 429 durant 30 s, 1 min, 2 min… fins a 15 min. Un login correcte posa el comptador a zero. |
| GET | `/api/estat` | Hora, sincronització NTP, IP, què sona, proper toc, tocs d'avui amb estat, silenci, `seleccio {mode, canco}`, recompte de cançons, `demo` |
| GET/PATCH | `/api/config` | Llegeix o canvia `tocs`, `festius`, `ajustos`, `seleccio`, `actiu`, `silenci_avui` (bool). Amb validació. |
| GET/POST | `/api/cancons` | Llistat (durada amb mutagen, si està activa, inici, vegades) i pujada multipart (`fitxers`). Neteja els noms i evita duplicats. |
| PATCH/DELETE | `/api/cancons/<nom>` | `activa`, `inici` / esborrar |
| GET | `/api/cancons/<nom>/audio` | Per escoltar-la des del navegador (admet Range) |
| POST | `/api/toca` | `{canco?, segons}`. Toca ara (manual). |
| POST | `/api/atura` | Atura amb un fos curt |
| POST | `/api/periode` | Canvia la cançó del dia o de la setmana |
| GET | `/api/historial` | Les últimes 300 entrades |
| POST | `/api/contrasenya` | `{actual, nova}` |
| GET | `/api/copia` | Descarrega `config.json` sense la contrasenya |
| POST | `/api/apaga` | Apaga la Raspberry amb `sudo -n /usr/bin/systemctl poweroff`, al cap de 2 s. Abans comprova el permís (`sudo -n -l`); si no en té, 400. `installa.sh` posa la regla a `/etc/sudoers.d/timbre`, validada amb `visudo -cf`. En mode demo no fa res. |

### Web (`web/index.html`)
- Pestanyes a la barra inferior: **Inici · Horari · Cançons · Festius · Historial · Ajustos**. També s'hi pot accedir per hash (`#cancons`).
- **Inici:** rellotge de la Raspberry (sincronitzat amb un offset), targeta "Ara sona" amb barra i botó d'aturar, o bé "Proper toc" amb compte enrere. Llista d'avui amb xips (Ha sonat / Pendent / Ara / No ha sonat / Silenci), línia "Cançó d'avui: X [Canvia-la]", interruptors "Timbre actiu" i "Silenci només avui", i botó "Toca una cançó ara". Avisos: mode demo, hora no sincronitzada, cap cançó activa, timbre aturat, festiu.
- **Horari:** targetes editables (nom, hora, durada, botons de dies, interruptor, esborrar). Barra "Tens canvis sense desar" amb Desfés / Desa. Avisa si hi ha hores repetides i si surts amb canvis pendents.
- **Cançons:** targeta "Com sonen les cançons" (4 modes amb ràdio i desplegable per al mode fixa), zona per pujar fitxers (arrossegar o seleccionar, amb progrés), cerca, llista amb previsualització, interruptor d'activa, menú ⋯ ("Comença al segon", "Toca-la ara per megafonia", "Posa-la per a avui / aquesta setmana / Fes que soni sempre aquesta", "Esborra") i xip "Avui / Aquesta setmana / Sempre".
- **Festius:** formulari des de / fins a / nom, llista de festius vinents i plegable "Festius ja passats".
- **Historial:** agrupat per dies.
- **Ajustos:** volum, igualar volum (loudnorm), espera inicial, fos, no repetir, canvi de contrasenya, **Aparença** (Clara / Fosca / Com el dispositiu), còpia de seguretat, sortir i **Apaga la Raspberry**.
- **Tema:** per defecte **clar**, encara que el dispositiu estigui en mode fosc (21/10: en Pol ho veia tot negre amb Windows en mode fosc). Es tria a Ajustos → Aparença i es guarda a `localStorage` (`tema`), és a dir, en cada aparell. Un script al `<head>` posa `data-tema` a `<html>` abans de pintar. Tokens CSS a `:root`, `:root[data-tema="fosc"]` i `@media (prefers-color-scheme:dark) :root[data-tema="auto"]`.

---

## 6. Com provar-ho sense Raspberry

```bash
pip install flask waitress mutagen      # ffmpeg opcional, per crear mp3 de prova
bash tools/demo.sh                      # http://localhost:8099
bash tools/proves-api.sh                # en una altra terminal
python3 tools/captures.py <carpeta>     # captures amb Playwright (contrasenya de proves "2468")
```
`TIMBRE_DEMO=1` substitueix mpv per `sleep`, així que no surt so. Variables útils: `TIMBRE_DIR` (on van les dades), `TIMBRE_PORT` i `TIMBRE_AUDIO` (dispositiu de mpv).

**Proves ja passades a la conversa (en mode demo):** un toc programat dispara a l'hora amb 3 s de retard; es rebutgen hores, fitxers i camins invàlids (401/400/404); a la pujada, els fitxers que no són d'àudio es rebutgen; els modes cada_toc, dia (es repeteix), canvia-la, forçar cançó, desactivar la del dia (en tria una altra), setmana (clau ISO correcta), fixa (valida que existeixi) i "periode" en mode fixa (error) funcionen; la web no dona errors de JS; s'han fet captures en mòbil (390 px), escriptori i mode fosc.

**NO provat encara:** res a la Raspberry real (vegeu riscos).

---

## 7. Estat actual i PENDENTS (18/10/2026)

**Repositori:** https://github.com/poldpm/timbre-escola (branca `main`). La Raspberry s'instal·la amb `git clone` + `bash installa.sh` i s'actualitza amb `git pull && bash installa.sh` (vegeu GUIA.md). `installa.sh` copia `timbre.py` i `web/` a `~/timbre/`, on hi ha les dades. **El repo és públic per decisió d'en Pol** (18/10): se li ha explicat que els privats són gratuïts i ha preferit deixar-lo així. No hi ha secrets, perquè les dades reals són a la Pi i al `.gitignore`. **No pugis mai contrasenyes, IP, dades de la wifi ni dades personals.**

**Riscos de la revisió del 18/10 ja arreglats:** configuració a prova de talls de llum, detecció de "Ha fallat", límit d'intents de login, contrasenya triada a `installa.sh` abans d'engegar la web, galetes `HttpOnly` i `SameSite=Lax`, validació amb `enter()` (400 en lloc de 500), `ESTAT_LOCK` per a `estat.json` i `ESPAI_RESERVAT` (300 MB) a les pujades (la resposta inclou `sense_espai`).

**Riscos que encara queden (no són de codi o s'han de provar a la Pi):** el filtre `loudnorm` pot endarrerir l'inici uns segons; els dos rellotges (Theben i Pi) poden desquadrar-se (la protecció de 3 s és petita); si la placa és una Pi 3 B (no B+), la wifi només és de 2,4 GHz.


En Pol **ja té la microSD**. La Raspberry Pi 3 l'hi deixa algú (és gratis). En el moment del traspàs, no sabem si ja la té a les mans.

1. **Apuntar l'horari real del Theben** (MENU → PROGRAM → consultar): cada ON i OFF. Durada a la web = OFF − ON − ~5 s.
2. **Comprovar que és el rellotge qui treu el JEDIA de standby** (mirar el LED en un toc real).
3. **Tipus de wifi de la sala:** si és WPA2-Enterprise o té portal captiu, cal cable de xarxa. Sense internet no hi ha hora fiable, perquè la Pi 3 **no té RTC**.
4. **Connector de l'entrada del JEDIA** on va el Fonestar (RCA o jack) per saber quin cable cal.
5. **Demanar a informàtica una IP fixa (reserva DHCP)** per a la Raspberry, i connectar-la a la mateixa wifi que el personal. Es donarà l'enllaç `http://IP` a la directora i a qui calgui.
6. Primera instal·lació real seguint `GUIA.md` i un primer toc amb en Pol al costat. **És el primer cop que en Pol fa servir una Raspberry:** la prepara a casa sense pantalla (portàtil Windows + PowerShell/SSH, Raspberry connectada al router amb cable, wifi de l'escola ja posada a l'Imager), prova el so amb auriculars i després la porta a l'escola. Guia'l pas a pas si t'ho demana.
7. Copiar la cançó actual del pen com a `reserva.mp3`.

## 8. Riscos i coses a verificar a la Raspberry real

**Comprovat a la Raspberry real (21/10, a casa d'en Pol):** Raspberry Pi OS Lite 64-bit (kernel 6.18.50+rpt-rpi-v8, Debian). `installa.sh` acaba bé (tots els paquets d'apt hi són) i el servei queda `active (running)`. `aplay -l` mostra **`card 1: Headphones`**, així que el valor per defecte de `TIMBRE_AUDIO` és correcte. Primer problema real: un cable micro-USB de mòbil feia que la Pi es reiniciés en bucle (LED vermell intermitent, verd apagat); amb un altre cable va, però `vcgencmd get_throttled` dona `0x50000` (hi ha hagut baixada de tensió des de l'arrencada) amb un carregador de 5 V 2,1 A. **Recomanat: alimentador oficial de 2,5 A abans de deixar-la a l'escola.** L'usuari de la Pi és `poldelpozo`.


- **Nom del dispositiu ALSA:** s'ha suposat `alsa/plughw:CARD=Headphones,DEV=0` (Raspberry Pi OS Bookworm, jack analògic). Verifica-ho amb `aplay -l` i `mpv --audio-device=help`. Si no coincideix, canvia la variable d'entorn `TIMBRE_AUDIO` al servei o la constant.
- El **jack analògic de la Pi 3** pot fer soroll de fons. Si molesta, la solució és una targeta de so USB (~5 €).
- El filtre `loudnorm` de mpv fa servir CPU. A la Pi 3 hauria d'anar bé, però si es talla, posa `normalitza=false`.
- **Port 80** sense root, amb `AmbientCapabilities=CAP_NET_BIND_SERVICE` al servei.
- **`timbre.local` (mDNS)** potser no funciona en alguns Android. La web i l'instal·lador mostren també la IP. Seria bo fixar la IP o fer una reserva DHCP.
- **Sense HTTPS:** el navegador no deixarà fer servir el micròfon (per això no hi ha "gravar un avís"). La contrasenya viatja en clar per la wifi de l'escola. És acceptable en una LAN, però tingues-ho en compte.
- La contrasenya es tria a `installa.sh` (amb `timbre.py --contrasenya`), abans d'engegar el servei. **La contrasenya és un codi de 4 xifres per decisió d'en Pol (18/10)**: la sessió dura 90 dies i no vol posar res més llarg. Se li va proposar un mínim de 10 caràcters i ho va descartar. El protegeix el límit d'intents (5 lliures, després bloqueig de 30 s doblant fins a 15 min) i que la web només s'obre des de la wifi de l'escola. No ho tornis a proposar. **El codi real no ha d'aparèixer mai al repo.**
- Paquets `python3-flask`, `python3-waitress` i `python3-mutagen` d'apt a Bookworm: no s'ha comprovat que hi siguin tots. Si en falta algun, cal fer servir `pip install --break-system-packages`. Si no hi ha waitress, el codi fa servir el servidor de Flask.
- **Canvi d'hora estiu/hivern:** la Raspberry el fa sola. El Theben també pot fer-lo automàticament, però el protocol diu que es fa a mà. **Cal vigilar que no quedin desquadrats** l'endemà del canvi.
- Dues coses del Theben que no s'han tocat: si té el canvi d'hora automàtic activat i com va de precisió (el protocol parla d'una vida útil de 5 anys).

## 9. Idees per al futur (n'hem parlat o surten de forma natural)

- ~~Accés des de fora de l'escola~~ **DESCARTAT per en Pol (18/10):** només s'hi entra des de la wifi de l'escola. Se li van explicar Tailscale (cal instal·lar l'app a cada usuari) i Tailscale Funnel (enllaç públic, però caldria reforçar el login: límit d'intents, contrasenya llarga, cookies Secure). Ho va trobar massa complicat per a la directora. No ho tornis a proposar si ell no ho demana.
- **Calendari de cançons temàtiques:** una cançó o llista diferent per dates (Nadal, Sant Jordi, final de curs).
- **Llistes / categories** de cançons.
- **Avisos per megafonia:** text a veu, o un fitxer pujat per tocar a una hora concreta un sol cop.
- **Que la Raspberry engegui ella mateixa l'ampli** i substituir el Theben (amb un relé). **Només ho pot fer l'instal·lador (Llach, 93 850 45 05)** i caldria revisar-ho amb l'escola.
- **PWA** (manifest + icona) per "instal·lar" la web al mòbil. Ara la guia només diu "Afegeix a la pantalla d'inici".
- Comprovació de salut: avís (per correu, per exemple) si la Raspberry no ha sonat en un toc.

## 10. Seguretat i límits que s'han de respectar

- **Amplificador 2 (Apart PA240P, sirenes): no tocar-lo mai** ni proposar-ho.
- **No proposar a en Pol manipulacions de 230 V.** Qualsevol canvi a la caixa del rellotge, el relé o els borns sense caixa l'ha de fer l'instal·lador.
- La Raspberry només es connecta per **àudio de línia** a una entrada del JEDIA, i s'alimenta d'un endoll normal de la regleta.
