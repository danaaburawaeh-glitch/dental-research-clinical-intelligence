# التنصيب — العربية

**Dental Research & Clinical Intelligence by Dr. Dana** · الإصدار 1.0.2

ثلاثة طرق بحسب مستوى الخبرة. أغلب المستخدمين يحتاجون **الطريقة أ**.

---

## أ. التنصيب عبر المتجر (الطريقة المعتادة)

تحتاجين إلى Claude Code مثبَّتاً ومسجَّلاً دخوله. **ولا تحتاجين إلى حساب GitHub.**

```bash
claude plugin marketplace add danaaburawaeh-glitch/dental-research-clinical-intelligence
claude plugin install dana-dental-research@dana-dental
```

للتحقق:

```bash
claude plugin list                          # المتوقَّع: الإصدار 1.0.2، مُفعَّل
claude plugin details dana-dental-research  # المتوقَّع: Skills (9)
```

للبدء:

```bash
claude
```
```
/dana-dental-research:start
```

للتحديث لاحقاً:

```bash
claude plugin marketplace update dana-dental
claude plugin install dana-dental-research@dana-dental
```

---

## ب. دليل المبتدئات (بدون Terminal)

إذا لم تكن كتابة الأوامر مألوفة لك، استخدمي المنصِّب الرسومي: حمّلي ملف `.pkg`، وانقري نقراً
مزدوجاً، ثم Continue، ثم Install. سينفّذ الأمرين أعلاه نيابةً عنك.

ولأن المنصِّب **غير موقَّع من Apple**، سيظهر تحذير عند أول فتح. انقري بالزر الأيمن على الملف ←
**Open** ← **Open**، أو اسمحي به من **System Settings ← Privacy & Security ← Open Anyway**.

الشرح الكامل بالعربية يأتي مع المنصِّب في ملف `INSTALL_WITHOUT_TERMINAL_AR.md`.

---

## ج. التنصيب المحلي (للمطوّرين)

للعمل على الإضافة أو تجربة تعديل غير منشور:

```bash
git clone https://github.com/danaaburawaeh-glitch/dental-research-clinical-intelligence.git
claude plugin marketplace add /absolute/path/to/dental-research-clinical-intelligence
claude plugin install dana-dental-research@dana-dental
```

هذا يسجّل نسختك المحلية، فتسري التعديلات عند
`claude plugin marketplace update dana-dental`. مناسب للتطوير، وغير مناسب للاستخدام الفعلي — لأن
التنصيب يصبح معتمداً على مجلد قد تنقلينه أو تحذفينه.

للتحقق من ملف الإصدار المُحمَّل:

```bash
cd releases && shasum -a 256 -c SHA256SUMS.txt
```

---

## المهارات التسع

| المهارة | ما تفعله |
|---|---|
| `start` | تعرّفك بالنظام وتوجّه سؤالك إلى المسار المناسب |
| `clinical-governance` | تطبّق قواعد السلامة والأدلة والخصوصية والتنظيم |
| `clinical-case` | تحليل حالة كامل عبر التسلسل التشخيصي المحكوم |
| `triage` | تتعامل أولاً مع الأعراض العاجلة والتورم والرضّ والنزف |
| `esthetic-prosthodontics` | تحكم التخطيط التجميلي والتعويضي الثابت الاختياري |
| `treatment-plan-audit` | تراجع خطة قائمة مراجعة عدائية |
| `scientific-problem-selection` | تساعد في اختيار سؤال بحثي وتقليل مخاطره |
| `evidence-research` | تسترجع الأدلة المنشورة وتتحقق منها وتقيّمها |
| `quality-control` | تفحص المخرَج قبل الاعتماد عليه |

---

## حل المشكلات

| المشكلة | الحل |
|---|---|
| `claude: command not found` | ثبّتي Claude Code ثم أعيدي فتح Terminal |
| المتجر غير موجود | أعيدي تنفيذ أمر `marketplace add` وتحققي من الاتصال |
| الإضافة مثبَّتة لكن المهارات لا تظهر | `claude plugin enable dana-dental-research` ثم أعيدي تشغيل Claude Code |
| فشل البحث | فشل البحث **ليس** دليلاً على عدم وجود دليل. أعيدي المحاولة عند الاتصال |
| `NOT CONNECTED — AUTH REQUIRED` لـ SFDA | متوقَّع. الوضع السعودي يعود بـ«يتطلب تحققاً»؛ تحقّقي مع الهيئة مباشرة |

للإزالة:

```bash
claude plugin uninstall dana-dental-research@dana-dental
claude plugin marketplace remove dana-dental
```
