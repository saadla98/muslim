<div dir="rtl">

# 🕌 بوت الأذكار والأدعية — Telegram

بوت تيليگرام احترافي يقدّم **الأذكار والأدعية الصحيحة** من السنّة النبوية، بالعربية، عبر قوائم أنيقة وبحث ذكيّ بالكتابة.

</div>

---

## ✨ المميّزات

- 📿 **12 تصنيفًا (أكثر من 150 ذكرًا ودعاءً):** أذكار الصباح، المساء، النوم، الاستيقاظ، الأذان، أذكار الصلاة (داخلها)، بعد الصلاة، التسبيح والذكر المطلق، أدعية الحياة اليومية، أدعية من القرآن، أذكار الحج والعمرة، وأدعية متنوّعة.
- 🔎 **بحث بالكتابة:** يكتب المستخدم «دعاء الخروج من المنزل» فيجيبه البوت مباشرةً — يعمل بتشكيل أو بدونه.
- 🎛️ **واجهة أزرار (Inline Keyboards):** تصفّح سهل بين التصنيفات والأدعية.
- 🖋️ **عرض واضح:** نصّ الدعاء داخل اقتباس (blockquote) مع فاصل أنيق ثم التكرار والفضل والمصدر.
- 📚 **مصدر لكل ذكر:** (البخاري، مسلم، السنن مع تصحيح الألباني…) وعدد التكرار والفضل.
- ⚙️ أوامر منظّمة: `/start` `/menu` `/search` `/help` + أمر لكل تصنيف.

---

<div dir="rtl">

## 🗂️ هيكلة المشروع

```
telegram-bot/
├── run.py                  ← نقطة التشغيل
├── requirements.txt
├── .env.example            ← انسخه إلى .env وضع التوكن
├── data/                   ← قاعدة بيانات الأذكار (JSON)
│   ├── categories.json
│   ├── adhkar_sabah.json
│   ├── adhkar_masaa.json
│   ├── adhkar_nawm.json
│   ├── adhkar_istiqadh.json
│   ├── adhkar_adhan.json
│   ├── adhkar_salah_fi.json
│   ├── adhkar_salah.json
│   ├── adhkar_dhikr.json
│   ├── adiyah_yawmiyyah.json
│   ├── adiyah_quraniyyah.json
│   ├── adhkar_hajj.json
│   └── adiyah_mutafarriqah.json
└── src/
    ├── config.py           ← الإعدادات و.env
    ├── data_loader.py      ← تحميل البيانات + محرّك البحث
    ├── texts.py            ← نصوص الواجهة والتنسيق
    ├── keyboards.py        ← لوحات الأزرار
    ├── bot.py              ← بناء التطبيق وتشغيله
    └── handlers/
        ├── commands.py     ← /start /help /menu /search + التصنيفات
        ├── callbacks.py    ← ضغطات الأزرار
        └── search.py       ← البحث بالكتابة
```

</div>

---

## 🚀 التشغيل

### 1) الحصول على توكن

<div dir="rtl">

افتح [@BotFather](https://t.me/BotFather) على تيليگرام → `/newbot` → اتبع الخطوات → انسخ التوكن.

</div>

### 2) الإعداد والتشغيل (Windows / PowerShell)

```powershell
cd telegram-bot
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env       # ثم ضع BOT_TOKEN داخل .env
python run.py
```

### على Linux / macOS

```bash
cd telegram-bot
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # ثم ضع BOT_TOKEN
python run.py
```

---

## 💬 طريقة الاستعمال

| ماذا تفعل | النتيجة |
|-----------|---------|
| `/start` | رسالة ترحيب + القائمة الرئيسية |
| ضغط زرّ تصنيف | قائمة الأذكار داخله |
| كتابة «دعاء السفر» | البوت يرسل الدعاء مباشرة |
| كتابة «أذكار الصباح» | يفتح تصنيف أذكار الصباح |
| `/sabah` , `/masaa` … | فتح تصنيف مباشرةً |

---

<div dir="rtl">

## ➕ إضافة أذكار جديدة

كل ما عليك تعديل ملفّات `data/*.json`. كل مدخل بهذا الشكل:

</div>

```json
{
  "id": "معرّف_فريد",
  "title": "عنوان الدعاء",
  "keywords": ["كلمات", "للبحث"],
  "text": "نصّ الدعاء بالتشكيل",
  "repeat": "عدد المرّات",
  "reference": "المصدر (البخاري / مسلم ...)",
  "benefit": "الفضل (اختياري)"
}
```

<div dir="rtl">

لإضافة **تصنيف جديد**: أضف سطرًا في `categories.json` وأنشئ ملفّ JSON الخاصّ به.

## 📖 ملاحظة شرعية

المحتوى مجموعٌ من مصادر السنّة الصحيحة (حصن المسلم والصحيحين والسنن مع التصحيح)، مع ذكر المرجع. يُرجى مراجعة أهل العلم عند الحاجة، والتنبيه على أي خطأ لإصلاحه.

</div>
