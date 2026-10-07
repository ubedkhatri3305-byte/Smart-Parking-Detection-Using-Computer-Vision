// Vercel Serverless Function: Live Frame Analyzer for Cloud Deployments
import scanMultiframeHandler from './scan-multiframe.js';

export default function handler(req, res) {
  // Directly forward to the high-accuracy frame handler
  return scanMultiframeHandler(req, res);
}
