import asyncio
import traceback
from playwright.async_api import async_playwright
from dotenv import load_dotenv
from helpers import (
    login,
    go_to_profile,
    get_profile_posts,
    get_post_comments,
    save_to_csv,
)

load_dotenv()

# Variables de entorno
INSTAGRAM_USER = "data.user_wppb"
INSTAGRAM_PASSWORD = "Cliford99"
NAVIGATION_DELAY = 10000
# FIRST_link = "https://www.instagram.com/rappicolombia/p/C3gJ28MOAEr/"
# FIRST_link = "https://www.instagram.com/rappicolombia/p/C3JC1l5OJOY/"


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(locale="en-US")
        page = await context.new_page()

        try:
            # Iniciar sesión
            await login(page, INSTAGRAM_USER, INSTAGRAM_PASSWORD)
            account = "rappicolombia"

            # Ir a un perfil
            await go_to_profile(page, account)

            # Obtener links de los posts
            links_to_visit = await get_profile_posts(page)

            # Obtener los datos de cada post:
            for link_to_visit in links_to_visit:
                print(f"Getting comments from: {link_to_visit}")
                ig_comments = await get_post_comments(context, link_to_visit)
                save_to_csv(
                    account=account, link=link_to_visit, ig_comments=ig_comments
                )

            # Cerrar sesión
            await page.goto("https://www.instagram.com/accounts/logout/")
            await page.wait_for_timeout(NAVIGATION_DELAY)

            await browser.close()

        except Exception as e:
            await browser.close()
            print("-----")
            print(e)
            print("-----")
            traceback.print_exc()


# Ejecuta la función principal
asyncio.run(main())
