import asyncio
from playwright.async_api import async_playwright
from dotenv import load_dotenv
import os
import traceback

load_dotenv()

# Variables de entorno
INSTAGRAM_USER = "data.user_wppb"
INSTAGRAM_PASSWORD = "Cliford99"

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        try:
            # Navegar a Instagram e iniciar sesión
            await page.goto("https://www.instagram.com/")
            await page.fill("input[name='username']", INSTAGRAM_USER)
            await page.fill("input[name='password']", INSTAGRAM_PASSWORD)
            await page.click("button[type='submit']")
            await page.wait_for_timeout(5000)  # Esperar 5 segundos

            # Intentar cerrar el cuadro de diálogo "Guardar información de inicio de sesión"
            try:
                await page.click('text="Ahora no"', timeout=5000)
            except asyncio.exceptions.TimeoutError:
                print("El cuadro de diálogo 'Ahora no' no estaba presente o no se pudo cerrar.")

            # Intentar cerrar el cuadro de diálogo "Activar notificaciones"
            try:
                await page.click('text="Ahora no"', timeout=5000)
            except asyncio.exceptions.TimeoutError:
                print("El cuadro de diálogo 'Activar notificaciones' no estaba presente o no se pudo cerrar.")

            # Esperar a que la casilla de búsqueda esté presente y visible
            await page.wait_for_selector('input[placeholder="Buscar"]', state="visible")

            # Hacer clic en la casilla de búsqueda
            await page.click('input[placeholder="Buscar"]')

            # Escribir en la casilla de búsqueda letra por letra
            search_query = "rappicolombia"
            for letter in search_query:
                await page.type('input[placeholder="Buscar"]', letter)
                await page.wait_for_timeout(500)  # Esperar medio segundo entre cada letra

            # Esperar 3 segundos para que los resultados de la búsqueda se carguen
            await page.wait_for_timeout(3000)

            # Hacer clic en el primer resultado de la búsqueda
            await page.click('a[href^="/rappicolombia/"]', timeout=5000)

            # Esperar 6 segundos con el perfil abierto
            await page.wait_for_timeout(6000)

        except Exception as e:
            print(f"Error: {e}")
            traceback.print_exc()
        finally:
            # Cerrar sesión y el navegador
            await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
