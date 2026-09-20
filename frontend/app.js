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

// Global Application State
const state = {
  currentTab: 'cv-lab',
  currentScenario: 'scenario_1_aerial',
  currentVehicle: 'suv',
  customDimensions: { length: 4.6, width: 1.9 },
  customFile: null,
  activeLot: null,
  flowStep: 1,
  map: null,
  mapMarkers: [],
  routeLine: null,
  analysisResult: null,
  vehiclesData: {
    suv: { name: 'SUV / 4x4', icon: '🚙', dims: '4.6 × 1.9m' },
    sedan: { name: 'Sedan', icon: '🚗', dims: '4.4 × 1.8m' },
    compact: { name: 'Compact', icon: '🚘', dims: '3.8 × 1.7m' },
    bike: { name: 'Motorcycle', icon: '🏍️', dims: '2.0 × 0.8m' }
  }
};

// Initialize Application on DOM Ready
document.addEventListener('DOMContentLoaded', () => {
  initTabs();
  initVehicleSelectors();
  initScenarioControls();
  initCVControls();
  initFlowStepper();
  
  // Initial CV pipeline execution
  runCVAnalysis();
});

// ==========================================================================
// TABS NAVIGATION
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

  const configApiBtn = document.getElementById('btn-config-api');
  if (configApiBtn) {
    configApiBtn.addEventListener('click', () => {
      const current = localStorage.getItem('PARKVISION_BACKEND_URL') || API_BASE || 'http://localhost:8000';
      const input = prompt(
        'Enter your Render / Cloud Backend URL:\n(e.g., https://smart-parking-cv.onrender.com or http://localhost:8000)\n\nLeave blank to use default relative URL.',
        current
      );
      if (input !== null) {
        if (input.trim()) {
          localStorage.setItem('PARKVISION_BACKEND_URL', input.trim());
        } else {
          localStorage.removeItem('PARKVISION_BACKEND_URL');
        }
        API_BASE = getApiBase();
        alert(`API server set to: ${API_BASE || '(Relative root)'}`);
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
  } else if (tabId === 'driver-flow') {
    renderFlowStage(state.flowStep);
  }
}

// ==========================================================================
// VEHICLE SPECIFICATION SELECTION (Step 5)
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
  toggleCustomBtn.addEventListener('click', () => {
    customContainer.classList.toggle('hidden');
  });

  const lenInput = document.getElementById('custom-length');
  const widInput = document.getElementById('custom-width');
  [lenInput, widInput].forEach(input => {
    input.addEventListener('change', () => {
      state.customDimensions.length = parseFloat(lenInput.value) || 4.6;
      state.customDimensions.width = parseFloat(widInput.value) || 1.9;
      runCVAnalysis();
    });
  });
}

function setVehicle(vehKey) {
  state.currentVehicle = vehKey;
  const vInfo = state.vehiclesData[vehKey];
  if (vInfo) {
    document.getElementById('nav-veh-icon').textContent = vInfo.icon;
    document.getElementById('nav-veh-name').textContent = vInfo.name;
    document.getElementById('nav-veh-dims').textContent = `(${vInfo.dims})`;
  }
  // Re-run CV analysis to refresh suitability calculations
  runCVAnalysis();
}

// ==========================================================================
// SCENARIO & UPLOAD CONTROLS (Step 3)
// ==========================================================================
function initScenarioControls() {
  const scenarioSelect = document.getElementById('scenario-select');
  scenarioSelect.addEventListener('change', (e) => {
    state.currentScenario = e.target.value;
    state.customFile = null;
    runCVAnalysis();
  });

  const fileInput = document.getElementById('file-input');
  fileInput.addEventListener('change', (e) => {
    if (e.target.files && e.target.files[0]) {
      state.customFile = e.target.files[0];
      runCVAnalysis();
    }
  });

  const dropArea = document.getElementById('drop-area');
  ['dragenter', 'dragover'].forEach(eventName => {
    dropArea.addEventListener(eventName, (e) => {
      e.preventDefault();
      dropArea.classList.add('drag-active');
    }, false);
  });
  ['dragleave', 'drop'].forEach(eventName => {
    dropArea.addEventListener(eventName, (e) => {
      e.preventDefault();
      dropArea.classList.remove('drag-active');
    }, false);
  });
  dropArea.addEventListener('drop', (e) => {
    const dt = e.dataTransfer;
    if (dt.files && dt.files[0]) {
      state.customFile = dt.files[0];
      runCVAnalysis();
    }
  });
}

function initCVControls() {
  const runBtn = document.getElementById('run-cv-btn');
  runBtn.addEventListener('click', () => runCVAnalysis());

  const resetBtn = document.getElementById('btn-reset-view');
  resetBtn.addEventListener('click', () => {
    state.customFile = null;
    document.getElementById('scenario-select').value = 'scenario_1_aerial';
    state.currentScenario = 'scenario_1_aerial';
    runCVAnalysis();
  });

  const fullBtn = document.getElementById('btn-fullscreen');
  fullBtn.addEventListener('click', () => {
    const imgWrapper = document.getElementById('image-wrapper');
    if (!document.fullscreenElement) {
      imgWrapper.requestFullscreen().catch(err => alert(err.message));
    } else {
      document.exitFullscreen();
    }
  });

  // Layer toggles
  document.getElementById('toggle-bev-view').addEventListener('change', (e) => {
    const bevCard = document.getElementById('bev-container');
    bevCard.style.display = e.target.checked ? 'flex' : 'none';
  });
}

// ==========================================================================
// CORE COMPUTER VISION INFERENCE CALL (Step 2, 4, 5, 7, 8)
// ==========================================================================
async function runCVAnalysis() {
  const loadingOverlay = document.getElementById('cv-loading');
  loadingOverlay.classList.remove('hidden');

  try {
    const formData = new FormData();
    formData.append('vehicle_type', state.currentVehicle);
    formData.append('custom_length', state.customDimensions.length);
    formData.append('custom_width', state.customDimensions.width);

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
    renderCVResults(data);
  } catch (error) {
    console.error('Error running CV analysis:', error);
  } finally {
    loadingOverlay.classList.add('hidden');
  }
}

function renderCVResults(data) {
  if (!data || !data.success) return;

  // 1. Update Main Display Images
  const mainImg = document.getElementById('cv-main-image');
  mainImg.src = data.annotated_image;

  const bevImg = document.getElementById('cv-bev-image');
  if (data.bev_image) {
    bevImg.src = data.bev_image;
    document.getElementById('bev-container').style.display = 'flex';
  } else {
    document.getElementById('bev-container').style.display = 'none';
  }

  // 2. Update Top HUD Counters
  document.getElementById('hud-total').textContent = data.summary.total_slots;
  document.getElementById('hud-avail').textContent = data.summary.available;
  document.getElementById('hud-occ').textContent = data.summary.occupied;
  document.getElementById('hud-blocked').textContent = data.summary.blocked;

  const fitCount = data.slots.filter(s => s.status === 'AVAILABLE' && s.vehicle_fit && s.vehicle_fit.is_suitable).length;
  const fitTag = document.getElementById('hud-fit-tag');
  fitTag.textContent = `${fitCount} Space${fitCount === 1 ? '' : 's'} Fit ${data.vehicle.name}`;

  // 3. Update Step 8 Recommendation Card
  const recCard = document.getElementById('recommendation-card');
  const recSlot = data.recommended_slot;
  if (recSlot) {
    document.getElementById('rec-slot-title').textContent = recSlot.label || `Bay ${recSlot.id}`;
    document.getElementById('rec-status-pill').textContent = `${recSlot.status_icon} ${recSlot.status}`;
    document.getElementById('rec-status-pill').className = `rec-pill green`;
    
    document.getElementById('rec-rule-pill').textContent = recSlot.rules.rule_badge;
    document.getElementById('rec-dims-text').textContent = `${recSlot.metrics.width_m}m (W) × ${recSlot.metrics.length_m}m (L)`;
    document.getElementById('rec-guidance-text').textContent = recSlot.vehicle_fit.message;
    recCard.style.display = 'flex';
  } else {
    document.getElementById('rec-slot-title').textContent = 'No Spaces Fit';
    document.getElementById('rec-status-pill').textContent = '🔴 Full / Too Small';
    document.getElementById('rec-status-pill').className = `rec-pill red`;
    document.getElementById('rec-dims-text').textContent = '—';
    document.getElementById('rec-guidance-text').textContent = `All spaces in this camera view are either occupied, blocked, or too small for your ${data.vehicle.name}.`;
  }

  // 4. Populate Detailed Slots Breakdown List
  const slotsList = document.getElementById('slots-list-container');
  slotsList.innerHTML = '';
  data.slots.forEach(s => {
    const card = document.createElement('div');
    card.className = 'slot-item-card';

    let badgeClass = 'badge-avail';
    if (s.status === 'OCCUPIED') badgeClass = 'badge-occ';
    if (s.status === 'BLOCKED') badgeClass = 'badge-block';

    const fitNote = s.status === 'AVAILABLE' ? s.vehicle_fit.fit_badge : (s.occupied_by || s.blocked_reason || '—');

    card.innerHTML = `
      <div class="slot-item-info">
        <div class="slot-card-header">
          <span class="slot-item-title">${s.label}</span>
          <span class="slot-item-dims">${s.metrics.width_m}×${s.metrics.length_m}m</span>
        </div>
        <div class="slot-item-desc">${fitNote} • ${s.rules.rule_badge}</div>
      </div>
      <div class="slot-item-status-badge ${badgeClass}">
        ${s.status_icon} ${s.status}
      </div>
    `;
    slotsList.appendChild(card);
  });

  // 5. Populate Diagnostics (YOLO Detections & Homography Matrix)
  const detList = document.getElementById('diag-detections-list');
  detList.innerHTML = '';
  data.detections.slice(0, 10).forEach(d => {
    const row = document.createElement('div');
    row.className = 'diag-det-row';
    row.innerHTML = `
      <span>[${d.category.toUpperCase()}] <strong>${d.class_name}</strong></span>
      <span>${Math.round(d.confidence * 100)}%</span>
    `;
    detList.appendChild(row);
  });
  if (data.detections.length > 10) {
    const more = document.createElement('div');
    more.className = 'diag-det-row';
    more.textContent = `... and ${data.detections.length - 10} more detections`;
    detList.appendChild(more);
  }

  const matrixDisplay = document.getElementById('matrix-display');
  if (data.homography_matrix) {
    const formattedRows = data.homography_matrix.map(row => 
      `[ ${row.map(val => val.toExponential(3)).join('  ')} ]`
    ).join('\n');
    matrixDisplay.textContent = formattedRows;
  } else {
    matrixDisplay.textContent = 'Default Calibrated Metric Matrix';
  }
}

// ==========================================================================
// TAB 2: GPS MAP & NEARBY LOTS (Step 6)
// ==========================================================================
async function initOrRefreshMap() {
  if (!state.map) {
    const mapElement = document.getElementById('leaflet-map');
    if (!mapElement) return;

    // Center on downtown hub
    const centerPos = [37.7749, -122.4194];
    state.map = L.map('leaflet-map', {
      zoomControl: true
    }).setView(centerPos, 15);

    // Clean OpenStreetMap Tile Layer
    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '&copy; OpenStreetMap contributors',
      maxZoom: 19
    }).addTo(state.map);

    // User Location Pulse Marker
    const userIcon = L.divIcon({
      className: 'user-map-pin',
      html: `<div style="background:#3b82f6;width:20px;height:20px;border-radius:50%;border:3px solid white;box-shadow:0 0 15px #3b82f6;"></div>`,
      iconSize: [20, 20],
      iconAnchor: [10, 10]
    });
    L.marker(centerPos, { icon: userIcon }).addTo(state.map).bindPopup('<strong>📍 Your Vehicle Location</strong><br>GPS Active').openPopup();

    // Fetch and place parking lot facilities
    loadMapParkingLots(centerPos);
  } else {
    state.map.invalidateSize();
  }
}

async function loadMapParkingLots(userPos) {
  try {
    const response = await fetch(`${API_BASE}/api/parking/locations`);
    const lots = await response.json();

    const lotsList = document.getElementById('nearby-lots-list');
    lotsList.innerHTML = '';

    lots.forEach((lot, idx) => {
      // Add Marker
      const lotIcon = L.divIcon({
        className: 'lot-map-pin',
        html: `<div style="background:${lot.live_available > 0 ? '#10b981' : '#ef4444'};color:white;font-weight:bold;font-size:11px;padding:3px 7px;border-radius:12px;border:2px solid white;box-shadow:0 2px 10px rgba(0,0,0,0.5);">${lot.live_available} 🅿️</div>`,
        iconSize: [40, 24],
        iconAnchor: [20, 12]
      });

      const marker = L.marker([lot.latitude, lot.longitude], { icon: lotIcon }).addTo(state.map);
      marker.bindPopup(`<strong>${lot.name}</strong><br>${lot.live_available} Spaces Free<br>Rate: ${lot.price_per_hr}/hr`);
      
      marker.on('click', () => selectParkingLot(lot, userPos));

      // Add Sidebar Card
      const card = document.createElement('div');
      card.className = `lot-card ${idx === 0 ? 'active' : ''}`;
      card.innerHTML = `
        <div class="lot-header">
          <span class="lot-name">${lot.name}</span>
          <span class="lot-distance">${lot.distance_km} km</span>
        </div>
        <div class="lot-meta">
          <span>${lot.type}</span>
          <span class="lot-avail-tag">${lot.live_available} Spaces Available</span>
          <span>${lot.price_per_hr}/hr</span>
        </div>
        <div class="lot-actions">
          <button class="btn-nav-lot" onclick="event.stopPropagation(); triggerNavigation('${lot.id}')">
            🧭 Navigate & Scan
          </button>
        </div>
      `;
      card.addEventListener('click', () => selectParkingLot(lot, userPos));
      lotsList.appendChild(card);

      // Select first lot by default
      if (idx === 0) {
        selectParkingLot(lot, userPos);
      }
    });
  } catch (err) {
    console.error('Failed to load GPS lots:', err);
  }
}

function selectParkingLot(lot, userPos) {
  state.activeLot = lot;

  // Highlight card
  document.querySelectorAll('.lot-card').forEach(c => c.classList.remove('active'));

  // Update Route Polyline
  if (state.routeLine) {
    state.map.removeLayer(state.routeLine);
  }
  const routeCoords = [
    userPos || [37.7749, -122.4194],
    [lot.latitude, lot.longitude]
  ];
  state.routeLine = L.polyline(routeCoords, {
    color: '#3b82f6',
    weight: 4,
    dashArray: '8, 8',
    opacity: 0.85
  }).addTo(state.map);

  // Update Bottom Route Bar
  const routeCard = document.getElementById('map-route-card');
  document.getElementById('route-dest-name').textContent = lot.name;
  document.getElementById('route-dist').textContent = lot.distance_km;
  document.getElementById('route-time').textContent = Math.round(lot.distance_km * 3);
  document.getElementById('route-avail').textContent = `${lot.live_available} Spaces Free`;
  routeCard.classList.remove('hidden');

  // Wire Arrive Button
  const arriveBtn = document.getElementById('btn-arrive-simulate');
  arriveBtn.onclick = () => {
    // Switch to CV Lab and load this lot's camera scenario
    if (lot.scenario_key) {
      state.currentScenario = lot.scenario_key;
      document.getElementById('scenario-select').value = lot.scenario_key;
    }
    switchTab('cv-lab');
    runCVAnalysis();
  };
}

window.triggerNavigation = function(lotId) {
  const lot = GPS_PARKING_LOCATIONS_FALLBACK.find(l => l.id === lotId) || state.activeLot;
  if (lot && lot.scenario_key) {
    state.currentScenario = lot.scenario_key;
    document.getElementById('scenario-select').value = lot.scenario_key;
    switchTab('cv-lab');
    runCVAnalysis();
  }
};

const GPS_PARKING_LOCATIONS_FALLBACK = [
  { id: 'lot-1', name: 'Metro Grand Plaza Deck', scenario_key: 'scenario_1_aerial' },
  { id: 'lot-2', name: 'Civic Center Curbside Bays', scenario_key: 'scenario_2_driver' },
  { id: 'lot-3', name: 'Market Square Rooftop Deck', scenario_key: 'scenario_3_rooftop' },
  { id: 'lot-4', name: 'Harbor View Compact Bays', scenario_key: 'scenario_4_tight' }
];

// ==========================================================================
// TAB 3: FULL 8-STEP DRIVER FLOW SIMULATOR (Step 8)
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
  
  const stepContent = {
    1: {
      title: 'Step 1: Vehicle Details Specification',
      desc: 'Enter your vehicle profile and real-world dimensions to ensure parking spots fit with safe door clearances.',
      html: `
        <div style="display:flex;gap:1.5rem;align-items:center;flex-wrap:wrap;">
          <div style="font-size:3.5rem;">🚙</div>
          <div>
            <h4 style="color:#fff;font-size:1.2rem;margin-bottom:0.3rem;">Selected: ${state.vehiclesData[state.currentVehicle].name}</h4>
            <p style="color:#94a3b8;font-size:0.9rem;">Dimensions: <strong>${state.vehiclesData[state.currentVehicle].dims}</strong> | Min Clearance: <strong>0.3m</strong></p>
          </div>
        </div>
        <div style="margin-top:1.5rem;display:flex;gap:1rem;">
          <button class="action-btn glow-btn" style="max-width:260px;" onclick="setFlowStep(2)">Proceed to Step 2: GPS →</button>
        </div>
      `
    },
    2: {
      title: 'Step 2: Find Nearby Parking Location (GPS)',
      desc: 'GPS queries the nearest registered and public parking facilities based on live vacancy data.',
      html: `
        <div style="display:flex;gap:1rem;align-items:center;">
          <div style="font-size:3rem;">📍</div>
          <div>
            <h4 style="color:#fff;font-size:1.1rem;">Found: Metro Grand Plaza Deck (0.4 km away)</h4>
            <p style="color:#94a3b8;font-size:0.85rem;">18 Spaces Available • $4.50/hr • Registered Facility ✅</p>
          </div>
        </div>
        <div style="margin-top:1.5rem;display:flex;gap:1rem;">
          <button class="action-btn glow-btn" style="max-width:260px;" onclick="setFlowStep(3)">Start Navigation →</button>
        </div>
      `
    },
    3: {
      title: 'Step 3: Navigate & Reach Parking Lot',
      desc: 'Drive to the selected parking location. Turn-by-turn navigation guides you to the entrance.',
      html: `
        <div style="display:flex;gap:1rem;align-items:center;">
          <div style="font-size:3rem;">🚗💨</div>
          <div>
            <h4 style="color:#fff;font-size:1.1rem;">Navigating via Market Street...</h4>
            <p style="color:#94a3b8;font-size:0.85rem;">ETA: 2 mins • Turn right in 150 meters</p>
          </div>
        </div>
        <div style="margin-top:1.5rem;display:flex;gap:1rem;">
          <button class="action-btn glow-btn" style="max-width:260px;" onclick="setFlowStep(4)">Arrived Safely → Stop & Scan</button>
        </div>
      `
    },
    4: {
      title: 'Step 4: Smartphone Camera Scan Mode',
      desc: 'Mount phone on dashboard or hold forward to capture the parking row ahead.',
      html: `
        <div style="display:flex;gap:1rem;align-items:center;">
          <div style="font-size:3rem;">📱</div>
          <div>
            <h4 style="color:#fff;font-size:1.1rem;">Camera Feed Initialized (1080p 60fps)</h4>
            <p style="color:#94a3b8;font-size:0.85rem;">Scanning parking row with road plane perspective...</p>
          </div>
        </div>
        <div style="margin-top:1.5rem;display:flex;gap:1rem;">
          <button class="action-btn glow-btn" style="max-width:260px;" onclick="setFlowStep(5)">Run YOLO + Homography →</button>
        </div>
      `
    },
    5: {
      title: 'Step 5: YOLO Detection & Space Analysis (CV Core)',
      desc: 'Deep learning model detects all vehicles and obstacles. Camera homography rectifies perspective.',
      html: `
        <div style="display:flex;gap:1rem;align-items:center;">
          <div style="font-size:3rem;">🔬</div>
          <div>
            <h4 style="color:#fff;font-size:1.1rem;">YOLOv8 + 3×3 Projective Homography Active</h4>
            <p style="color:#94a3b8;font-size:0.85rem;">Detected: 4 Cars 🔴 | 1 Obstacle 🟡 | 2 Vacant Spaces 🟢</p>
          </div>
        </div>
        <div style="margin-top:1.5rem;display:flex;gap:1rem;">
          <button class="action-btn glow-btn" style="max-width:260px;" onclick="setFlowStep(6)">Check Vehicle Fit →</button>
        </div>
      `
    },
    6: {
      title: 'Step 6: Vehicle Space Fit Verification',
      desc: 'Calculates physical slot width & length in meters. Compares against your vehicle footprint.',
      html: `
        <div style="display:flex;gap:1rem;align-items:center;">
          <div style="font-size:3rem;">📐</div>
          <div>
            <h4 style="color:#fff;font-size:1.1rem;">Bay 3: 2.7m (W) × 5.5m (L)</h4>
            <p style="color:#34d399;font-size:0.85rem;font-weight:bold;">🟢 Optimal Fit: Vehicle requires 1.9m W. Safe clearance: +0.82m</p>
          </div>
        </div>
        <div style="margin-top:1.5rem;display:flex;gap:1rem;">
          <button class="action-btn glow-btn" style="max-width:260px;" onclick="setFlowStep(7)">Verify Parking Rules →</button>
        </div>
      `
    },
    7: {
      title: 'Step 7: Parking Rule & Zone Verification',
      desc: 'Verifies slot zone against municipal rules (Registered ✅ / Permitted ✅ / No Parking ❌).',
      html: `
        <div style="display:flex;gap:1rem;align-items:center;">
          <div style="font-size:3rem;">⚖️</div>
          <div>
            <h4 style="color:#fff;font-size:1.1rem;">Zone Status: Registered Commercial Facility ✅</h4>
            <p style="color:#94a3b8;font-size:0.85rem;">Authorized bay. No tow-away or hydrant restrictions detected.</p>
          </div>
        </div>
        <div style="margin-top:1.5rem;display:flex;gap:1rem;">
          <button class="action-btn glow-btn" style="max-width:260px;" onclick="setFlowStep(8)">Generate Recommendation →</button>
        </div>
      `
    },
    8: {
      title: 'Step 8: Final Smart Recommendation & Guidance',
      desc: 'System issues audio/visual recommendation guiding you directly into the optimal space.',
      html: `
        <div style="background:rgba(16,185,129,0.15);border:1px solid rgba(16,185,129,0.4);padding:1.5rem;border-radius:12px;">
          <h3 style="color:#34d399;font-size:1.4rem;margin-bottom:0.4rem;">★ PARK IN BAY 3 ★</h3>
          <p style="color:#fff;font-size:0.95rem;line-height:1.5;">
            🟢 Space Available & Legal<br>
            🚙 Optimal Fit for your SUV (2.7m width × 5.5m length)<br>
            ✨ Pull forward 12 meters and turn steering wheel 35° right.
          </p>
        </div>
        <div style="margin-top:1.5rem;display:flex;gap:1rem;">
          <button class="action-btn glow-btn" style="max-width:260px;" onclick="switchTab('cv-lab')">Open Live CV Inspector 🔬</button>
          <button class="action-btn" style="max-width:200px;background:rgba(255,255,255,0.1);color:#fff;" onclick="setFlowStep(1)">Restart Flow ↺</button>
        </div>
      `
    }
  };

  const current = stepContent[stepNum];
  body.innerHTML = `
    <h3 style="color:#fff;font-family:var(--font-display);font-size:1.35rem;margin-bottom:0.5rem;">${current.title}</h3>
    <p style="color:#94a3b8;font-size:0.9rem;margin-bottom:1.5rem;">${current.desc}</p>
    ${current.html}
  `;
}
