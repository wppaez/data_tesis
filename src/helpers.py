import asyncio
from typing import Literal
from playwright.async_api import Page

NAVIGATION_DELAY = 10000

MESSAGES = {
    "NOT_NOW": "El cuadro de diálogo 'Ahora no' no estaba presente o no se pudo cerrar.",
    "NOTIFICATIONS": "El cuadro de diálogo 'Activar notificaciones' no estaba presente o no se pudo cerrar.",
}


async def close_not_now(
    page: Page, kind: Literal["NOT_NOW", "NOTIFICATIONS"] = "NOT_NOW"
):
    """Closes a dialog that contains the "Not now" or the "Ahora no" text content,

    Args:
        page (Page): Playwright page instance
        kind (Literal[&quot;NOT_NOW&quot;, &quot;NOTIFICATIONS&quot;], optional): Message to print. Defaults to "NOT_NOW".
    """
    try:
        ahora_no_is_visible = await page.get_by_role(
            "button", name="Ahora No"
        ).is_visible()

        if ahora_no_is_visible:
            await page.get_by_role("button", name="Ahora No").click()
            return

        not_now_is_visible = await page.get_by_role(
            "button", name="Not Now"
        ).is_visible()

        if not_now_is_visible:
            await page.get_by_role("button", name="Not Now").click()
            return

    except asyncio.exceptions.TimeoutError:
        print(MESSAGES[kind])

    finally:
        return


async def login(page: Page, username: str, password: str):
    # Navegar a Instagram e iniciar sesión
    await page.goto("https://www.instagram.com/")
    await page.fill("input[name='username']", username)
    await page.fill("input[name='password']", password)
    await page.click("button[type='submit']")
    await page.wait_for_timeout(NAVIGATION_DELAY)

    # Cerrar diálogos
    await close_not_now(page)
    await page.wait_for_timeout(NAVIGATION_DELAY)

    await close_not_now(page, "NOTIFICATIONS")
    return


async def go_to_profile(page: Page, profile: str):
    # Buscar
    await page.get_by_role("link", name="Search Search").click()
    await page.wait_for_timeout(NAVIGATION_DELAY)
    await page.get_by_placeholder("Search").click()
    await page.get_by_placeholder("Search").fill(profile)
    await page.keyboard.press("Enter")

    # Ir al perfil
    await page.click(f"a[href='/{profile}/']")
    await page.wait_for_timeout(NAVIGATION_DELAY)

    # Ir a la sección de publicaciones (posts)
    await page.get_by_role("tab", name="Posts").click()
    await page.wait_for_timeout(NAVIGATION_DELAY)
    return


async def get_profile_posts(page: Page) -> list[str]:
    # Obtener el número total de posts
    total_posts_text = await page.locator(
        '[role="main"] section ul :nth-child(1)'
    ).first.text_content()
    total_posts = int((total_posts_text or "").replace("posts", ""))
    print(f"Total number of posts: {total_posts}")

    # Extraer todos los posts
    posts = await page.locator('[role="main"] [role="tablist"] ~ div a').count()
    hrefs = []
    while posts < total_posts:
        links_query = '[role="main"] [role="tablist"] ~ div a'
        links = await page.locator(links_query).all()
        href_cache = [await link.get_attribute("href") for link in links[-12:]]
        hrefs.extend(href_cache)
        await page.keyboard.press("End")
        await page.wait_for_timeout(3000)
        posts += 12
        print(posts, total_posts, len(hrefs))

    links = await page.locator('[role="main"] [role="tablist"] ~ div a').all()
    remaining = total_posts - len(hrefs)
    href_cache = [await link.get_attribute("href") for link in links[-remaining:]]
    hrefs.extend(href_cache)

    # Completar el link de los posts
    profile_url = page.url
    links_to_visit = [f"{profile_url}/{href}".replace("///", "/") for href in hrefs]

    return links_to_visit
