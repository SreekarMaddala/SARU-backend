const API_BASE = 'http://localhost:8000';

export async function getUsers(token) {
  const res = await fetch(`${API_BASE}/users/`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Failed to fetch users');
  }
  return res.json();
}
