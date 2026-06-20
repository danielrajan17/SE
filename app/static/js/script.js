/**
 * script.js — CycloneOPS PRO Dashboard Logic
 * PyTorch Model + Live General Weather (OWM) + Forecast Animation
 */

// --- 1. OPENWEATHERMAP API KEY ---
// Paste your copied key here (e.g., "8d4f..."). Wait 15 mins for it to activate!
const OWM_API_KEY = "a5ffaf9c7e1169b726a7c026d28ac071"; 

// ── LEAFLET MAP ───────────────────────────────────────────
const map = L.map("map", {
  center: [12, 82],
  zoom: 5,
  zoomControl: false,
  attributionControl: false,
});

L.tileLayer(
  "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
  { maxZoom: 19 }
).addTo(map);

L.tileLayer(
  "https://server.arcgisonline.com/ArcGIS/rest/services/Reference/World_Boundaries_and_Places/MapServer/tile/{z}/{y}/{x}",
  { maxZoom: 19, opacity: 0.7 }
).addTo(map);

L.control.zoom({ position: "bottomright" }).addTo(map);

let clickMarker = null;
map.on("click", function (e) {
  const lat = e.latlng.lat.toFixed(2);
  const lon = e.latlng.lng.toFixed(2);
  document.getElementById("p_lat").value = lat;
  document.getElementById("p_lon").value = lon;
  placeClickMarker(lat, lon);
  setAlert("loading", "📍", `Position: ${lat}°N, ${lon}°E — Edit values & click PREDICT`);
});

function placeClickMarker(lat, lon) {
  if (clickMarker) map.removeLayer(clickMarker);
  const icon = L.divIcon({
    className: "",
    html: `<div style="width:16px;height:16px;border-radius:50%;background:#ffb400;border:2px solid #fff;box-shadow:0 0 10px rgba(255,180,0,.8)"></div>`,
    iconSize: [16, 16],
    iconAnchor: [8, 8],
  });
  clickMarker = L.marker([lat, lon], { icon }).addTo(map);
}

// ── WIND INIT ─────────────────────────────────────────────
if (typeof WindLayer !== "undefined") {
    WindLayer.init();
}

// ── ALERT HELPER ─────────────────────────────────────────
function setAlert(type, icon, msg) {
  const bar = document.getElementById("alertBar");
  if(bar) {
      bar.className = "alert-bar alert-" + type;
      document.getElementById("alertIcon").textContent = icon;
      document.getElementById("alertText").textContent = msg;
  }
}

// ── GENERAL LIVE WEATHER LAYERS (OWM) ────────────────────
const layerState = { wind: true, rain: false, cloud: false, temp: false };

// These pull LIVE data for the entire map (Not just the cyclone)
const weatherLayers = {
  rain: L.tileLayer(`https://tile.openweathermap.org/map/precipitation_new/{z}/{x}/{y}.png?appid=${OWM_API_KEY}`),
  cloud: L.tileLayer(`https://tile.openweathermap.org/map/clouds_new/{z}/{x}/{y}.png?appid=${OWM_API_KEY}`),
  temp: L.tileLayer(`https://tile.openweathermap.org/map/temp_new/{z}/{x}/{y}.png?appid=${OWM_API_KEY}`)
};

window.toggleLayer = function(name) {
  layerState[name] = !layerState[name];
  document.getElementById(name + "Btn").classList.toggle("active", layerState[name]);

  if (name === "wind") {
    if (typeof WindLayer !== "undefined") {
      WindLayer.setActive(layerState.wind);
      setAlert(
        layerState.wind ? "success" : "loading",
        layerState.wind ? "💨" : "⚠",
        layerState.wind ? "Wind layer active" : "Wind layer disabled"
      );
    }
  } else {
    // Check if API key is provided
    if (OWM_API_KEY === "YOUR_API_KEY_HERE" || OWM_API_KEY === "") {
        setAlert("error", "⚠", "Please add OpenWeatherMap API Key in script.js!");
        layerState[name] = false;
        document.getElementById(name + "Btn").classList.remove("active");
        return;
    }

    // Toggle General Map Layers
    if (layerState[name]) {
      weatherLayers[name].addTo(map);
      setAlert("success", "✔", `${name.charAt(0).toUpperCase() + name.slice(1)} map layer active!`);
    } else {
      map.removeLayer(weatherLayers[name]);
      setAlert("loading", "⏳", `${name.charAt(0).toUpperCase() + name.slice(1)} map layer removed.`);
    }
  }
};

// ── PANEL TOGGLE ─────────────────────────────────────────
let panelOpen = true;
window.togglePanel = function() {
  panelOpen = !panelOpen;
  document.getElementById("predictPanel").classList.toggle("hidden", !panelOpen);
  if (!panelOpen) document.getElementById("resultPopup").style.display = "none";
};

// ── TRAIN MODEL ──────────────────────────────────────────
window.trainModel = function() {
  setAlert("loading", "⟳", "Training PyTorch Neural Network...");
  fetch("/api/train", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ epochs: 200, lr: 0.001 }), 
  })
    .then((r) => r.json())
    .then((d) => {
      if (d.success) {
        setAlert("success", "✔", `Model trained successfully!`);
        loadMapData();
      } else {
        setAlert("error", "⚠", d.error || "Training failed");
      }
    });
};

// ── LOAD MAP DATA ─────────────────────────────────────────
let dataLayer = null;

function loadMapData() {
  fetch("/api/data")
    .then((r) => r.json())
    .then((d) => {
      if (d.error) return;
      if (dataLayer) map.removeLayer(dataLayer);
      dataLayer = L.geoJSON(d.geojson, {
        pointToLayer(feature, latlng) {
          return L.circleMarker(latlng, {
            radius: 3.5, fillColor: feature.properties.color, color: feature.properties.color,
            weight: 1, opacity: 0.6, fillOpacity: 0.5,
          });
        },
        onEachFeature(feature, layer) {
          const p = feature.properties;
          layer.bindTooltip(
            `<b style="color:${p.color}">${p.category}</b><br>${p.date} | MSW: ${p.msw} kt<br>Risk: ${p.risk}`,
            { className: "track-popup", sticky: true }
          );
        },
      }).addTo(map);
      setAlert("success", "✔", `Loaded ${d.stats.total} IMD records`);
    });
}

// ── FORECAST ANIMATION VARIABLES ──────────────────────────

// ── PREDICT (PyTorch) ─────────────────────────────────────
let predMarker = null;

window.runPredict = function() {
  const lat = parseFloat(document.getElementById("p_lat").value);
  const lon = parseFloat(document.getElementById("p_lon").value);
  const ecp = parseFloat(document.getElementById("p_ecp").value);
  const dp  = parseFloat(document.getElementById("p_dp").value);
  const msw = parseFloat(document.getElementById("p_msw").value);
  const ci  = parseFloat(document.getElementById("p_ci").value);

  if ([lat, lon, ecp, dp, msw, ci].some(isNaN)) {
    setAlert("error", "⚠", "Please fill all input fields!");
    return;
  }

  setAlert("loading", "⟳", "Running PyTorch prediction...");

  fetch("/api/predict", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ lat, lon, ci, ecp, dp, msw }),
  })
    .then((r) => r.json())
    .then((res) => {
      if (res.error) { setAlert("error", "⚠", res.error); return; }
      showResult(res, lat, lon, msw);
    });
};

function showResult(res, lat, lon, msw) {
  const color = res.color;

  if (predMarker) map.removeLayer(predMarker);
  const icon = L.divIcon({
    className: "",
    html: `<div style="position:relative;display:flex;align-items:center;justify-content:center;width:60px;height:60px">
      <div style="position:absolute;width:58px;height:58px;border-radius:50%;border:1.5px solid ${color};opacity:.35;animation:cycloneRing 1.5s infinite"></div>
      <div style="position:absolute;width:38px;height:38px;border-radius:50%;border:1.5px solid ${color};opacity:.6;animation:cycloneRing 1.5s .3s infinite"></div>
      <div style="width:20px;height:20px;border-radius:50%;background:${color};box-shadow:0 0 14px ${color}"></div>
      <style>@keyframes cycloneRing{0%{transform:scale(1)}50%{transform:scale(1.1)}100%{transform:scale(1)}}</style>
    </div>`,
    iconSize: [60, 60],
    iconAnchor: [30, 30],
  });

  let confText = typeof res.confidence === 'number' && res.confidence <= 1 
                 ? (res.confidence * 100).toFixed(1) + "%" 
                 : res.confidence;

  predMarker = L.marker([lat, lon], { icon })
    .addTo(map)
    .bindPopup(
      `<div style="font-family:'Share Tech Mono',monospace;font-size:12px;color:#fff;padding:4px">
        <b style="color:${color};font-size:18px">${res.category}</b><br>
        ${res.full_name}<br>Risk: ${res.risk}<br>
        MSW: ${msw} kt | ECP: ${document.getElementById("p_ecp").value} hPa<br>
        Confidence: ${confText}
      </div>`,
      { className: "track-popup" }
    )
    .openPopup();

  map.flyTo([lat, lon], Math.max(map.getZoom(), 6), { animate: true, duration: 1.2 });

  document.getElementById("resBadge").textContent   = res.category;
  document.getElementById("resBadge").style.color   = color;
  document.getElementById("resBadge").style.borderColor = color;
  document.getElementById("resBadge").style.background  = color + "18";
  document.getElementById("resName").textContent    = res.full_name;
  document.getElementById("resRisk").textContent    = `Risk: ${res.risk}`;
  document.getElementById("resRisk").style.color    = color;
  
  let confVal = parseFloat(confText);
  document.getElementById("rbConf").style.width     = (isNaN(confVal) ? 0 : confVal) + "%";
  document.getElementById("rvConf").textContent     = confText;
  
  document.getElementById("rsDist").textContent     = res.avg_dist ? parseFloat(res.avg_dist).toFixed(3) : "N/A";
  document.getElementById("rsMsw").textContent      = msw;
  
  document.getElementById("resultPopup").style.display = "block";

  if (typeof WindLayer !== "undefined") {
      WindLayer.setColor(color);
  }

  setAlert("success", "✔", `Predicted: ${res.category} — ${res.full_name} | Confidence: ${confText}`);
}

// ── CSV UPLOAD ────────────────────────────────────────────
window.uploadCSV = function(event) {
  const file = event.target.files[0];
  if (!file) return;
  setAlert("loading", "⟳", `Uploading ${file.name}...`);

  const fd = new FormData();
  fd.append("file", file);

  fetch("/api/upload", { method: "POST", body: fd })
    .then((r) => r.json())
    .then((d) => {
      if (d.success) {
        setAlert("success", "✔", `${d.message} — Re-training PyTorch model...`);
        setTimeout(window.trainModel, 600);
      } else {
        setAlert("error", "⚠", d.error || "Upload failed");
      }
    })
    .catch((e) => setAlert("error", "⚠", "Upload error: " + e.message));

  event.target.value = "";
};

// ── API SCAN ─────────────────────────────────────────────
window.apiScan = function() {
  setAlert("loading", "🛰", "Scanning IMD RSMC API...");
  fetch("/api/scan")
    .then((r) => r.json())
    .then((d) => setAlert("success", "✔", d.message))
    .catch(() => setAlert("error", "⚠", "API scan failed"));
};

// ── INIT ─────────────────────────────────────────────────
(function init() {
  fetch("/api/status")
    .then((r) => r.json())
    .then((d) => {
      if (d.model_ready) {
        setAlert("success", "✔", "PyTorch model ready");
        loadMapData();
      } else {
        setAlert("loading", "⟳", "No model found — training now...");
        window.trainModel();
      }
    })
    .catch(() => setAlert("error", "⚠", "Could not connect to server"));
})();