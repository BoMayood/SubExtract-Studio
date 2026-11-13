# SubExtract Studio — Developed by NoYz
# Intellectual Property & Copyright (c) 2026 NoYz. All Rights Reserved.
# Bilingual (English & Arabic) Localization Dictionary

TRANSLATIONS = {
    "en": {
        "app_title": "SubExtract Studio — Developed by NoYz",
        "header_title": "SubExtract Studio",
        "header_subtitle": "Professional Video Subtitle Extractor & AI Translation Suite",
        "branding_badge": "Developed by NoYz",
        "footer_text": "SubExtract Studio v2.5 | Developed by NoYz | All Rights Reserved © 2026",
        
        # Mode Tabs
        "tab_video_mode": "Video Batch Processing",
        "tab_subtitle_mode": "Standalone Subtitle Studio",
        
        # Video Batch Mode
        "drag_drop_video": "Drag & Drop Video Files Here (MKV, MP4, MOV, WEBM) or Click Browse",
        "btn_browse_videos": "Browse Video Files",
        "btn_select_all": "Select All",
        "btn_deselect_all": "Deselect All",
        "btn_remove_selected": "Remove Selected",
        "btn_clear_queue": "Clear Queue",
        "chk_burn_in": "Burn-In Subtitles (Hardcoded into video)",
        "chk_save_beside": "Save Subtitles Beside Source Video File",
        "btn_select_output_dir": "Choose Output Folder",
        "lbl_output_format": "Output Format:",
        "btn_start_batch": "Start Batch Processing",
        "btn_extract_and_translate": "Extract and Translate Directly",
        "btn_extract_only": "Extract Subtitles Only",
        "btn_quick_extract_trans": "Extract & Translate",
        "btn_cancel": "Cancel",
        "col_select": "Translate",
        "col_status": "Status",
        "col_filename": "File Name",
        "col_streams": "Subtitle Track",
        "col_duration": "Duration",
        "col_actions": "Actions",
        "btn_open_folder": "Open Folder",
        
        # Subtitle Mode
        "drag_drop_subs": "Drag & Drop Subtitle Files Here (.srt, .ass, .vtt) or Click Browse",
        "btn_browse_subs": "Browse Subtitles",
        "btn_clear_sub_queue": "Clear Subtitles",
        "btn_translate_all_subs": "Batch Translate Subtitles",
        "btn_convert_format": "Convert Format",
        "btn_detect_lang": "Detect Language",
        "lbl_target_lang": "Target Language:",
        "lbl_engine": "Engine:",
        "lbl_source_lang": "Source Language:",
        
        # Pro Tools & Editor
        "editor_title": "Live Subtitle Viewer & Text Flow Inspector",
        "btn_find_replace": "Find & Replace",
        "btn_time_shift": "Time Shift / Sync",
        "btn_save_subtitle": "Save Subtitle (Ctrl+S)",
        "btn_reload_cues": "Reload Original",
        "col_cue_idx": "#",
        "col_cue_start": "Start Time",
        "col_cue_end": "End Time",
        "col_cue_text": "Subtitle Text (Click to Edit)",
        
        # Styling & Preview
        "preview_title": "Live Video Subtitle Preview Player",
        "style_panel_title": "Advanced Subtitle Styling & Typography",
        "lbl_font_family": "Font Family:",
        "lbl_font_size": "Font Size:",
        "lbl_font_color": "Text Color:",
        "lbl_outline_color": "Outline Color:",
        "lbl_outline_width": "Outline Width:",
        "chk_bold": "Bold",
        "chk_italic": "Italic",
        "lbl_alignment": "Alignment:",
        "btn_reset_styles": "Reset to Default",
        
        # Settings & Theme
        "btn_settings": "Settings",
        "btn_about": "About",
        "theme_selector": "Theme:",
        "lang_selector": "Language:",
        
        # Settings Dialog
        "settings_dialog_title": "SubExtract Studio — Application Settings",
        "group_ai_api": "AI Translation Configuration (Custom API Key)",
        "lbl_ai_provider": "AI Provider:",
        "lbl_ai_api_key": "AI API Key:",
        "lbl_ai_model": "AI Model:",
        "lbl_ai_endpoint": "API Endpoint URL:",
        "btn_test_api_key": "Test API Key",
        "btn_testing_key": "⏳ Verifying API Key...",
        "title_test_api_key": "AI API Key Verification",
        "api_key_empty": "❌ API Key field is empty!\nPlease paste your API key first, then click Test.",
        "api_test_success_gemini": "✅ Connected successfully to Google Gemini!\nActive Model: {model}{notice}\nResponse: {response}\nLatency: {latency} ms",
        "api_test_success_openai": "✅ Connected successfully to OpenAI / AI API!\nModel: {model}\nResponse: {response}\nLatency: {latency} ms",
        "api_test_failed_gemini": "❌ Unable to connect to Google Gemini models:\n{error}",
        "api_test_failed_openai": "❌ Connection failed (HTTP {status}):\n{error}",
        "api_test_err_network": "❌ Connection error: {error}",
        "api_err_invalid": "❌ Google Gemini API Key is invalid!\nDetails: {error}\nMake sure you copied the full key from Google AI Studio (aistudio.google.com).",
        "api_err_forbidden": "❌ Connection forbidden (403 Forbidden)!\nPlease verify that Generative Language API is enabled in your Google account.",
        "api_err_timeout": "❌ Connection to Google servers timed out.\nPlease check your internet connection.",
        "api_err_quota": "Current free quota exceeded (Quota Exceeded 429)",
        "api_err_busy": "Model {model} is experiencing temporary high demand (503), trying fallback model...",
        "api_notice_switched": "\n(Automatically switched to the fastest compatible model: {model})",
        "title_security_wipe": "Security Confirmation",
        "msg_security_wipe": "Are you sure you want to completely erase the AI API Key from this machine?",
        "title_api_cleared": "API Key Cleared",
        "msg_api_cleared": "The AI API Key was wiped from memory and configuration file.",
        "title_browse_tesseract": "Select Tesseract Binary",
        "btn_clear_api_key": "Clear API Key (Security Wipe)",
        "group_general": "General & OCR Settings",
        "lbl_tesseract_path": "Tesseract OCR Path:",
        "btn_browse_tesseract": "Browse...",
        "chk_sound_alerts": "Play Sound Alert on Batch Completion",
        "btn_save_settings": "Save Settings",
        "btn_close": "Close",
        
        # Find & Replace Dialog
        "find_replace_title": "Find & Replace Subtitle Text",
        "lbl_find_what": "Find what:",
        "lbl_replace_with": "Replace with:",
        "chk_match_case": "Match Case",
        "chk_whole_word": "Match Whole Word",
        "btn_replace_all": "Replace All",
        
        # Time Shift Dialog
        "time_shift_title": "Subtitle Time Shift / Sync Control",
        "lbl_shift_amount": "Shift by (Milliseconds):",
        "lbl_shift_hint": "(Positive = Delay / Forward, Negative = Earlier / Speed up)",
        "btn_apply_shift": "Apply Time Shift",
        
        # About Dialog
        "about_title": "About SubExtract Studio — NoYz",
        "about_heading": "SubExtract Studio",
        "about_version": "Version 2.5 Pro Edition",
        "about_copyright": "Developed and Designed by NoYz\nIntellectual Property & Copyright © 2026 NoYz. All Rights Reserved.",
        "about_description": (
            "SubExtract Studio is an elite, high-performance desktop suite for seamless video subtitle "
            "extraction, neural AI translation, hardcoded subtitle burn-in, OCR image processing, "
            "and professional typography styling.\n\n"
            "Engineered with zero-lag responsiveness, silent background processing, and complete "
            "Arabic/English bilingual support."
        ),
        
        # Online Subtitle Search Mode
        "tab_online_search": "Online Subtitle Search & Download",
        "drag_drop_online": "Drag & Drop Movie / Series Video Here to Auto-Detect and Search Subtitles",
        "btn_browse_movie": "Browse Video File",
        "btn_clear_online_results": "Clear Search Results",
        "lbl_search_query": "Movie / Series Title or Search Query:",
        "btn_search_online": "Search Subtitles Online",
        "col_match": "Match %",
        "col_title_year": "Title & Year",
        "col_release": "Release / Rip Name",
        "col_lang": "Language",
        "col_downloads": "Downloads / Rating",
        "col_download_action": "Download & Verify",
        "btn_download_verify": "Download & Verify",
        "status_searching": "Searching online subtitle databases...",
        "status_downloading": "Downloading, verifying and matching subtitle...",
        "msg_sub_downloaded": "Subtitle downloaded and verified successfully! ({count} cues)",
        "msg_sub_failed": "Failed to download or verify subtitle.",
        "btn_search_row": "Search Online",
        "verified_valid": "100% Valid & Synced",
        "lbl_detected_media": "Detected Media:",
        "btn_open_saved_sub": "Open Subtitle Folder",
        
        # Status Messages
        "status_ready": "Ready",
        "status_processing": "Processing...",
        "status_extracted": "Extracted Successfully",
        "status_extracted_trans": "Extracted & Translated",
        "status_completed": "Batch processing completed successfully!",
        "status_batch_failed": "Batch processing failed! No subtitles were saved.",
        "status_batch_partial": "Batch partially completed: {success} succeeded, {failed} failed.",
        "msg_batch_failed_desc": "No subtitle files were extracted or saved.\nPlease check that FFmpeg is available or review the error logs below.",
        "status_api_cleared": "API key was completely wiped from memory and configuration.",
        "status_styles_reset": "Subtitle typography reset to factory defaults."
    },
    
    "ar": {
        "app_title": "SubExtract Studio — تطوير NoYz",
        "header_title": "SubExtract Studio",
        "header_subtitle": "المنظومة الاحترافية لاستخراج وترجمة وضبط ترجمات الفيديو بالذكاء الاصطناعي",
        "branding_badge": "تطوير وإشراف NoYz",
        "footer_text": "SubExtract Studio v2.5 | تطوير NoYz | جميع الحقوق محفوظة © 2026",
        
        # Mode Tabs
        "tab_video_mode": "معالجة الفيديو واستخراج الترجمات",
        "tab_subtitle_mode": "استوديو ومحرر ملفات الترجمة",
        
        # Video Batch Mode
        "drag_drop_video": "اسحب وأفلت ملفات الفيديو هنا (MKV, MP4, MOV, WEBM) أو اضغط تصفح",
        "btn_browse_videos": "تصفح ملفات الفيديو",
        "btn_select_all": "تحديد الكل",
        "btn_deselect_all": "إلغاء تحديد الكل",
        "btn_remove_selected": "حذف المحدد",
        "btn_clear_queue": "مسح القائمة",
        "chk_burn_in": "حرق الترجمة نهائياً داخل الفيديو (Hardcoded)",
        "chk_save_beside": "حفظ ملف الترجمة بجانب ملف الفيديو الأصلي",
        "btn_select_output_dir": "اختيار مجلد الإخراج",
        "lbl_output_format": "صيغة الترجمة:",
        "btn_start_batch": "بدء المعالجة المجمعة",
        "btn_extract_and_translate": "⚡ استخراج وترجمة فورية",
        "btn_extract_only": "📥 استخراج ملف الترجمة فقط",
        "btn_quick_extract_trans": "⚡ استخراج وترجمة",
        "btn_cancel": "إلغاء العملية",
        "col_select": "ترجمة",
        "col_status": "الحالة",
        "col_filename": "اسم الملف",
        "col_streams": "مسار الترجمة المستخرج",
        "col_duration": "المدة الزمنية",
        "col_actions": "الإجراءات",
        "btn_open_folder": "فتح المجلد",
        
        # Subtitle Mode
        "drag_drop_subs": "اسحب وأفلت ملفات الترجمة هنا (.srt, .ass, .vtt) أو اضغط تصفح",
        "btn_browse_subs": "تصفح ملفات الترجمة",
        "btn_clear_sub_queue": "مسح ملفات الترجمة",
        "btn_translate_all_subs": "ترجمة ملفات الترجمة دفعة واحدة",
        "btn_convert_format": "تحويل الصيغة",
        "btn_detect_lang": "كشف اللغة تلقائياً",
        "lbl_target_lang": "اللغة المستهدفة:",
        "lbl_engine": "محرك الترجمة:",
        "lbl_source_lang": "لغة المصدر:",
        
        # Pro Tools & Editor
        "editor_title": "محرر نصوص الترجمة والتوقيت الزمني",
        "btn_find_replace": "بحث واستبدال",
        "btn_time_shift": "مزامنة وضبط التوقيت (Sync)",
        "btn_save_subtitle": "حفظ الترجمة (Ctrl+S)",
        "btn_reload_cues": "استعادة الأصلي",
        "col_cue_idx": "#",
        "col_cue_start": "وقت البدء",
        "col_cue_end": "وقت الانتهاء",
        "col_cue_text": "نص الترجمة (انقر للتحرير)",
        
        # Styling & Preview
        "preview_title": "شاشة المعاينة الحية للترجمة",
        "style_panel_title": "تنسيق الخطوط والمظهر الطباعي للترجمة",
        "lbl_font_family": "نوع الخط:",
        "lbl_font_size": "حجم الخط:",
        "lbl_font_color": "لون النص:",
        "lbl_outline_color": "لون الإطار:",
        "lbl_outline_width": "سُمك الإطار:",
        "chk_bold": "عريض (Bold)",
        "chk_italic": "مائل (Italic)",
        "lbl_alignment": "المحاذاة:",
        "btn_reset_styles": "استعادة الضبط الافتراضي للخطوط",
        
        # Settings & Theme
        "btn_settings": "الإعدادات",
        "btn_about": "حول",
        "theme_selector": "المظهر:",
        "lang_selector": "اللغة:",
        
        # Settings Dialog
        "settings_dialog_title": "SubExtract Studio — إعدادات التطبيق",
        "group_ai_api": "إعدادات الترجمة بالذكاء الاصطناعي (مفتاح API الخاص)",
        "lbl_ai_provider": "مزود الذكاء الاصطناعي:",
        "lbl_ai_api_key": "مفتاح API:",
        "lbl_ai_model": "نموذج الذكاء الاصطناعي:",
        "lbl_ai_endpoint": "رابط نقطة النهاية (Endpoint):",
        "btn_test_api_key": "🔍 فحص مفتاح API",
        "btn_testing_key": "⏳ جاري الفحص...",
        "title_test_api_key": "فحص مفتاح API",
        "api_key_empty": "❌ حقل مفتاح API فارغ!\nيرجى لصق المفتاح أولاً ثم الضغط على فحص.",
        "api_test_success_gemini": "✅ تم الاتصال بنجاح بمفتاح Google Gemini!\nالنموذج النشط: {model}{notice}\nالاستجابة: {response}\nسرعة الاستجابة: {latency} ms",
        "api_test_success_openai": "✅ تم الاتصال بنجاح بـ OpenAI / AI API!\nالنموذج: {model}\nالاستجابة: {response}\nالسرعة: {latency} ms",
        "api_test_failed_gemini": "❌ تعذر الاتصال بنماذج Google Gemini:\n{error}",
        "api_test_failed_openai": "❌ فشل الاتصال (HTTP {status}):\n{error}",
        "api_test_err_network": "❌ خطأ أثناء الاتصال بالخادم: {error}",
        "api_err_invalid": "❌ مفتاح Google Gemini غير صالح (API Key Invalid)!\nالتفاصيل: {error}\nتأكد من نسخ المفتاح كاملاً من Google AI Studio (aistudio.google.com).",
        "api_err_forbidden": "❌ تم رفض الاتصال (403 Forbidden)!\nتأكد من تفعيل خدمة Generative Language API في حسابك.",
        "api_err_timeout": "❌ انتهت مهلة الاتصال بخوادم Google (Connection Timeout).\nتحقق من اتصال الإنترنت.",
        "api_err_quota": "تم تجاوز الحصة المجانية الحالية (Quota Exceeded 429)",
        "api_err_busy": "النموذج {model} عليه ضغط مؤقت (503)، جاري تجربة النموذج البديل...",
        "api_notice_switched": "\n(تم التبديل تلقائياً للنموذج الأسرع والأنسب: {model})",
        "title_security_wipe": "تأكيد أمني",
        "msg_security_wipe": "هل أنت متأكد من رغبتك في حذف مفتاح API تماماً من هذا الجهاز؟",
        "title_api_cleared": "تم مسح المفتاح",
        "msg_api_cleared": "تم مسح مفتاح API تماماً من الذاكرة وملف الإعدادات.",
        "title_browse_tesseract": "اختر ملف تشغيل Tesseract",
        "btn_clear_api_key": "مسح مفتاح API تماماً (مسح أمني)",
        "group_general": "الإعدادات العامة والتعرف الضوئي (OCR)",
        "lbl_tesseract_path": "مسار برنامج Tesseract OCR:",
        "btn_browse_tesseract": "تصفح...",
        "chk_sound_alerts": "تشغيل تنبيه صوتي هادئ عند انتهاء المعالجة",
        "btn_save_settings": "حفظ الإعدادات",
        "btn_close": "إغلاق",
        
        # Find & Replace Dialog
        "find_replace_title": "البحث والاستبدال في نصوص الترجمة",
        "lbl_find_what": "البحث عن:",
        "lbl_replace_with": "استبدال بـ:",
        "chk_match_case": "مطابقة حالة الأحرف",
        "chk_whole_word": "مطابقة الكلمة بالكامل",
        "btn_replace_all": "استبدال الكل فوراً",
        
        # Time Shift Dialog
        "time_shift_title": "تقديم وتأخير توقيت الترجمة (مزامنة)",
        "lbl_shift_amount": "قيمة الإزاحة (بالميللي ثانية):",
        "lbl_shift_hint": "(قيمة موجبة = تأخير / إلى الأمام ، قيمة سالبة = تقديم / أسرع)",
        "btn_apply_shift": "تطبيق إزاحة التوقيت",
        
        # About Dialog
        "about_title": "حول تطبيق SubExtract Studio — NoYz",
        "about_heading": "SubExtract Studio",
        "about_version": "الإصدار الاحترافي v2.5",
        "about_copyright": "تصميم وتطوير وبرمجة: NoYz\nالملكية الفكرية وحقوق النشر © 2026 NoYz. جميع الحقوق محفوظة.",
        "about_description": (
            "برنامج SubExtract Studio هو بيئة سطح مكتب متكاملة فائقة السرعة لاستخراج ترجمات الفيديو المدمجة، "
            "والترجمة العصبية بالذكاء الاصطناعي، وحرق الترجمات داخل الفيديو بشكل صلب، واستخراج النصوص من الصور (OCR)، "
            "مع محرر متقدم وتنسيق طباعي احترافي.\n\n"
            "تم بناؤه بأعلى معايير الأداء الخالي من التعليق، والمعالجة الصامتة في الخلفية، ودعم كامل للواجهتين العربية والإنجليزية."
        ),
        
        # Online Subtitle Search Mode
        "tab_online_search": "البحث عن الترجمات أونلاين وتحميلها",
        "drag_drop_online": "اسحب وأفلت ملف الفلم أو المسلسل هنا للبحث الفوري التلقائي عن ترجمته",
        "btn_browse_movie": "تصفح ملف الفيديو",
        "btn_clear_online_results": "مسح نتائج البحث",
        "lbl_search_query": "اسم الفلم أو المسلسل / عبارة البحث:",
        "btn_search_online": "🔍 بحث عن الترجمة عبر الإنترنت",
        "col_match": "نسبة التطابق",
        "col_title_year": "العنوان والسنة",
        "col_release": "النسخة / إصدار الفريق",
        "col_lang": "اللغة",
        "col_downloads": "التحميلات / التقييم",
        "col_download_action": "تحميل وفحص",
        "btn_download_verify": "⬇ تحميل ومطابقة",
        "status_searching": "جاري البحث في قواعد بيانات الترجمة عبر الإنترنت...",
        "status_downloading": "جاري تحميل الترجمة وفحص سلامتها ومطابقتها...",
        "msg_sub_downloaded": "تم تحميل الترجمة والتحقق من سلامتها وتطابقها بنجاح! ({count} سطر)",
        "msg_sub_failed": "فشل تحميل الترجمة أو التحقق من سلامتها.",
        "btn_search_row": "بحث أونلاين",
        "verified_valid": "سليمة ومتطابقة 100%",
        "lbl_detected_media": "المحتوى المكتشف:",
        "btn_open_saved_sub": "فتح مجلد الترجمة المحفوظة",
        
        # Status Messages
        "status_ready": "جاهز للعمل",
        "status_processing": "جاري المعالجة...",
        "status_extracted": "تم الاستخراج بنجاح",
        "status_extracted_trans": "تم الاستخراج والترجمة",
        "status_completed": "تمت معالجة القائمة بنجاح تام!",
        "status_batch_failed": "فشلت معالجة الدفعة! لم يتم استخراج أو حفظ أي ملف ترجمة.",
        "status_batch_partial": "اكتملت المعالجة جزئياً: نجح {success}، وفشل {failed}.",
        "msg_batch_failed_desc": "لم يتم استخراج أو حفظ أي ملف ترجمة.\nيرجى التأكد من توفر أداة FFmpeg أو مراجعة سجل الأخطاء بالأسفل.",
        "status_api_cleared": "تم مسح مفتاح API تماماً من الذاكرة والملف.",
        "status_styles_reset": "تمت استعادة إعدادات الخطوط الافتراضية بنجاح."
    }
}

class I18n:
    """Manages bilingual UI strings and dynamic language switching."""
    current_lang = "en"

    @classmethod
    def set_language(cls, lang_code: str):
        if lang_code in TRANSLATIONS:
            cls.current_lang = lang_code

    @classmethod
    def t(cls, key: str) -> str:
        lang_dict = TRANSLATIONS.get(cls.current_lang, TRANSLATIONS["en"])
        return lang_dict.get(key, TRANSLATIONS["en"].get(key, key))
