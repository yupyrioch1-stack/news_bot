import feedparser
import requests
from bs4 import BeautifulSoup
from telegram import Bot
import asyncio
import os

# --- [ဖြည့်စွက်ရန်] ---
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
DB_FILE = "sent_news_database.txt"

# RSS သတင်းရင်းမြစ်များ
RSS_SOURCES = [
    "https://gcaptain.com/feed/",
    "https://www.marineinsight.com/feed/",
    "https://maritime-executive.com/rss"
]

# DMA Scraping URL
DMA_URL = "https://dma.gov.mm/category/seafarers/seafarer-news/"

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
            for entry in feed.entries[:3]: # တစ်ဆိုဒ်ကို ၃ ခုစီပဲ စစ်မယ်
                if entry.link not in sent_links:
                    message = f"⚓ **{entry.title}**\n\n🔗 Read More: {entry.link}"
                    await bot.send_message(chat_id=CHANNEL_ID, text=message, parse_mode='Markdown')
                    save_sent_link(entry.link)
                    sent_links.add(entry.link)
                    await asyncio.sleep(1) # Spam မဖြစ်အောင် ၁ စက္ကန့်နား
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