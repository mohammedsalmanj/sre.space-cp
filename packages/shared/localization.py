# SRE-Space Localization Dictionary
# Maps English status/log messages to Arabic

TRANSLATIONS = {
    # Scouting
    "Polling OTel traces...": "جاري فحص آثار OTel...",
    "Detected 1 error span.": "تم اكتشاف خطأ واحد.",
    "Detected anomaly -> HTTP 500: Database connection pool exhausted": "تم اكتشاف شذوذ -> HTTP 500: استنفاد تجمع اتصالات قاعدة البيانات",
    "Detected anomaly -> HTTP 500: ZeroDivisionError in quote calculator": "تم اكتشاف شذوذ -> HTTP 500: خطأ في القسمة على صفر في حاسبة العروض",
    
    # CAG
    "Checking Tier-1 Fast Cache for incident FAQ...": "جاري التحقق من ذاكرة التخزين المؤقت السريعة للمستوى الأول...",
    "INSTANT-HIT. Known incident signature.": "ضربة فورية. توقيع حادث معروف.",
    "Attempting to raise incident via GitHub...": "جاري محاولة فتح حادث عبر GitHub...",
    "Incident Raised (Cache Hit) ->": "تم رفع الحادث (إصابة ذاكرة التخزين المؤقت) ->",
    
    # Guardrail
    "Evaluating safety of remediation action...": "جاري تقييم سلامة إجراء الإصلاح...",
    "Action ALLOWED. Action is reversible and safe.": "الإجراء مسموح به. الإجراء يمكن التراجع عنه وآمن.",
    
    # Fixer
    "Analysis: Remediation Type identified as": "التحليل: تم تحديد نوع الإصلاح كـ",
    "Initiating Autonomous Lifecycle...": "جاري بدء دورة الحياة المستقلة...",
    "Branch Created:": "تم إنشاء الفرع:",
    "Changes Committed:": "تم حفظ التغييرات:",
    "PR Opened:": "تم فتح طلب سحب:",
    "matches safety policies. Merging...": "يطابق سياسات السلامة. جاري الدمج...",
    "Merge Complete. Triggering Deployment...": "اكتمل الدمج. جاري تشغيل النشر...",
    "Environment stabilized. Operations logic verified.": "استقرار البيئة. تم التحقق من منطق العمليات.",
    
    # General
    "Starting": "بدء",
    "System initialized. Awaiting requests...": "تم تهيئة النظام. في انتظار الطلبات...",
}

def localize(text, target_lang="en"):
    """
    Translates a given log message to the target language.
    If target_lang is 'en' or translation is missing, returns original text.
    """
    if target_lang != "ar":
        return text
    
    # Try exact match first
    if text in TRANSLATIONS:
        return TRANSLATIONS[text]
    
    # Try partial match for dynamic logs
    for key, value in TRANSLATIONS.items():
        if key in text:
            return text.replace(key, value)
            
    return text
