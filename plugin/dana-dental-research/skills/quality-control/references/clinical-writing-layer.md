<!--
REFERENCE-ID: clinical-writing-layer
VERSION: 1.2.1
CANONICAL-OWNER: clinical-governance
LAST-SYNCHRONIZED: 2026-09-02
Executable layer: clinical/clinical_writing.py.
-->

# Clinical Writing Layer

Loaded by: every skill that produces clinician-facing output.

## The separation

The engine reasons in labels — `HARD_BLOCKER`, `INSUFFICIENT_FOR_IRREVERSIBLE_TREATMENT`,
`POTENTIALLY_COMPROMISED`, `driver_problem_identified`. Those labels are load-bearing and they
stay. **What must not survive to the page is the label itself.**

A clinician handed `SUFFICIENCY: PARTIALLY_SUFFICIENT / HARD BLOCKER: YES / DRIVER_PROBLEM:
UNKNOWN` has received a debugging trace and been asked to do the translation themselves. The
system already did the reasoning; making the reader decode it wastes the work and obscures the one
thing they came for.

**Internal rigour unchanged. External language clinical.**

## Modes

| Mode | For |
|---|---|
| **CLINICAL** *(default)* | Natural clinician-facing consultation |
| ACADEMIC | More references, methodology, evidence strength |
| TEACHING | Explains why each decision is made |
| AUDIT | Internal gates, blockers, provenance, decision profiles |
| TECHNICAL | Developer / debug representation |

CLINICAL is used unless the clinician explicitly asks for audit, technical, governance, developer
or debug output. An unrecognised request falls back to CLINICAL, never to the most verbose mode.

## Translation, not exposure

| Internal | Clinician-facing |
|---|---|
| `HARD BLOCKER` | هذه المعلومة ضرورية قبل اتخاذ هذا القرار |
| `DECISION MODIFIER` | هذا العامل قد يغيّر اختيار العلاج أو ترتيبه |
| `RISK MODIFIER` | هذا العامل يرفع مستوى الخطورة لكنه لا يمنع العلاج تلقائيًا |
| `PLANNING REFINER` | هذه المعلومة تساعد في تحسين التصميم النهائي لكنها لا تمنع القرار الحالي |
| `UNDETERMINED` | لا يمكن تحديد الإنذار بدقة بعد |
| `POTENTIALLY_COMPROMISED` | الإنذار قد يكون أقل ملاءمة، ويحتاج تأكيد العوامل المؤثرة |
| `ELECTIVE_BUT_ACCEPTABLE` | العلاج اختياري وليس له استطباب بيولوجي، لكنه قد يكون مقبولًا بعد مناقشة التكلفة البيولوجية والبدائل |
| `DO_NOT_PROCEED` | لا أنصح بالمضي بهذا الخيار في الوضع الحالي |
| `INSUFFICIENT_FOR_IRREVERSIBLE_TREATMENT` | المعطيات الحالية كافية لتحديد الاتجاه العلاجي المحافظ، لكنها غير كافية بعد لاعتماد تحضير نهائي غير قابل للرجوع |

## Lead with the clinical message

The first visible paragraphs answer: **what do I think, why, and what should happen next.**

Never open an ordinary clinician-facing answer with data-sufficiency counts, red-flag counts,
field-completion percentages, internal case-state names or protocol codes.

## Structure — used, not emitted

التقييم السريري · المشكلة الرئيسية · التشخيص التفريقي · تفسير المعطيات الحالية · القرار السريري
الحالي · خطة العلاج وتسلسلها · البدائل · ما الذي قد يغيّر القرار · الإنذار · الأدلة العلمية
وحدودها · الخلاصة السريرية

Only **المشكلة الرئيسية** and **القرار السريري الحالي** are always required. A simple question
gets a short answer. Emitting eleven headings for a one-line question is the same failure as
emitting forty missing-data fields.

## Claim calibration

Use: تشير المعطيات إلى · يرفع الاحتمال · يتوافق مع · يُرجَّح · قد يكون عاملًا مساهمًا · تدعمه
الأدلة بدرجة · لا يمكن إثبات · لا يوجد ما يبرر افتراض

Avoid unless genuinely justified: يثبت · يؤكد قطعًا · دائمًا · حتمًا · السبب المباشر · الحل
الوحيد. A **negated** absolute — "لا يثبت" — is calibrated language, not an overclaim.

## Patient preference

Never adversarial. Prefer: *تفضيل المريضة مفهوم، لكنه لا يشكل بحد ذاته استطبابًا سريريًا* ·
*يمكن احترام الهدف الجمالي مع مناقشة التكلفة البيولوجية والبدائل* · *إذا اختارت المريضة المسار
الاختياري بعد موافقة مستنيرة، فيجب توثيق ذلك بوضوح*.

## Evidence presentation

Do not scatter `VERIFIED` / `DIRECT` / `MODERATE` / `L2` through the prose. Write the clinical
paragraph, then — where it helps — one compact line:

> Evidence: Systematic review · Citation verified · Moderate certainty · Partially direct

Citations support important claims; they do not interrupt every sentence. The numeric evidence
gate is unchanged.

## Red flags, proportionally

In a stable elective case with no emergency signal: *لا توجد في المعطيات الحالية مؤشرات إسعافية
واضحة* — then move on. Expand only when clinically relevant.

## What this layer does NOT change

Decision profiles, safety gates, contextual relevance, evidence verification, certainty,
directness, the numeric evidence gate, provenance and risk classification are all unchanged. Only
their translation into clinician-facing prose changed.
