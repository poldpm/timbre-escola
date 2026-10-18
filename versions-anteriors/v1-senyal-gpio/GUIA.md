# Timbre musical de l'escola — Guia d'instal·lació

**Com funciona:** el rellotge Theben continua manant, igual que ara. Quan dona corrent a l'endoll del timbre, un carregador USB avisa la Raspberry. La Raspberry toca una cançó a l'atzar d'una carpeta de Google Drive, sense repetir les últimes. Si el rellotge talla el corrent abans que acabi, la cançó s'apaga amb un fos.

---

## 1. Material

- Raspberry Pi 3 + carregador oficial (5 V / 2,5 A, micro-USB)
- microSD de 16 GB o més
- Carregador USB vell qualsevol + un cable USB que es pugui tallar
- Resistència d'**1 kΩ** (marró-negre-vermell) i de **2 kΩ** (vermell-negre-vermell)
- 3 cables dupont femella (o una mini placa de proves)
- Cable d'àudio: jack 3,5 mm a la Raspberry → el connector del cable que ara entra al Fonestar

## 2. Connexió de l'avís (només 5 V, res de 230 V)

Talla el cable USB i pela'l. Fes servir només el fil **vermell (+5 V)** i el **negre (GND)**. Aïlla els altres dos fils (verd i blanc) amb cinta.

```
 Fil vermell (+5V) ──[ 1 kΩ ]──┬──────► Pin 11 (GPIO17)
                               │
                            [ 2 kΩ ]
                               │
 Fil negre (GND) ──────────────┴──────► Pin 9 (GND)
```

Els pins de la Raspberry, amb el connector de 40 pins a dalt a la dreta:

```
  Pin 1 (3,3V) ● ● Pin 2
  Pin 3        ● ● Pin 4
  Pin 5        ● ● Pin 6
  Pin 7        ● ● Pin 8
  Pin 9 (GND)  ● ● Pin 10
  Pin 11(GPIO17)● ● Pin 12
```

> ⚠️ **Mai connectis el fil vermell directament al pin 11.** 5 V cremarien el pin. Les resistències el baixen a 3,3 V.

Abans d'endollar-ho a la Raspberry, comprova amb un tester que entre el pin 11 i el GND hi ha uns **3,3 V** quan el carregador té corrent.

## 3. Preparar la targeta

1. Al teu ordinador, instal·la **Raspberry Pi Imager** (raspberrypi.com/software).
2. Tria **Raspberry Pi 3** → **Raspberry Pi OS Lite (64-bit)** → la microSD.
3. A "Edita la configuració":
   - Nom de l'equip: `timbre`
   - Usuari i contrasenya: els que vulguis (apunta-te'ls)
   - Wifi: la de la sala de l'aparell. País: ES
   - Zona horària: Europe/Madrid
   - Pestanya Serveis: **activa SSH** amb contrasenya
4. Grava la targeta.

> Si la wifi de l'escola és d'usuari i contrasenya personal (tipus WPA2-Enterprise) o té pàgina d'accés, no funcionarà directament. En aquest cas, demana a informàtica un cable de xarxa o una wifi normal.

## 4. Primer arrencada i còpia dels fitxers

1. Posa la targeta a la Raspberry i endolla-la. Espera 2 minuts.
2. Des d'un ordinador **de la mateixa wifi**, obre un terminal (a Windows: PowerShell) i copia la carpeta:
   ```
   scp -r timbre usuari@timbre.local:~/instalacio
   ```
3. Connecta't:
   ```
   ssh usuari@timbre.local
   ```

## 5. Instal·lar

Dins de la Raspberry:
```
cd ~/instalacio
bash installa.sh
```

## 6. Connectar Google Drive

1. A Google Drive crea una carpeta que es digui exactament **`Timbre escola`** i hi puges les cançons. Les pots compartir amb altres mestres perquè també n'hi posin.
2. A la Raspberry, executa `rclone config` i respon:
   - `n` (nou remot) → nom: **`drive`**
   - Tipus: **drive** (Google Drive)
   - client_id i client_secret: deixa-ho en blanc (Intro)
   - scope: **2** (només lectura)
   - Opcions avançades: `n`
   - "Use auto config?": **`n`** (la Raspberry no té navegador)
3. Et mostrarà una ordre `rclone authorize "drive" ...`. Executa-la al **teu ordinador** (cal instal·lar-hi rclone des de rclone.org/downloads). S'obrirà el navegador, entres amb el compte de l'escola i et donarà un codi. Enganxa'l a la Raspberry.
4. Shared drive: `n`. Confirma amb `y` i surt amb `q`.
5. Prova-ho:
   ```
   ~/timbre/sincronitza.sh
   python3 ~/timbre/timbre.py --llista
   ```

## 7. Cançó de reserva

Copia la cançó que sona ara (la del pen del Fonestar) com a `~/timbre/reserva.mp3`. Només sonarà si la carpeta es buida.

```
scp canco_actual.mp3 usuari@timbre.local:~/timbre/reserva.mp3
```

## 8. Provar el so (fora d'horari de classe!)

1. Connecta el jack de la Raspberry al cable que anava al Fonestar.
2. Engega l'amplificador amb **POWER**, amb el **MASTER baix**.
3. A la Raspberry:
   ```
   python3 ~/timbre/timbre.py --prova
   ```
   Sonarà una cançó durant 20 segons i s'apagarà amb un fos.
4. Ajusta el volum amb la rodella de l'entrada al JEDIA, no amb la Raspberry.
5. Torna a deixar el MASTER i l'amplificador com estaven.

## 9. Instal·lació definitiva

1. Treu el transformador del Fonestar de l'endoll del rellotge (fletxa vermella) i hi endolles el **carregador-avís**.
2. Endolla la Raspberry a la **regleta blanca** (sempre té corrent).
3. Prova completa: al rellotge, MENU → MANUAL → OVERRIDE. Ha de sonar una cançó al cap de 2 segons. Cancel·la l'OVERRIDE i ha de fer el fos.
4. **Comprova que el rellotge torna al mode automàtic.**

## Ús del dia a dia

- **Canviar la música:** puja o esborra cançons a la carpeta de Drive. Es sincronitza cada nit a les 2:30.
- **Durada:** la cançó es talla amb un fos quan el rellotge apaga. No cal retallar els fitxers, però queda millor si el tros interessant és al principi.
- **Veure què ha sonat:** `cat ~/timbre/historial.log`
- **Veure si funciona:** `journalctl -u timbre -f`
- **Reiniciar el programa:** `sudo systemctl restart timbre`

## Pla de tornada

Si mai falla: desendolla el carregador-avís, torna a endollar el transformador del Fonestar al seu lloc i torna a connectar-li el cable d'àudio. El sistema torna a funcionar exactament com abans.

## Ajustos (a dalt de `timbre.py`)

| Ajust | Per defecte | Per a què serveix |
|---|---|---|
| `RETARD_INICI` | 2 s | Espera perquè l'amplificador s'engegui. Puja-ho si es perd l'inici de la cançó. |
| `DURADA_FOS` | 2,5 s | Durada del fos final |
| `NORMALITZA` | True | Iguala el volum entre cançons |
| `VOLUM` | 100 | Volum de sortida de la Raspberry |

Després de canviar-ne un: `sudo systemctl restart timbre`
