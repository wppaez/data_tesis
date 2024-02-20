import asyncio
import traceback
from playwright.async_api import async_playwright
from dotenv import load_dotenv
from helpers import login, go_to_profile, get_profile_posts

load_dotenv()

# Variables de entorno
INSTAGRAM_USER = "data.user_wppb"
INSTAGRAM_PASSWORD = "Cliford99"
NAVIGATION_DELAY = 10000


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(locale="en-US")
        page = await context.new_page()

        try:
            # Iniciar sesión
            await login(page, INSTAGRAM_USER, INSTAGRAM_PASSWORD)

            # Ir a un perfil
            await go_to_profile(page, "rappicolombia")

            # Obtener links de los posts
            links_to_visit = await get_profile_posts(page)

            link_to_visit = links_to_visit[0]
            is_reel = "/reel/" in link_to_visit
            post_tab = await context.new_page()
            await post_tab.goto(link_to_visit)
            await post_tab.wait_for_timeout(NAVIGATION_DELAY)
            await post_tab.wait_for_timeout(NAVIGATION_DELAY)
            comments_wrapper = await page.locator(
                '[role="main"] [role="presentation"] [role="presentation"] ul > [role="button"]'
            ).all()
            print(len(comments_wrapper))
            # caption = comments_wrapper[0] # for some reason doesn't work
            await post_tab.pause()

            print(links_to_visit)
            print(len(links_to_visit))

            # Cerrar sesión
            await page.goto("https://www.instagram.com/accounts/logout/")
            await page.wait_for_timeout(NAVIGATION_DELAY)

        except Exception as e:
            traceback.print_exc()
        finally:
            await browser.close()


# Ejecuta la función principal
asyncio.run(main())
