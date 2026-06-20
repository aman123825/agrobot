/**
 * Agrobot Remote Control - Client Application
 * Vanilla JavaScript, no frameworks.
 */

(function () {
    "use strict";

    // =========================================================================
    // WebSocket Connection
    // =========================================================================

    let ws = null;
    let reconnectAttempts = 0;
    const MAX_RECONNECT_DELAY = 30000;

    function getWsUrl() {
        const proto = window.location.protocol === "https:" ? "wss:" : "ws:";
        return proto + "//" + window.location.host + "/ws";
    }

    function connectWebSocket() {
        if (ws && (ws.readyState === WebSocket.OPEN || ws.readyState === WebSocket.CONNECTING)) {
            return;
        }

        ws = new WebSocket(getWsUrl());

        ws.onopen = function () {
            reconnectAttempts = 0;
            setConnectionStatus("connected", "Connected");
        };

        ws.onmessage = function (event) {
            try {
                const msg = JSON.parse(event.data);
                handleServerMessage(msg);
            } catch (e) {
                // Ignore non-JSON messages
            }
        };

        ws.onclose = function () {
            setConnectionStatus("disconnected", "Disconnected");
            scheduleReconnect();
        };

        ws.onerror = function () {
            setConnectionStatus("disconnected", "Error");
        };
    }

    function scheduleReconnect() {
        const delay = Math.min(1000 * Math.pow(2, reconnectAttempts), MAX_RECONNECT_DELAY);
        reconnectAttempts++;
        setConnectionStatus("warning", "Reconnecting...");
        setTimeout(connectWebSocket, delay);
    }

    function sendWsMessage(msg) {
        if (ws && ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify(msg));
        }
    }

    function setConnectionStatus(state, text) {
        const led = document.getElementById("status-led");
        const label = document.getElementById("status-text");
        led.className = "status-led " + state;
        label.textContent = text;
    }

    // =========================================================================
    // Server Message Handler
    // =========================================================================

    function handleServerMessage(msg) {
        switch (msg.type) {
            case "telemetry":
                updateTelemetry(msg.data);
                break;
            case "mission_status":
                updateMissionStatus(msg.data);
                break;
            case "pong":
                // Heartbeat response
                break;
        }
    }

    // =========================================================================
    // Telemetry Display
    // =========================================================================

    function updateTelemetry(data) {
        if (data.battery_pct !== undefined) {
            document.getElementById("telem-battery").textContent = data.battery_pct + "%";
        }
        if (data.lat !== undefined) {
            document.getElementById("telem-lat").textContent = data.lat.toFixed(6);
        }
        if (data.lng !== undefined) {
            document.getElementById("telem-lng").textContent = data.lng.toFixed(6);
        }
        if (data.speed !== undefined) {
            document.getElementById("telem-speed").textContent = data.speed.toFixed(2) + " m/s";
        }
        if (data.mode !== undefined) {
            document.getElementById("telem-mode").textContent = data.mode;
        }
        if (data.npk) {
            var n = data.npk.n || 0;
            var p = data.npk.p || 0;
            var k = data.npk.k || 0;
            document.getElementById("telem-npk").textContent = n + " / " + p + " / " + k;
        }
    }

    function updateMissionStatus(data) {
        // Update current mission indicator if needed
        if (data && data.current) {
            var items = document.querySelectorAll(".mission-item");
            items.forEach(function (item) {
                var idEl = item.querySelector(".mission-id");
                if (idEl && idEl.textContent === data.current.id) {
                    var badge = item.querySelector(".status-badge");
                    if (badge) {
                        badge.className = "status-badge active";
                        badge.textContent = "active";
                    }
                }
            });
        }
    }

    // =========================================================================
    // Virtual Joystick
    // =========================================================================

    var joystickArea = null;
    var joystickKnob = null;
    var isDragging = false;
    var lastCommand = "";
    var areaRect = null;

    function initJoystick() {
        joystickArea = document.getElementById("joystick-area");
        joystickKnob = document.getElementById("joystick-knob");

        // Mouse events
        joystickArea.addEventListener("mousedown", onJoystickStart);
        document.addEventListener("mousemove", onJoystickMove);
        document.addEventListener("mouseup", onJoystickEnd);

        // Touch events
        joystickArea.addEventListener("touchstart", onJoystickTouchStart, { passive: false });
        document.addEventListener("touchmove", onJoystickTouchMove, { passive: false });
        document.addEventListener("touchend", onJoystickEnd);

        // Stop button
        document.getElementById("btn-stop").addEventListener("click", function () {
            sendDriveCommand("STOP");
            resetKnob();
        });

        // PWM slider
        var pwmSlider = document.getElementById("pwm-slider");
        var pwmValue = document.getElementById("pwm-value");
        pwmSlider.addEventListener("input", function () {
            pwmValue.textContent = pwmSlider.value;
        });
    }

    function onJoystickStart(e) {
        e.preventDefault();
        isDragging = true;
        areaRect = joystickArea.getBoundingClientRect();
        processJoystickPosition(e.clientX, e.clientY);
    }

    function onJoystickTouchStart(e) {
        e.preventDefault();
        isDragging = true;
        areaRect = joystickArea.getBoundingClientRect();
        var touch = e.touches[0];
        processJoystickPosition(touch.clientX, touch.clientY);
    }

    function onJoystickMove(e) {
        if (!isDragging) return;
        e.preventDefault();
        processJoystickPosition(e.clientX, e.clientY);
    }

    function onJoystickTouchMove(e) {
        if (!isDragging) return;
        e.preventDefault();
        var touch = e.touches[0];
        processJoystickPosition(touch.clientX, touch.clientY);
    }

    function onJoystickEnd() {
        if (!isDragging) return;
        isDragging = false;
        resetKnob();
        sendDriveCommand("STOP");
        lastCommand = "STOP";
    }

    function processJoystickPosition(clientX, clientY) {
        if (!areaRect) return;

        var centerX = areaRect.left + areaRect.width / 2;
        var centerY = areaRect.top + areaRect.height / 2;
        var radius = areaRect.width / 2;

        var dx = clientX - centerX;
        var dy = clientY - centerY;

        // Clamp to circle
        var dist = Math.sqrt(dx * dx + dy * dy);
        var maxDist = radius - 25; // Keep knob within area
        if (dist > maxDist) {
            dx = (dx / dist) * maxDist;
            dy = (dy / dist) * maxDist;
        }

        // Move knob visually
        joystickKnob.style.transform = "translate(calc(-50% + " + dx + "px), calc(-50% + " + dy + "px))";

        // Determine direction from angle
        var deadzone = maxDist * 0.2;
        if (dist < deadzone) {
            // In deadzone, don't send command
            return;
        }

        var angle = Math.atan2(-dy, dx) * (180 / Math.PI); // -dy because Y is inverted
        var cmd = angleToCommand(angle);

        if (cmd !== lastCommand) {
            lastCommand = cmd;
            sendDriveCommand(cmd);
        }
    }

    function angleToCommand(angle) {
        // angle: 0=right, 90=up, 180/-180=left, -90=down
        if (angle > 45 && angle <= 135) return "FWD";
        if (angle > -135 && angle <= -45) return "BACK";
        if (angle > 135 || angle <= -135) return "LEFT";
        return "RIGHT";
    }

    function resetKnob() {
        if (joystickKnob) {
            joystickKnob.style.transform = "translate(-50%, -50%)";
        }
    }

    function sendDriveCommand(cmd) {
        sendWsMessage({ type: "drive", cmd: cmd });
    }

    // =========================================================================
    // Mission Control
    // =========================================================================

    function initMissionControl() {
        var form = document.getElementById("mission-form");
        form.addEventListener("submit", function (e) {
            e.preventDefault();
            createMission();
        });

        // Initial load
        loadMissions();
    }

    function createMission() {
        var typeEl = document.getElementById("mission-type");
        var zoneEl = document.getElementById("mission-zone");
        var paramsEl = document.getElementById("mission-params");

        var missionType = typeEl.value;
        if (!missionType) return;

        var zone;
        try {
            zone = JSON.parse(zoneEl.value || "{}");
        } catch (e) {
            alert("Invalid zone JSON");
            return;
        }

        var params = {};
        if (paramsEl.value.trim()) {
            try {
                params = JSON.parse(paramsEl.value);
            } catch (e) {
                alert("Invalid params JSON");
                return;
            }
        }

        fetch("/api/missions", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ type: missionType, zone: zone, params: params }),
        })
            .then(function (res) { return res.json(); })
            .then(function (data) {
                if (data.error) {
                    alert("Error: " + data.error);
                } else {
                    typeEl.value = "";
                    zoneEl.value = "";
                    paramsEl.value = "";
                    loadMissions();
                }
            })
            .catch(function (err) {
                alert("Request failed: " + err.message);
            });
    }

    function loadMissions() {
        fetch("/api/missions")
            .then(function (res) { return res.json(); })
            .then(function (data) {
                renderMissions(data.missions || []);
            })
            .catch(function () {
                // Silently fail if server is unreachable
            });
    }

    function renderMissions(missions) {
        var container = document.getElementById("mission-list");

        if (!missions.length) {
            container.innerHTML = '<p class="empty-message">No missions</p>';
            return;
        }

        var html = "";
        missions.forEach(function (m) {
            var canCancel = m.status === "queued" || m.status === "active";
            html += '<div class="mission-item">';
            html += '  <div class="mission-info">';
            html += '    <span class="mission-id">' + escapeHtml(m.id) + '</span>';
            html += '    <span class="mission-type">' + escapeHtml(m.type) + '</span>';
            html += '  </div>';
            html += '  <span class="status-badge ' + escapeHtml(m.status) + '">' + escapeHtml(m.status) + '</span>';
            if (canCancel) {
                html += '  <button class="btn btn-cancel" data-id="' + escapeHtml(m.id) + '">Cancel</button>';
            }
            html += '</div>';
        });
        container.innerHTML = html;

        // Bind cancel buttons
        container.querySelectorAll(".btn-cancel").forEach(function (btn) {
            btn.addEventListener("click", function () {
                cancelMission(btn.getAttribute("data-id"));
            });
        });
    }

    function cancelMission(id) {
        fetch("/api/missions/" + encodeURIComponent(id), { method: "DELETE" })
            .then(function (res) { return res.json(); })
            .then(function () { loadMissions(); })
            .catch(function () {});
    }

    // =========================================================================
    // Plant Database
    // =========================================================================

    var allPlants = {};

    function initPlantDB() {
        document.getElementById("btn-refresh-plants").addEventListener("click", loadPlants);
        document.getElementById("plant-filter").addEventListener("input", filterPlants);
        loadPlants();
    }

    function loadPlants() {
        fetch("/api/plants")
            .then(function (res) { return res.json(); })
            .then(function (data) {
                allPlants = data.plants || {};
                renderPlants(allPlants);
            })
            .catch(function () {});
    }

    function filterPlants() {
        var query = document.getElementById("plant-filter").value.toLowerCase();
        if (!query) {
            renderPlants(allPlants);
            return;
        }
        var filtered = {};
        Object.keys(allPlants).forEach(function (id) {
            var plant = allPlants[id];
            var lastObs = plant.observations && plant.observations.length
                ? plant.observations[plant.observations.length - 1]
                : null;
            var searchStr = id.toLowerCase();
            if (lastObs && lastObs.disease_class) {
                searchStr += " " + lastObs.disease_class.toLowerCase();
            }
            if (searchStr.indexOf(query) !== -1) {
                filtered[id] = plant;
            }
        });
        renderPlants(filtered);
    }

    function renderPlants(plants) {
        var container = document.getElementById("plant-list");
        var ids = Object.keys(plants);

        if (!ids.length) {
            container.innerHTML = '<p class="empty-message">No plants tracked</p>';
            return;
        }

        var html = "";
        ids.forEach(function (id) {
            var p = plants[id];
            var lastObs = p.observations && p.observations.length
                ? p.observations[p.observations.length - 1]
                : null;
            var healthText = lastObs
                ? lastObs.disease_class + " (" + (lastObs.confidence * 100).toFixed(0) + "%)"
                : "No observations";

            html += '<div class="plant-item">';
            html += '  <div class="plant-id">' + escapeHtml(id) + '</div>';
            html += '  <div class="plant-coords">Lat: ' + p.lat.toFixed(6) + ', Lng: ' + p.lng.toFixed(6) + '</div>';
            html += '  <div class="plant-health">Health: ' + escapeHtml(healthText) + '</div>';
            html += '  <div class="plant-coords">Observations: ' + (p.observations ? p.observations.length : 0) + '</div>';
            html += '</div>';
        });
        container.innerHTML = html;
    }

    // =========================================================================
    // Camera Feed
    // =========================================================================

    function initCamera() {
        var img = document.getElementById("camera-feed");
        var placeholder = document.getElementById("camera-placeholder");

        // Attempt MJPEG stream
        img.src = "/stream";
        img.onload = function () {
            img.classList.add("active");
            placeholder.style.display = "none";
        };
        img.onerror = function () {
            // Stream not available, try periodic JPEG
            img.classList.remove("active");
            placeholder.style.display = "flex";
            startPeriodicCapture(img, placeholder);
        };
    }

    function startPeriodicCapture(img, placeholder) {
        var interval = setInterval(function () {
            var testImg = new Image();
            testImg.onload = function () {
                img.src = testImg.src;
                img.classList.add("active");
                placeholder.style.display = "none";
            };
            testImg.onerror = function () {
                // Still not available
            };
            testImg.src = "/capture?t=" + Date.now();
        }, 5000);
    }

    // =========================================================================
    // Utilities
    // =========================================================================

    function escapeHtml(str) {
        var div = document.createElement("div");
        div.textContent = str || "";
        return div.innerHTML;
    }

    // =========================================================================
    // Initialization
    // =========================================================================

    function init() {
        connectWebSocket();
        initJoystick();
        initMissionControl();
        initPlantDB();
        initCamera();

        // Periodic mission refresh
        setInterval(loadMissions, 10000);
    }

    // Start when DOM is ready
    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", init);
    } else {
        init();
    }
})();
