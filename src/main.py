import asyncio
import traceback
from playwright.async_api import async_playwright
from dotenv import load_dotenv
from helpers import close_not_now

load_dotenv()

# Variables de entorno
INSTAGRAM_USER = "data.user_wppb"
INSTAGRAM_PASSWORD = "Cliford99"
NAVIGATION_DELAY = 3000


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        try:
            # Navegar a Instagram e iniciar sesión
            await page.goto("https://www.instagram.com/")
            await page.fill("input[name='username']", INSTAGRAM_USER)
            await page.fill("input[name='password']", INSTAGRAM_PASSWORD)
            await page.click("button[type='submit']")
            await page.wait_for_timeout(NAVIGATION_DELAY)

            # Close dialogs
            await close_not_now(page)
            await page.wait_for_timeout(NAVIGATION_DELAY)

            await close_not_now(page, "NOTIFICATIONS")

            # Search a profile
            await page.get_by_role("link", name="Search Search").click()
            await page.wait_for_timeout(NAVIGATION_DELAY)

            profile_id = "rappicolombia"
            await page.get_by_placeholder("Search").click()
            await page.get_by_placeholder("Search").fill(profile_id)
            await page.keyboard.press("Enter")

            # Go to profile
            await page.get_by_role(
                "link", name=f"{profile_id}'s profile picture", exact=True
            ).click()
            await page.wait_for_timeout(NAVIGATION_DELAY)

            # Si necesitas averiguar como encontrar un elemento puedes usar esto:
            await page.pause()
            # Para salir del page.pause, en la terminal presionas CTRL + C, dos veces

        except Exception as e:
            print(f"Error: {e}")
            traceback.print_exc()
        finally:
            # Cerrar sesión y el navegador
            await page.close()
            await context.close()
            await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
