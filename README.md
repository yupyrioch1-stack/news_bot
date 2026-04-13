# ⚓ Maritime News Telegram Bot

ဤ Bot သည် နိုင်ငံတကာ ရေကြောင်းသတင်းရင်းမြစ်များနှင့် မြန်မာ့ရေကြောင်းပို့ဆောင်ရေးညွှန်ကြားမှုဦးစီးဌာန (DMA) တို့မှ သတင်းအသစ်များကို အလိုအလျောက် စုစည်းပြီး Telegram Channel သို့ ပို့ပေးသော Bot ဖြစ်သည်။

---

## 🚀 Features

* **Multi-Source Fetching:** gCaptain, Marine Insight, Maritime Executive နှင့် DMA (Myanmar) တို့မှ သတင်းများကို စုစည်းပေးခြင်း။
* **Auto-Update:** GitHub Actions ကို အသုံးပြု၍ ၂၄ နာရီပတ်လုံး အလိုအလျောက် Run ပေးခြင်း။
* **Duplicate Prevention:** ပို့ပြီးသား သတင်းများကို Database ဖြင့် စစ်ဆေး၍ ထပ်မပို့အောင် ကာကွယ်ထားခြင်း။
* **Clean Formatting:** Telegram တွင် ဖတ်ရလွယ်ကူသော Markdown format ဖြင့် ပို့ပေးခြင်း။

---

## 🛠️ Setup & Installation

၁။ **Repository ကို Fork လုပ်ပါ သို့မဟုတ် Clone လုပ်ပါ:**
   ```bash
   git clone [https://github.com/yupyrioch1-stack/maritime-news-bot.git](https://github.com/yupyrioch1-stack/maritime-news-bot.git)

၂။ လိုအပ်သော Library များသွင်းရန်:
     ```bash
    pip install -r requirements.txt

၃။ GitHub Secrets သတ်မှတ်ရန်:
GitHub Repository Settings > Secrets and variables > Actions တွင် အောက်ပါတို့ကို ထည့်သွင်းပါ-

TELEGRAM_TOKEN: သင်၏ Bot Token

CHANNEL_ID: သင်၏ Telegram Channel Username (ဥပမာ- @my_channel)

၄။ Workflow Permission ပေးရန်:
Settings > Actions > General > Workflow permissions တွင် "Read and write permissions" ကို ရွေးပေးပါ။

📂 Project Structure
news_bot.py: ပင်မ Python code။

.github/workflows/main.yml: အလိုအလျောက် Run စေမည့် GitHub Action configuration။

sent_news_database.txt: ပို့ပြီးသားသတင်းများကို မှတ်သားထားသည့် Database။

requirements.txt: လိုအပ်သော Python libraries များစာရင်း။

💡 Contribution
ဤ Project အား ပိုမိုကောင်းမွန်အောင် ပြင်ဆင်လိုပါက Pull Request ပေးပို့နိုင်ပါသည်။

🏗️ Developed By
Developed & Maintained by @semap.info Providing technical solutions for Myanmar Seafarers.
