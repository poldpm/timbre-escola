# Captures automàtiques de la web amb Playwright.
# Ús: engega `bash tools/demo.sh` (contrasenya ja configurada com "2468", p. ex. amb tools/proves-api.sh)
#      i després: python3 tools/captures.py <carpeta_on_desar>  (crea <carpeta>/shots/*.png)
import sys, time
from playwright.sync_api import sync_playwright
S=sys.argv[1]; U="http://localhost:8099"; errs=[]
with sync_playwright() as p:
    b=p.chromium.launch()
    pg=b.new_page(viewport={"width":390,"height":844}, device_scale_factor=2)
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(U); time.sleep(0.6); pg.screenshot(path=f"{S}/shots/a-login.png")
    pg.fill("#login-pass","2468"); pg.click("#login-btn"); time.sleep(1.5)
    pg.screenshot(path=f"{S}/shots/b-inici.png")
    pg.click("nav button[data-s=cancons]"); time.sleep(1)
    pg.screenshot(path=f"{S}/shots/c-cancons.png")
    pg.click("#modes input[value=fixa]"); time.sleep(0.5)
    pg.select_option("#canco-fixa", "Here Comes the Sun.mp3"); time.sleep(1.2)
    print("toast:", pg.text_content("#toast"))
    pg.evaluate("window.scrollTo(0, 420)"); time.sleep(0.3)
    pg.click("[data-nom='Bon dia sol.mp3'] [data-obre]"); time.sleep(0.4)
    pg.screenshot(path=f"{S}/shots/d-fixa.png")
    pg.click("#modes input[value=dia]") if pg.is_visible("#modes input[value=dia]") else None
    pg.evaluate("window.scrollTo(0,0)"); pg.click("#modes input[value=dia]"); time.sleep(1)
    pg.click("nav button[data-s=inici]"); time.sleep(1)
    pg.click("#btn-toca-ara"); time.sleep(2.5)
    pg.screenshot(path=f"{S}/shots/e-sonant.png")
    pg.emulate_media(color_scheme="dark"); time.sleep(0.3)
    pg.screenshot(path=f"{S}/shots/f-dark.png")
    pg.emulate_media(color_scheme="light")
    pg.click("nav button[data-s=horari]"); time.sleep(0.8)
    pg.screenshot(path=f"{S}/shots/g-horari.png")
    b.close()
print("errors:", errs)
