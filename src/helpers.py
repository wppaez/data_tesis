import os
import csv
import asyncio
from re import findall
from datetime import date, timedelta, datetime
from typing import Literal, TypedDict
from playwright.async_api import Page, BrowserContext

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


class InstagramComment(TypedDict):
    link: str
    date: str
    caption: str
    comment: str
    comment_date: str


def includes_month(date_str: str | None) -> bool:
    if date_str is None:
        return False

    has_month = any(
        month_str.lower() in date_str.lower()
        for month_str in [
            "January",
            "February",
            "March",
            "April",
            "May",
            "June",
            "July",
            "August",
            "September",
            "October",
            "November",
            "December",
        ]
    )

    return has_month


def get_month(date_str: str) -> int | None:
    months = [
        "January",
        "February",
        "March",
        "April",
        "May",
        "June",
        "July",
        "August",
        "September",
        "October",
        "November",
        "December",
    ]
    for month_str in months:
        if month_str.lower() in date_str.lower():
            return months.index(month_str) + 1
    return None


def parse_date(
    date_str: str | None = None,
    offset: str | None = None,
    fixed_in_year: str | None = None,
) -> str:
    format = "%Y-%m-%d"
    date_to_parse = date_str or date.today().strftime(format)

    if not fixed_in_year is None:
        year_bits = [int(s) for s in findall(r"\d{4}", fixed_in_year)]
        year_bit = (
            str(datetime.now().year) if len(year_bits) == 0 else str(year_bits[0])
        )
        date_bits = [int(s) for s in findall(r"\b\d+\b", fixed_in_year)]
        date_bit = str(date_bits[0])
        month_bit = str(get_month(fixed_in_year))

        return f"{year_bit}-{month_bit.zfill(2)}-{date_bit.zfill(2)}"

    if offset is None:
        return date_to_parse

    expected_date = datetime.strptime(date_to_parse, format)
    if "days ago" in offset:
        expected_date = expected_date - timedelta(
            days=int(offset.replace("days ago", "").strip())
        )
    elif "day ago" in offset:
        expected_date = expected_date - timedelta(
            days=int(offset.replace("day ago", "").strip())
        )
    elif "h" in offset:
        expected_date = expected_date - timedelta(
            hours=int(offset.replace("h", "").strip())
        )
    elif "d" in offset:
        expected_date = expected_date - timedelta(
            days=int(offset.replace("d", "").strip())
        )
    elif "w" in offset:
        expected_date = expected_date - timedelta(
            weeks=int(offset.replace("w", "").strip())
        )

    return expected_date.strftime(format)


async def get_post_comments(
    context: BrowserContext, post_link: str
) -> list[InstagramComment]:
    # Ir al post
    post_tab = await context.new_page()
    await post_tab.goto(post_link)
    await post_tab.wait_for_timeout(NAVIGATION_DELAY)

    # Configurar queries
    drawer_query = '[role="main"] [role="presentation"] [role="presentation"]'
    date_query = f"{drawer_query} time"
    comment_query = f'{drawer_query} ul > [role="button"]'
    caption_query = "h1"
    content_query = 'h3 ~ div > span[dir="auto"]'
    comment_date_query = "time"

    # Cargar todos los comentarios
    load_more_comments_is_visible = await post_tab.get_by_role(
        "button", name="Load more comments"
    ).is_visible()

    while load_more_comments_is_visible:
        await post_tab.get_by_role(
            "button", name="Load more comments"
        ).scroll_into_view_if_needed()
        await post_tab.get_by_role("button", name="Load more comments").click()
        await post_tab.wait_for_timeout(3000)

        load_more_comments_is_visible = await post_tab.get_by_role(
            "button", name="Load more comments"
        ).is_visible()

    # Cargar comentarios ocultos
    hidden_comments_is_visible = await post_tab.get_by_role(
        "button", name="View hidden comments"
    ).is_visible()

    while hidden_comments_is_visible:
        await post_tab.get_by_role(
            "button", name="View hidden comments"
        ).scroll_into_view_if_needed()
        await post_tab.get_by_role("button", name="View hidden comments").click()
        await post_tab.wait_for_timeout(3000)

        hidden_comments_is_visible = await post_tab.get_by_role(
            "button", name="View hidden comments"
        ).is_visible()

    # Cargar respuestas a comentarios
    view_replies_count = await post_tab.get_by_role(
        "button", name="View replies"
    ).count()

    while view_replies_count > 0:
        view_replies_buttons = await post_tab.get_by_role(
            "button", name="View replies"
        ).all()

        # Cargar respuesta por cada lista de respuestas a cargar
        for view_reply_button in view_replies_buttons:
            view_reply_is_visible = await view_reply_button.is_visible()
            if not view_reply_is_visible:
                continue

            await view_reply_button.scroll_into_view_if_needed()
            await view_reply_button.click()
            await post_tab.wait_for_timeout(3000)

        # Revisar si aun tenemos respuestas por cargar
        view_replies_count = await post_tab.get_by_role(
            "button", name="View replies"
        ).count()

    # Obtener la fecha
    post_date = await post_tab.locator(date_query).last.text_content()
    if post_date is None:
        raise LookupError("Couldn't find post's date")

    post_date_has_month = includes_month(post_date)
    formatted_post_date = parse_date(
        fixed_in_year=post_date if post_date_has_month else None,
        offset=None if post_date_has_month else post_date,
    )

    comments_wrapper = await post_tab.locator(comment_query).all()

    # Obtener caption
    caption_wrapper = comments_wrapper.pop(0)
    post_caption = await caption_wrapper.locator(caption_query).first.text_content()
    if post_caption is None:
        raise LookupError("Couldn't find post's caption")

    # Extraer comentarios
    comments: list[InstagramComment] = []
    for comment_wrapper in comments_wrapper:
        comment = await comment_wrapper.locator(content_query).first.text_content()
        comment_date = await comment_wrapper.locator(
            comment_date_query
        ).first.text_content()
        if comment is None or comment_date is None:
            continue

        formatted_comment_date = parse_date(offset=comment_date)
        ig_comment: InstagramComment = {
            "link": post_link,
            "date": formatted_post_date,
            "caption": post_caption,
            "comment": comment,
            "comment_date": formatted_comment_date,
        }

        comments.append(ig_comment)

    await post_tab.close()

    return comments


def save_to_csv(account: str, link: str, ig_comments: list[InstagramComment]):
    folder = "./output"
    csv_headers = ["link", "date", "caption", "comment", "comment_date"]

    # Definir la ruta del archivo
    last_slash = link.rfind("/", 0, -1)
    post_id = link[last_slash:].replace("/", "").strip()
    filename = f"{post_id}.csv"

    # Definir la ruta del archivo
    if not os.path.exists(folder):
        os.makedirs(folder)
    if not os.path.exists(f"{folder}/{account}"):
        os.makedirs(f"{folder}/{account}")

    # Borrar archivo si ya existe
    try:
        os.remove(f"{folder}/{account}/{filename}")
    except:
        pass

    # Escribir archivo
    output_csv = open(
        f"{folder}/{account}/{filename}", "w", encoding="utf-8", newline=""
    )

    writer = csv.DictWriter(output_csv, fieldnames=csv_headers)
    writer.writeheader()
    writer.writerows(ig_comments)
    output_csv.close()

    output_csv.close()
    return
