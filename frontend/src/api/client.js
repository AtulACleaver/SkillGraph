import axios from 'axios';

const BASE_URL = import.meta.env.VITE_API_URL ?? '/api';
const REQUEST_TIMEOUT_MS = 25000;

export const api = axios.create({
  baseURL: BASE_URL,
  timeout: REQUEST_TIMEOUT_MS,
  headers: { 'Content-Type': 'application/json' },
});

export function isCancelled(err) {
  return axios.isCancel(err) || err?.code === 'ERR_CANCELED' || err?.name === 'CanceledError';
}

function normalizeError(err) {
  if (err && typeof err === 'object' && 'unrecognized' in err && 'title' in err) {
    return err;
  }
  const status = err?.response?.status || null;
  const detail = err?.response?.data?.detail;
  let title = 'Something went wrong';
  let message = err?.message || 'An unexpected error occurred';
  let unrecognized = [];

  if (detail) {
    if (typeof detail === 'string') {
      message = detail;
    } else {
      message = detail.message || message;
      unrecognized = detail.unrecognized || [];
    }
    if (status === 400 && unrecognized.length > 0) {
      title = "We couldn't recognize your skills";
    } else if (status === 400) {
      title = 'Invalid request';
    } else if (status === 404) {
      title = 'Not found';
    } else if (status >= 500) {
      title = 'Server error';
    }
  } else if (err?.code === 'ECONNABORTED' || err?.code === 'ETIMEDOUT' || /timeout/i.test(err?.message || '')) {
    title = 'Request timed out';
    message = "The server didn't respond within 25 seconds. This sometimes happens right after it wakes up, trying again usually works.";
  } else if (!err?.response) {
    title = 'Connection problem';
    message = "The request didn't reach the server. Check your internet connection.";
  }

  return { status, title, message, unrecognized };
}

export function toFriendlyError(err) {
  return normalizeError(err);
}

export async function getHealth({ signal } = {}) {
  try {
    const { data } = await api.get('/health', { signal });
    return data;
  } catch (err) {
    if (isCancelled(err)) throw err;
    try {
      const { data } = await api.get('/health', { signal });
      return data;
    } catch (retryErr) {
      if (isCancelled(retryErr)) throw retryErr;
      throw normalizeError(retryErr);
    }
  }
}

export async function getRoles({ signal } = {}) {
  try {
    const { data } = await api.get('/roles', { signal });
    return Array.isArray(data) ? data : [];
  } catch (err) {
    if (isCancelled(err)) throw err;
    try {
      const { data } = await api.get('/roles', { signal });
      return Array.isArray(data) ? data : [];
    } catch (retryErr) {
      if (isCancelled(retryErr)) throw retryErr;
      throw normalizeError(retryErr);
    }
  }
}

export async function searchSkills(q, { signal } = {}) {
  try {
    const { data } = await api.get('/skills', { params: { q }, signal });
    return Array.isArray(data) ? data : [];
  } catch (err) {
    if (isCancelled(err)) throw err;
    try {
      const { data } = await api.get('/skills', { params: { q }, signal });
      return Array.isArray(data) ? data : [];
    } catch (retryErr) {
      if (isCancelled(retryErr)) throw retryErr;
      throw normalizeError(retryErr);
    }
  }
}

export async function analyze(payload, { signal } = {}) {
  try {
    const { data } = await api.post('/analyze', payload, { signal });
    return data;
  } catch (err) {
    if (isCancelled(err)) throw err;
    throw normalizeError(err);
  }
}
