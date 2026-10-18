# Timbre musical de l'escola — Guia d'instal·lació

**Com funciona:** la Raspberry sap l'hora per internet i té el seu propi horari. A cada toc, toca una cançó a l'atzar sense repetir les últimes i l'apaga amb un fos. Tot es gestiona des d'una **web** que la mateixa Raspberry serveix a la xarxa de l'escola: horari, cançons, festius, historial i ajustos.

El **rellotge Theben no es toca**: continua engegant l'amplificador a les seves hores. Per això, les hores de la web **han de coincidir amb les del rellotge**.

**No cal pantalla ni teclat.** La Raspberry funciona "a cegues" i la controles des del portàtil: en una finestra hi escrius ordres i ella les executa (això és el que aquí anomenem **SSH**).

**Es prepara a casa i es porta a l'escola.** A casa la instal·les, hi poses les cançons i comproves que sona amb uns auriculars (passos 3 a 5). A l'escola només l'endolles, la connectes a l'amplificador i fas la prova final (passos 6 a 8).

---

## 1. Material

**Per preparar-la a casa:**
- **Raspberry Pi 3.**
- **Carregador micro-USB de 5 V i 2,5 A.** Mira si te'l donen amb la Raspberry. Un carregador de mòbil vell sovint no dona prou corrent i la Raspberry fa coses estranyes. L'oficial costa uns 10 €.
- **La microSD.**
- **Un lector de targetes per al portàtil.** Si el portàtil té ranura SD, fes servir l'adaptador de microSD a SD que sol venir amb la targeta. Si no, un lector USB costa uns 5 €.
- **El portàtil** (Windows). Hi instal·laràs **Raspberry Pi Imager**, que és gratuït. L'ordre `ssh` ja ve amb Windows.
- **Un cable de xarxa** per connectar la Raspberry al router de casa.
- **Uns auriculars o un altaveu amb jack de 3,5 mm**, per a la prova de so.

**Per a l'escola:**
- **Cable d'àudio:** jack de 3,5 mm a la banda de la Raspberry → el connector que demani l'entrada del JEDIA on ara va el Fonestar (mira si és RCA o jack).
- **Opcional: una caixeta per a la Raspberry** (5–8 €), que la protegeix de la pols i dels cops.

**Pla B** (només si no t'hi pots connectar des del portàtil): una pantalla o tele amb **HDMI** i un teclat USB.

## 2. Apuntar l'horari del rellotge

Al rellotge Theben: **MENU → PROGRAM → consultar (CHECK)**. Ves passant amb les fletxes i apunta cada hora d'encesa (ON) i d'apagada (OFF). Pots fer una foto de cada pantalla.

Per a cada toc, la **durada** és el temps entre l'ON i l'OFF menys uns 5 segons de marge.

## 3. Preparar la targeta

1. Al teu ordinador, instal·la **Raspberry Pi Imager** (raspberrypi.com/software).
2. Tria **Raspberry Pi 3** → **Raspberry Pi OS Lite (64-bit)** → la microSD.
3. A "Edita la configuració":
   - Nom de l'equip: `timbre`
   - Usuari i contrasenya: els que vulguis (apunta-te'ls)
   - Wifi: **la de l'escola** (la de la sala de l'aparell), encara que ho preparis a casa. A casa la connectaràs amb cable. País: ES
   - Zona horària: Europe/Madrid
   - Pestanya Serveis: **activa SSH** amb contrasenya
4. Grava la targeta.

> Si la wifi de l'escola és d'usuari i contrasenya personal (tipus WPA2-Enterprise) o té pàgina d'accés, no funcionarà directament. En aquest cas, demana a informàtica un cable de xarxa o una wifi normal. **La Raspberry necessita internet per saber l'hora exacta.**

## 4. Instal·lar

1. Posa la targeta a la Raspberry. Connecta-la al **router de casa amb el cable de xarxa** i, al final, endolla el carregador. Espera 2 minuts.
2. Al portàtil, connectat a la xarxa de casa, obre **PowerShell** (busca'l al menú Inici) i connecta't a la Raspberry:
   ```
   ssh usuari@timbre.local
   ```
   - `usuari` és el que vas posar a l'Imager.
   - El primer cop et preguntarà si confies en l'equip: escriu `yes` i prem Retorn.
   - Després et demanarà la contrasenya de l'usuari. **Mentre l'escrius no es veu res a la pantalla**: és normal, escriu-la i prem Retorn.
   - Si diu que no troba `timbre.local`, espera un parell de minuts més i torna-ho a provar. Si continua, entra a la pàgina del router de casa, busca l'equip "timbre" a la llista d'aparells connectats i fes servir la seva adreça: `ssh usuari@192.168.1.XX`.
3. Baixa el programa de GitHub i instal·la'l:
   ```
   sudo apt install -y git
   git clone https://github.com/poldpm/timbre-escola.git
   cd timbre-escola
   bash installa.sh
   ```
4. Cap al final et demanarà la **contrasenya de la web**: un **codi de 4 xifres**. Mentre l'escrius no es veurà res a la pantalla: és normal. El necessitaran totes les persones que hagin de gestionar el timbre, i només s'ha de posar el primer cop a cada mòbil o ordinador (es recorda 90 dies). **No l'apuntis enlloc del repositori de GitHub, que és públic.**
5. En acabar et mostrarà l'adreça de la web.

> Si el repositori de GitHub és **privat**, el `git clone` et demanarà usuari i contrasenya. Com a contrasenya no serveix la de GitHub: cal un *token* (github.com → Settings → Developer settings → Personal access tokens → Fine-grained, amb permís només de lectura d'aquest repositori).

## 5. Primer cop a la web

1. Des del portàtil o del mòbil, connectat a la **mateixa xarxa** que la Raspberry (a casa, la del router), obre **http://timbre.local**. Si no carrega, fes servir l'adreça amb números que ha mostrat l'instal·lador (per exemple `http://192.168.1.50`).
2. Entra amb el **codi de 4 xifres** que has triat a la instal·lació. Si t'equivoques 5 vegades seguides, la web et farà esperar uns minuts abans de tornar-ho a provar.
3. **Cançons:** puja-les. Des de l'ordinador pots arrossegar-ne moltes de cop.
4. **Prova de so amb auriculars** (la prova més important): connecta uns auriculars o un altaveu al jack de la Raspberry i ves a **Inici → Toca una cançó ara**. Si sona, a l'escola també sonarà. Si surt "No ha sonat: No s'ha pogut obrir la sortida d'àudio", mira l'apartat [Si surt «Ha fallat»](#si-surt-ha-fallat).
5. **Horari:** posa-hi les hores i durades reals del pas 2 i desa.
6. **Festius:** afegeix-hi les vacances i els dies festius del curs.

Per apagar-la abans de portar-la a l'escola, per SSH: `sudo poweroff`. Espera que s'apagui la llum verda i desendolla-la.

> Consell: guarda la web a la pantalla d'inici del mòbil (menú del navegador → "Afegeix a la pantalla d'inici"). Així la tindràs com una app.

## 6. Portar-la a l'escola

1. Endolla la Raspberry a la **regleta blanca**, que té corrent sempre, i espera 2 minuts. Es connectarà sola a la wifi de l'escola.
2. Amb el mòbil connectat a la **mateixa wifi**, obre **http://timbre.local**.
3. Si no carrega: **a l'escola l'adreça amb números és diferent de la de casa**. Demana-la a informàtica (busquen l'equip "timbre" al router) i, de pas, demana'ls que li **reservin aquesta IP fixa**. Aquesta serà l'adreça que donaràs a la directora i a qui calgui.
4. Si no es connecta de cap manera, probablement la wifi de l'escola és d'usuari i contrasenya personal o té pàgina d'accés: caldrà un cable de xarxa (vegeu el pas 3).

## 7. Provar el so amb l'amplificador (fora d'horari de classe!)

1. Connecta el jack de la Raspberry al cable que anava al Fonestar.
2. Engega l'amplificador amb **POWER**, amb el **MASTER baix**.
3. A la web: **Inici → Toca una cançó ara**.
4. Ajusta el volum amb la rodella de l'entrada al JEDIA, no amb la Raspberry.
5. Torna a deixar el MASTER i l'amplificador com estaven.

## 8. Instal·lació definitiva

1. Deixa la Raspberry endollada a la **regleta blanca**.
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
