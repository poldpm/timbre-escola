# Timbre musical de l'escola — Guia d'instal·lació

**Com funciona:** la Raspberry sap l'hora per internet i té el seu propi horari. A cada toc, toca una cançó a l'atzar sense repetir les últimes i l'apaga amb un fos. Tot es gestiona des d'una **web** que la mateixa Raspberry serveix a la xarxa de l'escola: horari, cançons, festius, historial i ajustos.

El **rellotge Theben no es toca**: continua engegant l'amplificador a les seves hores. Per això, les hores de la web **han de coincidir amb les del rellotge**.

---

## 1. Material

- Raspberry Pi 3 + carregador oficial (5 V / 2,5 A, micro-USB)
- microSD (la que ja tens)
- Cable d'àudio: jack 3,5 mm a la Raspberry → el connector del cable que ara entra al Fonestar (mira si és RCA o jack)

## 2. Apuntar l'horari del rellotge

Al rellotge Theben: **MENU → PROGRAM → consultar (CHECK)**. Ves passant amb les fletxes i apunta cada hora d'encesa (ON) i d'apagada (OFF). Pots fer una foto de cada pantalla.

Per a cada toc, la **durada** és el temps entre l'ON i l'OFF menys uns 5 segons de marge.

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

## 4. Instal·lar

1. Posa la targeta a la Raspberry i endolla-la. Espera 2 minuts.
2. Des d'un ordinador **de la mateixa wifi**, obre un terminal (a Windows: PowerShell) i connecta't a la Raspberry:
   ```
   ssh usuari@timbre.local
   ```
   (`usuari` és el que vas posar a l'Imager. El primer cop et preguntarà si confies en l'equip: respon `yes`.)
3. Baixa el programa de GitHub i instal·la'l:
   ```
   sudo apt install -y git
   git clone https://github.com/poldpm/timbre-escola.git
   cd timbre-escola
   bash installa.sh
   ```
4. En acabar et mostrarà l'adreça de la web.

> Si el repositori de GitHub és **privat**, el `git clone` et demanarà usuari i contrasenya. Com a contrasenya no serveix la de GitHub: cal un *token* (github.com → Settings → Developer settings → Personal access tokens → Fine-grained, amb permís només de lectura d'aquest repositori).

## 5. Primer cop a la web

1. Des del mòbil o l'ordinador, connectat a la **mateixa wifi**, obre **http://timbre.local**. Si no carrega, fes servir l'adreça amb números que ha mostrat l'instal·lador (per exemple `http://192.168.1.50`).
2. Tria una **contrasenya**. Només la necessitaran les persones que hagin de gestionar el timbre.
3. Ves a **Inici → Toca una cançó ara** (amb l'amplificador apagat, només per veure que no surt cap error). Si surt "No ha sonat: No s'ha pogut obrir la sortida d'àudio", mira l'apartat [Si surt «Ha fallat»](#si-surt-ha-fallat).
4. **Horari:** posa-hi les hores i durades reals del pas 2 i desa.
5. **Cançons:** puja-les. Des de l'ordinador pots arrossegar-ne moltes de cop.
6. **Festius:** afegeix-hi les vacances i els dies festius del curs.

> Consell: guarda la web a la pantalla d'inici del mòbil (menú del navegador → "Afegeix a la pantalla d'inici"). Així la tindràs com una app.

## 6. Provar el so (fora d'horari de classe!)

1. Connecta el jack de la Raspberry al cable que anava al Fonestar.
2. Engega l'amplificador amb **POWER**, amb el **MASTER baix**.
3. A la web: **Inici → Toca una cançó ara**.
4. Ajusta el volum amb la rodella de l'entrada al JEDIA, no amb la Raspberry.
5. Torna a deixar el MASTER i l'amplificador com estaven.

## 7. Instal·lació definitiva

1. Endolla la Raspberry a la **regleta blanca**, que té corrent sempre.
2. Deixa el cable d'àudio connectat a la Raspberry. El Fonestar es pot quedar on és, desconnectat, com a recanvi.
3. **No toquis el rellotge.**
4. Al primer toc real, sigues-hi a prop per comprovar que tot quadra.

## Què es pot fer des de la web

| Pantalla | Què hi trobes |
|---|---|
| **Inici** | Hora de la Raspberry, què sona ara (amb botó d'aturar), proper toc, tocs d'avui, interruptor del timbre, "silenci només avui" i "toca una cançó ara" |
| **Horari** | Afegir, canviar o esborrar tocs: nom, hora, durada i dies de la setmana |
| **Cançons** | Pujar, escoltar al mòbil, activar/desactivar, triar a quin segon comença, tocar-la ara per megafonia i esborrar |
| **Cançons → Com sonen** | Una de diferent a cada toc · la mateixa tot el dia (l'endemà una altra) · la mateixa tota la setmana (canvia cada dilluns) · sempre una de concreta. La d'avui o de la setmana es pot canviar amb «Canvia-la» o triar-la des de la llista |
| **Festius** | Dies solts o períodes de vacances en què no sona |
| **Historial** | Què ha sonat i quan |
| **Ajustos** | Volum, igualar volum entre cançons, espera inicial, fos, quantes cançons recents no es repeteixen, contrasenya i còpia de seguretat |

**Recorda:** si canvies una hora a la web, canvia-la també al rellotge. Si no, la música sonarà amb l'amplificador apagat i no se sentirà.

## Canvi d'hora (estiu/hivern)

La Raspberry el fa sola. El rellotge s'ha de canviar a mà, com diu el protocol de la paret, si no ho fa automàticament.

## Actualitzar el programa

Quan hi hagi canvis nous a GitHub, connecta't per SSH i executa:
```
cd ~/timbre-escola
git pull
bash installa.sh
```
L'horari, les cançons, l'historial i la contrasenya no es toquen: són a `~/timbre`, no a la carpeta del programa.

## Si surt «Ha fallat»

Quan la Raspberry intenta tocar i no pot, a la web surt un avís vermell a **Inici**, el toc es marca com a **Ha fallat** i l'**Historial** n'explica el motiu.

- **"No s'ha pogut obrir la sortida d'àudio"**: el nom de la sortida d'àudio no és el que toca. Per SSH, mira com es diu amb `aplay -l` (busca la línia del jack, normalment `Headphones`). Si no és `Headphones`, escriu `sudo systemctl edit timbre` i afegeix:
  ```
  [Service]
  Environment=TIMBRE_AUDIO=alsa/plughw:CARD=NomQueSurt,DEV=0
  ```
  Desa, i fes `sudo systemctl restart timbre`.
- **"El fitxer no es pot reproduir"**: aquella cançó està malmesa. Esborra-la i torna-la a pujar.

## Si he oblidat la contrasenya

Connecta't per SSH i executa:
```
cd ~/timbre && python3 timbre.py --contrasenya
sudo systemctl restart timbre
```

## Pla de tornada

Si mai falla: torna a connectar el cable d'àudio al Fonestar amb el seu pen. El sistema torna a funcionar exactament com abans.

## Ordres útils (per SSH)

- Veure si funciona: `journalctl -u timbre -f`
- Reiniciar el programa: `sudo systemctl restart timbre`
- Prova de so sense web: `cd ~/timbre && python3 timbre.py --prova`
