# Cronologia de la conversa original (claude.ai, octubre 2026)

Resum pas a pas del que es va dir i decidir. És un complement del `CLAUDE.md`.

**9/10 (8:26)**: En Pol envia fotos de la caixa del rellotge, del protocol de la paret, del Fonestar FS-2900 i del rack (JEDIA JPA-1240A + Apart PA240P "AMPLI 2"). Explica el problema: un sol USB amb una sola cançó, algú l'ha d'anar a canviar i cansa. Vol un sol pen amb moltes cançons que vagin variant.
→ Primera hipòtesi: el rellotge dona corrent i el Fonestar arrenca des de la pista 1. Es proposa una prova gratuïta: mirar si REPEAT té un mode aleatori i si el reproductor recorda la pista. Les alternatives: una Raspberry Pi amb Drive o un reproductor comercial.

**15/10 (17:18)**: "Estic amb l'aparell. Guia'm per fer la prova 1."
- El POWER del Fonestar **no l'encén**: només té corrent quan el rellotge activa.
- Es guia l'activació manual del Theben amb MENU → MANUAL → OVERRIDE, abaixant abans el MASTER del JEDIA i traient el pen.
- Modes de REPEAT: **repeat, repeat album, repeat all**. No té aleatori.
- Prova de memòria: **torna a sonar la 1**. → El Fonestar queda descartat.
- Es proposa un ESP32 + DFPlayer (~15–20 €) o una Raspberry Pi. **En Pol aconsegueix una Raspberry Pi 3 gratis** que li deixen.
- A la sala de l'aparell **hi ha wifi**.
- Foto de l'endoll (fletxa): el transformador del Fonestar va **directament a l'endoll del rellotge**.
- Es fa la **v1**: senyal GPIO amb divisor de resistències + Drive/rclone.

**15/10 (18:38)**: "No hi hauria una manera més fàcil que no impliqui resistències…? Que el propi codi ja sàpiga les hores… No és 100 % essencial que el rellotge s'utilitzi."
→ **v2**: horari propi amb `horari.txt` a Drive. S'explica que **el rellotge s'ha de quedar** perquè és qui engega l'amplificador.

**15/10**: Pregunta si continua necessitant la microSD (sí, és el disc de la Pi 3). Demana un enllaç d'Amazon Prime. El primer enllaç (SanDisk Ultra 32 GB, B073JWXGNT) **no està disponible**, i se li passen cerques de SanDisk Ultra, Samsung EVO Plus i Kingston Canvas Select Plus, comprant sempre a "Enviado y vendido por Amazon".

**18/10 (12:23)**: "Ja tinc la SD. Podríem fer una web on es puguin modificar les hores, controlar les cançons i tota la gestió de la megafonia?"
→ **v3**: web servida per la mateixa Raspberry. Es deixen de fer servir Drive i rclone. Provada en mode demo amb captures.

**18/10 (12:37)**: Demana poder configurar si sona la mateixa cançó tot el dia (i l'endemà una altra), una de diferent cada vegada o la mateixa tota la setmana. També vol l'estètica amb els **colors corporatius de Vedruna Escorial Vic**.
→ S'afegeixen els modes `cada_toc` / `dia` / `setmana` / `fixa`. Els colors s'extreuen del logo del Drive de l'escola (doc "LOGO ESCORIAL VIC VEDRUNA", a la carpeta de plantilles): **#810023** i **#E0003F**.

**18/10 (12:43)**: Demana extreure-ho tot per continuar amb **Claude Code**. D'aquí surt aquest repositori.
