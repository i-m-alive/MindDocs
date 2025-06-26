// Save token on login
export function saveToken(token) {
  localStorage.setItem('access_token', token);
}

// Get token for API headers
export function getToken() {
  return localStorage.getItem('access_token');
}

// Remove token on logout
export function removeToken() {
  localStorage.removeItem('access_token');
}
