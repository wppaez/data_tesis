import asyncio
from typing import Literal
from playwright.async_api import Page

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
