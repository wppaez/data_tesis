import asyncio
import traceback
from playwright.async_api import async_playwright
from dotenv import load_dotenv
from helpers import close_not_now

load_dotenv()

# Variables de entorno
INSTAGRAM_USER = "data.user_wppb"
INSTAGRAM_PASSWORD = "Cliford99"
NAVIGATION_DELAY = 10000

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(locale='en-US')
        page = await context.new_page()

        try:
            # Navegar a Instagram e iniciar sesión
            await page.goto("https://www.instagram.com/")
            await page.fill("input[name='username']", INSTAGRAM_USER)
            await page.fill("input[name='password']", INSTAGRAM_PASSWORD)
            await page.click("button[type='submit']")
            await page.wait_for_timeout(NAVIGATION_DELAY)

            # Cerrar diálogos
            await close_not_now(page)
            await page.wait_for_timeout(NAVIGATION_DELAY)

            await close_not_now(page, "NOTIFICATIONS")

            # Buscar un perfil
            await page.get_by_role("link", name="Search Search").click()
            await page.wait_for_timeout(NAVIGATION_DELAY)

            profile_id = "rappicolombia"
            await page.get_by_placeholder("Search").click()
            await page.get_by_placeholder("Search").fill(profile_id)
            await page.keyboard.press("Enter")

            # Ir al perfil
            await page.click(f"a[href='/{profile_id}/']")
            await page.wait_for_timeout(NAVIGATION_DELAY)

            # Ir a la sección de publicaciones (posts)
            await page.get_by_role("tab", name="Posts").click()
            await page.wait_for_timeout(NAVIGATION_DELAY)

            # Obtener el número total de posts
            total_posts = await page.evaluate(
                """() => {
                    const totalPostsElement = document.querySelector("span._ac2a span.html-span");
                    return totalPostsElement ? parseInt(totalPostsElement.innerText) : 0;
                }"""
            )
            print(f"Total number of posts: {total_posts}")

            # Hacer clic en cada post visible y extraer comentarios
            posts = await page.locator('[role="main"] [role="tablist"] ~ div a').count()
            links_to_visit = []
            while posts < total_posts:
                links = await page.locator('[role="main"] [role="tablist"] ~ div a').all()
                hrefs = [await link.get_attribute('href') for link in links[-12:]]
                links_to_visit.extend(hrefs)
                await page.keyboard.press("End")
                await page.wait_for_timeout(3000)
                posts += 12
                print(posts,total_posts, len(links_to_visit))
            
            links = await page.locator('[role="main"] [role="tablist"] ~ div a').all()
            remaining = posts - total_posts 
            hrefs = [await link.get_attribute('href') for link in links[-remaining:]]
            links_to_visit.extend(hrefs)
            print(links_to_visit)
                
            
            # Cerrar sesión
            await page.goto("https://www.instagram.com/accounts/logout/")
            await page.wait_for_timeout(NAVIGATION_DELAY)

        except Exception as e:
            traceback.print_exc()
        finally:
            await browser.close()

# Ejecuta la función principal
asyncio.run(main())
