/* Ride booking map + fare estimate */
(function () {
  const mapEl = document.getElementById('map');
  if (!mapEl) return;

  // Default center: Urlabari
  const map = L.map('map').setView([26.6635, 87.6025], 13);
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap',
    maxZoom: 19,
  }).addTo(map);

  let pickupMarker = null;
  let destMarker = null;
  let routeLine = null;

  function setPickup(lat, lng, label) {
    document.getElementById('pickup-lat').value = lat;
    document.getElementById('pickup-lng').value = lng;
    document.getElementById('pickup-address').value = label || `${lat.toFixed(5)}, ${lng.toFixed(5)}`;
    if (pickupMarker) map.removeLayer(pickupMarker);
    pickupMarker = L.marker([lat, lng], { title: 'Pickup' }).addTo(map);
    map.panTo([lat, lng]);
    estimateFare();
  }

  function setDest(lat, lng, label) {
    document.getElementById('dest-lat').value = lat;
    document.getElementById('dest-lng').value = lng;
    document.getElementById('dest-address').value = label || `${lat.toFixed(5)}, ${lng.toFixed(5)}`;
    if (destMarker) map.removeLayer(destMarker);
    destMarker = L.marker([lat, lng], { title: 'Destination' }).addTo(map);
    if (pickupMarker) {
      const b = L.latLngBounds([pickupMarker.getLatLng(), destMarker.getLatLng()]);
      map.fitBounds(b, { padding: [40, 40] });
    }
    estimateFare();
  }

  // Click map to set destination
  map.on('click', (e) => {
    setDest(e.latlng.lat, e.latlng.lng);
  });

  document.getElementById('use-gps')?.addEventListener('click', () => {
    if (!navigator.geolocation) {
      alert('Geolocation not supported');
      return;
    }
    navigator.geolocation.getCurrentPosition(
      (pos) => setPickup(pos.coords.latitude, pos.coords.longitude, 'Current location'),
      () => alert('Could not get location. Allow GPS permission.')
    );
  });

  // Auto-try GPS on load
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(
      (pos) => setPickup(pos.coords.latitude, pos.coords.longitude, 'Current location'),
      () => {}
    );
  }

  function haversine(lat1, lon1, lat2, lon2) {
    const R = 6371;
    const dLat = (lat2 - lat1) * Math.PI / 180;
    const dLon = (lon2 - lon1) * Math.PI / 180;
    const a = Math.sin(dLat / 2) ** 2 +
      Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
      Math.sin(dLon / 2) ** 2;
    return R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  }

  async function estimateFare() {
    const plat = parseFloat(document.getElementById('pickup-lat').value);
    const plng = parseFloat(document.getElementById('pickup-lng').value);
    const dlat = parseFloat(document.getElementById('dest-lat').value);
    const dlng = parseFloat(document.getElementById('dest-lng').value);
    const vt = document.querySelector('input[name="vehicle_type"]:checked');
    if (!plat || !dlat || !vt) return;

    const dist = haversine(plat, plng, dlat, dlng);
    const duration = dist * 3; // rough min

    try {
      const json = await window.api('/api/rides/estimate', {
        method: 'POST',
        body: JSON.stringify({
          vehicle_type_id: parseInt(vt.value),
          distance_km: dist,
          duration_minutes: duration,
        }),
      });
      if (json.ok) {
        document.getElementById('fare-preview').classList.remove('hidden');
        document.getElementById('fare-total').textContent = 'Rs. ' + json.fare.total_fare;
      }
    } catch (e) {
      console.error(e);
    }
  }

  document.querySelectorAll('input[name="vehicle_type"]').forEach(el => {
    el.addEventListener('change', estimateFare);
  });

  document.getElementById('btn-book')?.addEventListener('click', async () => {
    const plat = parseFloat(document.getElementById('pickup-lat').value);
    const plng = parseFloat(document.getElementById('pickup-lng').value);
    const dlat = parseFloat(document.getElementById('dest-lat').value);
    const dlng = parseFloat(document.getElementById('dest-lng').value);
    const vt = document.querySelector('input[name="vehicle_type"]:checked');
    if (!plat || !dlat || !vt) {
      alert('Set pickup (GPS) and destination (tap map)');
      return;
    }
    const dist = haversine(plat, plng, dlat, dlng);
    const json = await window.api('/api/rides/book', {
      method: 'POST',
      body: JSON.stringify({
        vehicle_type_id: parseInt(vt.value),
        pickup_lat: plat,
        pickup_lng: plng,
        destination_lat: dlat,
        destination_lng: dlng,
        pickup_address: document.getElementById('pickup-address').value,
        destination_address: document.getElementById('dest-address').value,
        distance_km: dist,
        duration_minutes: dist * 3,
      }),
    });
    if (json.ok) {
      alert('Ride booked! Job ID: ' + json.job_id + '\nFare: Rs. ' + json.total_fare);
      location.href = '/passenger/orders';
    } else {
      alert(json.error || 'Booking failed');
    }
  });
})();