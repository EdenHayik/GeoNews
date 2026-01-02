/**
 * Application configuration
 */

// In production, API calls go through Vercel proxy to Railway backend
// In development, API calls go directly to localhost:8000
export const API_BASE_URL = '/api';

export const config = {
  apiBaseUrl: API_BASE_URL,
  refreshInterval: 30000, // 30 seconds
};

