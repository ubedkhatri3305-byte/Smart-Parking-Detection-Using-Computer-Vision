export default function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  return res.status(200).json({
    status: 'ok',
    environment: 'vercel-edge-serverless',
    timestamp: new Date().toISOString(),
    service: 'ParkVision AI Computer Vision Service'
  });
}
