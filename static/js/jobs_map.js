(function () {
    'use strict';

    var STORAGE_KEY = 'hivefind.mapPrefs';
    var DEFAULT_CENTER = [33.7756, -84.3963];
    var DEFAULT_ZOOM = 11;

    var scriptTag = document.currentScript;
    var jobsUrl = scriptTag.getAttribute('data-jobs-url');

    var els = {
        useLocation: document.getElementById('use-location'),
        setLocation: document.getElementById('set-location'),
        manualLat: document.getElementById('manual-lat'),
        manualLng: document.getElementById('manual-lng'),
        locationStatus: document.getElementById('location-status'),
        radiusSlider: document.getElementById('radius-slider'),
        radiusValue: document.getElementById('radius-value'),
        filterEnabled: document.getElementById('filter-enabled'),
        rememberRadius: document.getElementById('remember-radius'),
        jobCount: document.getElementById('job-count')
    };

    var allJobs = [];
    var jobMarkers = [];
    var userLocation = null;
    var userMarker = null;
    var radiusCircle = null;

    var map = L.map('map').setView(DEFAULT_CENTER, DEFAULT_ZOOM);
    var esriLightGray = 'https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Light_Gray_Base/MapServer/tile/{z}/{y}/{x}';
    var esriLightGrayLabels = 'https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Light_Gray_Reference/MapServer/tile/{z}/{y}/{x}';
    L.tileLayer(esriLightGray, {
        maxZoom: 16,
        attribution: 'Tiles &copy; Esri &mdash; Esri, DeLorme, NAVTEQ'
    }).addTo(map);
    L.tileLayer(esriLightGrayLabels, { maxZoom: 16 }).addTo(map);

    function loadPrefs() {
        try {
            return JSON.parse(localStorage.getItem(STORAGE_KEY)) || {};
        } catch (e) {
            return {};
        }
    }

    function savePrefs(prefs) {
        try {
            localStorage.setItem(STORAGE_KEY, JSON.stringify(prefs));
        } catch (e) {
            return;
        }
    }

    function distanceMiles(lat1, lng1, lat2, lng2) {
        var R = 3958.8;
        var toRad = function (d) { return (d * Math.PI) / 180; };
        var dLat = toRad(lat2 - lat1);
        var dLng = toRad(lng2 - lng1);
        var a = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
            Math.cos(toRad(lat1)) * Math.cos(toRad(lat2)) *
            Math.sin(dLng / 2) * Math.sin(dLng / 2);
        return R * (2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a)));
    }

    function popupHtml(job) {
        var parts = ['<strong>' + escapeHtml(job.title) + '</strong>',
            escapeHtml(job.company)];
        var place = [job.city, job.state].filter(Boolean).join(', ');
        if (job.address) { parts.push(escapeHtml(job.address)); }
        if (place) { parts.push(escapeHtml(place)); }
        if (job.is_remote) { parts.push('<em>Remote friendly</em>'); }
        parts.push('Salary: ' + escapeHtml(job.salary));
        return '<div class="job-popup">' + parts.join('<br>') + '</div>';
    }

    function escapeHtml(value) {
        var div = document.createElement('div');
        div.textContent = value == null ? '' : String(value);
        return div.innerHTML;
    }

    function renderMarkers() {
        jobMarkers.forEach(function (m) { map.removeLayer(m.marker); });
        jobMarkers = [];
        allJobs.forEach(function (job) {
            var marker = L.marker([job.latitude, job.longitude]).bindPopup(popupHtml(job));
            jobMarkers.push({ job: job, marker: marker });
        });
        applyFilter();
    }

    function applyFilter() {
        var radius = parseInt(els.radiusSlider.value, 10);
        var filtering = els.filterEnabled.checked && userLocation !== null;
        var visible = 0;

        jobMarkers.forEach(function (entry) {
            var show = true;
            if (filtering) {
                var d = distanceMiles(
                    userLocation.lat, userLocation.lng,
                    entry.job.latitude, entry.job.longitude
                );
                show = d <= radius;
            }
            if (show) {
                if (!map.hasLayer(entry.marker)) { entry.marker.addTo(map); }
                visible += 1;
            } else if (map.hasLayer(entry.marker)) {
                map.removeLayer(entry.marker);
            }
        });

        drawRadiusCircle(filtering ? radius : null);
        updateCount(visible, filtering);
    }

    function drawRadiusCircle(radiusMiles) {
        if (radiusCircle) { map.removeLayer(radiusCircle); radiusCircle = null; }
        if (radiusMiles === null || !userLocation) { return; }
        radiusCircle = L.circle([userLocation.lat, userLocation.lng], {
            radius: radiusMiles * 1609.34,
            color: '#003057', weight: 1, fillColor: '#b3a369', fillOpacity: 0.12
        }).addTo(map);
    }

    function updateCount(visible, filtering) {
        if (filtering) {
            els.jobCount.textContent =
                visible + ' of ' + allJobs.length + ' jobs within ' +
                els.radiusSlider.value + ' miles';
        } else {
            els.jobCount.textContent = 'Showing all ' + allJobs.length + ' jobs';
        }
    }

    function setUserLocation(lat, lng, label) {
        userLocation = { lat: lat, lng: lng };
        if (userMarker) { map.removeLayer(userMarker); }
        userMarker = L.marker([lat, lng], {
            icon: L.divIcon({ className: 'user-pin', html: '◉', iconSize: [24, 24] })
        }).addTo(map).bindPopup('You are here');
        els.locationStatus.textContent = label ||
            ('Location set: ' + lat.toFixed(4) + ', ' + lng.toFixed(4));
        map.setView([lat, lng], 11);
        persist();
        applyFilter();
    }

    function persist() {
        if (!els.rememberRadius.checked) { return; }
        savePrefs({
            radius: parseInt(els.radiusSlider.value, 10),
            filterEnabled: els.filterEnabled.checked,
            location: userLocation
        });
    }

    els.radiusSlider.addEventListener('input', function () {
        els.radiusValue.textContent = els.radiusSlider.value;
        persist();
        applyFilter();
    });

    els.filterEnabled.addEventListener('change', function () {
        if (els.filterEnabled.checked && !userLocation) {
            els.locationStatus.textContent =
                'Set your location first to filter by distance.';
            els.filterEnabled.checked = false;
            return;
        }
        persist();
        applyFilter();
    });

    els.rememberRadius.addEventListener('change', function () {
        if (els.rememberRadius.checked) {
            persist();
        } else {
            savePrefs({});
        }
    });

    els.useLocation.addEventListener('click', function () {
        if (!navigator.geolocation) {
            els.locationStatus.textContent = 'Geolocation is not supported by your browser.';
            return;
        }
        els.locationStatus.textContent = 'Locating…';
        navigator.geolocation.getCurrentPosition(
            function (pos) {
                setUserLocation(pos.coords.latitude, pos.coords.longitude, 'Using your current location');
            },
            function () {
                els.locationStatus.textContent =
                    'Could not get your location. Enter it manually below.';
            }
        );
    });

    els.setLocation.addEventListener('click', function () {
        var lat = parseFloat(els.manualLat.value);
        var lng = parseFloat(els.manualLng.value);
        if (isNaN(lat) || isNaN(lng)) {
            els.locationStatus.textContent = 'Enter a valid latitude and longitude.';
            return;
        }
        setUserLocation(lat, lng);
    });

    function restorePrefs() {
        var prefs = loadPrefs();
        if (typeof prefs.radius === 'number') {
            els.radiusSlider.value = prefs.radius;
            els.radiusValue.textContent = prefs.radius;
            els.rememberRadius.checked = true;
        }
        if (prefs.location) {
            els.filterEnabled.checked = !!prefs.filterEnabled;
            setUserLocation(prefs.location.lat, prefs.location.lng,
                'Restored your saved commute location');
        }
    }

    function loadJobs() {
        fetch(jobsUrl)
            .then(function (r) { return r.json(); })
            .then(function (data) {
                allJobs = data.jobs || [];
                renderMarkers();
                if (allJobs.length === 0) {
                    els.jobCount.textContent =
                        'No jobs yet. Run "python manage.py seed_jobs" to add samples.';
                }
            })
            .catch(function () {
                els.jobCount.textContent = 'Could not load jobs.';
            });
    }

    restorePrefs();
    loadJobs();
})();
