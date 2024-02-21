import asyncio
import traceback
from playwright.async_api import async_playwright
from dotenv import load_dotenv
from helpers import login, go_to_profile, get_profile_posts, get_post_comments

load_dotenv()

# Variables de entorno
INSTAGRAM_USER = "data.user_wppb"
INSTAGRAM_PASSWORD = "Cliford99"
NAVIGATION_DELAY = 10000
FIRST_link = "https://www.instagram.com/rappicolombia/p/C3gJ28MOAEr/"


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(locale="en-US")
        page = await context.new_page()

        try:
            # Iniciar sesión
            await login(page, INSTAGRAM_USER, INSTAGRAM_PASSWORD)

            # Ir a un perfil
            # await go_to_profile(page, "rappicolombia")

            # Obtener links de los posts
            # links_to_visit = await get_profile_posts(page)

            # Obtener los datos de cada post:
            # for link_to_visit in links_to_visit:
            #     (caption, comments) = await get_post_comments(context, link_to_visit)

            link_to_visit = FIRST_link
            (caption, comments) = await get_post_comments(context, link_to_visit)

            print(caption)
            print(comments)

            await page.pause()

            # Cerrar sesión
            await page.goto("https://www.instagram.com/accounts/logout/")
            await page.wait_for_timeout(NAVIGATION_DELAY)

        except Exception as e:
            traceback.print_exc()
        finally:
            await browser.close()


# Ejecuta la función principal
asyncio.run(main())
