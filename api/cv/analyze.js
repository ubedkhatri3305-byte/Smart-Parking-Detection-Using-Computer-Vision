// Vercel Serverless Function: Single Frame & Scenario Analyzer
import scanMultiframeHandler from './scan-multiframe.js';

export default function handler(req, res) {
  return scanMultiframeHandler(req, res);
}
