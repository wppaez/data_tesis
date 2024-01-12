import time
import asyncio
from playwright.async_api import async_playwright
from dotenv import load_dotenv
import os

load_dotenv()

# Variables de entorno
INSTAGRAM_USER = "data.user_wppb"
INSTAGRAM_PASSWORD = "Cliford99"

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        # Navegar a Instagram
        await page.goto("https://www.instagram.com/")

        # Login
        await page.fill("input[name='username']", INSTAGRAM_USER)
        await page.fill("input[name='password']", INSTAGRAM_PASSWORD)
        await page.click("button[type='submit']")
        await page.wait_for_timeout(5000)  # Esperar 4 segundos

        # Not Now para notificaciones (si aparece)
        if await page.query_selector("button:has-text('Not Now')"):
            await page.click("button:has-text('Not Now')")
            await page.wait_for_timeout(5000)  # Esperar 4 segundos

        # Not Now para más notificaciones (si aparece)
        if await page.query_selector("button:has-text('Not Now')"):
            await page.click("button:has-text('Not Now')")
            await page.wait_for_timeout(5000)  # Esperar 4 segundos

        # Buscar 'rappicolombia'
        await page.click("svg[aria-label='Explore']")
        await page.wait_for_timeout(5000)  # Esperar 5 segundos

        # Introducir texto en la barra de búsqueda y presionar Enter
        await page.fill("input[placeholder='Search']", "rappicolombia")
        await page.press("input[placeholder='Search']", "Enter")
        await page.wait_for_timeout(5000)  # Esperar 4 segundos
        await page.press("input[placeholder='Search']", "Enter")
        await page.wait_for_timeout(5000)  # Esperar 4 segundos

if __name__ == "__main__":
    asyncio.run(main())