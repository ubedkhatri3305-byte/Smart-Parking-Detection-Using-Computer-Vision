export default function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  const payload = req.body || {};
  const name = String(payload.name || '').trim() || 'Registered User';
  const email = String(payload.email || '').trim().toLowerCase() || `${name.toLowerCase().replace(/[^a-z0-9]/g, '')}@parkvision.local`;
  const bikeModel = String(payload.bike_model || '').trim() || 'Honda Activa 6G';

  const user = {
    name: name,
    email: email,
    phone: String(payload.phone || '').trim(),
    license_plate: String(payload.license_plate || '').trim().toUpperCase() || 'MH-01-BK-' + Math.floor(1000 + Math.random() * 9000),
    bike_model: bikeModel,
    bike_type: payload.bike_type || 'bike_scooter',
    wheels: Number(payload.wheels) || 2,
    category: payload.category || 'Scooter',
    icon: payload.icon || '🛵',
    length_m: Number(payload.length_m) || 1.83,
    width_m: Number(payload.width_m) || 0.69,
    clearance_m: Number(payload.clearance_m) || 0.15
  };

  return res.status(200).json({
    success: true,
    user: user,
    message: `Welcome ${name}! ${bikeModel} registered successfully.`
  });
}
