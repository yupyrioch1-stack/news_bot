import feedparser
import requests
from bs4 import BeautifulSoup
from telegram import Bot
import asyncio
import os
from datetime import datetime, timezone

# --- [ဖြည့်စွက်ရန်] ---
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
DB_FILE = "sent_news_database.txt"

# --- SA Fleet Portal (Supabase) ---
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

# RSS သတင်းရင်းမြစ်များ
RSS_SOURCES = [
    "https://gcaptain.com/feed/",
    "https://www.marineinsight.com/feed/",
    "https://maritime-executive.com/rss"
]

# DMA Scraping URL
DMA_URL = "https://dma.gov.mm/category/seafarers/seafarer-news/"


def get_source_name(feed_url):
    """RSS URL ကနေ source name လှလှလေးထုတ်ခြင်း (e.g. gcaptain.com -> Gcaptain)"""
    try:
        domain = feed_url.split("//")[1].split("/")[0].replace("www.", "")
        return domain.split(".")[0].capitalize()
    except Exception:
        return "Maritime News"


def push_to_maritime_news(title, link, summary="", source="Maritime News", published_at=None):
    """SA Fleet Portal ရဲ့ maritime_news table ထဲ article တင်ခြင်း.
    link ကို unique key အဖြစ်သုံးပြီး upsert လုပ်တာမို့ ထပ်ခါထပ်ခါ run ရင်တောင် duplicate မဖြစ်ပါ။"""
    if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
        print("[Supabase] SUPABASE_URL / SUPABASE_SERVICE_KEY မထည့်ရသေးလို့ skip လုပ်လိုက်ပါတယ်")
        return
    url = f"{SUPABASE_URL}/rest/v1/maritime_news"
    headers = {
        "apikey": SUPABASE_SERVICE_KEY,
        "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "resolution=merge-duplicates",
    }
    payload = {
        "title": title,
        "link": link,
        "summary": (summary or "")[:500] or None,
        "source": source,
        "published_at": published_at or datetime.now(timezone.utc).isoformat(),
    }
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=10)
        if resp.status_code not in (200, 201):
            print(f"[Supabase] failed ({source}): {resp.status_code} {resp.text}")
    except Exception as e:
        print(f"[Supabase] error ({source}): {e}")


# ပို့ပြီးသားသတင်းများကို ဖတ်ခြင်း
def get_sent_links():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return set(line.strip() for line in f)
    return set()


# သတင်းအသစ်ကို Database ထဲသိမ်းခြင်း
def save_sent_link(link):
    with open(DB_FILE, "a", encoding="utf-8") as f:
        f.write(link + "\n")


async def fetch_rss_news(bot, sent_links):
    """နိုင်ငံတကာ RSS Feeds များမှ သတင်းယူခြင်း"""
    print("Checking RSS Feeds...")
    for url in RSS_SOURCES:
        try:
            feed = feedparser.parse(url)
            source_name = get_source_name(url)
            for entry in feed.entries[:3]:  # တစ်ဆိုဒ်ကို ၃ ခုစီပဲ စစ်မယ်
                if entry.link not in sent_links:
                    message = f"⚓ **{entry.title}**\n\n🔗 Read More: {entry.link}"
                    await bot.send_message(chat_id=CHANNEL_ID, text=message, parse_mode='Markdown')

                    # --- SA Fleet Portal ထဲ ထပ်တင်ခြင်း ---
                    summary_text = ""
                    if entry.get("summary"):
                        summary_text = BeautifulSoup(entry.summary, "html.parser").get_text().strip()
                    published_at = None
                    if entry.get("published_parsed"):
                        published_at = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc).isoformat()
                    push_to_maritime_news(entry.title, entry.link, summary_text, source_name, published_at)

                    save_sent_link(entry.link)
                    sent_links.add(entry.link)
                    await asyncio.sleep(1)  # Spam မဖြစ်အောင် ၁ စက္ကန့်နား
        except Exception as e:
            print(f"RSS Error ({url}): {e}")


async def fetch_dma_news(bot, sent_links):
    """DMA Website မှ Scraping နည်းဖြင့် သတင်းယူခြင်း"""
    print("Checking DMA News...")
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(DMA_URL, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')

        # WordPress article များကို ရှာခြင်း
        articles = soup.find_all('article', limit=3)
        for article in articles:
            title_tag = article.find('h2')
            link_tag = article.find('a')
            if title_tag and link_tag:
                title = title_tag.get_text(strip=True)
                link = link_tag['href']
                if link not in sent_links:
                    message = f"🇲🇲 **DMA (မြန်မာ့ရေကြောင်း) သတင်း**\n\n📌 {title}\n\n🔗 {link}"
                    await bot.send_message(chat_id=CHANNEL_ID, text=message, parse_mode='Markdown')

                    # --- SA Fleet Portal ထဲ ထပ်တင်ခြင်း ---
                    push_to_maritime_news(title, link, "", "DMA Myanmar")

                    save_sent_link(link)
                    sent_links.add(link)
                    await asyncio.sleep(1)
    except Exception as e:
        print(f"DMA Scraping Error: {e}")


async def main():
    print("--- Multi-Source News Bot Started ---")
    bot = Bot(token=TELEGRAM_TOKEN)
    sent_links = get_sent_links()

    # နှစ်မျိုးလုံးကို တစ်ပြိုင်တည်း စစ်မယ်
    await fetch_rss_news(bot, sent_links)
    await fetch_dma_news(bot, sent_links)
    print("--- Check Completed ---")


if __name__ == "__main__":
    asyncio.run(main())
