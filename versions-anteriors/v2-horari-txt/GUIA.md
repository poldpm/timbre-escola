# Timbre musical de l'escola — Guia d'instal·lació

**Com funciona:** la Raspberry sap l'hora per internet i llegeix l'horari d'un fitxer (`horari.txt`) de la carpeta de Drive **"Timbre escola"**. A cada hora del timbre toca una cançó a l'atzar de la mateixa carpeta, sense repetir les últimes, i l'apaga amb un fos.

El **rellotge Theben no es toca**: continua engegant l'amplificador a les seves hores. La Raspberry només substitueix el Fonestar com a font de música. Per això, les hores de `horari.txt` **han de coincidir amb les del rellotge**.

Sense resistències, sense soldar i sense tocar res de 230 V.

---

## 1. Material

- Raspberry Pi 3 + carregador oficial (5 V / 2,5 A, micro-USB)
- microSD de 16 GB o més
- Cable d'àudio: jack 3,5 mm a la Raspberry → el connector del cable que ara entra al Fonestar (mira si és RCA o jack)

## 2. Apuntar l'horari del rellotge

Al rellotge Theben: **MENU → PROGRAM → (consultar / CHECK)**. Ves passant amb les fletxes i apunta cada hora d'encesa (ON) i d'apagada (OFF). Fes una foto de cada pantalla si et va millor.

Per a cada toc, la **durada** de `horari.txt` és el temps entre l'ON i l'OFF menys uns 5 segons de marge.

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

> Si la wifi de l'escola és d'usuari i contrasenya personal (tipus WPA2-Enterprise) o té pàgina d'accés, no funcionarà directament. En aquest cas, demana a informàtica un cable de xarxa o una wifi normal. **La Raspberry necessita internet per saber l'hora exacta.**

## 4. Primera arrencada i instal·lació

1. Posa la targeta a la Raspberry i endolla-la. Espera 2 minuts.
2. Des d'un ordinador **de la mateixa wifi**, obre un terminal (a Windows: PowerShell), situa't on has descomprimit el zip i copia la carpeta:
   ```
   scp -r timbre usuari@timbre.local:~/instalacio
   ```
3. Connecta't i instal·la:
   ```
   ssh usuari@timbre.local
   cd ~/instalacio
   bash installa.sh
   ```

## 5. Carpeta de Drive

1. A Google Drive, crea una carpeta que es digui exactament **`Timbre escola`**.
2. Puja-hi les cançons. Les pots compartir amb altres mestres perquè també n'hi posin.
3. Puja-hi també el fitxer **`horari.txt`** del zip, **amb les hores reals del pas 2**. És un fitxer de text normal: es pot editar amb el Bloc de notes i tornar-lo a pujar. Les línies que comencen per `#` són comentaris.

Exemple:
```
09:00   60   dl-dv
11:30   45   dl-dv
15:00   60   dl-dv
festiu 2026-12-22..2027-01-07
```

## 6. Connectar Google Drive

1. A la Raspberry, executa `rclone config` i respon:
   - `n` (nou remot) → nom: **`drive`**
   - Tipus: **drive** (Google Drive)
   - client_id i client_secret: deixa-ho en blanc (Intro)
   - scope: **2** (només lectura)
   - Opcions avançades: `n`
   - "Use auto config?": **`n`** (la Raspberry no té navegador)
2. Et mostrarà una ordre `rclone authorize "drive" ...`. Executa-la al **teu ordinador** (cal instal·lar-hi rclone des de rclone.org/downloads). S'obrirà el navegador, entres amb el compte de l'escola i et donarà un codi. Enganxa'l a la Raspberry.
3. Shared drive: `n`. Confirma amb `y` i surt amb `q`.
4. Prova-ho:
   ```
   ~/timbre/sincronitza.sh
   python3 ~/timbre/timbre.py --llista
   ```
   Ha de mostrar les cançons, l'horari, el **proper toc** i "Hora sincronitzada: SI".

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

1. Endolla la Raspberry a la **regleta blanca**, que té corrent sempre.
2. Deixa el cable d'àudio connectat a la Raspberry. El Fonestar es pot quedar on és, desconnectat de l'àudio, com a recanvi.
3. **No toquis el rellotge.** Continua engegant l'amplificador com sempre.
4. Al primer toc real, sigues-hi a prop per comprovar que tot quadra.

## Ús del dia a dia

- **Canviar la música:** puja o esborra cançons a la carpeta de Drive.
- **Canviar hores o afegir festius:** edita `horari.txt` a Drive. **Si canvies una hora, canvia-la també al rellotge.**
- Els canvis arriben cada nit a les 2:30. Per aplicar-los ja, executa `~/timbre/sincronitza.sh` a la Raspberry.
- **Veure què ha sonat:** `cat ~/timbre/historial.log`
- **Veure si funciona:** `journalctl -u timbre -f`
- **Reiniciar el programa:** `sudo systemctl restart timbre`

## Canvi d'hora (estiu/hivern)

La Raspberry el fa sola. El rellotge s'ha de canviar a mà, com diu el protocol de la paret, si no ho fa automàticament.

## Pla de tornada

Si mai falla: torna a connectar el cable d'àudio al Fonestar amb el seu pen. El sistema torna a funcionar exactament com abans.

## Ajustos (a dalt de `timbre.py`)

| Ajust | Per defecte | Per a què serveix |
|---|---|---|
| `RETARD_INICI` | 3 s | Espera després de l'hora perquè l'amplificador s'engegui. Puja-ho si es perd l'inici de la cançó. |
| `DURADA_FOS` | 3 s | Durada del fos final |
| `NORMALITZA` | True | Iguala el volum entre cançons |
| `VOLUM` | 100 | Volum de sortida de la Raspberry |

Després de canviar-ne un: `sudo systemctl restart timbre`
