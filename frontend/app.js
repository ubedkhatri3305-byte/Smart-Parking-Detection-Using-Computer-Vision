// ==========================================================================
// PARKVISION BIKE CV - CORE CLIENT APPLICATION
// Real-Life User & Bike Registration, Live GPS Locator, WebRTC Camera Scanner,
// Computer Vision Space Matching, AR Viewport Overlay, and Zero-Fee Routing
// ==========================================================================

// Cloud Backend URL Resolver (supports local dev, Render, and Vercel)
function getApiBase() {
  const custom = localStorage.getItem('PARKVISION_BACKEND_URL');
  if (custom) return custom.replace(/\/$/, '');
  if (window.location.origin.includes(':8000') || window.location.origin.includes(':5173')) {
    return 'http://localhost:8000';
  }
  return '';
}

let API_BASE = getApiBase();

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

  // Resize handler for Leaflet Map & AR Canvas
  window.addEventListener('resize', () => {
    if (state.map) {
      setTimeout(() => state.map.invalidateSize(), 150);
    }
    resizeARCanvas();
  });

  // Run initial diagnostic CV analysis for lab view
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

    if (riderNameEl) riderNameEl.textContent = p.name;
    if (vehNameEl) vehNameEl.textContent = p.bikeModel;
    if (vehDimsEl) vehDimsEl.textContent = `(${p.length}m × ${p.width}m)`;
    if (vehPlateEl) vehPlateEl.textContent = p.licensePlate || 'NO-PLATE';

    const camBikeTag = document.getElementById('cam-active-bike-tag');
    if (camBikeTag) {
      camBikeTag.textContent = `🏍️ ${p.bikeModel} (${p.length}m × ${p.width}m)`;
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
      camBikeTag.textContent = `🏍️ Register or Login to Auto-Match`;
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

  // --- VEHICLE AUTOCOMPLETE & AUTO-FETCH FROM REAL DATASET ---
  let debounceTimer = null;
  if (modelInput && suggestionsList) {
    modelInput.addEventListener('input', (e) => {
      clearTimeout(debounceTimer);
      const q = e.target.value.trim();
      if (!q || q.length < 2) {
        suggestionsList.innerHTML = '';
        suggestionsList.classList.add('hidden');
        return;
      }

      debounceTimer = setTimeout(async () => {
        try {
          const res = await fetch(`${API_BASE}/api/vehicles/search?q=${encodeURIComponent(q)}`);
          const data = await res.json();
          const list = data.vehicles || [];

          if (list.length === 0) {
            suggestionsList.innerHTML = '<div style="padding:0.6rem 0.85rem;font-size:0.8rem;color:var(--text-muted);">No match found in dataset. Enter length and width manually.</div>';
            suggestionsList.classList.remove('hidden');
            return;
          }

          suggestionsList.innerHTML = '';
          list.forEach(v => {
            const item = document.createElement('div');
            item.className = 'autocomplete-item';
            item.innerHTML = `
              <div class="auto-item-name">${v.icon || '🏍️'} ${v.name}</div>
              <div class="auto-item-meta">
                <span class="auto-item-cat">${v.category}</span>
                <span class="auto-item-dims">${v.length_m}m × ${v.width_m}m</span>
              </div>
            `;
            item.addEventListener('click', () => {
              modelInput.value = v.name;
              lengthInput.value = v.length_m;
              widthInput.value = v.width_m;
              if (clearanceInput && v.clearance_m) clearanceInput.value = v.clearance_m;
              suggestionsList.classList.add('hidden');
              if (autofillIndicator && autofillText) {
                autofillText.textContent = `⚡ ${v.name}: Length ${v.length_m}m × Width ${v.width_m}m auto-detected from vehicle dataset`;
                autofillIndicator.classList.remove('hidden');
              }
              showToast(`✨ Auto-fetched: ${v.name} (${v.length_m}m × ${v.width_m}m)`);
            });
            suggestionsList.appendChild(item);
          });
          suggestionsList.classList.remove('hidden');
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

    modelInput.addEventListener('blur', async () => {
      const q = modelInput.value.trim();
      if (q && (!lengthInput.value || !widthInput.value)) {
        try {
          const res = await fetch(`${API_BASE}/api/vehicles/lookup?name=${encodeURIComponent(q)}`);
          if (res.ok) {
            const data = await res.json();
            if (data.vehicle) {
              const v = data.vehicle;
              lengthInput.value = v.length_m;
              widthInput.value = v.width_m;
              if (clearanceInput && v.clearance_m) clearanceInput.value = v.clearance_m;
              if (autofillIndicator && autofillText) {
                autofillText.textContent = `⚡ ${v.name}: Length ${v.length_m}m × Width ${v.width_m}m auto-detected from vehicle dataset`;
                autofillIndicator.classList.remove('hidden');
              }
            }
          }
        } catch (e) {}
      }
    });
  }

  // Submit Registration
  if (formRegister) {
    formRegister.addEventListener('submit', async (e) => {
      e.preventDefault();
      const payload = {
        name: nameInput.value.trim(),
        email: emailInput.value.trim(),
        password: passInput.value,
        phone: phoneInput.value.trim(),
        bike_model: modelInput.value.trim(),
        length_m: parseFloat(lengthInput.value) || 2.14,
        width_m: parseFloat(widthInput.value) || 0.84,
        clearance_m: parseFloat(clearanceInput.value) || 0.20,
        license_plate: plateInput.value.trim().toUpperCase() || 'MH-02-AB-1234'
      };

      try {
        const res = await fetch(`${API_BASE}/api/auth/register`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
        const result = await res.json();
        if (!res.ok) {
          alert(result.detail || 'Registration failed.');
          return;
        }

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
        showToast(`✅ Registered successfully: ${profile.bikeModel}`);
        refreshUserGPS();
        if (state.currentTab === 'cv-lab') runCVAnalysis();
      } catch (err) {
        console.error('Registration error:', err);
        alert('Could not connect to registration server.');
      }
    });
  }

  // Submit Login
  if (formLogin) {
    formLogin.addEventListener('submit', async (e) => {
      e.preventDefault();
      const payload = {
        email: loginEmail.value.trim(),
        password: loginPass.value
      };

      try {
        const res = await fetch(`${API_BASE}/api/auth/login`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
        const result = await res.json();
        if (!res.ok) {
          alert(result.detail || 'Login failed. Please check credentials.');
          return;
        }

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
        showToast(`👋 Welcome back, ${profile.name}!`);
        refreshUserGPS();
        if (state.currentTab === 'cv-lab') runCVAnalysis();
      } catch (err) {
        console.error('Login error:', err);
        alert('Could not connect to login server.');
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
  try {
    const response = await fetch(`${API_BASE}/api/parking/nearby?lat=${state.userLocation[0]}&lng=${state.userLocation[1]}`);
    const lots = await response.json();
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
