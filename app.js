const apiBase = "YOUR_API_INVOKE_URL";
const cognitoDomain = "YOUR_COGNITO_DOMAIN";
const clientId = "YOUR_APP_CLIENT_ID";
const redirectUri = "YOUR_S3_WEBSITE_URL";

function login() {
  const url =
    `https://${cognitoDomain}/login?client_id=${clientId}` +
    `&response_type=token&scope=openid+email+profile` +
    `&redirect_uri=${encodeURIComponent(redirectUri)}`;
  window.location.href = url;
}

function logout() {
  localStorage.removeItem("id_token");
  const url =
    `https://${cognitoDomain}/logout?client_id=${clientId}` +
    `&logout_uri=${encodeURIComponent(redirectUri)}`;
  window.location.href = url;
}

function parseTokensFromUrl() {
  if (window.location.hash) {
    const hash = window.location.hash.substring(1);
    const params = new URLSearchParams(hash);
    const token = params.get("id_token");
    if (token) {
      localStorage.setItem("id_token", token);
      window.location.hash = "";
    }
  }
}

function getToken() {
  return localStorage.getItem("id_token");
}

async function apiFetch(path, options = {}) {
  const token = getToken();
  const headers = options.headers || {};
  if (token) headers["Authorization"] = token;
  headers["Content-Type"] = "application/json";

  const res = await fetch(`${apiBase}${path}`, {
    ...options,
    headers
  });

  if (!res.ok) {
    const err = await res.text();
    throw new Error(err);
  }

  return res.json();
}

async function loadItems() {
  const items = await apiFetch("/items");
  const tbody = document.getElementById("itemsBody");
  tbody.innerHTML = "";

  items.forEach(item => {
    const row = document.createElement("tr");
    row.innerHTML = `
      <td>${item.itemId}</td>
      <td>${item.itemName}</td>
      <td>${item.quantity}</td>
      <td>${item.category}</td>
      <td>${item.location}</td>
      <td>
        <button onclick='editItem(${JSON.stringify(item)})'>Edit</button>
        <button onclick='deleteItem("${item.itemId}")'>Delete</button>
      </td>
    `;
    tbody.appendChild(row);
  });
}

function editItem(item) {
  document.getElementById("itemId").value = item.itemId;
  document.getElementById("itemName").value = item.itemName;
  document.getElementById("quantity").value = item.quantity;
  document.getElementById("category").value = item.category;
  document.getElementById("location").value = item.location;
}

document.getElementById("itemForm").addEventListener("submit", async (e) => {
  e.preventDefault();

  const item = {
    itemId: document.getElementById("itemId").value,
    itemName: document.getElementById("itemName").value,
    quantity: document.getElementById("quantity").value,
    category: document.getElementById("category").value,
    location: document.getElementById("location").value
  };

  try {
    await apiFetch(`/items/${item.itemId}`, {
      method: "PUT",
      body: JSON.stringify(item)
    });
  } catch {
    await apiFetch("/items", {
      method: "POST",
      body: JSON.stringify(item)
    });
  }

  document.getElementById("itemForm").reset();
  loadItems();
});

async function deleteItem(itemId) {
  await apiFetch(`/items/${itemId}`, { method: "DELETE" });
  loadItems();
}

parseTokensFromUrl();
loadItems();