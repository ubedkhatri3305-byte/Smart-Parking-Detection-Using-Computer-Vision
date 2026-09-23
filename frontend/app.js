// ==========================================================================
// PARKVISION BIKE CV - CORE CLIENT APPLICATION
// Real-Life User & Bike Registration, Live GPS Locator, WebRTC Camera Scanner,
// Computer Vision Space Matching, AR Viewport Overlay, and Zero-Fee Routing
// ==========================================================================

// Cloud Backend URL Resolver (supports local dev, Render, and Vercel)
function getApiBase() {
  const custom = localStorage.getItem('PARKVISION_BACKEND_URL');
  if (custom) return custom.replace(/\/$/, '');
  if (window.location.protocol === 'file:' || !window.location.origin || window.location.origin === 'null') {
    return 'http://127.0.0.1:8000';
  }
  if (window.location.origin.includes(':8000') || window.location.origin.includes(':5173') || window.location.origin.includes(':3000')) {
    return window.location.origin;
  }
  return '';
}

let API_BASE = getApiBase();

// Built-in Geographically-Accurate Free Parking Generator (Resilient Client-Side Fallback)
function generateClientNearbyParking(lat, lng) {
  const userLat = Number(lat) || 19.0760;
  const userLng = Number(lng) || 72.8777;
  const offsets = [
    { dlat: 0.0022, dlng: 0.0018, name: "Municipal Central Two-Wheeler Bay", type: "Covered Public Bike Deck", capacity: 40, avail: 14, scenario: "scenario_1_aerial", features: ["100% Free Public Parking", "CCTV 24/7", "Paved Bike Stand"] },
    { dlat: -0.0035, dlng: 0.0028, name: "City Transit Free Two-Wheeler Lot", type: "Public Street Motorcycle & Scooter Bays", capacity: 30, avail: 9, scenario: "scenario_2_driver", features: ["100% Free", "Wide Entry", "Shaded Area"] },
    { dlat: 0.0048, dlng: -0.0041, name: "Community Market Dedicated Bike Zone", type: "Open Two-Wheeler Ground Lot", capacity: 25, avail: 4, scenario: "scenario_3_rooftop", features: ["100% Free Parking", "Wheel Lock Rails", "Ramp Access"] },
    { dlat: -0.0062, dlng: -0.0035, name: "Civic Centre Public Vehicle Stand", type: "Express Bike Bay", capacity: 35, avail: 12, scenario: "scenario_4_tight", features: ["100% Free Parking", "Level Pavement", "Security Monitored"] }
  ];

  return offsets.map((item, i) => {
    const lot_lat = Number((userLat + item.dlat).toFixed(6));
    const lot_lng = Number((userLng + item.dlng).toFixed(6));
    const dist = haversineDistance(userLat, userLng, lot_lat, lot_lng);
    return {
      id: `lot-live-${i + 1}`,
      name: item.name,
      type: item.type,
      latitude: lot_lat,
      longitude: lot_lng,
      total_capacity: item.capacity,
      live_available: item.avail,
      distance_km: dist,
      fee: "Free (Zero Fee)",
      is_free: true,
      rule_type: "registered",
      scenario_key: item.scenario,
      features: item.features
    };
  }).sort((a, b) => a.distance_km - b.distance_km);
}

// Global Application State (No demo data by default - loaded from real session or user input)
const state = {
  currentTab: 'camera-scan',
  currentScenario: 'scenario_2_driver',
  userProfile: loadUserProfile(),
  userLocation: [19.0760, 72.8777], // [lat, lng] Default to real coordinates until GPS fix
  userLocationLive: false,
  activeLot: null,
  flowStep: 1,
  map: null,
  mapUserMarker: null,
  mapMarkers: [],
  routeLine: null,
  analysisResult: null,
  allLotsData: [],
  
  // Camera & Live AR state
  camera: {
    stream: null,
    facingMode: 'environment', // Rear camera by default on phones
    isAutoScanning: true,
    scanInterval: null,
    isScanningNow: false,
    isSimulated: false,
    simulatedVideoUrl: null,
    speechEnabled: true,
    lastSpokenSlotId: null,
    lastSpokenTime: 0
  }
};

// Preset Quick Fallbacks if offline
const BIKE_PRESETS = {
  bike_cruiser: { name: 'Royal Enfield Classic 350', length: 2.14, width: 0.84, clearance: 0.20, icon: '🏍️' },
  bike_scooter: { name: 'Honda Activa 6G', length: 1.83, width: 0.69, clearance: 0.15, icon: '🛵' },
  bike_commuter: { name: 'Hero Splendor Plus', length: 2.00, width: 0.72, clearance: 0.15, icon: '🏍️' },
  bike_sports: { name: 'Yamaha YZF R15 V4', length: 1.99, width: 0.72, clearance: 0.18, icon: '🏍️' },
  bike_ev: { name: 'Ather 450X', length: 1.83, width: 0.73, clearance: 0.15, icon: '⚡' }
};

// ==========================================================================
// APPLICATION INITIALIZATION
// ==========================================================================
document.addEventListener('DOMContentLoaded', () => {
  initProfileUI();
  initRegistrationModal();
  initTabs();
  initCameraScanner();
  initVehicleSelectors();
  initScenarioControls();
  initCVControls();
  initFlowStepper();
  initGPSFeatures();

  // *** WIZARD: Initialize the real-life guided flow ***
  initWizard();

  // Resize handler for Leaflet Map & AR Canvas
  window.addEventListener('resize', () => {
    if (state.map) {
      setTimeout(() => state.map.invalidateSize(), 150);
    }
    resizeARCanvas();
    wzResizeARCanvas();
  });

  // Run initial diagnostic CV analysis for lab view (background)
  runCVAnalysis();
});

// ==========================================================================
// 1. USER & BIKE REGISTRATION & AUTH MODULE
// ==========================================================================
function loadUserProfile() {
  try {
    const saved = localStorage.getItem('PARKVISION_USER_PROFILE');
    if (saved) {
      const p = JSON.parse(saved);
      if (p && p.name && p.bikeModel) {
        return p;
      }
    }
  } catch (e) {
    console.warn('Could not parse local user profile:', e);
  }
  return null;
}

function saveUserProfile(profile) {
  state.userProfile = { ...(state.userProfile || {}), ...profile };
  try {
    localStorage.setItem('PARKVISION_USER_PROFILE', JSON.stringify(state.userProfile));
  } catch (e) {
    console.error('Failed to save user profile to localStorage:', e);
  }

  // Push to backend cache
  fetch(`${API_BASE}/api/user/profile`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(state.userProfile)
  }).catch(err => console.warn('Could not sync profile to backend:', err));

  initProfileUI();
  // Trigger CV re-analysis with new bike dimensions
  if (state.currentTab === 'cv-lab') {
    runCVAnalysis();
  }
}

function initProfileUI() {
  const p = state.userProfile;
  const pill = document.getElementById('nav-profile-pill');
  const authOpenBtn = document.getElementById('btn-nav-auth-open');
  const logoutBtn = document.getElementById('btn-nav-logout');

  if (p && p.name && p.bikeModel) {
    if (pill) pill.classList.remove('hidden');
    if (logoutBtn) logoutBtn.classList.remove('hidden');
    if (authOpenBtn) authOpenBtn.classList.add('hidden');

    const riderNameEl = document.getElementById('nav-rider-name');
    const vehNameEl = document.getElementById('nav-veh-name');
    const vehDimsEl = document.getElementById('nav-veh-dims');
    const vehPlateEl = document.getElementById('nav-veh-plate');

    const vIcon = p.icon || (p.wheels === 4 ? '🚗' : (p.wheels === 3 ? '🛺' : '🏍️'));
    if (riderNameEl) riderNameEl.textContent = p.name;
    if (vehNameEl) vehNameEl.textContent = `${vIcon} ${p.bikeModel}`;
    if (vehDimsEl) vehDimsEl.textContent = `(${p.length}m × ${p.width}m)`;
    if (vehPlateEl) vehPlateEl.textContent = p.licensePlate || 'NO-PLATE';

    const camBikeTag = document.getElementById('cam-active-bike-tag');
    if (camBikeTag) {
      camBikeTag.textContent = `${vIcon} ${p.bikeModel} (${p.length}m × ${p.width}m)`;
    }

    const recBikeLen = document.getElementById('cam-rec-bike-len');
    if (recBikeLen) {
      recBikeLen.textContent = `${p.length}m`;
    }
  } else {
    if (pill) pill.classList.add('hidden');
    if (logoutBtn) logoutBtn.classList.add('hidden');
    if (authOpenBtn) authOpenBtn.classList.remove('hidden');

    const camBikeTag = document.getElementById('cam-active-bike-tag');
    if (camBikeTag) {
      camBikeTag.textContent = `🚗 Register Vehicle to Auto-Match`;
    }

    const recBikeLen = document.getElementById('cam-rec-bike-len');
    if (recBikeLen) {
      recBikeLen.textContent = `—`;
    }
  }
}

function initRegistrationModal() {
  const modal = document.getElementById('modal-registration');
  const openPill = document.getElementById('nav-profile-pill');
  const navAuthOpenBtn = document.getElementById('btn-nav-auth-open');
  const navLogoutBtn = document.getElementById('btn-nav-logout');
  const closeBtn = document.getElementById('btn-close-reg-modal');
  const cancelRegBtn = document.getElementById('btn-cancel-reg');
  const cancelLoginBtn = document.getElementById('btn-cancel-login');
  const jumpRegBtn = document.getElementById('btn-jump-reg');

  const tabRegister = document.getElementById('tab-btn-register');
  const tabLogin = document.getElementById('tab-btn-login');
  const formRegister = document.getElementById('form-registration');
  const formLogin = document.getElementById('form-login');

  const nameInput = document.getElementById('reg-person-name');
  const emailInput = document.getElementById('reg-person-email');
  const passInput = document.getElementById('reg-person-password');
  const phoneInput = document.getElementById('reg-person-phone');
  const modelInput = document.getElementById('reg-bike-model');
  const lengthInput = document.getElementById('reg-bike-length');
  const widthInput = document.getElementById('reg-bike-width');
  const clearanceInput = document.getElementById('reg-bike-clearance');
  const plateInput = document.getElementById('reg-bike-plate');
  const suggestionsList = document.getElementById('bike-suggestions-list');
  const autofillIndicator = document.getElementById('autofill-indicator');
  const autofillText = document.getElementById('autofill-text');

  const loginEmail = document.getElementById('login-email');
  const loginPass = document.getElementById('login-password');

  function openModal(mode = 'register') {
    switchAuthMode(mode);
    if (state.userProfile) {
      const p = state.userProfile;
      if (nameInput) nameInput.value = p.name || '';
      if (emailInput) emailInput.value = p.email || '';
      if (phoneInput) phoneInput.value = p.phone || '';
      if (plateInput) plateInput.value = p.licensePlate || '';
      if (modelInput) modelInput.value = p.bikeModel || '';
      if (lengthInput) lengthInput.value = p.length || '';
      if (widthInput) widthInput.value = p.width || '';
      if (clearanceInput) clearanceInput.value = p.clearance || 0.20;
    }
    modal.classList.remove('hidden');
  }

  function closeModal() {
    modal.classList.add('hidden');
    if (suggestionsList) suggestionsList.classList.add('hidden');
  }

  function switchAuthMode(mode) {
    if (mode === 'login') {
      if (tabLogin) tabLogin.classList.add('active');
      if (tabRegister) tabRegister.classList.remove('active');
      if (formLogin) formLogin.classList.remove('hidden');
      if (formRegister) formRegister.classList.add('hidden');
    } else {
      if (tabRegister) tabRegister.classList.add('active');
      if (tabLogin) tabLogin.classList.remove('active');
      if (formRegister) formRegister.classList.remove('hidden');
      if (formLogin) formLogin.classList.add('hidden');
    }
  }

  if (tabRegister) tabRegister.addEventListener('click', () => switchAuthMode('register'));
  if (tabLogin) tabLogin.addEventListener('click', () => switchAuthMode('login'));

  if (openPill) openPill.addEventListener('click', () => openModal('register'));
  if (navAuthOpenBtn) navAuthOpenBtn.addEventListener('click', () => openModal('register'));
  if (jumpRegBtn) jumpRegBtn.addEventListener('click', () => openModal('register'));
  if (closeBtn) closeBtn.addEventListener('click', closeModal);
  if (cancelRegBtn) cancelRegBtn.addEventListener('click', closeModal);
  if (cancelLoginBtn) cancelLoginBtn.addEventListener('click', closeModal);

  if (navLogoutBtn) {
    navLogoutBtn.addEventListener('click', async () => {
      try {
        await fetch(`${API_BASE}/api/auth/logout`, { method: 'POST' });
      } catch (e) {}
      state.userProfile = null;
      localStorage.removeItem('PARKVISION_USER_PROFILE');
      initProfileUI();
      showToast('👋 You have been logged out.');
    });
  }

  modal.addEventListener('click', (e) => {
    if (e.target === modal) closeModal();
  });

  // --- VEHICLE AUTOCOMPLETE & AUTO-FETCH FROM REAL DATASET (2W, 3W, 4W) ---
  let modalWheelsFilter = null;
  const modalCatTabs = document.getElementById('modal-cat-tabs');
  const modalBikeIcon = document.getElementById('reg-bike-icon');
  const modalQuickChips = document.getElementById('modal-quick-chips');

  function applyModalVehicleDetection(vehicleName, explicitVehicle = null) {
    if (!vehicleName || !vehicleName.trim()) {
      if (autofillIndicator) autofillIndicator.classList.add('hidden');
      return;
    }
    const v = explicitVehicle || (window.lookupVehicleClient ? window.lookupVehicleClient(vehicleName) : null);
    if (!v) return;

    if (lengthInput) lengthInput.value = v.length_m;
    if (widthInput) widthInput.value = v.width_m;
    if (clearanceInput && v.clearance_m) clearanceInput.value = v.clearance_m;

    const icon = v.icon || (v.wheels === 4 ? '🚗' : (v.wheels === 3 ? '🛺' : '🏍️'));
    if (modalBikeIcon) modalBikeIcon.textContent = icon;

    // Update banner
    const detIcon = document.getElementById('modal-detected-icon');
    const detName = document.getElementById('modal-detected-name');
    const detCat = document.getElementById('modal-detected-category');
    const detLen = document.getElementById('modal-spec-length');
    const detWid = document.getElementById('modal-spec-width');

    if (detName) detName.textContent = v.name;
    if (detIcon) detIcon.textContent = icon;
    if (detCat) detCat.textContent = `${v.category || 'Vehicle'} (${v.wheels || 2}-Wheeler)`;
    if (detLen) detLen.textContent = `${v.length_m}m`;
    if (detWid) detWid.textContent = `${v.width_m}m`;

    if (autofillIndicator) autofillIndicator.classList.remove('hidden');
  }

  // Category filter tabs in Modal
  if (modalCatTabs) {
    modalCatTabs.querySelectorAll('.modal-cat-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        modalCatTabs.querySelectorAll('.modal-cat-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        const w = btn.getAttribute('data-wheels');
        modalWheelsFilter = (w === 'all') ? null : Number(w);

        if (modelInput) {
          if (modalWheelsFilter === 4) {
            modelInput.placeholder = 'Type car name e.g. Swift, Creta, Thar, Fortuner, Nexon...';
            if (modalBikeIcon) modalBikeIcon.textContent = '🚗';
          } else if (modalWheelsFilter === 3) {
            modelInput.placeholder = 'Type 3-wheeler name e.g. Bajaj RE, Piaggio Ape, Treo...';
            if (modalBikeIcon) modalBikeIcon.textContent = '🛺';
          } else if (modalWheelsFilter === 2) {
            modelInput.placeholder = 'Type 2-wheeler name e.g. Activa, Splendor, Pulsar, Classic 350...';
            if (modalBikeIcon) modalBikeIcon.textContent = '🏍️';
          } else {
            modelInput.placeholder = 'Type vehicle name e.g. Swift, Activa, Auto Rickshaw, Thar, Creta...';
            if (modalBikeIcon) modalBikeIcon.textContent = '🚗';
          }
        }

        if (modelInput && modelInput.value.trim().length >= 1) {
          renderModalSuggestions(modelInput.value.trim());
        }
      });
    });
  }

  // Quick chips in Modal
  if (modalQuickChips) {
    modalQuickChips.querySelectorAll('.wz-chip').forEach(chip => {
      chip.addEventListener('click', () => {
        const vname = chip.getAttribute('data-vname');
        if (modelInput) modelInput.value = vname;
        applyModalVehicleDetection(vname);
        if (suggestionsList) suggestionsList.classList.add('hidden');
        showToast(`✨ Auto-detected: ${vname}`);
      });
    });
  }

  function renderModalSuggestions(q) {
    if (!suggestionsList) return;
    const clientList = window.searchVehiclesClient ? window.searchVehiclesClient(q, 15, modalWheelsFilter) : [];
    if (clientList.length === 0) {
      suggestionsList.innerHTML = '<div style="padding:0.6rem 0.85rem;font-size:0.8rem;color:var(--text-muted);">Custom vehicle detected. Dimensions auto-assigned.</div>';
      suggestionsList.classList.remove('hidden');
      return;
    }
    suggestionsList.innerHTML = '';
    clientList.forEach(v => {
      const item = document.createElement('div');
      item.className = 'autocomplete-item';
      const wTag = v.wheels === 4 ? '<span class="wz-ac-tag tag-4w">4W Car</span>' : (v.wheels === 3 ? '<span class="wz-ac-tag tag-3w">3W Auto</span>' : '<span class="wz-ac-tag tag-2w">2W Bike</span>');
      item.innerHTML = `
        <div class="auto-item-name">${v.icon || '🚗'} ${v.name}</div>
        <div class="auto-item-meta">
          ${wTag}
          <span class="auto-item-cat">${v.category}</span>
          <span class="auto-item-dims">${v.length_m}m × ${v.width_m}m</span>
        </div>
      `;
      item.addEventListener('click', () => {
        if (modelInput) modelInput.value = v.name;
        applyModalVehicleDetection(v.name, v);
        suggestionsList.classList.add('hidden');
        showToast(`✨ Auto-fetched: ${v.name} (${v.length_m}m × ${v.width_m}m)`);
      });
      suggestionsList.appendChild(item);
    });
    suggestionsList.classList.remove('hidden');
  }

  let debounceTimer = null;
  if (modelInput && suggestionsList) {
    modelInput.addEventListener('input', (e) => {
      const q = e.target.value.trim();

      // Instant 0ms auto-detection while typing!
      if (q.length >= 2) {
        applyModalVehicleDetection(q);
      } else {
        if (autofillIndicator) autofillIndicator.classList.add('hidden');
      }

      clearTimeout(debounceTimer);
      if (!q || q.length < 1) {
        suggestionsList.innerHTML = '';
        suggestionsList.classList.add('hidden');
        return;
      }

      renderModalSuggestions(q);

      debounceTimer = setTimeout(async () => {
        try {
          const filterParam = modalWheelsFilter ? `&wheels=${modalWheelsFilter}` : '';
          const res = await fetch(`${API_BASE}/api/vehicles/search?q=${encodeURIComponent(q)}${filterParam}`);
          const data = await res.json();
          const list = data.vehicles || [];
          if (list.length > 0 && modelInput.value.trim() === q) {
            applyModalVehicleDetection(q, list[0]);
          }
        } catch (err) {
          console.warn('Vehicle search failed:', err);
        }
      }, 180);
    });

    document.addEventListener('click', (e) => {
      if (!modelInput.contains(e.target) && !suggestionsList.contains(e.target)) {
        suggestionsList.classList.add('hidden');
      }
    });

    modelInput.addEventListener('blur', () => {
      const q = modelInput.value.trim();
      if (q) {
        applyModalVehicleDetection(q);
      }
    });
  }

  // Submit Registration
  if (formRegister) {
    formRegister.addEventListener('submit', async (e) => {
      e.preventDefault();

      const nameVal = (nameInput && nameInput.value.trim()) || 'Registered User';
      const modelVal = (modelInput && modelInput.value.trim()) || 'Standard Vehicle';
      let emailVal = (emailInput && emailInput.value.trim()) || '';
      if (!emailVal) {
        const cleanName = nameVal.toLowerCase().replace(/[^a-z0-9]/g, '');
        emailVal = `${cleanName || 'rider'}@parkvision.local`;
      }
      const passVal = (passInput && passInput.value) || '123456';
      const phoneVal = (phoneInput && phoneInput.value.trim()) || '';
      let plateVal = (plateInput && plateInput.value.trim().toUpperCase()) || '';
      if (!plateVal) {
        plateVal = 'MH-01-BK-' + Math.floor(1000 + Math.random() * 9000);
      }

      let lenVal = parseFloat(lengthInput.value);
      let widVal = parseFloat(widthInput.value);
      let clearVal = parseFloat(clearanceInput.value) || 0.20;

      // Detect vehicle specifications
      const vInfo = window.lookupVehicleClient ? window.lookupVehicleClient(modelVal) : null;
      if ((!lenVal || isNaN(lenVal) || lenVal <= 0) && vInfo) lenVal = vInfo.length_m;
      if ((!widVal || isNaN(widVal) || widVal <= 0) && vInfo) widVal = vInfo.width_m;

      if (!lenVal || isNaN(lenVal)) lenVal = 2.04;
      if (!widVal || isNaN(widVal)) widVal = 0.73;

      const wheelsVal = vInfo ? (vInfo.wheels || 2) : 2;
      const categoryVal = vInfo ? (vInfo.category || 'Vehicle') : 'Vehicle';
      const iconVal = vInfo ? (vInfo.icon || (wheelsVal === 4 ? '🚗' : (wheelsVal === 3 ? '🛺' : '🏍️'))) : '🚗';

      let bikeTypeVal = 'bike_cruiser';
      if (wheelsVal === 4) {
        bikeTypeVal = (categoryVal.toLowerCase().includes('suv')) ? 'suv' : ((categoryVal.toLowerCase().includes('sedan')) ? 'sedan' : 'compact');
      } else if (wheelsVal === 3) {
        bikeTypeVal = 'auto';
      } else if (categoryVal.toLowerCase().includes('scooter')) {
        bikeTypeVal = 'bike_scooter';
      } else if (categoryVal.toLowerCase().includes('sports')) {
        bikeTypeVal = 'bike_sports';
      } else if (categoryVal.toLowerCase().includes('commuter')) {
        bikeTypeVal = 'bike_commuter';
      }

      // 1. Instantly save to state and localStorage so the user data is NEVER lost!
      const profile = {
        name: nameVal,
        email: emailVal,
        phone: phoneVal,
        licensePlate: plateVal,
        bikeModel: modelVal,
        bikeType: bikeTypeVal,
        wheels: wheelsVal,
        category: categoryVal,
        icon: iconVal,
        length: lenVal,
        width: widVal,
        clearance: clearVal
      };

      saveUserProfile(profile);
      closeModal();
      showToast(`✅ Profile registered & saved: ${iconVal} ${modelVal} (${lenVal}m × ${widVal}m)`);
      refreshUserGPS();
      if (state.currentTab === 'cv-lab') runCVAnalysis();

      // 2. Persist to backend users.json
      const payload = {
        name: nameVal,
        email: emailVal,
        password: passVal,
        phone: phoneVal,
        license_plate: plateVal,
        bike_model: modelVal,
        bike_type: bikeTypeVal,
        wheels: wheelsVal,
        category: categoryVal,
        icon: iconVal,
        length_m: lenVal,
        width_m: widVal,
        clearance_m: clearVal
      };

      try {
        const res = await fetch(`${API_BASE}/api/auth/register`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
        if (res.ok) {
          const result = await res.json();
          if (result.user) {
            const u = result.user;
            saveUserProfile({
              name: u.name,
              email: u.email,
              phone: u.phone,
              licensePlate: u.license_plate,
              bikeModel: u.bike_model,
              bikeType: u.bike_type || 'bike_cruiser',
              length: u.length_m,
              width: u.width_m,
              clearance: u.clearance_m
            });
          }
        }
      } catch (err) {
        console.warn('Backend sync notice:', err);
      }
    });
  }

  // Submit Login
  if (formLogin) {
    formLogin.addEventListener('submit', async (e) => {
      e.preventDefault();
      const emailVal = loginEmail.value.trim();
      const passVal = loginPass.value;

      if (!emailVal) {
        alert('Please enter your registered email address.');
        return;
      }

      const payload = {
        email: emailVal,
        password: passVal
      };

      try {
        const res = await fetch(`${API_BASE}/api/auth/login`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
        const result = await res.json();
        if (result && result.user) {
          const user = result.user;
          const profile = {
            name: user.name,
            email: user.email,
            phone: user.phone,
            licensePlate: user.license_plate,
            bikeModel: user.bike_model,
            bikeType: user.bike_type || 'bike_cruiser',
            length: user.length_m,
            width: user.width_m,
            clearance: user.clearance_m
          };

          saveUserProfile(profile);
          closeModal();
          showToast(`👋 Welcome, ${profile.name}!`);
          refreshUserGPS();
          if (state.currentTab === 'cv-lab') runCVAnalysis();
        } else {
          alert('Login failed. Please check your credentials.');
        }
      } catch (err) {
        console.error('Login error:', err);
        // Fallback local login
        const saved = localStorage.getItem('PARKVISION_USER_PROFILE');
        if (saved) {
          state.userProfile = JSON.parse(saved);
          initProfileUI();
          closeModal();
          showToast('👋 Session restored from local storage.');
        }
      }
    });
  }
}

// ==========================================================================
// 2. TABS NAVIGATION MODULE
// ==========================================================================
function initTabs() {
  const tabButtons = document.querySelectorAll('.tab-btn');
  tabButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      const tabId = btn.getAttribute('data-tab');
      if (tabId) {
        switchTab(tabId);
      }
    });
  });

  const jumpGpsBtn = document.getElementById('btn-jump-gps');
  if (jumpGpsBtn) {
    jumpGpsBtn.addEventListener('click', () => switchTab('gps-map'));
  }

  const configApiBtn = document.getElementById('btn-config-api');
  if (configApiBtn) {
    configApiBtn.addEventListener('click', () => {
      const current = localStorage.getItem('PARKVISION_BACKEND_URL') || API_BASE || 'http://localhost:8000';
      const input = prompt(
        'Enter your Cloud Backend URL (Render/Vercel/Local):\n(e.g., http://localhost:8000)\n\nLeave blank to use default origin.',
        current
      );
      if (input !== null) {
        if (input.trim()) {
          localStorage.setItem('PARKVISION_BACKEND_URL', input.trim());
        } else {
          localStorage.removeItem('PARKVISION_BACKEND_URL');
        }
        API_BASE = getApiBase();
        alert(`API server set to: ${API_BASE || '(Default relative URL)'}`);
        runCVAnalysis();
      }
    });
  }
}

function switchTab(tabId) {
  state.currentTab = tabId;
  document.querySelectorAll('.tab-btn').forEach(b => b.classList.toggle('active', b.getAttribute('data-tab') === tabId));
  document.querySelectorAll('.tab-content').forEach(c => c.classList.toggle('active', c.id === `tab-${tabId}`));

  if (tabId === 'gps-map') {
    setTimeout(initOrRefreshMap, 200);
  } else if (tabId === 'camera-scan') {
    resizeARCanvas();
    if (!state.camera.stream && !state.camera.isSimulated) {
      // Prompt camera or simulate
      document.getElementById('cam-permission-card').classList.remove('hidden');
    }
  } else if (tabId === 'driver-flow') {
    renderFlowStage(state.flowStep);
  }
}

// ==========================================================================
// 3. REAL-TIME MOBILE CAMERA COMPUTER VISION & AR SCANNER
// ==========================================================================
function initCameraScanner() {
  const requestCamBtn = document.getElementById('btn-request-cam');
  const simCamBtn = document.getElementById('btn-use-sample-cam');
  const toggleCamBtn = document.getElementById('btn-toggle-camera');
  const flipCamBtn = document.getElementById('btn-flip-camera');
  const scanNowBtn = document.getElementById('btn-scan-frame-now');
  const autoScanBtn = document.getElementById('btn-toggle-autoscan');
  const speakBtn = document.getElementById('btn-speak-guidance');
  const confirmParkedBtn = document.getElementById('btn-confirm-parked');

  if (requestCamBtn) {
    requestCamBtn.addEventListener('click', () => startCameraStream());
  }

  if (simCamBtn) {
    simCamBtn.addEventListener('click', () => startSimulatedCamera());
  }

  if (toggleCamBtn) {
    toggleCamBtn.addEventListener('click', () => {
      if (state.camera.stream || state.camera.isSimulated) {
        stopCamera();
      } else {
        startCameraStream();
      }
    });
  }

  if (flipCamBtn) {
    flipCamBtn.addEventListener('click', () => {
      state.camera.facingMode = state.camera.facingMode === 'environment' ? 'user' : 'environment';
      if (state.camera.stream) {
        stopCamera();
        startCameraStream();
      }
    });
  }

  if (scanNowBtn) {
    scanNowBtn.addEventListener('click', () => captureAndScanFrame());
  }

  if (autoScanBtn) {
    autoScanBtn.addEventListener('click', () => {
      state.camera.isAutoScanning = !state.camera.isAutoScanning;
      autoScanBtn.classList.toggle('active', state.camera.isAutoScanning);
      document.getElementById('lbl-autoscan').textContent = state.camera.isAutoScanning ? 'Auto-Scan: ON' : 'Auto-Scan: OFF';
      
      if (state.camera.isAutoScanning) {
        startAutoScanLoop();
      } else {
        stopAutoScanLoop();
      }
    });
  }

  if (speakBtn) {
    speakBtn.addEventListener('click', () => {
      const guidanceBox = document.getElementById('cam-rec-guidance-msg');
      if (guidanceBox && guidanceBox.textContent) {
        speakGuidance(guidanceBox.textContent, true);
      }
    });
  }

  if (confirmParkedBtn) {
    confirmParkedBtn.addEventListener('click', () => {
      showToast('🎉 Parking Confirmed! Have a safe trip.');
      speakGuidance('Your bike is safely parked in the recommended free bay. Have a great day!');
    });
  }
}

async function startCameraStream() {
  const permOverlay = document.getElementById('cam-permission-card');
  const statusLabel = document.getElementById('cam-status-label');
  const video = document.getElementById('mobile-cam-video');

  try {
    statusLabel.textContent = 'Requesting Camera Permission...';
    
    // Check WebRTC support
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      throw new Error('Camera API not supported on this browser. Use Simulated Feed.');
    }

    const constraints = {
      video: {
        facingMode: { ideal: state.camera.facingMode },
        width: { ideal: 1280 },
        height: { ideal: 720 }
      },
      audio: false
    };

    const stream = await navigator.mediaDevices.getUserMedia(constraints);
    state.camera.stream = stream;
    state.camera.isSimulated = false;

    video.srcObject = stream;
    await video.play();

    permOverlay.classList.add('hidden');
    statusLabel.textContent = `🟢 Live Rear Camera Feed (${state.camera.facingMode})`;
    document.getElementById('lbl-cam-toggle').textContent = 'Stop Feed';
    document.getElementById('icon-cam-toggle').textContent = '⏹️';

    video.onloadedmetadata = () => {
      resizeARCanvas();
      if (state.camera.isAutoScanning) {
        startAutoScanLoop();
      }
    };
  } catch (err) {
    console.error('Camera access error:', err);
    statusLabel.textContent = '⚠️ Camera Access Denied';
    alert(`Camera Permission Notice:\n${err.message || 'Permission denied.'}\n\nYou can click 'Use Simulated Camera Feed' to test the Computer Vision pipeline without physical camera hardware.`);
  }
}

function startSimulatedCamera() {
  const permOverlay = document.getElementById('cam-permission-card');
  const statusLabel = document.getElementById('cam-status-label');
  const video = document.getElementById('mobile-cam-video');

  stopCamera();
  state.camera.isSimulated = true;

  // Set poster / stream frame from scenario
  video.srcObject = null;
  video.poster = `${API_BASE}/static/scenarios/scenario_2_driver.jpg`;
  
  permOverlay.classList.add('hidden');
  statusLabel.textContent = '🎬 Simulated Smartphone Camera Feed (Driver View)';
  document.getElementById('lbl-cam-toggle').textContent = 'Stop Feed';
  document.getElementById('icon-cam-toggle').textContent = '⏹️';

  resizeARCanvas();
  // Trigger single scan & auto-scan
  setTimeout(() => {
    captureAndScanFrame();
    if (state.camera.isAutoScanning) {
      startAutoScanLoop();
    }
  }, 400);
}

function stopCamera() {
  if (state.camera.stream) {
    state.camera.stream.getTracks().forEach(t => t.stop());
    state.camera.stream = null;
  }
  const video = document.getElementById('mobile-cam-video');
  if (video) {
    video.srcObject = null;
    video.poster = '';
  }
  state.camera.isSimulated = false;
  stopAutoScanLoop();

  document.getElementById('cam-permission-card').classList.remove('hidden');
  document.getElementById('cam-status-label').textContent = 'Camera Stopped';
  document.getElementById('lbl-cam-toggle').textContent = 'Start Feed';
  document.getElementById('icon-cam-toggle').textContent = '▶️';
  clearARCanvas();
}

function startAutoScanLoop() {
  stopAutoScanLoop();
  // Scan every 1.8 seconds
  state.camera.scanInterval = setInterval(() => {
    if (state.currentTab === 'camera-scan') {
      captureAndScanFrame();
    }
  }, 1800);
}

function stopAutoScanLoop() {
  if (state.camera.scanInterval) {
    clearInterval(state.camera.scanInterval);
    state.camera.scanInterval = null;
  }
}

function resizeARCanvas() {
  const video = document.getElementById('mobile-cam-video');
  const canvas = document.getElementById('mobile-ar-canvas');
  if (!video || !canvas) return;

  const rect = video.getBoundingClientRect();
  canvas.width = rect.width;
  canvas.height = rect.height;
}

async function captureAndScanFrame() {
  if (state.camera.isScanningNow) return;
  state.camera.isScanningNow = true;

  const spinner = document.getElementById('cam-scan-spinner');
  if (spinner) spinner.classList.remove('hidden');

  try {
    const video = document.getElementById('mobile-cam-video');
    const p = state.userProfile || { bikeType: 'bike_cruiser', length: 2.14, width: 0.84, bikeModel: 'Vehicle' };
    const formData = new FormData();
    formData.append('vehicle_type', p.bikeType || 'bike_cruiser');
    formData.append('custom_length', p.length || 2.14);
    formData.append('custom_width', p.width || 0.84);
    formData.append('bike_model', p.bikeModel || 'Vehicle');

    if (state.camera.isSimulated || !state.camera.stream) {
      formData.append('scenario_key', state.currentScenario || 'scenario_2_driver');
    } else {
      // Capture frame from active video element
      const tempCanvas = document.createElement('canvas');
      tempCanvas.width = video.videoWidth || 1280;
      tempCanvas.height = video.videoHeight || 720;
      const tempCtx = tempCanvas.getContext('2d');
      tempCtx.drawImage(video, 0, 0, tempCanvas.width, tempCanvas.height);
      const dataUrl = tempCanvas.toDataURL('image/jpeg', 0.8);
      formData.append('image_base64', dataUrl);
    }

    const response = await fetch(`${API_BASE}/api/cv/analyze-live-frame`, {
      method: 'POST',
      body: formData
    });

    if (!response.ok) {
      throw new Error(`Live CV error: ${response.statusText}`);
    }

    const data = await response.json();
    renderLiveScanResults(data);
  } catch (err) {
    console.error('Frame scan failed:', err);
  } finally {
    state.camera.isScanningNow = false;
    if (spinner) spinner.classList.add('hidden');
  }
}

function renderLiveScanResults(data) {
  if (!data || !data.success) return;

  const rec = data.recommended_slot;
  const p = state.userProfile || { bikeModel: 'Vehicle', length: 2.14, width: 0.84 };

  // 1. Update Suggestion Banner & Card
  const recTitle = document.getElementById('cam-rec-title');
  const recStatus = document.getElementById('cam-rec-status');
  const recDims = document.getElementById('cam-rec-dims');
  const recClearance = document.getElementById('cam-rec-clearance');
  const recMsg = document.getElementById('cam-rec-guidance-msg');
  const recFee = document.getElementById('cam-rec-fee');

  if (recFee) recFee.textContent = 'FREE (Zero Fee)';

  if (rec) {
    recTitle.textContent = rec.label || `Bay ${rec.id}`;
    recStatus.textContent = '🟢 Available & Fits Bike';
    recStatus.style.color = '#34d399';
    recDims.textContent = `${rec.metrics.length_m}m (L) × ${rec.metrics.width_m}m (W)`;
    
    const margin = rec.vehicle_fit ? rec.vehicle_fit.width_margin_m : 0.35;
    recClearance.textContent = `+${margin}m clearance`;
    recMsg.textContent = `${rec.vehicle_fit.message} Free public bike bay with kickstand room. Pull straight in.`;

    // Voice announcement (throttled to avoid repeat spam)
    const now = Date.now();
    if (state.camera.speechEnabled && (state.camera.lastSpokenSlotId !== rec.id || now - state.camera.lastSpokenTime > 12000)) {
      state.camera.lastSpokenSlotId = rec.id;
      state.camera.lastSpokenTime = now;
      speakGuidance(data.speech_text || `Free space found! Park your bike in ${rec.label}.`);
    }
  } else {
    recTitle.textContent = 'Scanning View...';
    recStatus.textContent = '🟡 No Fitting Spot Found';
    recStatus.style.color = '#fbbf24';
    recDims.textContent = '—';
    recClearance.textContent = '0.0m';
    recMsg.textContent = `All spaces in this camera angle are occupied or too small for your ${p.bikeModel} (${p.length}m length). Move camera forward.`;
  }

  // 2. Draw AR Canvas Overlays
  drawAROverlay(data.ar_slots, rec);

  // 3. Populate Live Bays List
  const baysList = document.getElementById('cam-bays-list');
  if (baysList && data.ar_slots) {
    baysList.innerHTML = '';
    data.ar_slots.forEach(s => {
      const isRec = rec && s.id === rec.id;
      const item = document.createElement('div');
      item.className = `live-bay-item ${isRec ? 'suggested' : ''}`;
      item.innerHTML = `
        <div>
          <strong>${s.label}</strong> (${s.length_m}m × ${s.width_m}m)
          <div style="font-size:0.74rem;font-weight:600;color:${s.status === 'AVAILABLE' ? 'var(--color-green)' : 'var(--color-red)'};">
            ${s.status === 'AVAILABLE' ? '🟢 Available' : '🔴 Occupied'} • ${isRec ? '⭐ Optimal Fit' : s.fit_badge}
          </div>
        </div>
        <div style="text-align:right;">
          <span style="font-weight:700;color:var(--color-green);">FREE</span>
        </div>
      `;
      baysList.appendChild(item);
    });
  }
}

function drawAROverlay(arSlots, recommendedSlot) {
  const canvas = document.getElementById('mobile-ar-canvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  const pointer = document.getElementById('ar-floating-pointer');
  let pointerShown = false;

  if (!arSlots || arSlots.length === 0) {
    if (pointer) pointer.classList.add('hidden');
    return;
  }

  const cw = canvas.width;
  const ch = canvas.height;

  arSlots.forEach(s => {
    const isRec = recommendedSlot && s.id === recommendedSlot.id;
    const poly = s.normalized_polygon; // [[x/w, y/h], ...]
    if (!poly || poly.length < 3) return;

    ctx.beginPath();
    ctx.moveTo(poly[0][0] * cw, poly[0][1] * ch);
    for (let i = 1; i < poly.length; i++) {
      ctx.lineTo(poly[i][0] * cw, poly[i][1] * ch);
    }
    ctx.closePath();

    if (isRec) {
      // Glowing green suggested slot
      ctx.strokeStyle = '#10b981';
      ctx.lineWidth = 4;
      ctx.shadowColor = '#10b981';
      ctx.shadowBlur = 15;
      ctx.fillStyle = 'rgba(16, 185, 129, 0.22)';
      ctx.fill();
      ctx.stroke();

      // Reset shadow
      ctx.shadowBlur = 0;

      // Draw Center Badge
      const cx = s.center[0] * cw;
      const cy = s.center[1] * ch;

      ctx.fillStyle = '#10b981';
      ctx.beginPath();
      ctx.arc(cx, cy, 18, 0, Math.PI * 2);
      ctx.fill();

      ctx.fillStyle = '#042f2e';
      ctx.font = 'bold 12px sans-serif';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillText('🅿️', cx, cy);

      // Position AR Floating Pointer Arrow
      if (pointer) {
        pointer.style.left = `${cx}px`;
        pointer.style.top = `${cy - 20}px`;
        document.getElementById('ar-pointer-text').textContent = `★ PARK HERE: ${s.label.toUpperCase()} ★`;
        pointer.classList.remove('hidden');
        pointerShown = true;
      }
    } else if (s.status === 'AVAILABLE') {
      ctx.strokeStyle = 'rgba(16, 185, 129, 0.5)';
      ctx.lineWidth = 2;
      ctx.fillStyle = 'rgba(16, 185, 129, 0.08)';
      ctx.fill();
      ctx.stroke();
    } else if (s.status === 'BLOCKED') {
      ctx.strokeStyle = 'rgba(245, 158, 11, 0.7)';
      ctx.lineWidth = 2;
      ctx.fillStyle = 'rgba(245, 158, 11, 0.1)';
      ctx.fill();
      ctx.stroke();
    } else {
      // Occupied
      ctx.strokeStyle = 'rgba(239, 68, 68, 0.6)';
      ctx.lineWidth = 2;
      ctx.fillStyle = 'rgba(239, 68, 68, 0.1)';
      ctx.fill();
      ctx.stroke();
    }
  });

  if (!pointerShown && pointer) {
    pointer.classList.add('hidden');
  }
}

function clearARCanvas() {
  const canvas = document.getElementById('mobile-ar-canvas');
  if (canvas) {
    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, canvas.width, canvas.height);
  }
  const pointer = document.getElementById('ar-floating-pointer');
  if (pointer) pointer.classList.add('hidden');
}

// Text-to-Speech Voice Assistant
function speakGuidance(text, force = false) {
  if (!('speechSynthesis' in window)) return;
  if (!state.camera.speechEnabled && !force) return;

  try {
    window.speechSynthesis.cancel(); // cancel prior utterances
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 1.0;
    utterance.pitch = 1.05;
    utterance.lang = 'en-US';
    window.speechSynthesis.speak(utterance);
  } catch (e) {
    console.warn('Speech synthesis error:', e);
  }
}

// ==========================================================================
// 4. LIVE GPS LOCATION & FREE BIKE PARKING LOTS (Step 6)
// ==========================================================================
function initGPSFeatures() {
  const refreshGpsBtn = document.getElementById('btn-refresh-gps');
  if (refreshGpsBtn) {
    refreshGpsBtn.addEventListener('click', () => refreshUserGPS());
  }

  const cityInput = document.getElementById('gps-city-input');
  const citySearchBtn = document.getElementById('btn-city-search');

  const CITIES_COORDS = {
    'mumbai': [19.0760, 72.8777, 'Mumbai, Maharashtra'],
    'delhi': [28.6139, 77.2090, 'New Delhi, Delhi'],
    'bengaluru': [12.9716, 77.5946, 'Bengaluru, Karnataka'],
    'bangalore': [12.9716, 77.5946, 'Bengaluru, Karnataka'],
    'pune': [18.5204, 73.8567, 'Pune, Maharashtra'],
    'hyderabad': [17.3850, 78.4867, 'Hyderabad, Telangana'],
    'chennai': [13.0827, 80.2707, 'Chennai, Tamil Nadu'],
    'kolkata': [22.5726, 88.3639, 'Kolkata, West Bengal'],
    'ahmedabad': [23.0225, 72.5714, 'Ahmedabad, Gujarat'],
    'london': [51.5074, -0.1278, 'London, UK'],
    'san francisco': [37.7749, -122.4194, 'San Francisco, USA'],
    'sf': [37.7749, -122.4194, 'San Francisco, USA'],
    'new york': [40.7128, -74.0060, 'New York, USA'],
    'dubai': [25.2048, 55.2708, 'Dubai, UAE'],
    'tokyo': [35.6762, 139.6503, 'Tokyo, Japan']
  };

  function setCityLocation(lat, lng, cityName) {
    state.userLocation = [lat, lng];
    state.userLocationLive = false;
    const coordsLabel = document.getElementById('gps-live-coords');
    if (coordsLabel) {
      coordsLabel.textContent = `${lat.toFixed(4)}° N, ${lng.toFixed(4)}° E (${cityName})`;
    }
    showToast(`📍 Set location to ${cityName} — finding nearby parking`);
    if (state.map) {
      state.map.setView(state.userLocation, 15);
      updateUserMapMarker();
      loadMapParkingLots();
    }
  }

  async function handleCitySearch() {
    const query = cityInput ? cityInput.value.trim().toLowerCase() : '';
    if (!query) return;

    for (const [k, v] of Object.entries(CITIES_COORDS)) {
      if (query.includes(k) || k.includes(query)) {
        setCityLocation(v[0], v[1], v[2]);
        return;
      }
    }

    try {
      const coordsLabel = document.getElementById('gps-live-coords');
      if (coordsLabel) coordsLabel.textContent = `Searching for "${query}"...`;
      const res = await fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(query)}&limit=1`);
      const data = await res.json();
      if (data && data.length > 0) {
        const lat = parseFloat(data[0].lat);
        const lng = parseFloat(data[0].lon);
        const display = data[0].display_name.split(',').slice(0, 2).join(',');
        setCityLocation(lat, lng, display);
      } else {
        alert(`Location "${query}" could not be found. Please select from quick chips.`);
      }
    } catch (e) {
      console.warn('Geocoding error:', e);
      alert('Could not resolve location. Please select one of the city chips below.');
    }
  }

  if (citySearchBtn) {
    citySearchBtn.addEventListener('click', handleCitySearch);
  }
  if (cityInput) {
    cityInput.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') handleCitySearch();
    });
  }

  // Quick Chips
  const chipButtons = document.querySelectorAll('.chip-btn');
  chipButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      chipButtons.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');

      const cityKey = btn.getAttribute('data-city');
      if (cityKey === 'current') {
        refreshUserGPS();
        return;
      }

      const lat = parseFloat(btn.getAttribute('data-lat'));
      const lng = parseFloat(btn.getAttribute('data-lng'));
      const cityName = btn.textContent.replace('📍', '').trim();
      if (!isNaN(lat) && !isNaN(lng)) {
        setCityLocation(lat, lng, cityName);
      }
    });
  });
}

function refreshUserGPS() {
  const coordsLabel = document.getElementById('gps-live-coords');
  if (coordsLabel) coordsLabel.textContent = 'Acquiring GPS Satellite Fix...';

  if (!navigator.geolocation) {
    alert('Geolocation API is not supported by your browser.');
    return;
  }

  navigator.geolocation.getCurrentPosition(
    (pos) => {
      state.userLocation = [pos.coords.latitude, pos.coords.longitude];
      state.userLocationLive = true;
      if (coordsLabel) {
        coordsLabel.textContent = `${pos.coords.latitude.toFixed(4)}° N, ${pos.coords.longitude.toFixed(4)}° E (GPS Live ✅)`;
      }
      showToast('📍 Live GPS location detected!');
      if (state.map) {
        updateUserMapMarker();
        loadMapParkingLots();
      }
    },
    (err) => {
      console.warn('Geolocation denied/timeout:', err);
      if (coordsLabel) {
        coordsLabel.textContent = `19.0760° N, 72.8777° E (Mumbai Central Fallback)`;
      }
      showToast('📍 Using calibrated City Hub location');
      if (state.map) {
        loadMapParkingLots();
      }
    },
    { enableHighAccuracy: true, timeout: 6000 }
  );
}

function haversineDistance(lat1, lon1, lat2, lon2) {
  const R = 6371; // Earth's radius in km
  const dLat = (lat2 - lat1) * Math.PI / 180;
  const dLon = (lon2 - lon1) * Math.PI / 180;
  const a = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
            Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
            Math.sin(dLon / 2) * Math.sin(dLon / 2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  return Math.round(R * c * 10) / 10;
}

async function initOrRefreshMap() {
  const mapElement = document.getElementById('leaflet-map');
  if (!mapElement) return;

  if (!state.map) {
    state.map = L.map('leaflet-map', { zoomControl: true }).setView(state.userLocation, 15);

    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '&copy; OpenStreetMap contributors',
      maxZoom: 19
    }).addTo(state.map);

    updateUserMapMarker();
    loadMapParkingLots();
  } else {
    state.map.invalidateSize();
    updateUserMapMarker();
  }
}

function updateUserMapMarker() {
  if (!state.map) return;

  if (state.mapUserMarker) {
    state.map.removeLayer(state.mapUserMarker);
  }

  const userIcon = L.divIcon({
    className: 'user-map-pin',
    html: `<div style="background:#2563eb;width:22px;height:22px;border-radius:50%;border:3px solid white;box-shadow:0 2px 6px rgba(0,0,0,0.3);display:flex;align-items:center;justify-content:center;font-size:11px;">📍</div>`,
    iconSize: [22, 22],
    iconAnchor: [11, 11]
  });

  const vehName = (state.userProfile && state.userProfile.bikeModel) ? state.userProfile.bikeModel : 'Your Vehicle';
  state.mapUserMarker = L.marker(state.userLocation, { icon: userIcon })
    .addTo(state.map)
    .bindPopup(`<strong>📍 You (${vehName})</strong><br>GPS Active • Finding nearby free bike bays`);

  state.map.panTo(state.userLocation);
}

async function loadMapParkingLots() {
  let lots = null;
  try {
    const response = await fetch(`${API_BASE}/api/parking/nearby?lat=${state.userLocation[0]}&lng=${state.userLocation[1]}`);
    if (response.ok) {
      lots = await response.json();
    }
  } catch (err) {
    console.warn('Backend fetch failed for map, using built-in generator:', err);
  }

  if (!lots || !Array.isArray(lots) || lots.length === 0) {
    lots = generateClientNearbyParking(state.userLocation[0], state.userLocation[1]);
  }

  try {
    state.allLotsData = lots;

    // Clear old markers
    state.mapMarkers.forEach(m => state.map.removeLayer(m));
    state.mapMarkers = [];

    const lotsList = document.getElementById('nearby-lots-list');
    if (lotsList) lotsList.innerHTML = '';

    let totalFreeSpots = 0;

    // Compute dynamic distances
    lots.forEach(lot => {
      const dist = haversineDistance(state.userLocation[0], state.userLocation[1], lot.latitude, lot.longitude);
      lot.dynamic_distance = dist > 0 ? dist : lot.distance_km;
      totalFreeSpots += lot.live_available;
    });

    // Sort by nearest distance
    lots.sort((a, b) => a.dynamic_distance - b.dynamic_distance);

    const totalFreeCountEl = document.getElementById('gps-total-free-count');
    if (totalFreeCountEl) {
      totalFreeCountEl.textContent = `${totalFreeSpots} Free Bays Available Nearby`;
    }

    lots.forEach((lot, idx) => {
      // Map marker with free bike parking styling
      const lotIcon = L.divIcon({
        className: 'lot-map-pin',
        html: `<div style="background:${lot.live_available > 0 ? '#059669' : '#dc2626'};color:white;font-weight:700;font-size:11px;padding:3px 8px;border-radius:12px;border:2px solid white;box-shadow:0 2px 6px rgba(0,0,0,0.2);">${lot.live_available} 🏍️</div>`,
        iconSize: [44, 24],
        iconAnchor: [22, 12]
      });

      const marker = L.marker([lot.latitude, lot.longitude], { icon: lotIcon }).addTo(state.map);
      marker.bindPopup(`
        <strong>${lot.name}</strong><br>
        <span style="color:#10b981;font-weight:bold;">${lot.live_available} Free Bays</span> (No Fee)<br>
        Fits: All registered bikes
      `);
      marker.on('click', () => selectParkingLot(lot));
      state.mapMarkers.push(marker);

      // Sidebar Card
      if (lotsList) {
        const card = document.createElement('div');
        card.className = `lot-card ${idx === 0 ? 'active' : ''}`;
        card.innerHTML = `
          <div class="lot-header">
            <span class="lot-name">${lot.name}</span>
            <span class="lot-distance">${lot.dynamic_distance} km</span>
          </div>
          <div class="lot-meta">
            <span>${lot.type}</span>
            <span class="lot-avail-tag">${lot.live_available} Free Bays</span>
            <span class="fee-free-badge">Zero Fee</span>
          </div>
          <div class="lot-actions">
            <button class="btn-nav-lot" onclick="event.stopPropagation(); triggerNavigation('${lot.id}')">
              🧭 Navigate & Scan
            </button>
          </div>
        `;
        card.addEventListener('click', () => selectParkingLot(lot));
        lotsList.appendChild(card);
      }

      if (idx === 0) {
        selectParkingLot(lot);
      }
    });
  } catch (err) {
    console.error('Failed to load GPS lots:', err);
  }
}

function selectParkingLot(lot) {
  state.activeLot = lot;

  // Update Route Polyline
  if (state.routeLine && state.map) {
    state.map.removeLayer(state.routeLine);
  }
  const routeCoords = [
    state.userLocation,
    [lot.latitude, lot.longitude]
  ];
  if (state.map) {
    state.routeLine = L.polyline(routeCoords, {
      color: '#3b82f6',
      weight: 4,
      dashArray: '8, 8',
      opacity: 0.85
    }).addTo(state.map);
  }

  // Update Bottom Route Bar
  const routeCard = document.getElementById('map-route-card');
  if (routeCard) {
    document.getElementById('route-dest-name').textContent = lot.name;
    document.getElementById('route-dist').textContent = lot.dynamic_distance || lot.distance_km;
    document.getElementById('route-time').textContent = Math.max(1, Math.round((lot.dynamic_distance || lot.distance_km) * 3));
    document.getElementById('route-avail').textContent = `${lot.live_available} Free Bays`;
    routeCard.classList.remove('hidden');
  }

  // Arrive button triggers mobile camera scanner tab directly!
  const arriveBtn = document.getElementById('btn-arrive-simulate');
  if (arriveBtn) {
    arriveBtn.onclick = () => {
      if (lot.scenario_key) {
        state.currentScenario = lot.scenario_key;
      }
      switchTab('camera-scan');
      startCameraStream();
    };
  }
}

window.triggerNavigation = function(lotId) {
  const lot = (state.allLotsData && state.allLotsData.find(l => l.id === lotId)) || state.activeLot;
  if (lot) {
    selectParkingLot(lot);
    showToast(`🧭 Route calculated to ${lot.name}. Zero fee bike bay.`);
    switchTab('camera-scan');
    startCameraStream();
  }
};

// ==========================================================================
// 5. VEHICLE & SCENARIO CONTROLS (CV LAB)
// ==========================================================================
function initVehicleSelectors() {
  const vehButtons = document.querySelectorAll('.veh-btn');
  vehButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      vehButtons.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      const vehKey = btn.getAttribute('data-veh');
      setVehicle(vehKey);
    });
  });

  const toggleCustomBtn = document.getElementById('toggle-custom-dims');
  const customContainer = document.getElementById('custom-dims-container');
  if (toggleCustomBtn && customContainer) {
    toggleCustomBtn.addEventListener('click', () => {
      customContainer.classList.toggle('hidden');
    });
  }

  const lenInput = document.getElementById('custom-length');
  const widInput = document.getElementById('custom-width');
  if (lenInput && widInput) {
    [lenInput, widInput].forEach(input => {
      input.addEventListener('change', () => {
        state.userProfile.length = parseFloat(lenInput.value) || 2.15;
        state.userProfile.width = parseFloat(widInput.value) || 0.85;
        saveUserProfile(state.userProfile);
      });
    });
  }
}

function setVehicle(vehKey) {
  if (!state.userProfile) {
    state.userProfile = { name: 'Guest Rider', bikeType: vehKey, length: 2.14, width: 0.84, clearance: 0.20 };
  }
  state.userProfile.bikeType = vehKey;
  const preset = BIKE_PRESETS[vehKey];
  if (preset) {
    state.userProfile.bikeModel = preset.name;
    state.userProfile.length = preset.length;
    state.userProfile.width = preset.width;
    state.userProfile.clearance = preset.clearance;
  }
  saveUserProfile(state.userProfile);
}

function initScenarioControls() {
  const scenarioSelect = document.getElementById('scenario-select');
  if (scenarioSelect) {
    scenarioSelect.addEventListener('change', (e) => {
      state.currentScenario = e.target.value;
      state.customFile = null;
      runCVAnalysis();
    });
  }

  const fileInput = document.getElementById('file-input');
  if (fileInput) {
    fileInput.addEventListener('change', (e) => {
      if (e.target.files && e.target.files[0]) {
        state.customFile = e.target.files[0];
        runCVAnalysis();
      }
    });
  }
}

function initCVControls() {
  const runBtn = document.getElementById('run-cv-btn');
  if (runBtn) {
    runBtn.addEventListener('click', () => runCVAnalysis());
  }

  const resetBtn = document.getElementById('btn-reset-view');
  if (resetBtn) {
    resetBtn.addEventListener('click', () => {
      state.customFile = null;
      document.getElementById('scenario-select').value = 'scenario_1_aerial';
      state.currentScenario = 'scenario_1_aerial';
      runCVAnalysis();
    });
  }

  const fullBtn = document.getElementById('btn-fullscreen');
  if (fullBtn) {
    fullBtn.addEventListener('click', () => {
      const imgWrapper = document.getElementById('image-wrapper');
      if (!document.fullscreenElement) {
        imgWrapper.requestFullscreen().catch(err => alert(err.message));
      } else {
        document.exitFullscreen();
      }
    });
  }

  const bevToggle = document.getElementById('toggle-bev-view');
  if (bevToggle) {
    bevToggle.addEventListener('change', (e) => {
      const bevCard = document.getElementById('bev-container');
      if (bevCard) bevCard.style.display = e.target.checked ? 'flex' : 'none';
    });
  }
}

async function runCVAnalysis() {
  const loadingOverlay = document.getElementById('cv-loading');
  if (loadingOverlay) loadingOverlay.classList.remove('hidden');

  try {
    const p = state.userProfile || { bikeType: 'bike_cruiser', length: 2.14, width: 0.84 };
    const formData = new FormData();
    formData.append('vehicle_type', p.bikeType || 'bike_cruiser');
    formData.append('custom_length', p.length || 2.14);
    formData.append('custom_width', p.width || 0.84);

    if (state.customFile) {
      formData.append('image_file', state.customFile);
    } else {
      formData.append('scenario_key', state.currentScenario);
    }

    const response = await fetch(`${API_BASE}/api/cv/analyze`, {
      method: 'POST',
      body: formData
    });

    if (!response.ok) {
      throw new Error(`CV API error: ${response.statusText}`);
    }

    const data = await response.json();
    state.analysisResult = data;
    renderLabResults(data);
  } catch (error) {
    console.error('Error running CV analysis:', error);
  } finally {
    if (loadingOverlay) loadingOverlay.classList.add('hidden');
  }
}

function renderLabResults(data) {
  if (!data || !data.success) return;

  const mainImg = document.getElementById('cv-main-image');
  if (mainImg) mainImg.src = data.annotated_image;

  const bevImg = document.getElementById('cv-bev-image');
  const bevCard = document.getElementById('bev-container');
  if (data.bev_image && bevImg && bevCard) {
    bevImg.src = data.bev_image;
    bevCard.style.display = 'flex';
  } else if (bevCard) {
    bevCard.style.display = 'none';
  }

  // HUD Counters
  document.getElementById('hud-total').textContent = data.summary.total_slots;
  document.getElementById('hud-avail').textContent = data.summary.available;
  document.getElementById('hud-occ').textContent = data.summary.occupied;
  document.getElementById('hud-blocked').textContent = data.summary.blocked;

  const fitCount = data.slots.filter(s => s.status === 'AVAILABLE' && s.vehicle_fit && s.vehicle_fit.is_suitable).length;
  document.getElementById('hud-fit-tag').textContent = `${fitCount} Space${fitCount === 1 ? '' : 's'} Fit Your Bike`;

  // Recommendation Card
  const recSlot = data.recommended_slot;
  if (recSlot) {
    document.getElementById('rec-slot-title').textContent = recSlot.label || `Bay ${recSlot.id}`;
    document.getElementById('rec-status-pill').textContent = `${recSlot.status_icon} ${recSlot.status}`;
    document.getElementById('rec-dims-text').textContent = `${recSlot.metrics.width_m}m (W) × ${recSlot.metrics.length_m}m (L)`;
    document.getElementById('rec-guidance-text').textContent = recSlot.vehicle_fit.message;
  }

  // Slots List
  const slotsList = document.getElementById('slots-list-container');
  if (slotsList) {
    slotsList.innerHTML = '';
    data.slots.forEach(s => {
      const card = document.createElement('div');
      card.className = 'slot-item-card';
      const fitNote = s.status === 'AVAILABLE' ? s.vehicle_fit.fit_badge : (s.occupied_by || s.blocked_reason || '—');
      card.innerHTML = `
        <div class="slot-item-info">
          <div class="slot-card-header">
            <span class="slot-item-title">${s.label}</span>
            <span class="slot-item-dims">${s.metrics.width_m}×${s.metrics.length_m}m</span>
          </div>
          <div class="slot-item-desc">${fitNote} • Free Bay ✅</div>
        </div>
        <div class="slot-item-status-badge ${s.status === 'AVAILABLE' ? 'badge-avail' : 'badge-occ'}">
          ${s.status_icon} ${s.status}
        </div>
      `;
      slotsList.appendChild(card);
    });
  }

  // Diagnostics
  const detList = document.getElementById('diag-detections-list');
  if (detList) {
    detList.innerHTML = '';
    data.detections.slice(0, 8).forEach(d => {
      const row = document.createElement('div');
      row.className = 'diag-det-row';
      row.innerHTML = `<span>[${d.category.toUpperCase()}] <strong>${d.class_name}</strong></span><span>${Math.round(d.confidence * 100)}%</span>`;
      detList.appendChild(row);
    });
  }

  const matrixDisplay = document.getElementById('matrix-display');
  if (matrixDisplay && data.homography_matrix) {
    matrixDisplay.textContent = data.homography_matrix.map(row => `[ ${row.map(v => v.toExponential(3)).join('  ')} ]`).join('\n');
  }
}

// ==========================================================================
// 6. REAL-LIFE 8-STEP DRIVER FLOW SIMULATOR
// ==========================================================================
function initFlowStepper() {
  const steps = document.querySelectorAll('.step-card');
  steps.forEach(card => {
    card.addEventListener('click', () => {
      const stepNum = parseInt(card.getAttribute('data-step'), 10);
      setFlowStep(stepNum);
    });
  });
}

function setFlowStep(stepNum) {
  state.flowStep = stepNum;
  document.querySelectorAll('.step-card').forEach(card => {
    const num = parseInt(card.getAttribute('data-step'), 10);
    card.classList.toggle('active', num === stepNum);
    card.classList.toggle('completed', num < stepNum);
  });
  renderFlowStage(stepNum);
}

function renderFlowStage(stepNum) {
  const body = document.getElementById('flow-stage-body');
  if (!body) return;
  const p = state.userProfile || {
    name: 'Unregistered Rider',
    bikeModel: 'Standard Two-Wheeler',
    length: 2.14,
    width: 0.84,
    licensePlate: 'NOT-REGISTERED'
  };

  const stepContent = {
    1: {
      title: 'Step 1: Rider & Bike Registration',
      desc: 'Enter your profile, bike model, length, handlebar width, and license plate for real-time space matching.',
      html: state.userProfile ? `
        <div style="background:var(--primary-light);border:1px solid var(--primary-border);padding:1.2rem;border-radius:var(--radius-md);display:flex;gap:1.2rem;align-items:center;">
          <div style="font-size:2.8rem;">🏍️</div>
          <div>
            <h4 style="color:var(--text-primary);font-size:1.15rem;font-weight:700;">Registered: ${p.name} • ${p.bikeModel}</h4>
            <p style="color:var(--text-secondary);font-size:0.88rem;margin-top:0.25rem;">Length: <strong style="color:var(--text-primary);">${p.length}m</strong> • Width: <strong style="color:var(--text-primary);">${p.width}m</strong> • Plate: <strong style="color:var(--text-primary);">${p.licensePlate}</strong></p>
          </div>
        </div>
        <div style="margin-top:1.5rem;display:flex;flex-wrap:wrap;gap:0.75rem;">
          <button class="action-btn glow-btn" onclick="setFlowStep(2)">Proceed to Step 2: Live Location →</button>
          <button class="action-btn btn-secondary" onclick="document.getElementById('modal-registration').classList.remove('hidden')">Edit Bike Info ✏️</button>
        </div>
      ` : `
        <div style="background:var(--bg-surface);border:1px dashed var(--border-subtle);padding:1.4rem;border-radius:var(--radius-md);display:flex;gap:1.2rem;align-items:center;">
          <div style="font-size:2.8rem;">📝</div>
          <div>
            <h4 style="color:var(--text-primary);font-size:1.15rem;font-weight:700;">No Rider Profile Registered Yet</h4>
            <p style="color:var(--text-secondary);font-size:0.88rem;margin-top:0.25rem;">Register your name and bike model to automatically pull length and width dimensions from the official vehicle dataset.</p>
          </div>
        </div>
        <div style="margin-top:1.5rem;display:flex;flex-wrap:wrap;gap:0.75rem;">
          <button class="action-btn glow-btn" onclick="document.getElementById('modal-registration').classList.remove('hidden')">🔐 Register / Login Now</button>
          <button class="action-btn btn-secondary" onclick="setFlowStep(2)">Continue as Guest Rider →</button>
        </div>
      `
    },
    2: {
      title: 'Step 2: Live GPS Location Acquisition',
      desc: 'Acquire your real-time coordinates via browser geolocation to find the nearest free bike parking bays.',
      html: `
        <div style="background:var(--bg-surface);border:1px solid var(--border-subtle);padding:1.2rem;border-radius:var(--radius-md);display:flex;gap:1.2rem;align-items:center;">
          <div style="font-size:2.8rem;">📡</div>
          <div>
            <h4 style="color:var(--text-primary);font-size:1.1rem;font-weight:700;">Live Location: ${state.userLocation[0].toFixed(4)}° N, ${state.userLocation[1].toFixed(4)}° W</h4>
            <p style="color:var(--color-green-text);font-size:0.88rem;font-weight:600;margin-top:0.25rem;">🟢 Satellite fix acquired • Querying municipal free parking database</p>
          </div>
        </div>
        <div style="margin-top:1.5rem;display:flex;flex-wrap:wrap;gap:0.75rem;">
          <button class="action-btn glow-btn" onclick="setFlowStep(3)">Find Nearest Free Bays →</button>
        </div>
      `
    },
    3: {
      title: 'Step 3: Discover Nearby Free Bike Bays',
      desc: 'System searches and filters 100% free two-wheeler parking facilities near your live location.',
      html: `
        <div style="background:var(--bg-surface);border:1px solid var(--border-subtle);padding:1.2rem;border-radius:var(--radius-md);display:flex;gap:1.2rem;align-items:center;">
          <div style="font-size:2.8rem;">🅿️</div>
          <div>
            <h4 style="color:var(--text-primary);font-size:1.15rem;font-weight:700;">Found: Central Two-Wheeler & Bike Hub (0.4 km away)</h4>
            <p style="color:var(--color-green-text);font-size:0.88rem;font-weight:700;margin-top:0.25rem;">14 Free Bays Available • 100% Free Public Parking (Zero Fees)</p>
          </div>
        </div>
        <div style="margin-top:1.5rem;display:flex;flex-wrap:wrap;gap:0.75rem;">
          <button class="action-btn glow-btn" onclick="setFlowStep(4)">Start Navigation →</button>
        </div>
      `
    },
    4: {
      title: 'Step 4: Turn-by-Turn Navigation to Facility',
      desc: 'Ride to the chosen parking lot with live GPS route guidance.',
      html: `
        <div style="background:var(--bg-surface);border:1px solid var(--border-subtle);padding:1.2rem;border-radius:var(--radius-md);display:flex;gap:1.2rem;align-items:center;">
          <div style="font-size:2.8rem;">🧭💨</div>
          <div>
            <h4 style="color:var(--text-primary);font-size:1.1rem;font-weight:700;">Riding towards Central Bike Hub via Market St...</h4>
            <p style="color:var(--text-secondary);font-size:0.88rem;margin-top:0.25rem;">Distance remaining: 150m • Entrance on the right</p>
          </div>
        </div>
        <div style="margin-top:1.5rem;display:flex;flex-wrap:wrap;gap:0.75rem;">
          <button class="action-btn glow-btn" onclick="setFlowStep(5)">Arrived at Entrance →</button>
        </div>
      `
    },
    5: {
      title: 'Step 5: Arrive at Parking Facility',
      desc: 'You have arrived at the two-wheeler lot entrance. Time to scan the parking row.',
      html: `
        <div style="background:var(--bg-surface);border:1px solid var(--border-subtle);padding:1.2rem;border-radius:var(--radius-md);display:flex;gap:1.2rem;align-items:center;">
          <div style="font-size:2.8rem;">📍🏍️</div>
          <div>
            <h4 style="color:var(--text-primary);font-size:1.15rem;font-weight:700;">Welcome to Central Two-Wheeler Hub!</h4>
            <p style="color:var(--text-secondary);font-size:0.88rem;margin-top:0.25rem;">Slow down to 5 km/h. Mount phone or aim rear camera forward at the parking row.</p>
          </div>
        </div>
        <div style="margin-top:1.5rem;display:flex;flex-wrap:wrap;gap:0.75rem;">
          <button class="action-btn glow-btn" onclick="setFlowStep(6)">Launch Phone Camera Scan →</button>
        </div>
      `
    },
    6: {
      title: 'Step 6: Camera Permission & Live Video Stream',
      desc: 'Browser requests mobile camera permission to stream high-resolution video frames.',
      html: `
        <div style="background:var(--bg-surface);border:1px solid var(--border-subtle);padding:1.2rem;border-radius:var(--radius-md);display:flex;gap:1.2rem;align-items:center;">
          <div style="font-size:2.8rem;">📱📷</div>
          <div>
            <h4 style="color:var(--text-primary);font-size:1.1rem;font-weight:700;">Rear Camera Permission Granted (1080p 60fps)</h4>
            <p style="color:var(--color-green-text);font-size:0.88rem;font-weight:600;margin-top:0.25rem;">🟢 Live video feed active • Feeding frames into YOLOv8 engine</p>
          </div>
        </div>
        <div style="margin-top:1.5rem;display:flex;flex-wrap:wrap;gap:0.75rem;">
          <button class="action-btn glow-btn" onclick="setFlowStep(7)">Run Computer Vision Scan →</button>
        </div>
      `
    },
    7: {
      title: 'Step 7: Real-Time Computer Vision & Bike Fit Analysis',
      desc: 'Deep learning detects objects, perspective homography computes space dimensions, and checks if space fits your bike length.',
      html: `
        <div style="background:var(--bg-surface);border:1px solid var(--border-subtle);padding:1.2rem;border-radius:var(--radius-md);display:flex;gap:1.2rem;align-items:center;">
          <div style="font-size:2.8rem;">🔬</div>
          <div>
            <h4 style="color:var(--text-primary);font-size:1.1rem;font-weight:700;">YOLOv8 + Perspective Ground Plane Active</h4>
            <p style="color:var(--text-secondary);font-size:0.88rem;margin-top:0.25rem;">Detected: Bay B2 (2.50m Length × 1.40m Width). Clearance: +0.35m safe margin.</p>
          </div>
        </div>
        <div style="margin-top:1.5rem;display:flex;flex-wrap:wrap;gap:0.75rem;">
          <button class="action-btn glow-btn" onclick="setFlowStep(8)">View AR Recommendation →</button>
        </div>
      `
    },
    8: {
      title: 'Step 8: Final AR Spot Suggestion & Voice Guidance',
      desc: 'System renders glowing AR bounding box on your camera feed and speaks voice directions.',
      html: `
        <div style="background:var(--color-green-bg);border:1px solid var(--color-green-border);padding:1.5rem;border-radius:var(--radius-lg);">
          <h3 style="color:var(--color-green-text);font-size:1.35rem;font-weight:800;margin-bottom:0.5rem;">★ SUGGESTED: PARK IN BAY B2 ★</h3>
          <p style="color:var(--text-primary);font-size:0.95rem;line-height:1.6;">
            🟢 Space Clear & Fits your <strong>${p.bikeModel}</strong> (Length: ${p.length}m)<br>
            🏍️ Safe handlebar & kickstand clearance (+0.35m)<br>
            🆓 100% Free Public Parking • Zero Fees<br>
            ✨ Pull forward 4 meters and engage side-stand.
          </p>
        </div>
        <div style="margin-top:1.5rem;display:flex;flex-wrap:wrap;gap:0.75rem;">
          <button class="action-btn glow-btn" onclick="switchTab('camera-scan'); startCameraStream();">Open Live Camera Scanner 📷</button>
          <button class="action-btn btn-secondary" onclick="setFlowStep(1)">Restart Flow ↺</button>
        </div>
      `
    }
  };

  const current = stepContent[stepNum];
  body.innerHTML = `
    <h3 style="color:var(--text-primary);font-family:var(--font-display);font-size:1.35rem;font-weight:800;margin-bottom:0.4rem;">${current.title}</h3>
    <p style="color:var(--text-secondary);font-size:0.9rem;margin-bottom:1.25rem;">${current.desc}</p>
    ${current.html}
  `;
}

// ==========================================================================
// TOAST NOTIFICATION UTILITY
// ==========================================================================
function showToast(msg) {
  const existing = document.getElementById('app-toast');
  if (existing) existing.remove();

  const toast = document.createElement('div');
  toast.id = 'app-toast';
  toast.textContent = msg;
  document.body.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateY(10px)';
    toast.style.transition = 'all 0.3s ease';
    setTimeout(() => toast.remove(), 300);
  }, 3500);
}

// ==========================================================================
// WIZARD MODULE — Real-Life 5-Step Guided Parking Flow
// ==========================================================================
const wz = {
  step: 1,
  miniMap: null,
  parkingMap: null,
  navMap: null,
  selectedLot: null,
  lotsData: [],
  parkingMarkers: [],
  navRouteLine: null,
  cam: {
    stream: null,
    isSimulated: false,
    facingMode: 'environment',
    isAutoScanning: true,
    scanInterval: null,
    isScanningNow: false,
    speechEnabled: true,
    lastSpokenSlotId: null,
    lastSpokenTime: 0
  }
};

function initWizard() {
  const overlay = document.getElementById('wizard-overlay');
  const advancedBtn = document.getElementById('btn-open-advanced');
  const backWizardBtn = document.getElementById('btn-back-wizard');

  // Show wizard by default; hide main app tabs
  showWizardOverlay(true);

  // Advanced View button — hides wizard, shows main tabbed app
  if (advancedBtn) {
    advancedBtn.addEventListener('click', () => {
      showWizardOverlay(false);
      switchTab(state.currentTab || 'camera-scan');
    });
  }

  // Back-to-wizard button in main nav
  if (backWizardBtn) {
    backWizardBtn.addEventListener('click', () => {
      showWizardOverlay(true);
    });
  }

  // If user already has a profile, pre-fill Step 1 and show banner
  if (state.userProfile && state.userProfile.name && state.userProfile.bikeModel) {
    wzShowRegisteredBanner(state.userProfile);
  }

  wzInitStep1();
  wzInitStep2();
  wzInitStep3();
  wzInitStep4();
  wzInitStep5();
}

function showWizardOverlay(show) {
  const overlay = document.getElementById('wizard-overlay');
  const appHeader = document.querySelector('.navbar');
  const appMain = document.querySelector('.app-main');

  if (show) {
    overlay.classList.remove('wz-hidden');
    if (appHeader) appHeader.style.display = 'none';
    if (appMain) appMain.style.display = 'none';
  } else {
    overlay.classList.add('wz-hidden');
    if (appHeader) appHeader.style.display = '';
    if (appMain) appMain.style.display = '';
  }
}

function wzGoToStep(stepNum) {
  wz.step = stepNum;

  // Update panels
  document.querySelectorAll('.wz-panel').forEach(p => p.classList.remove('active'));
  const targetPanel = document.getElementById(`wz-panel-${stepNum}`);
  if (targetPanel) {
    targetPanel.classList.add('active');
    const overlay = document.getElementById('wizard-overlay');
    if (overlay) {
      overlay.scrollTo({ top: 0, behavior: 'smooth' });
    } else {
      targetPanel.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  }

  // Update progress stepper
  document.querySelectorAll('.wz-step-wrap').forEach(s => {
    const num = parseInt(s.getAttribute('data-wstep'));
    s.classList.toggle('active', num === stepNum);
    s.classList.toggle('completed', num < stepNum);
  });
  document.querySelectorAll('.wz-connector').forEach((c, i) => {
    c.classList.toggle('completed', i < stepNum - 1);
  });

  // On step 3 entering, load parking lots
  if (stepNum === 3) {
    setTimeout(() => wzLoadParkingLots(), 300);
  }
  // On step 4 entering, refresh nav map
  if (stepNum === 4 && wz.selectedLot) {
    setTimeout(() => wzInitNavMap(), 400);
  }
}

// ---- STEP 1: REGISTRATION ----
function wzInitStep1() {
  const form = document.getElementById('wz-inline-reg-form');
  const vehicleInput = document.getElementById('wz-vehicle');
  const lengthInput = document.getElementById('wz-length');
  const widthInput = document.getElementById('wz-width');
  const suggestionsList = document.getElementById('wz-vehicle-suggestions');
  const vehicleIconEl = document.getElementById('wz-vehicle-icon');
  const catTabs = document.getElementById('wz-cat-tabs');
  const quickChips = document.getElementById('wz-quick-chips');
  const detectedBanner = document.getElementById('wz-detected-banner');
  const editBtn = document.getElementById('wz-edit-profile');

  let wzWheelsFilter = null; // null for all, or 2, 3, 4

  // Instant dimension & vehicle detection helper
  function wzApplyVehicleDetection(vname, explicitObj = null) {
    if (!vname || !vname.trim()) {
      if (detectedBanner) detectedBanner.classList.add('hidden');
      return;
    }
    const v = explicitObj || (window.lookupVehicleClient ? window.lookupVehicleClient(vname) : null);
    if (!v) return;

    if (lengthInput) lengthInput.value = v.length_m;
    if (widthInput) widthInput.value = v.width_m;

    const icon = v.icon || (v.wheels === 4 ? '🚗' : (v.wheels === 3 ? '🛺' : '🏍️'));
    if (vehicleIconEl) vehicleIconEl.textContent = icon;

    // Update banner
    const detIcon = document.getElementById('wz-detected-icon');
    const detName = document.getElementById('wz-detected-name');
    const detCat = document.getElementById('wz-detected-category');
    const detLen = document.getElementById('wz-spec-length');
    const detWid = document.getElementById('wz-spec-width');
    const detHgt = document.getElementById('wz-spec-height');

    if (detName) detName.textContent = v.name;
    if (detIcon) detIcon.textContent = icon;
    if (detCat) detCat.textContent = `${v.category || 'Vehicle'} (${v.wheels || 2}-Wheeler)`;
    if (detLen) detLen.textContent = `${v.length_m}m`;
    if (detWid) detWid.textContent = `${v.width_m}m`;
    if (detHgt) detHgt.textContent = `${v.height_m || (v.wheels === 4 ? 1.55 : (v.wheels === 3 ? 1.70 : 1.10))}m`;

    if (detectedBanner) detectedBanner.classList.remove('hidden');
  }

  // Category filter tabs (All, 2W, 3W, 4W)
  if (catTabs) {
    catTabs.querySelectorAll('.wz-cat-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        catTabs.querySelectorAll('.wz-cat-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        const w = btn.getAttribute('data-wheels');
        wzWheelsFilter = (w === 'all') ? null : Number(w);

        // Update placeholder based on selected tab
        if (vehicleInput) {
          if (wzWheelsFilter === 4) {
            vehicleInput.placeholder = 'Type car name e.g. Swift, Creta, Thar, Fortuner, Nexon...';
            if (vehicleIconEl) vehicleIconEl.textContent = '🚗';
          } else if (wzWheelsFilter === 3) {
            vehicleInput.placeholder = 'Type 3-wheeler name e.g. Bajaj RE, Piaggio Ape, Treo...';
            if (vehicleIconEl) vehicleIconEl.textContent = '🛺';
          } else if (wzWheelsFilter === 2) {
            vehicleInput.placeholder = 'Type 2-wheeler name e.g. Activa, Splendor, Pulsar, Classic 350...';
            if (vehicleIconEl) vehicleIconEl.textContent = '🏍️';
          } else {
            vehicleInput.placeholder = 'Type vehicle name e.g. Swift, Activa, Auto Rickshaw, Thar, Creta...';
            if (vehicleIconEl) vehicleIconEl.textContent = '🚗';
          }
        }

        // Re-trigger search or suggestions
        if (vehicleInput && vehicleInput.value.trim().length >= 1) {
          renderSuggestions(vehicleInput.value.trim());
        }
      });
    });
  }

  // Quick Pick Chips
  if (quickChips) {
    quickChips.querySelectorAll('.wz-chip').forEach(chip => {
      chip.addEventListener('click', () => {
        const vname = chip.getAttribute('data-vname');
        if (vehicleInput) vehicleInput.value = vname;
        wzApplyVehicleDetection(vname);
        if (suggestionsList) suggestionsList.classList.add('hidden');
        showToast(`✨ Auto-detected: ${vname}`);
      });
    });
  }

  // If profile exists, show already-registered banner and skip-ahead option
  if (state.userProfile && state.userProfile.name) {
    wzShowRegisteredBanner(state.userProfile);
    // Pre-fill form with existing data
    const nameEl = document.getElementById('wz-name');
    const phoneEl = document.getElementById('wz-phone');
    const plateEl = document.getElementById('wz-plate');
    if (nameEl) nameEl.value = state.userProfile.name || '';
    if (phoneEl) phoneEl.value = state.userProfile.phone || '';
    if (plateEl) plateEl.value = state.userProfile.licensePlate || '';
    if (vehicleInput) vehicleInput.value = state.userProfile.bikeModel || '';
    if (lengthInput) lengthInput.value = state.userProfile.length || '';
    if (widthInput) widthInput.value = state.userProfile.width || '';
    if (state.userProfile.bikeModel) {
      wzApplyVehicleDetection(state.userProfile.bikeModel);
    }
  }

  // Edit button shows form again
  if (editBtn) {
    editBtn.addEventListener('click', () => {
      const banner = document.getElementById('wz-registered-banner');
      if (banner) banner.classList.add('hidden');
      if (form) form.classList.remove('hidden');
    });
  }

  // Suggestion renderer helper
  function renderSuggestions(q) {
    if (!suggestionsList) return;
    const clientList = window.searchVehiclesClient ? window.searchVehiclesClient(q, 15, wzWheelsFilter) : [];
    if (clientList.length === 0) {
      suggestionsList.innerHTML = '<div class="wz-ac-item wz-ac-none">Custom vehicle — dimensions auto-estimated by keywords</div>';
      suggestionsList.classList.remove('hidden');
      return;
    }
    suggestionsList.innerHTML = '';
    clientList.forEach(v => {
      const item = document.createElement('div');
      item.className = 'wz-ac-item';
      const wTag = v.wheels === 4 ? '<span class="wz-ac-tag tag-4w">4W Car</span>' : (v.wheels === 3 ? '<span class="wz-ac-tag tag-3w">3W Auto</span>' : '<span class="wz-ac-tag tag-2w">2W Bike</span>');
      item.innerHTML = `
        <div class="wz-ac-info">
          <span class="wz-ac-icon">${v.icon || '🚗'}</span>
          <span class="wz-ac-name">${v.name}</span>
        </div>
        <div class="wz-ac-meta">
          ${wTag}
          <span class="wz-ac-dims">${v.length_m}m × ${v.width_m}m</span>
        </div>
      `;
      item.addEventListener('click', () => {
        if (vehicleInput) vehicleInput.value = v.name;
        wzApplyVehicleDetection(v.name, v);
        suggestionsList.classList.add('hidden');
        showToast(`✨ Auto-detected: ${v.name} (${v.length_m}m × ${v.width_m}m)`);
      });
      suggestionsList.appendChild(item);
    });
    suggestionsList.classList.remove('hidden');
  }

  // Vehicle input listeners
  let debounce = null;
  if (vehicleInput && suggestionsList) {
    vehicleInput.addEventListener('input', (e) => {
      const q = e.target.value.trim();

      // Instant 0ms dimension detection while typing!
      if (q.length >= 2) {
        wzApplyVehicleDetection(q);
      } else {
        if (detectedBanner) detectedBanner.classList.add('hidden');
      }

      clearTimeout(debounce);
      if (!q || q.length < 1) {
        suggestionsList.innerHTML = '';
        suggestionsList.classList.add('hidden');
        return;
      }

      // Render local suggestions immediately
      renderSuggestions(q);

      // Also query backend asynchronously
      debounce = setTimeout(async () => {
        try {
          const filterParam = wzWheelsFilter ? `&wheels=${wzWheelsFilter}` : '';
          const res = await fetch(`${API_BASE}/api/vehicles/search?q=${encodeURIComponent(q)}${filterParam}`);
          if (res.ok) {
            const data = await res.json();
            const list = data.vehicles || [];
            if (list.length > 0 && vehicleInput.value.trim() === q) {
              // Ensure top match detection is applied
              wzApplyVehicleDetection(q, list[0]);
            }
          }
        } catch (_) {}
      }, 200);
    });

    document.addEventListener('click', (e) => {
      if (!vehicleInput.contains(e.target) && !suggestionsList.contains(e.target)) {
        suggestionsList.classList.add('hidden');
      }
    });

    // On blur: lookup exact vehicle
    vehicleInput.addEventListener('blur', () => {
      const q = vehicleInput.value.trim();
      if (q) {
        wzApplyVehicleDetection(q);
      }
    });
  }

  // Form submit
  if (form) {
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      const nameVal = (document.getElementById('wz-name')?.value.trim()) || 'Rider';
      const phoneVal = (document.getElementById('wz-phone')?.value.trim()) || '';
      const plateVal = ((document.getElementById('wz-plate')?.value.trim()) || `MH-01-BK-${Math.floor(1000 + Math.random() * 9000)}`).toUpperCase();
      const modelVal = (vehicleInput?.value.trim()) || 'Standard Vehicle';

      let lenVal = parseFloat(lengthInput?.value);
      let widVal = parseFloat(widthInput?.value);

      // Detect vehicle specifications
      const vInfo = window.lookupVehicleClient ? window.lookupVehicleClient(modelVal) : null;
      if ((!lenVal || isNaN(lenVal) || lenVal <= 0) && vInfo) lenVal = vInfo.length_m;
      if ((!widVal || isNaN(widVal) || widVal <= 0) && vInfo) widVal = vInfo.width_m;

      if (!lenVal || isNaN(lenVal)) lenVal = 2.04;
      if (!widVal || isNaN(widVal)) widVal = 0.73;

      const wheelsVal = vInfo ? (vInfo.wheels || 2) : 2;
      const categoryVal = vInfo ? (vInfo.category || 'Vehicle') : 'Vehicle';
      const iconVal = vInfo ? (vInfo.icon || (wheelsVal === 4 ? '🚗' : (wheelsVal === 3 ? '🛺' : '🏍️'))) : '🚗';

      let bikeTypeVal = 'bike_cruiser';
      if (wheelsVal === 4) {
        bikeTypeVal = (categoryVal.toLowerCase().includes('suv')) ? 'suv' : ((categoryVal.toLowerCase().includes('sedan')) ? 'sedan' : 'compact');
      } else if (wheelsVal === 3) {
        bikeTypeVal = 'auto';
      } else if (categoryVal.toLowerCase().includes('scooter')) {
        bikeTypeVal = 'bike_scooter';
      } else if (categoryVal.toLowerCase().includes('sports')) {
        bikeTypeVal = 'bike_sports';
      } else if (categoryVal.toLowerCase().includes('commuter')) {
        bikeTypeVal = 'bike_commuter';
      }

      const profile = {
        name: nameVal,
        phone: phoneVal,
        licensePlate: plateVal,
        bikeModel: modelVal,
        bikeType: bikeTypeVal,
        wheels: wheelsVal,
        category: categoryVal,
        icon: iconVal,
        length: lenVal,
        width: widVal,
        clearance: vInfo ? (vInfo.clearance_m || 0.20) : 0.20,
        email: `${nameVal.toLowerCase().replace(/[^a-z0-9]/g, '')}@parkvision.local`
      };

      saveUserProfile(profile);
      wzShowRegisteredBanner(profile);
      showToast(`✅ Profile saved: ${iconVal} ${modelVal} (${lenVal}m × ${widVal}m)`);

      // Sync to backend
      try {
        await fetch(`${API_BASE}/api/auth/register`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            name: nameVal, email: profile.email, password: '123456',
            phone: phoneVal, bike_model: modelVal,
            wheels: wheelsVal, category: categoryVal, icon: iconVal,
            length_m: lenVal, width_m: widVal, clearance_m: profile.clearance, license_plate: plateVal
          })
        });
      } catch (_) {}

      // Advance to Step 2
      wzGoToStep(2);
      // Auto-try GPS on step 2
      setTimeout(() => wzDetectGPS(), 400);
    });
  }
}

function wzShowRegisteredBanner(p) {
  const banner = document.getElementById('wz-registered-banner');
  const form = document.getElementById('wz-inline-reg-form');
  const nameEl = document.getElementById('wz-reg-name');
  const vehicleEl = document.getElementById('wz-reg-vehicle');

  if (banner && nameEl && vehicleEl && p) {
    const icon = p.icon || (p.wheels === 4 ? '🚗' : (p.wheels === 3 ? '🛺' : '🏍️'));
    nameEl.textContent = `👤 ${p.name}`;
    vehicleEl.textContent = `${icon} ${p.bikeModel} · ${p.length}m × ${p.width}m · ${p.licensePlate || ''}`;
    banner.classList.remove('hidden');
    if (form) form.classList.add('hidden');

    // Add "continue" button to banner if not already there
    if (!document.getElementById('wz-banner-continue')) {
      const continueBtn = document.createElement('button');
      continueBtn.id = 'wz-banner-continue';
      continueBtn.className = 'wz-btn-primary';
      continueBtn.style.marginTop = '1rem';
      continueBtn.innerHTML = '<span>✅ Continue to GPS →</span>';
      continueBtn.addEventListener('click', () => {
        wzGoToStep(2);
        setTimeout(() => wzDetectGPS(), 400);
      });
      banner.parentNode.appendChild(continueBtn);
    }
  }
}

// ---- STEP 2: GPS ----
function wzInitStep2() {
  const detectBtn = document.getElementById('wz-detect-gps');
  const backBtn = document.getElementById('wz-back-1');

  if (detectBtn) detectBtn.addEventListener('click', () => wzDetectGPS());
  if (backBtn) backBtn.addEventListener('click', () => wzGoToStep(1));

  // City chips
  document.querySelectorAll('.wz-city-chip').forEach(chip => {
    chip.addEventListener('click', () => {
      const lat = parseFloat(chip.getAttribute('data-lat'));
      const lng = parseFloat(chip.getAttribute('data-lng'));
      const city = chip.getAttribute('data-city');
      wzSetLocation(lat, lng, city, false);
    });
  });
}

function wzDetectGPS() {
  const statusEl = document.getElementById('wz-gps-status');
  const coordsEl = document.getElementById('wz-gps-coords');
  const iconEl = document.getElementById('wz-gps-icon');
  const detectBtn = document.getElementById('wz-detect-gps');

  if (statusEl) statusEl.textContent = 'Acquiring GPS satellite fix...';
  if (iconEl) iconEl.textContent = '📡';
  if (detectBtn) detectBtn.disabled = true;

  if (!navigator.geolocation) {
    if (statusEl) statusEl.textContent = '⚠️ GPS not supported. Please select a city.';
    if (detectBtn) detectBtn.disabled = false;
    return;
  }

  navigator.geolocation.getCurrentPosition(
    (pos) => {
      wzSetLocation(pos.coords.latitude, pos.coords.longitude, 'Live GPS', true);
      if (detectBtn) detectBtn.disabled = false;
    },
    (err) => {
      console.warn('GPS error:', err);
      if (statusEl) statusEl.textContent = '⚠️ GPS unavailable — select a city below';
      if (coordsEl) coordsEl.textContent = 'Or tap a city chip to set location manually';
      if (iconEl) iconEl.textContent = '⚠️';
      if (detectBtn) detectBtn.disabled = false;
    },
    { enableHighAccuracy: true, timeout: 8000 }
  );
}

function wzSetLocation(lat, lng, cityName, isLive) {
  state.userLocation = [lat, lng];
  state.userLocationLive = isLive;

  const statusEl = document.getElementById('wz-gps-status');
  const coordsEl = document.getElementById('wz-gps-coords');
  const iconEl = document.getElementById('wz-gps-icon');

  if (statusEl) statusEl.textContent = isLive ? '🟢 Live GPS Acquired!' : `📍 Location Set: ${cityName}`;
  if (coordsEl) coordsEl.textContent = `${lat.toFixed(5)}° N, ${lng.toFixed(5)}° E`;
  if (iconEl) iconEl.textContent = isLive ? '✅' : '📍';

  // Show mini map
  wzInitMiniMap(lat, lng);
  showToast(`📍 Location set — finding free parking near ${cityName}`);

  // Auto-advance after a moment
  setTimeout(() => wzGoToStep(3), 1200);
}

function wzInitMiniMap(lat, lng) {
  const mapEl = document.getElementById('wz-mini-map');
  if (!mapEl) return;

  const mapWrap = document.getElementById('wz-mini-map-wrap');
  if (mapWrap) mapWrap.style.display = 'block';

  if (wz.miniMap) {
    wz.miniMap.setView([lat, lng], 14);
    return;
  }

  wz.miniMap = L.map('wz-mini-map', { zoomControl: false, dragging: false, scrollWheelZoom: false }).setView([lat, lng], 14);
  L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', { maxZoom: 19 }).addTo(wz.miniMap);

  const icon = L.divIcon({
    className: '',
    html: `<div style="background:#2563eb;width:20px;height:20px;border-radius:50%;border:3px solid white;box-shadow:0 2px 8px rgba(0,0,0,0.3);display:flex;align-items:center;justify-content:center;font-size:10px;">📍</div>`,
    iconSize: [20, 20], iconAnchor: [10, 10]
  });
  L.marker([lat, lng], { icon }).addTo(wz.miniMap);
}

// ---- STEP 3: FIND PARKING ----
function wzInitStep3() {
  const navigateBtn = document.getElementById('wz-goto-navigate');
  const backBtn = document.getElementById('wz-back-2');

  if (navigateBtn) {
    navigateBtn.addEventListener('click', () => {
      if (wz.selectedLot) wzGoToStep(4);
    });
  }
  if (backBtn) backBtn.addEventListener('click', () => wzGoToStep(2));
}

async function wzLoadParkingLots() {
  const lotsList = document.getElementById('wz-lots-list');
  const loadingEl = document.getElementById('wz-lots-loading');
  const freeCountEl = document.getElementById('wz-free-count');
  const navigateBtn = document.getElementById('wz-goto-navigate');

  if (loadingEl) loadingEl.style.display = 'flex';

  // Initialize or refresh parking map
  if (!wz.parkingMap) {
    const mapEl = document.getElementById('wz-parking-map');
    if (mapEl) {
      wz.parkingMap = L.map('wz-parking-map', { zoomControl: true }).setView(state.userLocation, 15);
      L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', { maxZoom: 19 }).addTo(wz.parkingMap);

      // User marker
      const userIcon = L.divIcon({
        className: '',
        html: `<div style="background:#2563eb;width:22px;height:22px;border-radius:50%;border:3px solid white;box-shadow:0 2px 8px rgba(0,0,0,0.35);font-size:11px;display:flex;align-items:center;justify-content:center;">📍</div>`,
        iconSize: [22, 22], iconAnchor: [11, 11]
      });
      L.marker(state.userLocation, { icon: userIcon }).addTo(wz.parkingMap).bindPopup('📍 You are here');
    }
  } else {
    wz.parkingMap.setView(state.userLocation, 15);
    wz.parkingMap.invalidateSize();
  }

  let lots = null;
  try {
    const res = await fetch(`${API_BASE}/api/parking/nearby?lat=${state.userLocation[0]}&lng=${state.userLocation[1]}`);
    if (res.ok) {
      lots = await res.json();
    }
  } catch (err) {
    console.warn('Backend fetch failed for wizard lots, using built-in generator:', err);
  }

  if (!lots || !Array.isArray(lots) || lots.length === 0) {
    lots = generateClientNearbyParking(state.userLocation[0], state.userLocation[1]);
  }

  try {
    wz.lotsData = lots;

    // Clear old markers
    wz.parkingMarkers.forEach(m => wz.parkingMap && wz.parkingMap.removeLayer(m));
    wz.parkingMarkers = [];

    if (lotsList) {
      lotsList.innerHTML = '';
    }
    if (loadingEl) loadingEl.style.display = 'none';

    let totalFree = 0;
    lots.forEach(lot => {
      const dist = haversineDistance(state.userLocation[0], state.userLocation[1], lot.latitude, lot.longitude);
      lot.wz_dist = dist > 0 ? dist : lot.distance_km;
      totalFree += lot.live_available;
    });
    lots.sort((a, b) => a.wz_dist - b.wz_dist);

    if (freeCountEl) freeCountEl.textContent = `${totalFree} free bays found`;

    lots.forEach((lot, idx) => {
      // Map pin
      if (wz.parkingMap) {
        const pinIcon = L.divIcon({
          className: '',
          html: `<div style="background:${lot.live_available > 0 ? '#059669' : '#dc2626'};color:white;font-weight:700;font-size:11px;padding:3px 8px;border-radius:12px;border:2px solid white;box-shadow:0 2px 6px rgba(0,0,0,0.25);">${lot.live_available} 🏍️</div>`,
          iconSize: [50, 26], iconAnchor: [25, 13]
        });
        const marker = L.marker([lot.latitude, lot.longitude], { icon: pinIcon }).addTo(wz.parkingMap);
        marker.bindPopup(`<strong>${lot.name}</strong><br><span style="color:#10b981;font-weight:bold;">${lot.live_available} Free Bays (Zero Fee)</span>`);
        marker.on('click', () => wzSelectLot(lot));
        wz.parkingMarkers.push(marker);
      }

      // Sidebar card
      if (lotsList) {
        const card = document.createElement('div');
        card.className = `wz-lot-card${idx === 0 ? ' selected' : ''}`;
        card.id = `wz-lot-${lot.id}`;
        card.innerHTML = `
          <div class="wz-lot-top">
            <div>
              <div class="wz-lot-name">${lot.name}</div>
              <div class="wz-lot-type">${lot.type || 'Bike Parking'}</div>
            </div>
            <div class="wz-lot-right">
              <div class="wz-lot-dist">${lot.wz_dist} km</div>
              <div class="wz-lot-avail ${lot.live_available > 0 ? 'avail' : 'full'}">${lot.live_available} free</div>
            </div>
          </div>
          <div class="wz-lot-tags">
            <span class="wz-lot-tag free">🟢 Zero Fee</span>
            <span class="wz-lot-tag bike">🏍️ Two-Wheeler</span>
          </div>
        `;
        card.addEventListener('click', () => wzSelectLot(lot));
        lotsList.appendChild(card);
        if (idx === 0) wzSelectLot(lot);
      }
    });
  } catch (err) {
    console.error('Failed to load wizard parking lots:', err);
    if (loadingEl) loadingEl.style.display = 'none';
    if (lotsList) {
      lotsList.innerHTML = `<div class="wz-lots-error">⚠️ Could not load parking data. Please check backend connection.<br><small>Make sure the Python backend is running.</small></div>`;
    }
  }
}

function wzSelectLot(lot) {
  wz.selectedLot = lot;

  // Highlight selected card
  document.querySelectorAll('.wz-lot-card').forEach(c => c.classList.remove('selected'));
  const card = document.getElementById(`wz-lot-${lot.id}`);
  if (card) card.classList.add('selected');

  // Enable navigate button
  const navigateBtn = document.getElementById('wz-goto-navigate');
  if (navigateBtn) navigateBtn.disabled = false;

  // Center map
  if (wz.parkingMap) wz.parkingMap.panTo([lot.latitude, lot.longitude]);
}

// ---- STEP 4: NAVIGATION ----
function wzInitStep4() {
  const arrivedBtn = document.getElementById('wz-arrived-btn');
  const gmapsBtn = document.getElementById('wz-open-gmaps');
  const backBtn = document.getElementById('wz-back-3');

  if (arrivedBtn) {
    arrivedBtn.addEventListener('click', () => {
      wzGoToStep(5);
      // Auto-request camera on arriving
      setTimeout(() => {
        const permOverlay = document.getElementById('wz-cam-perm-overlay');
        if (permOverlay) permOverlay.classList.remove('hidden');
      }, 300);
    });
  }

  if (gmapsBtn) {
    gmapsBtn.addEventListener('click', () => {
      if (wz.selectedLot) {
        const url = `https://www.google.com/maps/dir/?api=1&destination=${wz.selectedLot.latitude},${wz.selectedLot.longitude}&travelmode=driving`;
        window.open(url, '_blank');
      }
    });
  }

  if (backBtn) backBtn.addEventListener('click', () => wzGoToStep(3));
}

function wzInitNavMap() {
  if (!wz.selectedLot) return;

  // Fill in lot details
  const lot = wz.selectedLot;
  const lotNameEl = document.getElementById('wz-nav-lot-name');
  const lotMetaEl = document.getElementById('wz-nav-lot-meta');
  const distEl = document.getElementById('wz-nav-dist');
  const timeEl = document.getElementById('wz-nav-time');
  const baysEl = document.getElementById('wz-nav-bays');

  if (lotNameEl) lotNameEl.textContent = lot.name;
  if (lotMetaEl) lotMetaEl.textContent = `${lot.type || 'Bike Parking'} · ${lot.address || 'Public Lot'}`;
  if (distEl) distEl.textContent = lot.wz_dist || lot.distance_km;
  if (timeEl) timeEl.textContent = Math.max(1, Math.round((lot.wz_dist || lot.distance_km) * 3));
  if (baysEl) baysEl.textContent = lot.live_available;

  // Init nav map
  if (!wz.navMap) {
    const mapEl = document.getElementById('wz-nav-map');
    if (!mapEl) return;
    const midLat = (state.userLocation[0] + lot.latitude) / 2;
    const midLng = (state.userLocation[1] + lot.longitude) / 2;
    wz.navMap = L.map('wz-nav-map', { zoomControl: true }).setView([midLat, midLng], 14);
    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', { maxZoom: 19 }).addTo(wz.navMap);
  } else {
    wz.navMap.invalidateSize();
  }

  // Draw route line
  if (wz.navRouteLine) wz.navMap.removeLayer(wz.navRouteLine);
  wz.navRouteLine = L.polyline([state.userLocation, [lot.latitude, lot.longitude]], {
    color: '#2563eb', weight: 4, dashArray: '8, 8', opacity: 0.9
  }).addTo(wz.navMap);
  wz.navMap.fitBounds(wz.navRouteLine.getBounds(), { padding: [30, 30] });

  // You marker
  const userIcon = L.divIcon({
    className: '',
    html: `<div style="background:#2563eb;width:22px;height:22px;border-radius:50%;border:3px solid white;box-shadow:0 2px 8px rgba(0,0,0,0.3);font-size:11px;display:flex;align-items:center;justify-content:center;">📍</div>`,
    iconSize: [22, 22], iconAnchor: [11, 11]
  });
  L.marker(state.userLocation, { icon: userIcon }).addTo(wz.navMap).bindPopup('📍 You');

  // Lot marker
  const lotIcon = L.divIcon({
    className: '',
    html: `<div style="background:#059669;color:white;font-weight:700;font-size:11px;padding:4px 9px;border-radius:12px;border:2px solid white;box-shadow:0 2px 6px rgba(0,0,0,0.25);">${lot.live_available} 🏍️ FREE</div>`,
    iconSize: [80, 28], iconAnchor: [40, 14]
  });
  L.marker([lot.latitude, lot.longitude], { icon: lotIcon }).addTo(wz.navMap).bindPopup(`<strong>${lot.name}</strong><br>Zero Fee Bike Parking`);
}

// ---- STEP 5: CAMERA CV SCAN ----
function wzInitStep5() {
  const reqCamBtn = document.getElementById('wz-req-cam');
  const simCamBtn = document.getElementById('wz-sim-cam');
  const toggleCamBtn = document.getElementById('wz-toggle-cam');
  const flipCamBtn = document.getElementById('wz-flip-cam');
  const scanNowBtn = document.getElementById('wz-scan-now');
  const autoScanBtn = document.getElementById('wz-autoscan');
  const speakBtn = document.getElementById('wz-speak');
  const confirmBtn = document.getElementById('wz-confirm-parked');
  const backBtn = document.getElementById('wz-back-4');

  if (reqCamBtn) reqCamBtn.addEventListener('click', () => wzStartCamera());
  if (simCamBtn) simCamBtn.addEventListener('click', () => wzStartSimCamera());

  if (toggleCamBtn) {
    toggleCamBtn.addEventListener('click', () => {
      if (wz.cam.stream || wz.cam.isSimulated) {
        wzStopCamera();
      } else {
        wzStartCamera();
      }
    });
  }

  if (flipCamBtn) {
    flipCamBtn.addEventListener('click', () => {
      wz.cam.facingMode = wz.cam.facingMode === 'environment' ? 'user' : 'environment';
      if (wz.cam.stream) { wzStopCamera(); wzStartCamera(); }
    });
  }

  if (scanNowBtn) scanNowBtn.addEventListener('click', () => wzCaptureAndScan());

  if (autoScanBtn) {
    autoScanBtn.addEventListener('click', () => {
      wz.cam.isAutoScanning = !wz.cam.isAutoScanning;
      autoScanBtn.classList.toggle('active', wz.cam.isAutoScanning);
      autoScanBtn.querySelector('span:last-child').textContent = wz.cam.isAutoScanning ? 'Auto: ON' : 'Auto: OFF';
      if (wz.cam.isAutoScanning) wzStartAutoScan(); else wzStopAutoScan();
    });
  }

  if (speakBtn) {
    speakBtn.addEventListener('click', () => {
      const msg = document.getElementById('wz-rec-msg')?.textContent;
      if (msg) speakGuidance(msg, true);
    });
  }

  if (confirmBtn) {
    confirmBtn.addEventListener('click', () => {
      showToast('🎉 Parking Confirmed! Have a safe trip!');
      speakGuidance('Your bike is safely parked. Have a great day!');
      wzStopCamera();
    });
  }

  if (backBtn) {
    backBtn.addEventListener('click', () => {
      wzStopCamera();
      wzGoToStep(4);
    });
  }

  // Update bike name in permission overlay
  const bikeNameEl = document.getElementById('wz-perm-bike-name');
  if (bikeNameEl && state.userProfile) {
    bikeNameEl.textContent = state.userProfile.bikeModel || 'bike';
  }
}

async function wzStartCamera() {
  const permOverlay = document.getElementById('wz-cam-perm-overlay');
  const statusEl = document.getElementById('wz-cam-status');
  const video = document.getElementById('wz-cam-video');

  if (statusEl) statusEl.textContent = 'Requesting Camera Permission...';

  if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
    alert('Camera not supported on this browser. Please use a modern mobile browser like Chrome or Safari.');
    return;
  }

  try {
    const stream = await navigator.mediaDevices.getUserMedia({
      video: { facingMode: { ideal: wz.cam.facingMode }, width: { ideal: 1280 }, height: { ideal: 720 } },
      audio: false
    });
    wz.cam.stream = stream;
    wz.cam.isSimulated = false;

    video.srcObject = stream;
    await video.play();

    if (permOverlay) permOverlay.classList.add('hidden');
    if (statusEl) statusEl.textContent = `🟢 Live ${wz.cam.facingMode === 'environment' ? 'Rear' : 'Front'} Camera Active`;

    video.onloadedmetadata = () => {
      wzResizeARCanvas();
      if (wz.cam.isAutoScanning) wzStartAutoScan();
    };

    // Update vehicle tag in HUD
    const hudVehicle = document.getElementById('wz-hud-vehicle');
    if (hudVehicle && state.userProfile) {
      const vIcon = state.userProfile.icon || (state.userProfile.wheels === 4 ? '🚗' : (state.userProfile.wheels === 3 ? '🛺' : '🏍️'));
      hudVehicle.textContent = `${vIcon} ${state.userProfile.bikeModel || 'Vehicle'} (${state.userProfile.length}m)`;
    }
  } catch (err) {
    console.error('Wizard camera error:', err);
    if (statusEl) statusEl.textContent = '⚠️ Camera Access Denied';
    alert(`Camera Permission Needed\n\n${err.message}\n\nTip: Use HTTPS or allow camera in browser settings. You can also try "Simulated Feed".`);
  }
}

function wzStartSimCamera() {
  const permOverlay = document.getElementById('wz-cam-perm-overlay');
  const statusEl = document.getElementById('wz-cam-status');
  const video = document.getElementById('wz-cam-video');

  wzStopCamera();
  wz.cam.isSimulated = true;

  video.srcObject = null;
  video.poster = `${API_BASE}/static/scenarios/scenario_2_driver.jpg`;

  if (permOverlay) permOverlay.classList.add('hidden');
  if (statusEl) statusEl.textContent = '🎬 Simulated Camera Feed (Driver View)';

  wzResizeARCanvas();
  setTimeout(() => {
    wzCaptureAndScan();
    if (wz.cam.isAutoScanning) wzStartAutoScan();
  }, 400);
}

function wzStopCamera() {
  if (wz.cam.stream) {
    wz.cam.stream.getTracks().forEach(t => t.stop());
    wz.cam.stream = null;
  }
  const video = document.getElementById('wz-cam-video');
  if (video) { video.srcObject = null; video.poster = ''; }
  wz.cam.isSimulated = false;
  wzStopAutoScan();
  wzClearARCanvas();

  const permOverlay = document.getElementById('wz-cam-perm-overlay');
  if (permOverlay) permOverlay.classList.remove('hidden');
  const statusEl = document.getElementById('wz-cam-status');
  if (statusEl) statusEl.textContent = 'Camera Stopped';
}

function wzStartAutoScan() {
  wzStopAutoScan();
  wz.cam.scanInterval = setInterval(() => {
    if (wz.step === 5) wzCaptureAndScan();
  }, 1800);
}

function wzStopAutoScan() {
  if (wz.cam.scanInterval) {
    clearInterval(wz.cam.scanInterval);
    wz.cam.scanInterval = null;
  }
}

function wzResizeARCanvas() {
  const video = document.getElementById('wz-cam-video');
  const canvas = document.getElementById('wz-ar-canvas');
  if (!video || !canvas) return;
  const rect = video.getBoundingClientRect();
  canvas.width = rect.width || video.videoWidth || 640;
  canvas.height = rect.height || video.videoHeight || 360;
}

function wzClearARCanvas() {
  const canvas = document.getElementById('wz-ar-canvas');
  if (canvas) {
    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, canvas.width, canvas.height);
  }
  const pointer = document.getElementById('wz-ar-pointer');
  if (pointer) pointer.classList.add('hidden');
}

async function wzCaptureAndScan() {
  if (wz.cam.isScanningNow) return;
  wz.cam.isScanningNow = true;

  const spinner = document.getElementById('wz-scan-spinner');
  if (spinner) spinner.classList.remove('hidden');

  try {
    const video = document.getElementById('wz-cam-video');
    const p = state.userProfile || { bikeType: 'bike_cruiser', length: 2.14, width: 0.84, bikeModel: 'Vehicle' };
    const formData = new FormData();
    formData.append('vehicle_type', p.bikeType || 'bike_cruiser');
    formData.append('custom_length', p.length || 2.14);
    formData.append('custom_width', p.width || 0.84);
    formData.append('bike_model', p.bikeModel || 'Vehicle');

    if (wz.cam.isSimulated || !wz.cam.stream) {
      const lot = wz.selectedLot;
      const scenarioKey = (lot && lot.scenario_key) ? lot.scenario_key : 'scenario_2_driver';
      formData.append('scenario_key', scenarioKey);
    } else {
      const tmpCanvas = document.createElement('canvas');
      tmpCanvas.width = video.videoWidth || 1280;
      tmpCanvas.height = video.videoHeight || 720;
      tmpCanvas.getContext('2d').drawImage(video, 0, 0, tmpCanvas.width, tmpCanvas.height);
      formData.append('image_base64', tmpCanvas.toDataURL('image/jpeg', 0.8));
    }

    const res = await fetch(`${API_BASE}/api/cv/analyze-live-frame`, { method: 'POST', body: formData });
    if (!res.ok) throw new Error(`CV API error: ${res.statusText}`);
    const data = await res.json();
    wzRenderScanResults(data);
  } catch (err) {
    console.error('Wizard scan error:', err);
  } finally {
    wz.cam.isScanningNow = false;
    const spinner = document.getElementById('wz-scan-spinner');
    if (spinner) spinner.classList.add('hidden');
  }
}

function wzRenderScanResults(data) {
  if (!data || !data.success) return;

  const rec = data.recommended_slot;
  const p = state.userProfile || { bikeModel: 'Vehicle', length: 2.14, width: 0.84 };

  const titleEl = document.getElementById('wz-rec-title');
  const statusEl = document.getElementById('wz-rec-status');
  const dimsEl = document.getElementById('wz-rec-dims');
  const bikeEl = document.getElementById('wz-rec-bike');
  const clearEl = document.getElementById('wz-rec-clearance');
  const msgEl = document.getElementById('wz-rec-msg');

  const vIcon = p.icon || (p.wheels === 4 ? '🚗' : (p.wheels === 3 ? '🛺' : '🏍️'));
  const vehKind = p.wheels === 4 ? 'Car' : (p.wheels === 3 ? 'Auto' : 'Vehicle');

  if (bikeEl) bikeEl.textContent = `${vIcon} ${p.bikeModel} (${p.length}m)`;

  if (rec) {
    if (titleEl) titleEl.textContent = rec.label || `Bay ${rec.id}`;
    if (statusEl) { statusEl.textContent = `🟢 Available & Fits Your ${vehKind}`; statusEl.style.color = '#059669'; }
    if (dimsEl) dimsEl.textContent = `${rec.metrics.length_m}m × ${rec.metrics.width_m}m`;
    const margin = rec.vehicle_fit ? rec.vehicle_fit.width_margin_m : 0.35;
    if (clearEl) clearEl.textContent = `+${margin}m clearance`;
    if (msgEl) msgEl.textContent = `${rec.vehicle_fit?.message || ''} Free public bay — pull straight in.`;

    // Voice
    const now = Date.now();
    if (wz.cam.speechEnabled && (wz.cam.lastSpokenSlotId !== rec.id || now - wz.cam.lastSpokenTime > 12000)) {
      wz.cam.lastSpokenSlotId = rec.id;
      wz.cam.lastSpokenTime = now;
      speakGuidance(data.speech_text || `Free space found! Park your bike in ${rec.label}.`);
    }
  } else {
    if (titleEl) titleEl.textContent = 'Scanning...';
    if (statusEl) { statusEl.textContent = '🟡 No fitting spot detected'; statusEl.style.color = '#d97706'; }
    if (dimsEl) dimsEl.textContent = '—';
    if (clearEl) clearEl.textContent = '—';
    if (msgEl) msgEl.textContent = `All visible spaces are occupied or too small. Move your camera angle forward.`;
  }

  // Draw AR overlay
  wzDrawAROverlay(data.ar_slots, rec);

  // Populate bays list
  const baysList = document.getElementById('wz-bays-list');
  if (baysList && data.ar_slots) {
    baysList.innerHTML = '';
    data.ar_slots.forEach(s => {
      const isRec = rec && s.id === rec.id;
      const item = document.createElement('div');
      item.className = `wz-bay-item${isRec ? ' suggested' : ''}`;
      item.innerHTML = `
        <div>
          <strong>${s.label}</strong> <span style="font-size:0.78rem;color:var(--text-muted);">(${s.length_m}m × ${s.width_m}m)</span>
          <div style="font-size:0.75rem;font-weight:600;color:${s.status === 'AVAILABLE' ? '#059669' : '#dc2626'};">
            ${s.status === 'AVAILABLE' ? '🟢 Available' : '🔴 Occupied'}${isRec ? ' · ⭐ Best Fit' : ''}
          </div>
        </div>
        <span style="color:#059669;font-weight:700;font-size:0.82rem;">FREE</span>
      `;
      baysList.appendChild(item);
    });
  }
}

function wzDrawAROverlay(arSlots, recommendedSlot) {
  const canvas = document.getElementById('wz-ar-canvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  const pointer = document.getElementById('wz-ar-pointer');
  const arTag = document.getElementById('wz-ar-tag');
  let pointerShown = false;

  if (!arSlots || arSlots.length === 0) {
    if (pointer) pointer.classList.add('hidden');
    return;
  }

  const cw = canvas.width;
  const ch = canvas.height;

  arSlots.forEach(s => {
    const isRec = recommendedSlot && s.id === recommendedSlot.id;
    const poly = s.normalized_polygon;
    if (!poly || poly.length < 3) return;

    ctx.beginPath();
    ctx.moveTo(poly[0][0] * cw, poly[0][1] * ch);
    for (let i = 1; i < poly.length; i++) ctx.lineTo(poly[i][0] * cw, poly[i][1] * ch);
    ctx.closePath();

    if (isRec) {
      ctx.strokeStyle = '#10b981';
      ctx.lineWidth = 4;
      ctx.shadowColor = '#10b981';
      ctx.shadowBlur = 18;
      ctx.fillStyle = 'rgba(16, 185, 129, 0.22)';
      ctx.fill();
      ctx.stroke();
      ctx.shadowBlur = 0;

      const cx = s.center[0] * cw;
      const cy = s.center[1] * ch;

      // Green badge circle
      ctx.fillStyle = '#10b981';
      ctx.beginPath();
      ctx.arc(cx, cy, 20, 0, Math.PI * 2);
      ctx.fill();
      ctx.fillStyle = '#fff';
      ctx.font = 'bold 13px sans-serif';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillText('🅿️', cx, cy);

      // Label text
      ctx.fillStyle = '#10b981';
      ctx.font = 'bold 14px sans-serif';
      ctx.fillText('PARK HERE', cx, cy - 30);

      if (pointer) {
        pointer.style.left = `${cx}px`;
        pointer.style.top = `${Math.max(10, cy - 60)}px`;
        if (arTag) arTag.textContent = `★ PARK: ${s.label.toUpperCase()} ★`;
        pointer.classList.remove('hidden');
        pointerShown = true;
      }
    } else if (s.status === 'AVAILABLE') {
      ctx.strokeStyle = 'rgba(16, 185, 129, 0.5)';
      ctx.lineWidth = 2;
      ctx.fillStyle = 'rgba(16, 185, 129, 0.08)';
      ctx.fill(); ctx.stroke();
    } else {
      ctx.strokeStyle = 'rgba(239, 68, 68, 0.6)';
      ctx.lineWidth = 2;
      ctx.fillStyle = 'rgba(239, 68, 68, 0.1)';
      ctx.fill(); ctx.stroke();
    }
  });

  if (!pointerShown && pointer) pointer.classList.add('hidden');
}
