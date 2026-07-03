<div dir="rtl">

# 🕌 مشروع muslim

مشروع إسلامي كبير — يُبنى وِحدة (module) بوِحدة، كل وِحدة فـ folder مستقل، بجودة احترافية وتاريخ git منظّم.

</div>

---

## 📦 الوحدات (Modules)

| الوحدة | الوصف | الحالة |
|--------|-------|--------|
| [`telegram-bot/`](./telegram-bot) | بوت تيليگرام للأذكار والأدعية الصحيحة بالعربية (قوائم + بحث) | ✅ v1 |
| _(قادم)_ | وحدات إضافية حسب خارطة الطريق | ⏳ |

<div dir="rtl">

## 🗂️ الهيكلة

```
muslim/
├── README.md            ← هذا الملف
├── TODO.md              ← خارطة الطريق والمهام
├── LICENSE
├── .gitignore
└── telegram-bot/        ← الوحدة الأولى: بوت الأذكار والأدعية
```

## 🌿 طريقة العمل مع git (Workflow)

- كل مهمة/ميزة تُنجَز فـ **branch مستقل** (مثال: `feature/telegram-bot`).
- بعد الانتهاء والاختبار → **merge** فـ `main`.
- الـ remote:

```
origin → https://github.com/saadla98/muslim.git
```

```bash
# مثال دورة عمل مهمة
git checkout -b feature/xxx
#   ... العمل + الاختبار ...
git add -A && git commit -m "feat: ..."
git checkout main && git merge --no-ff feature/xxx
git push origin main
```

</div>

---

## 🚀 تشغيل بوت تيليگرام

<div dir="rtl">

راجع الدليل الكامل: **[`telegram-bot/README.md`](./telegram-bot/README.md)**

</div>

```bash
cd telegram-bot
python -m venv .venv && .venv\Scripts\activate   # Windows
pip install -r requirements.txt
copy .env.example .env    # ثم ضع BOT_TOKEN داخله
python run.py
```

---

<div dir="rtl">

## 📖 ملاحظة حول المحتوى

محتوى الأذكار والأدعية مأخوذ من مصادر السنة الصحيحة (حصن المسلم / الصحيحين / السنن مع التصحيح)، مع ذكر المرجع لكل ذكر. يُستحبّ دائمًا مراجعة أهل العلم.

</div>
