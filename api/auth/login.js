export default function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  const payload = req.body || {};
  const isGuest = Boolean(payload.is_guest);
  const rawId = String(payload.email || payload.identifier || payload.username || '').trim();

  if (isGuest || rawId.toLowerCase() === 'guest@parkvision.local') {
    const guestUser = {
      name: 'Guest Rider',
      email: 'guest@parkvision.local',
      phone: '+91 98765 43210',
      license_plate: 'MH-02-GT-2026',
      bike_model: 'Honda Activa 6G',
      bike_type: 'bike_scooter',
      wheels: 2,
      category: 'Scooter',
      icon: '🛵',
      length_m: 1.83,
      width_m: 0.69,
      clearance_m: 0.15
    };
    return res.status(200).json({
      success: true,
      user: guestUser,
      message: 'Demo pass activated! Welcome, Guest Rider.'
    });
  }

  if (!rawId) {
    return res.status(400).json({
      success: false,
      message: 'Please enter an email, username, or phone number to sign in.'
    });
  }

  const rawName = rawId.includes('@') ? rawId.split('@')[0] : rawId;
  const cleanName = rawName.charAt(0).toUpperCase() + rawName.slice(1);
  const user = {
    name: cleanName || 'Rider',
    email: rawId.includes('@') ? rawId.toLowerCase() : `${rawId.replace(/\s+/g, '').toLowerCase()}@parkvision.local`,
    phone: '',
    license_plate: 'MH-01-BK-' + Math.floor(1000 + Math.random() * 9000),
    bike_model: 'Honda Activa 6G',
    bike_type: 'bike_scooter',
    wheels: 2,
    category: 'Scooter',
    icon: '🛵',
    length_m: 1.83,
    width_m: 0.69,
    clearance_m: 0.15
  };

  return res.status(200).json({
    success: true,
    user: user,
    message: `Welcome back, ${user.name}!`
  });
}
