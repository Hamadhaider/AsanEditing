"""Gemini website automation using a persistent local browser profile.

The first connection opens a visible browser. The user signs in manually. This code
never asks for, stores, or automates a Google password or 2-step verification.
Gemini's website UI can change; selectors intentionally have fallbacks.
"""
import asyncio, base64
from pathlib import Path
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError
from .config import BROWSER_PROFILE, GEMINI_URL

class GeminiBrowser:
    def __init__(self):
        self.playwright = None
        self.context = None
        self.page = None
        self.lock = asyncio.Lock()

    async def connect(self):
        if self.context and self.page and not self.page.is_closed():
            return {"connected": True, "url": self.page.url}
        self.playwright = await async_playwright().start()
        BROWSER_PROFILE.mkdir(parents=True, exist_ok=True)
        self.context = await self.playwright.chromium.launch_persistent_context(
            user_data_dir=str(BROWSER_PROFILE), headless=False,
            viewport={"width": 1440, "height": 960}, args=["--disable-blink-features=AutomationControlled"]
        )
        self.page = self.context.pages[0] if self.context.pages else await self.context.new_page()
        await self.page.goto(GEMINI_URL, wait_until="domcontentloaded")
        return {"connected": True, "url": self.page.url, "instruction": "Sign in manually if prompted, then return to AsanEditing."}

    async def generate_image(self, prompt: str, destination: Path):
        async with self.lock:
            if not self.context or not self.page or self.page.is_closed():
                await self.connect()
            page = self.page
            if "accounts.google.com" in page.url:
                raise RuntimeError("Gemini needs sign-in. Complete Google sign-in in the opened browser, then retry.")
            await page.goto(GEMINI_URL, wait_until="domcontentloaded")
            await page.wait_for_timeout(2500)
            textbox = None
            selectors = [
                'div[contenteditable="true"][role="textbox"]',
                'rich-textarea div[contenteditable="true"]',
                'textarea',
                '[aria-label*="prompt" i]',
            ]
            for selector in selectors:
                loc = page.locator(selector).first
                try:
                    if await loc.is_visible(timeout=1800):
                        textbox = loc
                        break
                except Exception:
                    pass
            if textbox is None:
                raise RuntimeError("Could not find Gemini's prompt box. Gemini may have changed its interface; open the browser and check the page.")
            before = await page.locator("img").count()
            await textbox.click()
            try:
                await textbox.fill(prompt)
            except Exception:
                await page.keyboard.insert_text(prompt)
            await page.keyboard.press("Enter")
            # Wait for Gemini to finish generating; image generation can take a while.
            await page.wait_for_timeout(12000)
            image_bytes = None
            for _ in range(36):
                imgs = page.locator("img")
                count = await imgs.count()
                for i in range(count - 1, max(-1, before - 1), -1):
                    img = imgs.nth(i)
                    try:
                        if not await img.is_visible():
                            continue
                        src = await img.get_attribute("src")
                        if not src or src.startswith("chrome-extension:"):
                            continue
                        data = await img.evaluate("async el => { const r = await fetch(el.src); const b = await r.blob(); return await new Promise((ok, bad) => { const fr = new FileReader(); fr.onload = () => ok(fr.result); fr.onerror = bad; fr.readAsDataURL(b); }); }")
                        if isinstance(data, str) and "," in data:
                            image_bytes = base64.b64decode(data.split(",", 1)[1])
                            if len(image_bytes) > 30000:
                                break
                    except Exception:
                        continue
                if image_bytes:
                    break
                await page.wait_for_timeout(5000)
            if not image_bytes:
                raise RuntimeError("Gemini did not expose a downloadable generated image. Check the open Gemini tab; it may need a manual confirmation or the interface may have changed.")
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(image_bytes)
            return destination

    async def close(self):
        if self.context:
            await self.context.close()
        if self.playwright:
            await self.playwright.stop()
        self.context = self.page = self.playwright = None

browser = GeminiBrowser()
