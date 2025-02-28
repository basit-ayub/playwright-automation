import sys
import asyncio
import random
import json
import os
from datetime import datetime
from dataclasses import dataclass
from playwright.async_api import async_playwright
from playwright.async_api import TimeoutError as PlaywrightTimeoutError

#Variables
WEBSITES_TO_VISIT = 3
INSTANCES_COUNT = 10
ELEMENT_SEARCH_TIMEOUT = 3
PAGE_LOAD_TIMEOUT = 60000

#CLI arguments
for i in range(1, len(sys.argv)):
    if sys.argv[i] == "--websites" or sys.argv[i] == "-w":
        WEBSITES_TO_VISIT = int(sys.argv[i + 1])
    elif sys.argv[i] == "--instances" or sys.argv[i] == "-i":
        INSTANCES_COUNT = int(sys.argv[i + 1])

@dataclass
class User:
    user_agent: str
    os_type: str
    timezone: str
    screen_size: dict
    location: dict



USERS = [
    User(  # Windows
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36",
        os_type="Windows",
        timezone="America/New_York",
        screen_size={"width": 1920, "height": 1080},
        location={"latitude": 40.7128, "longitude": -74.0060}
    ),
    User(  # Linux
        user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36",
        os_type="Linux",
        timezone="Europe/Berlin",
        screen_size={"width": 1366, "height": 768},
        location={"latitude": 52.5200, "longitude": 13.4050}
    ),
    User(  # Mac
        user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
        os_type="Mac",
        timezone="Europe/London",
        screen_size={"width": 1440, "height": 900},
        location={"latitude": 51.5074, "longitude": -0.1278}
    ),
    User(  # iOS (iPhone)
        user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/537.36 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/537.36",
        os_type="iOS",
        timezone="America/Los_Angeles",
        screen_size={"width": 375, "height": 812},
        location={"latitude": 34.0522, "longitude": -118.2437}
    ),
    User(  # Android (Samsung Galaxy)
        user_agent="Mozilla/5.0 (Linux; Android 10; SM-G975F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 Mobile Safari/537.36",
        os_type="Android",
        timezone="Asia/Tokyo",
        screen_size={"width": 414, "height": 896},
        location={"latitude": 35.6895, "longitude": 139.6917}
    ),
    User(  # Android (Google Pixel)
        user_agent="Mozilla/5.0 (Linux; Android 11; Pixel 4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.210 Mobile Safari/537.36",
        os_type="Android",
        timezone="Asia/Hong_Kong",
        screen_size={"width": 414, "height": 896},
        location={"latitude": 22.3193, "longitude": 114.1694}
    )
]


WEBSITES = (
    "https://www.w3schools.com",
    "https://www.geeksforgeeks.org",
    "https://www.learnpython.org",
    "https://stackoverflow.com",
    "https://www.codechef.com",
    "https://www.reddit.com"
)

def log_interaction(instance_number, site, action, details):
    log_file_path = f"logs/instance_{instance_number + 1}.json"

    if not os.path.exists("logs"):
        os.makedirs("logs")

    # Load existing logs if the file exists
    if os.path.exists(log_file_path):
        try:
            with open(log_file_path, "r") as log_file:
                logs = json.load(log_file)
        except (json.JSONDecodeError, FileNotFoundError):
            logs = []
    else:
        logs = []

    log_entry = {
        "instance_number": instance_number,
        "timestamp": datetime.now().isoformat(),
        "site": site,
        "action": action,
        "details": details
    }
    logs.append(log_entry)

    # Write updated logs back to the file
    with open(log_file_path, "w") as log_file:
        json.dump(logs, log_file, indent=4)




def get_session_file_path(instance_number):
    return f"sessions/instance_{instance_number + 1}_session.json"


async def save_session_data(context, instance_number):
    session_data = await context.storage_state()
    session_file_path = get_session_file_path(instance_number)

    if not os.path.exists("sessions"):
        os.makedirs("sessions")

    with open(session_file_path, "w") as session_file:
        json.dump(session_data, session_file, indent=4)


async def load_session_data(instance_number):
    session_file_path = get_session_file_path(instance_number)

    if os.path.exists(session_file_path):
        try:
            with open(session_file_path, "r") as session_file:
                return json.load(session_file)
        except (json.JSONDecodeError, FileNotFoundError):
            return None

    return None

async def mouse_movement(page, element):
    box = await element.bounding_box()
    if box:
        x, y = box["x"] + box["width"] / 2, box["y"] + box["height"] / 2
        await page.mouse.move(x, y, steps=random.randint(10, 30))
        await asyncio.sleep(random.uniform(0.2, 1))


async def random_scroll(page):
    for _ in range(random.randint(3, 6)):
        scroll_y = random.randint(200, 800)
        await page.mouse.wheel(0, scroll_y)
        await asyncio.sleep(random.uniform(1, 3))


async def dismiss_popups(page):
    try:
        popups = await page.query_selector_all("button, a, div")
        for popup in popups:
            text = await popup.inner_text()
            if any(phrase in text.lower() for phrase in ["accept", "agree", "okay", "close", "x", "dismiss"]):
                await popup.click()
                await asyncio.sleep(random.uniform(0.5, 1))
                return True
    except Exception:
        pass
    return False


async def random_hover(page, instance_number, site):
    try:
        await dismiss_popups(page)
        elements = await page.query_selector_all("a[href], button:not([disabled])")
        start_time = asyncio.get_event_loop().time()

        while elements and (asyncio.get_event_loop().time() - start_time) < ELEMENT_SEARCH_TIMEOUT:
            element = random.choice(elements)

            if await element.is_visible() and await element.is_enabled():
                if await page.evaluate("el => window.getComputedStyle(el).pointerEvents", element) == "none":
                    continue

                await element.scroll_into_view_if_needed()
                await element.hover()

                element_text = await element.inner_text() if await element.inner_text() else "No text"
                element_tag = await page.evaluate("el => el.tagName", element)

                log_interaction(instance_number, site, "hover", {"tag": element_tag, "text": element_text})
                return

    except AttributeError:
        log_interaction(instance_number, site, "error", {"error": "Hover Element Not Found"})
    except Exception as e:
        log_interaction(instance_number, site, "error", {"error": str(e)})


async def realistic_typing(page, instance_number, site):
    try:
        await dismiss_popups(page)
        inputs = await page.query_selector_all("input[type='text'], textarea")
        start_time = asyncio.get_event_loop().time()

        while inputs and (asyncio.get_event_loop().time() - start_time) < ELEMENT_SEARCH_TIMEOUT:
            input_field = random.choice(inputs)

            if await input_field.is_visible() and await input_field.is_enabled():
                await input_field.scroll_into_view_if_needed()
                await input_field.click()

                text = "What are C++ pointers?"
                for char in text:
                    await input_field.type(char, delay=random.uniform(50, 200))

                log_interaction(instance_number, site, "typing", {"text": text})
                return

    except AttributeError:
        log_interaction(instance_number, site, "error", {"error": "Typing Element Not Found"})
    except Exception as e:
        log_interaction(instance_number, site, "error", {"error": str(e)})


async def random_click(page, instance_number, site):
    try:
        await dismiss_popups(page)
        elements = await page.query_selector_all(
            "a[href], button:not([disabled]), div[role='button'], span[role='button']"
        )

        start_time = asyncio.get_event_loop().time()

        for _ in range(4):
            if (asyncio.get_event_loop().time() - start_time) > ELEMENT_SEARCH_TIMEOUT:
                return

            element = random.choice(elements)

            if await element.is_visible() and await element.is_enabled():
                bounding = await element.bounding_box()
                if bounding:
                    is_obstructed = await page.evaluate(
                        '''(el) => {
                            let rect = el.getBoundingClientRect();
                            let topEl = document.elementFromPoint(rect.x + rect.width / 2, rect.y + rect.height / 2);
                            return topEl !== el;
                        }''', element
                    )
                    if is_obstructed:
                        continue

                element_text = await element.inner_text() if await element.inner_text() else "No text"
                element_tag = await page.evaluate("el => el.tagName", element)

                await mouse_movement(page, element)
                await element.click()
                log_interaction(instance_number, site, "click", {"tag": element_tag, "text": element_text})
                await asyncio.sleep(random.uniform(1, 3))
                return

    except AttributeError:
        log_interaction(instance_number, site, "error", {"error": "Element Not Found"})
    except Exception as e:
        log_interaction(instance_number, site, "error", {"error": str(e)})


async def mimic_browsing(page, instance_number, site):
    start_time = asyncio.get_event_loop().time()
    while (asyncio.get_event_loop().time() - start_time) < random.uniform(35, 45):
        action = random.choice(["scroll", "hover", "click", "typing"])

        if action == "scroll":
            await random_scroll(page)
            log_interaction(instance_number, site, "scroll", {})
        elif action == "hover":
            await random_hover(page, instance_number, site)
        elif action == "click":
            await random_click(page, instance_number, site)
        elif action == "typing":
            await realistic_typing(page, instance_number, site)
            log_interaction(instance_number, site, "typing", {})

        await asyncio.sleep(random.uniform(2, 5))  # Pause between actions


async def close_extra_tabs(context):
    while True:
        await asyncio.sleep(1)
        if len(context.pages) > 1:
            for page in context.pages[1:]:
                await page.close()


async def open_browser(instance_number, p):
    user = random.choice(USERS)
    session_data = await load_session_data(instance_number)

    browser = await p.chromium.launch(headless=True)
    context = await browser.new_context(
        user_agent=user.user_agent,
        geolocation=user.location,
        timezone_id=user.timezone,
        viewport=user.screen_size,
        permissions=["geolocation"],
        color_scheme=random.choice(["light", "dark"]),
        extra_http_headers={"Referer": "https://www.google.com"},
        storage_state=session_data
    )

    await (context.add_init_script
        ("""
        Object.defineProperty(navigator, 'mediaDevices', {
            get: () => ({
                getUserMedia: () => Promise.reject(new Error("WebRTC Disabled")),
                enumerateDevices: () => Promise.resolve([]),
                getDisplayMedia: () => Promise.reject(new Error("Screen sharing blocked")),
            })
        });

        window.RTCPeerConnection = function() {
            console.log("Blocked WebRTC connection attempt");
            return null;
        };

        window.RTCDataChannel = function() {
            console.log("Blocked RTCDataChannel");
            return null;
        };
    """))

    page = await context.new_page()

    asyncio.create_task(close_extra_tabs(context))

    selected_sites = random.sample(WEBSITES, WEBSITES_TO_VISIT)

    for site in selected_sites:
        try:
            start_time = datetime.now()
            await page.goto(site, timeout=PAGE_LOAD_TIMEOUT, wait_until="domcontentloaded")
            log_interaction(instance_number, site, "visited", {"url": site})

            await mimic_browsing(page, instance_number, site)

            time_spent = (datetime.now() - start_time).total_seconds()
            log_interaction(instance_number, site, "time_spent", {"seconds": time_spent})


        except PlaywrightTimeoutError:
            log_interaction(instance_number, site, "error", {"error": "Page Load Timeout"})
        except Exception as e:
            log_interaction(instance_number, site, "error", {"error": str(e)})

    await save_session_data(context, instance_number)
    await asyncio.sleep(2)
    await context.close()
    await browser.close()


async def main():
    async with async_playwright() as p:
        await asyncio.gather(*(open_browser(i, p) for i in range(INSTANCES_COUNT)))

asyncio.run(main())