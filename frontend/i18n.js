// ==========================================================================
// PARKVISION AI - INTERNATIONALIZATION (i18n) ENGINE
// Multi-Language Support with Dynamic Switching & Persistent Preference
// Default: English (en) | Supported: en, hi, gu, mr, es, fr
// ==========================================================================

(function() {
  'use strict';

  const LANGUAGES = {
    en: { name: 'English', nativeName: 'English', flag: '🇬🇧', speechLang: 'en-US' },
    hi: { name: 'Hindi', nativeName: 'हिन्दी', flag: '🇮🇳', speechLang: 'hi-IN' },
    gu: { name: 'Gujarati', nativeName: 'ગુજરાતી', flag: '🇮🇳', speechLang: 'gu-IN' },
    mr: { name: 'Marathi', nativeName: 'मराठी', flag: '🇮🇳', speechLang: 'mr-IN' },
    es: { name: 'Spanish', nativeName: 'Español', flag: '🇪🇸', speechLang: 'es-ES' },
    fr: { name: 'French', nativeName: 'Français', flag: '🇫🇷', speechLang: 'fr-FR' }
  };

  const TRANSLATIONS = {
    en: {
      // Branding & Header
      brand_title: 'PARKVISION',
      brand_accent: 'AI',
      brand_sub: 'Smart Parking Detection · Zero Fees · Free Public Bays',
      btn_arch: '⭐ Architecture & Dataset',
      btn_advanced: '⚙️ Advanced View',
      btn_wizard: '🧙 Wizard View',
      btn_auth_open: '🔐 Register / Login',
      btn_logout: '🚪 Sign Out',
      lang_label: 'Language',

      // Wizard Stepper
      step_vehicle: 'Vehicle',
      step_location: 'Location',
      step_parking: 'Find Parking',
      step_navigate: 'Navigate',
      step_ar: 'AR Scan',

      // Wizard Step 1: Vehicle
      wz_s1_tag: 'Step 1 of 5',
      wz_s1_title: 'Select Your Vehicle Profile',
      wz_s1_sub: 'Enter ONLY the vehicle name (Car, Auto Rickshaw, Bike, Scooter, or EV) — length & width are automatically detected instantly from 200+ vehicles!',
      lbl_full_name: 'Full Name',
      ph_full_name: 'e.g. Rahul Sharma',
      lbl_mobile: 'Mobile Number',
      ph_mobile: '+91 XXXXX XXXXX',
      lbl_veh_filter: 'Vehicle Type Filter',
      cat_all: '🌟 All Vehicles',
      cat_2w: '🏍️ 2-Wheeler (Bikes & Scooters)',
      cat_3w: '🛺 3-Wheeler (Auto Rickshaw)',
      cat_4w: '🚗 4-Wheeler (Cars & SUVs)',
      lbl_veh_name: 'Vehicle Name / Model',
      hint_veh_name: 'Type name only — dimensions auto-detect',
      ph_veh_name: 'Type vehicle name e.g. Swift, Activa, Auto Rickshaw, Thar, Creta, Treo...',
      lbl_quick_pick: '⚡ Quick Pick:',
      lbl_length: 'Length (m)',
      lbl_width: 'Width (m)',
      tag_auto: '✨ Auto-Detected',
      lbl_plate: 'Plate / Reg Number',
      ph_plate: 'e.g. MH-02-AB-1234',
      btn_save_loc: '🚀 Save & Detect My Location',
      btn_edit: '✏️ Edit',

      // Wizard Step 2: Location
      wz_s2_tag: 'Step 2 of 5',
      wz_s2_title: 'Detect Your Live Location',
      wz_s2_sub: 'We need your GPS location to find the nearest free bike parking bays. Your location stays private and is never stored.',
      gps_waiting: 'Waiting to acquire GPS fix...',
      gps_click_hint: 'Click the button below to start',
      lbl_or_set_city: 'Or set location:',
      btn_detect_gps: '📍 Detect My GPS Location',
      btn_back: '← Back',

      // Wizard Step 3: Find Parking
      wz_s3_tag: 'Step 3 of 5',
      wz_s3_title: 'Free Parking Near You',
      wz_s3_sub: 'Showing 100% free public bike parking lots nearby. Zero fees, no booking required. Tap a lot to select it.',
      finding_free_parking: 'Finding free parking near you...',
      badge_free_public: '🟢 100% Free Public Parking',
      bays_found: 'free bays found',
      btn_nav_lot: '🧭 Navigate to Selected Lot →',

      // Wizard Step 4: Navigate
      wz_s4_tag: 'Step 4 of 5',
      wz_s4_title: 'Navigate to Parking Lot',
      wz_s4_sub: 'Drive to the selected parking facility. When you arrive, tap the button below to launch the camera scanner.',
      badge_zero_fee: 'Zero Fee',
      lbl_km_away: 'km away',
      lbl_mins: 'mins',
      lbl_free_bays: 'free bays',
      gmaps_tip: 'Open Google Maps for turn-by-turn directions, or just follow the map above. Tap "I\'ve Arrived" when you reach the entrance.',
      btn_arrived: "📍 I've Arrived — Launch Camera Scanner →",
      btn_open_gmaps: '🗺️ Open in Google Maps',

      // Wizard Step 5: Camera Scan
      wz_s5_tag: 'Step 5 of 5',
      wz_s5_title: 'Point Camera at Parking Row',
      wz_s5_sub: 'AI detects empty spaces and suggests the best spot for your bike. 100% free — zero fees, no booking.',
      pointer_park_here: 'POTENTIALLY SUITABLE',
      perm_req_title: 'Camera Permission Required',
      perm_req_desc: 'Allow your phone\'s rear camera to scan the parking row. The AI will highlight the best available spot that fits your vehicle.',
      perm_security: '🔒 Frames are processed locally for parking detection only. Nothing is stored.',
      btn_allow_cam: '📷 Allow & Open Camera',
      btn_sim_cam: '🎬 Use Simulated Feed',
      scan_radar: 'YOLOv8 Scanning...',
      cam_ready: 'Camera Ready',
      cam_free_parking: '🟢 FREE Parking',
      cam_stop: 'Stop',
      cam_start: 'Start',
      cam_flip: 'Flip',
      cam_scan_now: 'Scan Now',
      cam_auto_on: 'Auto: ON',
      cam_auto_off: 'Auto: OFF',
      cam_speak: 'Speak',
      rec_badge: '⭐ SUGGESTED SPOT FOR YOUR VEHICLE',
      rec_scanning: 'Scanning...',
      rec_point_cam: 'Point camera at parking row',
      spec_bay_size: 'Bay Size:',
      spec_your_veh: 'Your Vehicle:',
      spec_clearance: 'Clearance:',
      spec_parking_fee: 'Parking Fee:',
      fee_free_val: 'FREE (Zero Fee)',
      rec_aim_msg: 'Aim your camera at the parking row to detect available spaces.',
      btn_parked_done: '✅ Vehicle Parked — Done!',
      detected_bays_title: 'Detected Bays in View',
      btn_back_map: '← Back to Map',

      // Registration & Login Modal
      tab_register: '📝 Register Rider & Vehicle',
      tab_login: '🔑 Existing User Login',
      lbl_login_id: 'Email, Username, or Mobile',
      auth_create_title: 'Create Your Rider Account',
      auth_create_desc: 'Enter your vehicle name — length and width are automatically fetched from our real vehicle dataset.',
      lbl_email: 'Email Address',
      ph_email: 'you@example.com (or auto-generated)',
      lbl_pwd: 'Password',
      ph_pwd: 'Create password (default: 123456)',
      btn_close: 'Close',
      btn_complete_reg: '🚀 Complete Registration & Find Free Bays',
      auth_login_title: 'Welcome Back',
      auth_login_desc: 'Sign in to access your registered vehicle profile and find free parking.',
      ph_login_email: 'you@example.com',
      ph_login_pwd: 'Enter password',
      btn_signin: '🔑 Sign In',

      // Advanced Tabs
      nav_tab_arch: 'Architecture & Dataset',
      nav_tab_camera: 'Mobile Camera Scanner',
      nav_tab_map: 'Live GPS & Free Bays',
      nav_tab_cv: 'CV Diagnostics Lab',
      nav_tab_flow: 'Real-Life 8-Step Flow',
      nav_tab_rules: 'Parking Rules',
      nav_tab_api: 'API Server',

      // Toasts & Speech
      toast_profile_saved: '✅ Profile saved successfully!',
      toast_gps_detected: '📍 GPS location acquired: ',
      toast_parked_success: '🎉 Parking Confirmed! Have a safe trip!',
      speech_parked_success: 'Your vehicle is safely parked. Have a great day!',
      speech_rec_bay: 'Recommended spot found! Park your vehicle in {bay}. Free parking.',
      speech_no_spot: 'No suitable parking spot currently in view. Please pan the camera.'
    },

    hi: {
      // Branding & Header
      brand_title: 'PARKVISION',
      brand_accent: 'AI',
      brand_sub: 'स्मार्ट पार्किंग डिटेक्शन · शून्य शुल्क · निःशुल्क सार्वजनिक स्थान',
      btn_arch: '⭐ आर्किटेक्चर और डेटासेट',
      btn_advanced: '⚙️ उन्नत दृश्य (Advanced)',
      btn_wizard: '🧙 विज़ार्ड दृश्य',
      btn_auth_open: '🔐 रजिस्टर / लॉगिन',
      btn_logout: '🚪 साइन आउट',
      lang_label: 'भाषा',

      // Wizard Stepper
      step_vehicle: 'वाहन',
      step_location: 'स्थान',
      step_parking: 'पार्किंग खोजें',
      step_navigate: 'नेविगेट',
      step_ar: 'एआर स्कैन',

      // Wizard Step 1: Vehicle
      wz_s1_tag: 'चरण 1 / 5',
      wz_s1_title: 'अपना वाहन प्रोफ़ाइल चुनें',
      wz_s1_sub: 'केवल वाहन का नाम दर्ज करें (कार, ऑटो रिक्शा, बाइक, स्कूटर, या ईवी) — लंबाई और चौड़ाई 200+ वाहनों के डेटाबेस से तुरंत पहचानी जाएगी!',
      lbl_full_name: 'पूरा नाम',
      ph_full_name: 'उदा. राहुल शर्मा',
      lbl_mobile: 'मोबाइल नंबर',
      ph_mobile: '+91 XXXXX XXXXX',
      lbl_veh_filter: 'वाहन प्रकार फ़िल्टर',
      cat_all: '🌟 सभी वाहन',
      cat_2w: '🏍️ 2-पहिया (बाइक और स्कूटर)',
      cat_3w: '🛺 3-पहिया (ऑटो रिक्शा)',
      cat_4w: '🚗 4-पहिया (कार और एसयूवी)',
      lbl_veh_name: 'वाहन का नाम / मॉडल',
      hint_veh_name: 'केवल नाम लिखें — माप स्वतः पहचाने जाते हैं',
      ph_veh_name: 'वाहन का नाम लिखें जैसे Swift, Activa, Auto Rickshaw, Thar, Creta, Treo...',
      lbl_quick_pick: '⚡ त्वरित चयन:',
      lbl_length: 'लंबाई (मीटर)',
      lbl_width: 'चौड़ाई (मीटर)',
      tag_auto: '✨ स्वतः पहचाना गया',
      lbl_plate: 'पंजीकरण नंबर / प्लेट',
      ph_plate: 'उदा. MH-02-AB-1234',
      btn_save_loc: '🚀 सहेजें और मेरा स्थान खोजें',
      btn_edit: '✏️ संपादित करें',

      // Wizard Step 2: Location
      wz_s2_tag: 'चरण 2 / 5',
      wz_s2_title: 'अपना लाइव स्थान खोजें',
      wz_s2_sub: 'निकटतम निःशुल्क बाइक पार्किंग खोजने के लिए जीपीएस आवश्यक है। आपका स्थान निजी रहता है और संग्रहीत नहीं होता।',
      gps_waiting: 'जीपीएस सिग्नल की प्रतीक्षा...',
      gps_click_hint: 'शुरू करने के लिए नीचे दिए गए बटन पर क्लिक करें',
      lbl_or_set_city: 'या शहर चुनें:',
      btn_detect_gps: '📍 मेरा जीपीएस स्थान खोजें',
      btn_back: '← पीछे जाएं',

      // Wizard Step 3: Find Parking
      wz_s3_tag: 'चरण 3 / 5',
      wz_s3_title: 'आपके निकट निःशुल्क पार्किंग',
      wz_s3_sub: 'निकटतम 100% निःशुल्क सार्वजनिक पार्किंग स्थल। कोई शुल्क नहीं, बुकिंग की आवश्यकता नहीं। चुनने के लिए टैप करें।',
      finding_free_parking: 'निकटतम निःशुल्क पार्किंग खोजी जा रही है...',
      badge_free_public: '🟢 100% निःशुल्क सार्वजनिक पार्किंग',
      bays_found: 'खाली स्थान मिले',
      btn_nav_lot: '🧭 चुने गए स्थान पर नेविगेट करें →',

      // Wizard Step 4: Navigate
      wz_s4_tag: 'चरण 4 / 5',
      wz_s4_title: 'पार्किंग स्थल पर नेविगेट करें',
      wz_s4_sub: 'चुनी गई पार्किंग सुविधा तक ड्राइव करें। पहुंचने पर नीचे दिए गए बटन को दबाकर कैमरा स्कैनर खोलें।',
      badge_zero_fee: 'शून्य शुल्क',
      lbl_km_away: 'किमी दूर',
      lbl_mins: 'मिनट',
      lbl_free_bays: 'खाली स्थान',
      gmaps_tip: 'टर्न-बाय-टर्न दिशाओं के लिए Google Maps खोलें या ऊपर दिए गए नक्शे का पालन करें। प्रवेश द्वार पर पहुंचकर "मैं पहुंच गया" दबाएं।',
      btn_arrived: '📍 मैं पहुंच गया — कैमरा स्कैनर शुरू करें →',
      btn_open_gmaps: '🗺️ Google Maps में खोलें',

      // Wizard Step 5: Camera Scan
      wz_s5_tag: 'चरण 5 / 5',
      wz_s5_title: 'कैमरे को पार्किंग पंक्ति की ओर करें',
      wz_s5_sub: 'एआई खाली स्थानों का पता लगाता है और आपके वाहन के लिए सबसे उपयुक्त स्थान सुझाता है। 100% निःशुल्क।',
      pointer_park_here: 'संभावित उपयुक्त पार्किंग',
      perm_req_title: 'कैमरा अनुमति आवश्यक',
      perm_req_desc: 'पार्किंग पंक्ति को स्कैन करने के लिए अपने फोन के रियर कैमरे की अनुमति दें। एआई आपके वाहन के लिए सर्वश्रेष्ठ स्थान सुझाएगा।',
      perm_security: '🔒 वीडियो केवल स्थानीय रूप से प्रोसेस होता है। कुछ भी स्टोर नहीं होता।',
      btn_allow_cam: '📷 अनुमति दें और कैमरा खोलें',
      btn_sim_cam: '🎬 सिम्युलेटेड कैमरा उपयोग करें',
      scan_radar: 'YOLOv8 स्कैनिंग जारी...',
      cam_ready: 'कैमरा तैयार है',
      cam_free_parking: '🟢 निःशुल्क पार्किंग',
      cam_stop: 'रोकें',
      cam_start: 'शुरू करें',
      cam_flip: 'कैमरा पलटें',
      cam_scan_now: 'अभी स्कैन करें',
      cam_auto_on: 'ऑटो: चालू',
      cam_auto_off: 'ऑटो: बंद',
      cam_speak: 'आवाज (Speak)',
      rec_badge: '⭐ आपके वाहन के लिए अनुशंसित स्थान',
      rec_scanning: 'स्कैन हो रहा है...',
      rec_point_cam: 'कैमरा पार्किंग पंक्ति की ओर करें',
      spec_bay_size: 'स्थान का आकार:',
      spec_your_veh: 'आपका वाहन:',
      spec_clearance: 'सुरक्षित दूरी:',
      spec_parking_fee: 'पार्किंग शुल्क:',
      fee_free_val: 'निःशुल्क (शून्य शुल्क)',
      rec_aim_msg: 'उपलब्ध खाली स्थान खोजने के लिए कैमरे को पार्किंग पंक्ति की ओर रखें।',
      btn_parked_done: '✅ वाहन पार्क हो गया — संपन्न!',
      detected_bays_title: 'पहचाने गए पार्किंग स्थान',
      btn_back_map: '← नक्शे पर वापस जाएं',

      // Registration & Login Modal
      tab_register: '📝 राइडर और वाहन पंजीकरण',
      tab_login: '🔑 मौजूदा उपयोगकर्ता लॉगिन',
      auth_create_title: 'अपना राइडर खाता बनाएं',
      auth_create_desc: 'वाहन का नाम दर्ज करें — लंबाई और चौड़ाई हमारे डेटाबेस से स्वचालित रूप से लोड होगी।',
      lbl_email: 'ईमेल पता',
      ph_email: 'you@example.com (या स्वतः उत्पन्न)',
      lbl_pwd: 'पासवर्ड',
      ph_pwd: 'पासवर्ड बनाएं (डिफ़ॉल्ट: 123456)',
      btn_close: 'बंद करें',
      btn_complete_reg: '🚀 पंजीकरण पूरा करें और निःशुल्क स्थान खोजें',
      auth_login_title: 'स्वागत है',
      auth_login_desc: 'अपने वाहन प्रोफ़ाइल तक पहुंचने और निःशुल्क पार्किंग खोजने के लिए साइन इन करें।',
      ph_login_email: 'you@example.com',
      ph_login_pwd: 'पासवर्ड दर्ज करें',
      btn_signin: '🔑 साइन इन करें',

      // Advanced Tabs
      nav_tab_arch: 'आर्किटेक्चर और डेटाबेस',
      nav_tab_camera: 'मोबाइल कैमरा स्कैनर',
      nav_tab_map: 'लाइव जीपीएस और खाली स्थान',
      nav_tab_cv: 'कंप्यूटर विज़न लैब',
      nav_tab_flow: '8-चरणीय ड्राइवर प्रवाह',
      nav_tab_rules: 'पार्किंग नियम',
      nav_tab_api: 'एपीआई सर्वर',

      // Toasts & Speech
      toast_profile_saved: '✅ वाहन प्रोफ़ाइल सफलतापूर्वक सहेजी गई!',
      toast_gps_detected: '📍 जीपीएस स्थान प्राप्त हुआ: ',
      toast_parked_success: '🎉 पार्किंग की पुष्टि हुई! आपकी यात्रा शुभ हो!',
      speech_parked_success: 'आपका वाहन सुरक्षित रूप से पार्क हो गया है। आपका दिन शुभ हो!',
      speech_rec_bay: 'अनुशंसित स्थान मिला! अपने वाहन को {bay} में पार्क करें। पार्किंग निःशुल्क है।',
      speech_no_spot: 'वर्तमान दृश्य में कोई उपयुक्त स्थान नहीं मिला। कृपया कैमरा घुमाएं।'
    },

    gu: {
      // Branding & Header
      brand_title: 'PARKVISION',
      brand_accent: 'AI',
      brand_sub: 'સ્માર્ટ પાર્કિંગ ડિટેક્શન · શૂન્ય ફી · મફત જાહેર પાર્કિંગ',
      btn_arch: '⭐ આર્કિટેક્ચર અને ડેટાસેટ',
      btn_advanced: '⚙️ એડવાન્સ્ડ વ્યૂ',
      btn_wizard: '🧙 વિઝાર્ડ વ્યૂ',
      btn_auth_open: '🔐 રજીસ્ટર / લોગિન',
      btn_logout: '🚪 સાઇન આઉટ',
      lang_label: 'ભાષા',

      // Wizard Stepper
      step_vehicle: 'વાહન',
      step_location: 'સ્થાન',
      step_parking: 'પાર્કિંગ શોધો',
      step_navigate: 'નેવિગેટ',
      step_ar: 'એઆર સ્કેન',

      // Wizard Step 1: Vehicle
      wz_s1_tag: 'પગલું 1 / 5',
      wz_s1_title: 'તમારું વાહન પ્રોફાઇલ પસંદ કરો',
      wz_s1_sub: 'માત્ર વાહનનું નામ દાખલ કરો (કાર, ઓટો રિક્ષા, બાઇક, સ્કૂટર, અથવા ઇવી) — લંબાઈ અને પહોળાઈ 200+ વાહનોમાંથી આપોઆપ મળી જશે!',
      lbl_full_name: 'પૂરું નામ',
      ph_full_name: 'દા.ત. રાહુલ શર્મા',
      lbl_mobile: 'મોબાઇલ નંબર',
      ph_mobile: '+91 XXXXX XXXXX',
      lbl_veh_filter: 'વાહન પ્રકાર ફિલ્ટર',
      cat_all: '🌟 તમામ વાહનો',
      cat_2w: '🏍️ 2-વ્હીલર (બાઇક અને સ્કૂટર)',
      cat_3w: '🛺 3-વ્હીલર (ઓટો રિક્ષા)',
      cat_4w: '🚗 4-વ્હીલર (કાર અને એસયુવી)',
      lbl_veh_name: 'વાહનનું નામ / મોડેલ',
      hint_veh_name: 'માત્ર નામ લખો — માપ આપમેળે શોધાય છે',
      ph_veh_name: 'વાહનનું નામ લખો દા.ત. Swift, Activa, Auto Rickshaw, Thar, Creta, Treo...',
      lbl_quick_pick: '⚡ ઝડપી પસંદગી:',
      lbl_length: 'લંબાઈ (મીટર)',
      lbl_width: 'પહોળાઈ (મીટર)',
      tag_auto: '✨ આપમેળે શોધાયેલ',
      lbl_plate: 'વાહન નંબર / પ્લેટ',
      ph_plate: 'દા.ત. GJ-03-AB-1234',
      btn_save_loc: '🚀 સાચવો અને મારું સ્થાન શોધો',
      btn_edit: '✏️ ફેરફાર કરો',

      // Wizard Step 2: Location
      wz_s2_tag: 'પગલું 2 / 5',
      wz_s2_title: 'તમારું લાઇવ સ્થાન શોધો',
      wz_s2_sub: 'સૌથી નજીકની મફત પાર્કિંગ જગ્યાઓ શોધવા માટે જીપીએસ સ્થાન જરૂરી છે. તમારું સ્થાન ખાનગી રહે છે.',
      gps_waiting: 'જીપીએસ સિગ્નલની રાહ જોઈ રહ્યા છીએ...',
      gps_click_hint: 'શરૂ કરવા માટે નીચેના બટન પર ક્લિક કરો',
      lbl_or_set_city: 'અથવા શહેર પસંદ કરો:',
      btn_detect_gps: '📍 મારું જીપીએસ સ્થાન શોધો',
      btn_back: '← પાછા જાઓ',

      // Wizard Step 3: Find Parking
      wz_s3_tag: 'પગલું 3 / 5',
      wz_s3_title: 'તમારી નજીક મફત પાર્કિંગ',
      wz_s3_sub: 'નજીકની 100% મફત જાહેર પાર્કિંગ સુવિધાઓ દર્શાવે છે. કોઈ ફી નથી, કોઈ બુકિંગની જરૂર નથી.',
      finding_free_parking: 'નજીકમાં મફત પાર્કિંગ શોધાઈ રહ્યું છે...',
      badge_free_public: '🟢 100% મફત જાહેર પાર્કિંગ',
      bays_found: 'ખાલી જગ્યાઓ મળી',
      btn_nav_lot: '🧭 પસંદ કરેલા લોટ તરફ નેવિગેટ કરો →',

      // Wizard Step 4: Navigate
      wz_s4_tag: 'પગલું 4 / 5',
      wz_s4_title: 'પાર્કિંગ લોટ તરફ નેવિગેટ કરો',
      wz_s4_sub: 'પસંદ કરેલ પાર્કિંગ સ્થળ સુધી વાહન ચલાવો. પહોંચ્યા પછી કેમેરા સ્કેનર ખોલવા નીચેનું બટન દબાવો.',
      badge_zero_fee: 'શૂન્ય ફી',
      lbl_km_away: 'કિમી દૂર',
      lbl_mins: 'મિનિટ',
      lbl_free_bays: 'ખાલી જગ્યાઓ',
      gmaps_tip: 'Google Maps માં દિશાઓ જોવા માટે બટન દબાવો અથવા ઉપરના નકશાને અનુસરો. પહોંચ્યા પછી "હું પહોંચી ગયો" દબાવો.',
      btn_arrived: '📍 હું પહોંચી ગયો — કેમેરા સ્કેનર શરૂ કરો →',
      btn_open_gmaps: '🗺️ Google Maps માં ખોલો',

      // Wizard Step 5: Camera Scan
      wz_s5_tag: 'પગલું 5 / 5',
      wz_s5_title: 'કેમેરાને પાર્કિંગ લાઇન તરફ રાખો',
      wz_s5_sub: 'એઆઇ ખાલી જગ્યાઓ શોધે છે અને તમારા વાહન માટે શ્રેષ્ઠ સ્થાન સૂચવે છે. 100% મફત.',
      pointer_park_here: 'સંભવિત યોગ્ય પાર્કિંગ',
      perm_req_title: 'કેમેરા પરવાનગી જરૂરી',
      perm_req_desc: 'પાર્કિંગ લાઇન સ્કેન કરવા માટે ફોનના કેમેરાની મંજૂરી આપો. એઆઇ યોગ્ય સ્થાન હાઇલાઇટ કરશે.',
      perm_security: '🔒 વિડીયો માત્ર લોકલ પ્રોસેસ થાય છે. કંઈપણ સંગ્રહિત થતું નથી.',
      btn_allow_cam: '📷 મંજૂરી આપો અને કેમેરા ખોલો',
      btn_sim_cam: '🎬 સિમ્યુલેટેડ કેમેરા વાપરો',
      scan_radar: 'YOLOv8 સ્કેનિંગ ચાલુ છે...',
      cam_ready: 'કેમેરા તૈયાર છે',
      cam_free_parking: '🟢 મફત પાર્કિંગ',
      cam_stop: 'રોકો',
      cam_start: 'શરૂ કરો',
      cam_flip: 'કેમેરા ફેરવો',
      cam_scan_now: 'હમણાં સ્કેન કરો',
      cam_auto_on: 'ઓટો: ચાલુ',
      cam_auto_off: 'ઓટો: બંધ',
      cam_speak: 'અવાજ (Speak)',
      rec_badge: '⭐ તમારા વાહન માટે ભલામણ કરેલ સ્થાન',
      rec_scanning: 'સ્કેન થઈ રહ્યું છે...',
      rec_point_cam: 'કેમેરા પાર્કિંગ લાઇન તરફ રાખો',
      spec_bay_size: 'જગ્યાનું માપ:',
      spec_your_veh: 'તમારું વાહન:',
      spec_clearance: 'સુરક્ષિત માર્જિન:',
      spec_parking_fee: 'પાર્કિંગ ફી:',
      fee_free_val: 'મફત (શૂન્ય ફી)',
      rec_aim_msg: 'ખાલી જગ્યાઓ શોધવા માટે કેમેરાને પાર્કિંગ લાઇન તરફ સ્થિર રાખો.',
      btn_parked_done: '✅ વાહન પાર્ક થઈ ગયું — પૂર્ણ!',
      detected_bays_title: 'શોધાયેલ પાર્કિંગ સ્પોટ્સ',
      btn_back_map: '← નકશા પર પાછા જાઓ',

      // Registration & Login Modal
      tab_register: '📝 વાહન અને રાઇડર નોંધણી',
      tab_login: '🔑 હાલના વપરાશકર્તા લૉગિન',
      auth_create_title: 'નવું ખાતું બનાવો',
      auth_create_desc: 'વાહનનું નામ દાખલ કરો — લંબાઈ અને પહોળાઈ આપમેળે આવી જશે.',
      lbl_email: 'ઈમેલ એડ્રેસ',
      ph_email: 'you@example.com (અથવા ઓટો-જનરેટેડ)',
      lbl_pwd: 'પાસવર્ડ',
      ph_pwd: 'પાસવર્ડ બનાવો (ડિફૉલ્ટ: 123456)',
      btn_close: 'બંધ કરો',
      btn_complete_reg: '🚀 નોંધણી પૂર્ણ કરો અને પાર્કિંગ શોધો',
      auth_login_title: 'સ્વાગત છે',
      auth_login_desc: 'તમારા રજીસ્ટર વાહનને ઍક્સેસ કરવા અને મફત પાર્કિંગ શોધવા માટે સાઇન ઇન કરો.',
      ph_login_email: 'you@example.com',
      ph_login_pwd: 'પાસવર્ડ દાખલ કરો',
      btn_signin: '🔑 સાઇન ઇન કરો',

      // Advanced Tabs
      nav_tab_arch: 'આર્કિટેક્ચર અને ડેટાસેટ',
      nav_tab_camera: 'મોબાઇલ કેમેરા સ્કેનર',
      nav_tab_map: 'લાઇવ જીપીએસ અને મફત પાર્કિંગ',
      nav_tab_cv: 'સીવી ડાયગ્નોસ્ટિક્સ લેબ',
      nav_tab_flow: '8-સ્ટેપ ડ્રાઈવર ફ્લો',
      nav_tab_rules: 'પાર્કિંગ નિયમો',
      nav_tab_api: 'એપીઆઈ સર્વર',

      // Toasts & Speech
      toast_profile_saved: '✅ પ્રોફાઇલ સફળતાપૂર્વક સાચવવામાં આવી!',
      toast_gps_detected: '📍 જીપીએસ સ્થાન મળ્યું: ',
      toast_parked_success: '🎉 પાર્કિંગ કન્ફર્મ થયું! તમારી મુસાફરી સુખદ રહે!',
      speech_parked_success: 'તમારું વાહન સુરક્ષિત રીતે પાર્ક થઈ ગયું છે. તમારો દિવસ સારો રહે!',
      speech_rec_bay: 'યોગ્ય જગ્યા મળી! તમારા વાહનને {bay} માં પાર્ક કરો. પાર્કિંગ તદ્દન મફત છે.',
      speech_no_spot: 'હાલમાં કોઈ યોગ્ય ખાલી જગ્યા દેખાતી નથી. કૃપા કરીને કેમેરા ફેરવો.'
    },

    mr: {
      // Branding & Header
      brand_title: 'PARKVISION',
      brand_accent: 'AI',
      brand_sub: 'स्मार्ट पार्किंग शोध प्रणाली · शून्य शुल्क · मोफत सार्वजनिक जागा',
      btn_arch: '⭐ आर्किटेक्चर आणि डेटासेट',
      btn_advanced: '⚙️ प्रगत दृश्य (Advanced)',
      btn_wizard: '🧙 विझार्ड दृश्य',
      btn_auth_open: '🔐 नोंदणी / लॉगिन',
      btn_logout: '🚪 बाहेर पडा',
      lang_label: 'भाषा',

      // Wizard Stepper
      step_vehicle: 'वाहन',
      step_location: 'स्थान',
      step_parking: 'पार्किंग शोधा',
      step_navigate: 'नेव्हिगेट',
      step_ar: 'एआर स्कॅन',

      // Wizard Step 1: Vehicle
      wz_s1_tag: 'टप्पा 1 / 5',
      wz_s1_title: 'तुमचे वाहन प्रोफाइल निवडा',
      wz_s1_sub: 'फक्त वाहनाचे नाव प्रविष्ट करा (कार, रिक्षा, बाईक, स्कूटर) — लांबी आणि रुंदी 200+ वाहनांमधून आपोआप शोधली जाईल!',
      lbl_full_name: 'पूर्ण नाव',
      ph_full_name: 'उदा. राहुल शर्मा',
      lbl_mobile: 'मोबाईल नंबर',
      ph_mobile: '+91 XXXXX XXXXX',
      lbl_veh_filter: 'वाहन प्रकार फिल्टर',
      cat_all: '🌟 सर्व वाहने',
      cat_2w: '🏍️ 2-चाकी (बाईक आणि स्कूटर)',
      cat_3w: '🛺 3-चाकी (ऑटो रिक्षा)',
      cat_4w: '🚗 4-चाकी (कार आणि एसयूव्ही)',
      lbl_veh_name: 'वाहनाचे नाव / मॉडेल',
      hint_veh_name: 'फक्त नाव लिहा — परिमाणे आपोआप शोधली जातात',
      ph_veh_name: 'वाहनाचे नाव लिहा उदा. Swift, Activa, Auto Rickshaw, Thar, Creta, Treo...',
      lbl_quick_pick: '⚡ त्वरित निवड:',
      lbl_length: 'लांबी (मीटर)',
      lbl_width: 'रुंदी (मीटर)',
      tag_auto: '✨ आपोआप शोधले',
      lbl_plate: 'गाडी क्रमांक / नंबर प्लेट',
      ph_plate: 'उदा. MH-02-AB-1234',
      btn_save_loc: '🚀 जतन करा आणि स्थान शोधा',
      btn_edit: '✏️ संपादित करा',

      // Wizard Step 2: Location
      wz_s2_tag: 'टप्पा 2 / 5',
      wz_s2_title: 'तुमचे थेट स्थान शोधा',
      wz_s2_sub: 'जवळपासची मोफत पार्किंग शोधण्यासाठी जीपीएस आवश्यक आहे. तुमचे स्थान खाजगी राहील.',
      gps_waiting: 'जीपीएस सिग्नलची वाट पाहत आहे...',
      gps_click_hint: 'सुरू करण्यासाठी खालील बटणावर क्लिक करा',
      lbl_or_set_city: 'किंवा शहर निवडा:',
      btn_detect_gps: '📍 माझे जीपीएस स्थान शोधा',
      btn_back: '← मागे जा',

      // Wizard Step 3: Find Parking
      wz_s3_tag: 'टप्पा 3 / 5',
      wz_s3_title: 'जवळपास मोफत पार्किंग',
      wz_s3_sub: 'जवळपासच्या 100% मोफत सार्वजनिक जागा. कोणतेही शुल्क नाही, बुकिंगची गरज नाही.',
      finding_free_parking: 'जवळपास मोफत पार्किंग शोधत आहे...',
      badge_free_public: '🟢 100% मोफत सार्वजनिक पार्किंग',
      bays_found: 'मोफत जागा सापडल्या',
      btn_nav_lot: '🧭 निवडलेल्या जागेकडे नेव्हिगेट करा →',

      // Wizard Step 4: Navigate
      wz_s4_tag: 'टप्पा 4 / 5',
      wz_s4_title: 'पार्किंगकडे नेव्हिगेट करा',
      wz_s4_sub: 'निवडलेल्या पार्किंगकडे जा. पोहोचल्यावर खालील बटण दाबून कॅमेरा स्कॅनर सुरू करा.',
      badge_zero_fee: 'शून्य शुल्क',
      lbl_km_away: 'किमी अंतरावर',
      lbl_mins: 'मिनिटे',
      lbl_free_bays: 'मोफत जागा',
      gmaps_tip: 'Google Maps मध्ये दिशानिर्देश मिळवण्यासाठी क्लिक करा किंवा नकाशा फॉलो करा. पोहोचल्यावर "मी पोहोचलो" दाबा.',
      btn_arrived: '📍 मी पोहोचलो — कॅमेरा स्कॅनर सुरू करा →',
      btn_open_gmaps: '🗺️ Google Maps मध्ये उघडा',

      // Wizard Step 5: Camera Scan
      wz_s5_tag: 'टप्पा 5 / 5',
      wz_s5_title: 'कॅमेरा पार्किंग रांगेकडे दाखवा',
      wz_s5_sub: 'एआय रिकाम्या जागा शोधून तुमच्या वाहनासाठी योग्य जागा सुचवते. 100% मोफत.',
      pointer_park_here: 'संभाव्य योग्य पार्किंग',
      perm_req_title: 'कॅमेरा परवानगी आवश्यक',
      perm_req_desc: 'पार्किंग रांग स्कॅन करण्यासाठी कॅमेरा परवानगी द्या. एआय सर्वोत्तम जागा दाखवेल.',
      perm_security: '🔒 व्हिडिओ फक्त स्थानिक पातळीवर प्रोसेस केला जातो.',
      btn_allow_cam: '📷 परवानगी द्या आणि कॅमेरा सुरू करा',
      btn_sim_cam: '🎬 सिम्युलेटेड कॅमेरा वापरा',
      scan_radar: 'YOLOv8 स्कॅनिंग सुरू आहे...',
      cam_ready: 'कॅमेरा सज्ज आहे',
      cam_free_parking: '🟢 मोफत पार्किंग',
      cam_stop: 'थांबवा',
      cam_start: 'सुरू करा',
      cam_flip: 'कॅमेरा उलटा करा',
      cam_scan_now: 'आता स्कॅन करा',
      cam_auto_on: 'ऑटो: सुरू',
      cam_auto_off: 'ऑटो: बंद',
      cam_speak: 'आवाज (Speak)',
      rec_badge: '⭐ तुमच्या वाहनासाठी शिफारस केलेली जागा',
      rec_scanning: 'स्कॅन होत आहे...',
      rec_point_cam: 'कॅमेरा पार्किंग रांगेकडे धरा',
      spec_bay_size: 'जागेचा आकार:',
      spec_your_veh: 'तुमचे वाहन:',
      spec_clearance: 'सुरक्षित अंतर:',
      spec_parking_fee: 'पार्किंग शुल्क:',
      fee_free_val: 'मोफत (शून्य शुल्क)',
      rec_aim_msg: 'उपलब्ध जागा शोधण्यासाठी कॅमेरा पार्किंग रांगेकडे रोखा.',
      btn_parked_done: '✅ वाहन पार्क केले — पूर्ण!',
      detected_bays_title: 'दिसणाऱ्या पार्किंग जागा',
      btn_back_map: '← नकाशावर परत जा',

      // Registration & Login Modal
      tab_register: '📝 रायडर व वाहन नोंदणी',
      tab_login: '🔑 जुने वापरकर्ता लॉगिन',
      auth_create_title: 'खाते तयार करा',
      auth_create_desc: 'वाहनाचे नाव टाका — परिमाणे आपोआप घेतली जातील.',
      lbl_email: 'ईमेल पत्ता',
      ph_email: 'you@example.com (किंवा आपोआप)',
      lbl_pwd: 'पासवर्ड',
      ph_pwd: 'पासवर्ड तयार करा (डिफॉल्ट: 123456)',
      btn_close: 'बंद करा',
      btn_complete_reg: '🚀 नोंदणी पूर्ण करा व जागा शोधा',
      auth_login_title: 'स्वागत आहे',
      auth_login_desc: 'तुमच्या वाहनाच्या तपशीलात प्रवेश करण्यासाठी साइन इन करा.',
      ph_login_email: 'you@example.com',
      ph_login_pwd: 'पासवर्ड टाका',
      btn_signin: '🔑 साइन इन करा',

      // Advanced Tabs
      nav_tab_arch: 'आर्किटेक्चर व डेटासेट',
      nav_tab_camera: 'कॅमेरा स्कॅनर',
      nav_tab_map: 'थेट जीपीएस व मोफत जागा',
      nav_tab_cv: 'सीव्ही लॅब',
      nav_tab_flow: '8-टप्पे चालक प्रवाह',
      nav_tab_rules: 'पार्किंग नियम',
      nav_tab_api: 'एपीआय सर्व्हर',

      // Toasts & Speech
      toast_profile_saved: '✅ प्रोफाइल यशस्वीरित्या जतन झाले!',
      toast_gps_detected: '📍 जीपीएस स्थान मिळाले: ',
      toast_parked_success: '🎉 पार्किंग निश्चित झाले! प्रवास सुखकर होवो!',
      speech_parked_success: 'तुमचे वाहन सुरक्षित पार्क झाले आहे. तुमचा दिवस चांगला जावो!',
      speech_rec_bay: 'योग्य जागा सापडली! तुमचे वाहन {bay} मध्ये पार्क करा. पार्किंग मोफत आहे.',
      speech_no_spot: 'सध्या कोणतीही योग्य मोफत जागा दिसत नाही.'
    },

    es: {
      // Branding & Header
      brand_title: 'PARKVISION',
      brand_accent: 'AI',
      brand_sub: 'Detección Inteligente de Aparcamiento · Cero Tarifas · Plazas Públicas Gratuitas',
      btn_arch: '⭐ Arquitectura y Datos',
      btn_advanced: '⚙️ Vista Avanzada',
      btn_wizard: '🧙 Vista Asistente',
      btn_auth_open: '🔐 Registro / Login',
      btn_logout: '🚪 Cerrar Sesión',
      lang_label: 'Idioma',

      // Wizard Stepper
      step_vehicle: 'Vehículo',
      step_location: 'Ubicación',
      step_parking: 'Buscar Parking',
      step_navigate: 'Navegar',
      step_ar: 'Escaneo AR',

      // Wizard Step 1: Vehicle
      wz_s1_tag: 'Paso 1 de 5',
      wz_s1_title: 'Seleccione su Perfil de Vehículo',
      wz_s1_sub: '¡Ingrese SOLO el nombre del vehículo (Coche, Moto, Scooter o EV) — el largo y ancho se detectan automáticamente!',
      lbl_full_name: 'Nombre Completo',
      ph_full_name: 'ej. Carlos García',
      lbl_mobile: 'Teléfono Móvil',
      ph_mobile: '+34 XXX XXX XXX',
      lbl_veh_filter: 'Filtro por Tipo de Vehículo',
      cat_all: '🌟 Todos los Vehículos',
      cat_2w: '🏍️ 2 Ruedas (Motos y Scooters)',
      cat_3w: '🛺 3 Ruedas (Tuk-Tuk)',
      cat_4w: '🚗 4 Ruedas (Coches y SUV)',
      lbl_veh_name: 'Nombre / Modelo del Vehículo',
      hint_veh_name: 'Solo nombre — dimensiones automáticas',
      ph_veh_name: 'Escriba el nombre ej. Swift, Activa, Vespa, Thar, Creta...',
      lbl_quick_pick: '⚡ Acceso Rápido:',
      lbl_length: 'Longitud (m)',
      lbl_width: 'Anchura (m)',
      tag_auto: '✨ Auto-Detectado',
      lbl_plate: 'Matrícula',
      ph_plate: 'ej. 1234 ABC',
      btn_save_loc: '🚀 Guardar y Detectar Mi Ubicación',
      btn_edit: '✏️ Editar',

      // Wizard Step 2: Location
      wz_s2_tag: 'Paso 2 de 5',
      wz_s2_title: 'Detectar su Ubicación en Vivo',
      wz_s2_sub: 'Necesitamos su ubicación GPS para encontrar las plazas gratuitas más cercanas. Sus datos son privados.',
      gps_waiting: 'Esperando señal GPS...',
      gps_click_hint: 'Haga clic en el botón de abajo para comenzar',
      lbl_or_set_city: 'O seleccione una ciudad:',
      btn_detect_gps: '📍 Detectar Mi Ubicación GPS',
      btn_back: '← Atrás',

      // Wizard Step 3: Find Parking
      wz_s3_tag: 'Paso 3 de 5',
      wz_s3_title: 'Aparcamiento Gratuito Cercano',
      wz_s3_sub: 'Mostrando plazas 100% públicas y gratuitas cerca. Sin tarifas ni reservas. Toque para seleccionar.',
      finding_free_parking: 'Buscando aparcamiento gratuito cerca...',
      badge_free_public: '🟢 100% Aparcamiento Gratuito',
      bays_found: 'plazas libres encontradas',
      btn_nav_lot: '🧭 Navegar al Parking Seleccionado →',

      // Wizard Step 4: Navigate
      wz_s4_tag: 'Paso 4 de 5',
      wz_s4_title: 'Navegar al Parking',
      wz_s4_sub: 'Conduzca hasta la instalación seleccionada. Al llegar, pulse el botón para iniciar el escáner de cámara.',
      badge_zero_fee: 'Gratis',
      lbl_km_away: 'km de distancia',
      lbl_mins: 'minutos',
      lbl_free_bays: 'plazas libres',
      gmaps_tip: 'Abra Google Maps para navegación giro a giro o siga el mapa anterior. Pulse "He llegado" en la entrada.',
      btn_arrived: '📍 He Llegado — Abrir Escáner de Cámara →',
      btn_open_gmaps: '🗺️ Abrir en Google Maps',

      // Wizard Step 5: Camera Scan
      wz_s5_tag: 'Paso 5 de 5',
      wz_s5_title: 'Apunte la Cámara a la Fila de Plazas',
      wz_s5_sub: 'La IA detecta espacios libres y sugiere el mejor sitio para su vehículo. 100% gratis.',
      pointer_park_here: 'POTENCIALMENTE ADECUADO',
      perm_req_title: 'Permiso de Cámara Necesario',
      perm_req_desc: 'Permita el acceso a la cámara trasera. La IA resaltará el mejor espacio para su vehículo.',
      perm_security: '🔒 Los fotogramas se procesan de forma local. Nada se almacena.',
      btn_allow_cam: '📷 Permitir y Abrir Cámara',
      btn_sim_cam: '🎬 Usar Cámara Simulada',
      scan_radar: 'YOLOv8 Escaneando...',
      cam_ready: 'Cámara Lista',
      cam_free_parking: '🟢 Aparcamiento GRATIS',
      cam_stop: 'Detener',
      cam_start: 'Iniciar',
      cam_flip: 'Cambiar Cámara',
      cam_scan_now: 'Escanear Ahora',
      cam_auto_on: 'Auto: SÍ',
      cam_auto_off: 'Auto: NO',
      cam_speak: 'Voz (Speak)',
      rec_badge: '⭐ PLAZA SUGERIDA PARA SU VEHÍCULO',
      rec_scanning: 'Analizando...',
      rec_point_cam: 'Apunte la cámara a la fila de plazas',
      spec_bay_size: 'Tamaño Plaza:',
      spec_your_veh: 'Su Vehículo:',
      spec_clearance: 'Margen Seguro:',
      spec_parking_fee: 'Tarifa:',
      fee_free_val: 'GRATIS (0 €)',
      rec_aim_msg: 'Apunte la cámara a la fila de aparcamiento para detectar espacios libres.',
      btn_parked_done: '✅ Vehículo Aparcado — ¡Listo!',
      detected_bays_title: 'Plazas Detectadas en Vista',
      btn_back_map: '← Volver al Mapa',

      // Registration & Login Modal
      tab_register: '📝 Registro de Conductor y Vehículo',
      tab_login: '🔑 Iniciar Sesión',
      auth_create_title: 'Cree su Cuenta de Conductor',
      auth_create_desc: 'Ingrese el nombre de su vehículo — las dimensiones se cargarán automáticamente.',
      lbl_email: 'Correo Electrónico',
      ph_email: 'usuario@ejemplo.com',
      lbl_pwd: 'Contraseña',
      ph_pwd: 'Cree una contraseña (por defecto: 123456)',
      btn_close: 'Cerrar',
      btn_complete_reg: '🚀 Completar Registro y Buscar Plazas',
      auth_login_title: 'Bienvenido de Nuevo',
      auth_login_desc: 'Inicie sesión para acceder a su perfil y encontrar aparcamiento gratuito.',
      ph_login_email: 'usuario@ejemplo.com',
      ph_login_pwd: 'Su contraseña',
      btn_signin: '🔑 Iniciar Sesión',

      // Advanced Tabs
      nav_tab_arch: 'Arquitectura y Datos',
      nav_tab_camera: 'Escáner de Cámara Móvil',
      nav_tab_map: 'GPS en Vivo y Plazas Libres',
      nav_tab_cv: 'Laboratorio de Diagnóstico CV',
      nav_tab_flow: 'Flujo de Conductor en 8 Pasos',
      nav_tab_rules: 'Normativa de Aparcamiento',
      nav_tab_api: 'Servidor API',

      // Toasts & Speech
      toast_profile_saved: '✅ ¡Perfil guardado con éxito!',
      toast_gps_detected: '📍 Ubicación GPS obtenida: ',
      toast_parked_success: '🎉 ¡Aparcamiento confirmado! ¡Buen viaje!',
      speech_parked_success: 'Su vehículo está aparcado de forma segura. ¡Que tenga un excelente día!',
      speech_rec_bay: '¡Plaza encontrada! Aparque su vehículo en {bay}. El aparcamiento es gratuito.',
      speech_no_spot: 'No se detecta ninguna plaza adecuada en este momento.'
    },

    fr: {
      // Branding & Header
      brand_title: 'PARKVISION',
      brand_accent: 'AI',
      brand_sub: 'Détection Intelligente de Stationnement · 100% Gratuit · Places Libres',
      btn_arch: '⭐ Architecture et Données',
      btn_advanced: '⚙️ Vue Avancée',
      btn_wizard: '🧙 Vue Assistant',
      btn_auth_open: '🔐 Inscription / Connexion',
      btn_logout: '🚪 Se Déconnecter',
      lang_label: 'Langue',

      // Wizard Stepper
      step_vehicle: 'Véhicule',
      step_location: 'Localisation',
      step_parking: 'Trouver Place',
      step_navigate: 'Naviguer',
      step_ar: 'Scan RA',

      // Wizard Step 1: Vehicle
      wz_s1_tag: 'Étape 1 sur 5',
      wz_s1_title: 'Sélectionnez votre Profil Véhicule',
      wz_s1_sub: 'Entrez SEULEMENT le nom du véhicule (Voiture, Scooter, Moto, EV) — la longueur et la largeur sont automatiquement calculées !',
      lbl_full_name: 'Nom Complet',
      ph_full_name: 'ex. Thomas Dupont',
      lbl_mobile: 'Numéro de Mobile',
      ph_mobile: '+33 X XX XX XX XX',
      lbl_veh_filter: 'Filtrer par Catégorie',
      cat_all: '🌟 Tous les Véhicules',
      cat_2w: '🏍️ 2 Roues (Motos & Scooters)',
      cat_3w: '🛺 3 Roues (Tuk-Tuk)',
      cat_4w: '🚗 4 Roues (Voitures & SUV)',
      lbl_veh_name: 'Nom / Modèle du Véhicule',
      hint_veh_name: 'Nom seulement — dimensions automatiques',
      ph_veh_name: 'ex. Swift, Activa, Vespa, Clio, Thar, Creta...',
      lbl_quick_pick: '⚡ Choix Rapide :',
      lbl_length: 'Longueur (m)',
      lbl_width: 'Largeur (m)',
      tag_auto: '✨ Détecté Automatiquement',
      lbl_plate: 'Immatriculation',
      ph_plate: 'ex. AB-123-CD',
      btn_save_loc: '🚀 Enregistrer et Me Localiser',
      btn_edit: '✏️ Modifier',

      // Wizard Step 2: Location
      wz_s2_tag: 'Étape 2 sur 5',
      wz_s2_title: 'Détecter votre Position en Direct',
      wz_s2_sub: 'Nous utilisons votre position GPS pour trouver les places gratuites les plus proches. Vos données restent privées.',
      gps_waiting: 'Recherche du signal GPS...',
      gps_click_hint: 'Cliquez sur le bouton ci-dessous pour démarrer',
      lbl_or_set_city: 'Ou choisissez une ville :',
      btn_detect_gps: '📍 Détecter ma Position GPS',
      btn_back: '← Retour',

      // Wizard Step 3: Find Parking
      wz_s3_tag: 'Étape 3 sur 5',
      wz_s3_title: 'Places Gratuites à Proximité',
      wz_s3_sub: 'Affichage des parkings publics 100% gratuits à proximité. Sans frais ni réservation requise.',
      finding_free_parking: 'Recherche de parkings gratuits...',
      badge_free_public: '🟢 100% Stationnement Gratuit',
      bays_found: 'places libres trouvées',
      btn_nav_lot: '🧭 Naviguer vers ce Parking →',

      // Wizard Step 4: Navigate
      wz_s4_tag: 'Étape 4 sur 5',
      wz_s4_title: 'Naviguer vers le Parking',
      wz_s4_sub: 'Roulez jusqu\'au parking choisi. À votre arrivée, appuyez sur le bouton ci-dessous pour lancer la caméra.',
      badge_zero_fee: 'Gratuit',
      lbl_km_away: 'km restants',
      lbl_mins: 'min',
      lbl_free_bays: 'places libres',
      gmaps_tip: 'Ouvrez Google Maps pour le guidage pas à pas ou suivez la carte. Cliquez sur "Je suis arrivé" à l\'entrée.',
      btn_arrived: '📍 Je suis Arrivé — Lancer la Caméra →',
      btn_open_gmaps: '🗺️ Ouvrir dans Google Maps',

      // Wizard Step 5: Camera Scan
      wz_s5_tag: 'Étape 5 sur 5',
      wz_s5_title: 'Pointez la Caméra vers la Rangée',
      wz_s5_sub: 'L\'IA analyse les places libres et conseille le meilleur emplacement pour votre véhicule. 100% gratuit.',
      pointer_park_here: 'POTENTIELLEMENT ADAPTÉ',
      perm_req_title: 'Autorisation Caméra Requise',
      perm_req_desc: 'Autorisez l\'accès à la caméra arrière. L\'IA mettra en évidence l\'emplacement idéal.',
      perm_security: '🔒 Traitement local uniquement. Aucune image n\'est enregistrée.',
      btn_allow_cam: '📷 Autoriser et Ouvrir la Caméra',
      btn_sim_cam: '🎬 Utiliser la Caméra Simulée',
      scan_radar: 'Scan YOLOv8 en cours...',
      cam_ready: 'Caméra Prête',
      cam_free_parking: '🟢 Parking GRATUIT',
      cam_stop: 'Arrêter',
      cam_start: 'Démarrer',
      cam_flip: 'Changer Caméra',
      cam_scan_now: 'Scanner Maintenant',
      cam_auto_on: 'Auto : OUI',
      cam_auto_off: 'Auto : NON',
      cam_speak: 'Voix (Speak)',
      rec_badge: '⭐ EMPLACEMENT CONSEILLÉ POUR VOTRE VÉHICULE',
      rec_scanning: 'Analyse...',
      rec_point_cam: 'Pointez la caméra vers la rangée',
      spec_bay_size: 'Taille Place :',
      spec_your_veh: 'Votre Véhicule :',
      spec_clearance: 'Marge Sécurité :',
      spec_parking_fee: 'Tarif :',
      fee_free_val: 'GRATUIT (0 €)',
      rec_aim_msg: 'Pointez votre caméra vers la rangée de stationnement pour détecter les places disponibles.',
      btn_parked_done: '✅ Véhicule Garé — Terminé !',
      detected_bays_title: 'Places Détectées',
      btn_back_map: '← Retour à la Carte',

      // Registration & Login Modal
      tab_register: '📝 Enregistrement Conducteur & Véhicule',
      tab_login: '🔑 Connexion Existante',
      auth_create_title: 'Créez votre Compte Conducteur',
      auth_create_desc: 'Entrez le modèle du véhicule — les dimensions seront chargées automatiquement.',
      lbl_email: 'Adresse Email',
      ph_email: 'vous@exemple.com',
      lbl_pwd: 'Mot de passe',
      ph_pwd: 'Créez un mot de passe (par défaut : 123456)',
      btn_close: 'Fermer',
      btn_complete_reg: '🚀 Valider et Trouver des Places',
      auth_login_title: 'Bon Retour Parmi Nous',
      auth_login_desc: 'Connectez-vous pour retrouver votre profil et vous garer gratuitement.',
      ph_login_email: 'vous@exemple.com',
      ph_login_pwd: 'Mot de passe',
      btn_signin: '🔑 Se Connecter',

      // Advanced Tabs
      nav_tab_arch: 'Architecture & Données',
      nav_tab_camera: 'Caméra Scanner',
      nav_tab_map: 'GPS & Places Libres',
      nav_tab_cv: 'Laboratoire Diagnostic CV',
      nav_tab_flow: 'Parcours Conducteur en 8 Étapes',
      nav_tab_rules: 'Règles de Stationnement',
      nav_tab_api: 'Serveur API',

      // Toasts & Speech
      toast_profile_saved: '✅ Profil enregistré avec succès !',
      toast_gps_detected: '📍 Position GPS acquise : ',
      toast_parked_success: '🎉 Stationnement confirmé ! Bonne route !',
      speech_parked_success: 'Votre véhicule est garé en toute sécurité. Bonne journée !',
      speech_rec_bay: 'Emplacement idéal trouvé ! Garez-vous dans {bay}. Le stationnement est gratuit.',
      speech_no_spot: 'Aucun emplacement adapté n\'est visible pour le moment.'
    }
  };

  class I18nManager {
    constructor() {
      this.storageKey = 'parkvision_lang';
      this.defaultLang = 'en'; // DEFAULT IS ENGLISH
      this.currentLang = this.getSavedLang() || this.defaultLang;
      this.languages = LANGUAGES;
      this.translations = TRANSLATIONS;
    }

    getSavedLang() {
      try {
        const saved = localStorage.getItem(this.storageKey);
        if (saved && LANGUAGES[saved]) {
          return saved;
        }
      } catch (e) {
        console.warn('Could not read localStorage for language:', e);
      }
      return null;
    }

    t(key, fallback = '') {
      const langDict = this.translations[this.currentLang] || this.translations[this.defaultLang];
      if (langDict && langDict[key] !== undefined) {
        return langDict[key];
      }
      // fallback to English
      const enDict = this.translations[this.defaultLang];
      if (enDict && enDict[key] !== undefined) {
        return enDict[key];
      }
      return fallback || key;
    }

    setLanguage(lang) {
      if (!LANGUAGES[lang]) {
        console.warn(`Language ${lang} not supported. Defaulting to ${this.defaultLang}`);
        lang = this.defaultLang;
      }
      this.currentLang = lang;
      try {
        localStorage.setItem(this.storageKey, lang);
      } catch (e) {
        console.warn('Could not save language to localStorage:', e);
      }

      document.documentElement.setAttribute('lang', lang);
      this.updateDOM();
      this.updateDropdowns();

      // Emit event for dynamic components
      window.dispatchEvent(new CustomEvent('languageChanged', {
        detail: {
          lang: this.currentLang,
          speechLang: LANGUAGES[this.currentLang]?.speechLang || 'en-US',
          t: (k, fb) => this.t(k, fb)
        }
      }));
    }

    updateDOM() {
      // Elements with data-i18n
      const elements = document.querySelectorAll('[data-i18n]');
      elements.forEach(el => {
        const key = el.getAttribute('data-i18n');
        if (key) {
          const translated = this.t(key);
          if (el.hasAttribute('data-i18n-html')) {
            el.innerHTML = translated;
          } else {
            el.textContent = translated;
          }
        }
      });

      // Placeholders
      const inputs = document.querySelectorAll('[data-i18n-placeholder]');
      inputs.forEach(el => {
        const key = el.getAttribute('data-i18n-placeholder');
        if (key) {
          el.setAttribute('placeholder', this.t(key));
        }
      });

      // Titles / Tooltips
      const titles = document.querySelectorAll('[data-i18n-title]');
      titles.forEach(el => {
        const key = el.getAttribute('data-i18n-title');
        if (key) {
          el.setAttribute('title', this.t(key));
        }
      });
    }

    updateDropdowns() {
      const langInfo = LANGUAGES[this.currentLang] || LANGUAGES[this.defaultLang];
      const htmlContent = `<span class="lang-flag">${langInfo.flag}</span> <span class="lang-text-label">${langInfo.nativeName}</span>`;

      // Update Wizard header display
      const wzCurrent = document.getElementById('wz-lang-current');
      if (wzCurrent) {
        wzCurrent.innerHTML = htmlContent;
      }

      // Update Auth / Login top bar display
      const authCurrent = document.getElementById('auth-lang-current');
      if (authCurrent) {
        authCurrent.innerHTML = htmlContent;
      }

      // Update Nav header display
      const navCurrent = document.getElementById('nav-lang-current');
      if (navCurrent) {
        navCurrent.innerHTML = htmlContent;
      }

      // Update active option in menus
      document.querySelectorAll('.lang-option').forEach(btn => {
        const btnLang = btn.getAttribute('data-lang');
        btn.classList.toggle('active', btnLang === this.currentLang);
      });
    }

    initDropdownHandlers() {
      const setupDropdown = (toggleId, menuId) => {
        const toggle = document.getElementById(toggleId);
        const menu = document.getElementById(menuId);
        if (!toggle || !menu) return;

        toggle.addEventListener('click', (e) => {
          e.stopPropagation();
          const isOpen = menu.classList.contains('show');
          // Close any other open menus
          document.querySelectorAll('.lang-menu.show').forEach(m => m.classList.remove('show'));
          document.querySelectorAll('.lang-btn[aria-expanded="true"]').forEach(b => b.setAttribute('aria-expanded', 'false'));

          if (!isOpen) {
            menu.classList.add('show');
            toggle.setAttribute('aria-expanded', 'true');
          }
        });
      };

      setupDropdown('wz-lang-btn', 'wz-lang-menu');
      setupDropdown('auth-lang-btn', 'auth-lang-menu');
      setupDropdown('nav-lang-btn', 'nav-lang-menu');

      // Global option click delegate
      document.addEventListener('click', (e) => {
        const opt = e.target.closest('.lang-option');
        if (opt) {
          const selectedLang = opt.getAttribute('data-lang');
          if (selectedLang) {
            this.setLanguage(selectedLang);
          }
          document.querySelectorAll('.lang-menu.show').forEach(m => m.classList.remove('show'));
          document.querySelectorAll('.lang-btn[aria-expanded="true"]').forEach(b => b.setAttribute('aria-expanded', 'false'));
          return;
        }

        // Close when clicking outside
        if (!e.target.closest('.lang-selector-dropdown')) {
          document.querySelectorAll('.lang-menu.show').forEach(m => m.classList.remove('show'));
          document.querySelectorAll('.lang-btn[aria-expanded="true"]').forEach(b => b.setAttribute('aria-expanded', 'false'));
        }
      });

      // Escape key to close
      document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
          document.querySelectorAll('.lang-menu.show').forEach(m => m.classList.remove('show'));
          document.querySelectorAll('.lang-btn[aria-expanded="true"]').forEach(b => b.setAttribute('aria-expanded', 'false'));
        }
      });
    }

    init() {
      this.initDropdownHandlers();
      this.setLanguage(this.currentLang);
    }
  }

  // Expose global instance
  const i18n = new I18nManager();
  window.i18n = i18n;
  window.t = (key, fallback) => i18n.t(key, fallback);

  // Initialize as soon as DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => i18n.init());
  } else {
    i18n.init();
  }

})();
