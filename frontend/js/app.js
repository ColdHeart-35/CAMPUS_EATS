// frontend/js/app.js
// Plain JavaScript implementation for CampusEats front‑end.
// Handles authentication, role‑based view switching, student menu/cart, staff order handling, and admin dashboard.

const API_BASE = "http://127.0.0.1:8000"; // Backend base URL

// ---- Utility Functions ---------------------------------------------------
function apiRequest(method, path, body = null, requiresAuth = true) {
  const headers = { "Content-Type": "application/json" };
  if (requiresAuth) {
    const token = localStorage.getItem("jwt");
    if (!token) throw new Error("Missing JWT token");
    headers["Authorization"] = `Bearer ${token}`;
  }
  const options = { method, headers };
  if (body !== null) options.body = JSON.stringify(body);
  return fetch(API_BASE + path, options).then(async resp => {
    if (!resp.ok) {
      const err = await resp.json().catch(() => ({}));
      throw new Error(err.detail || resp.statusText);
    }
    return resp.json();
  });
}

function decodeJwtPayload(token) {
  try {
    const payload = token.split(".")[1];
    const decoded = atob(payload.replace(/-/g, "+").replace(/_/g, "/"));
    return JSON.parse(decoded);
  } catch (_) { return {}; }
}

function showSection(id) {
  document.querySelectorAll("section").forEach(sec => sec.style.display = "none");
  const el = document.getElementById(id);
  if (el) el.style.display = "block";
}

function showMessage(target, msg, type = "info") {
  const div = document.createElement("div");
  div.className = `msg ${type}`;
  div.textContent = msg;
  target.innerHTML = "";
  target.appendChild(div);
  setTimeout(() => div.remove(), 5000);
}

// ---- Authentication ------------------------------------------------------
async function handleLogin(event) {
  event.preventDefault();
  const email = document.getElementById("loginEmail").value.trim();
  const password = document.getElementById("loginPassword").value;
  const msgBox = document.getElementById("loginMsg");
  try {
    const formData = new URLSearchParams();
  formData.append("username", email);
  formData.append("password", password);
  const data = await apiRequest("POST", "/auth/login", formData, false);
    localStorage.setItem("jwt", data.access_token);
    const payload = decodeJwtPayload(data.access_token);
    localStorage.setItem("role", payload.role);
    initApp();
  } catch (e) {
    showMessage(msgBox, e.message, "error");
  }
}

async function handleRegister(event) {
  event.preventDefault();
  const email = document.getElementById("regEmail").value.trim();
  const password = document.getElementById("regPassword").value;
  const name = document.getElementById("regFullName").value.trim();
  const msgBox = document.getElementById("registerMsg");
  try {
    const data = await apiRequest("POST", "/auth/register", {
      email,
      password,
      full_name: name,
      role: "student"
    }, false);
    // Auto‑login after registration
    localStorage.setItem("jwt", data.access_token);
    const payload = decodeJwtPayload(data.access_token);
    localStorage.setItem("role", payload.role);
    initApp();
  } catch (e) {
    showMessage(msgBox, e.message, "error");
  }
}

function logout() {
  localStorage.removeItem("jwt");
  localStorage.removeItem("role");
  showSection("auth-section");
}

// ---- Student Dashboard ---------------------------------------------------
let studentCart = [];

async function loadStudentMenu() {
  const container = document.getElementById("foodMenu");
  container.innerHTML = "Loading…";
  try {
    const items = await apiRequest("GET", "/student/menu");
    renderMenuItems(items);
  } catch (e) {
    showMessage(container, e.message, "error");
  }
}

function renderMenuItems(items) {
  const container = document.getElementById("foodMenu");
  container.innerHTML = "";
  const list = document.createElement("div");
  list.className = "menu-list";
  items.forEach(item => {
    const card = document.createElement("div");
    card.className = "menu-card";
    card.innerHTML = `
      <h3>${item.name}</h3>
      <p>${item.description || ""}</p>
      <p><strong>₹${item.price.toFixed(2)}</strong> – ${item.category}</p>
      <button data-id="${item.id}" class="addBtn">Add to Cart</button>
    `;
    list.appendChild(card);
  });
  container.appendChild(list);
  container.querySelectorAll(".addBtn").forEach(btn => {
    btn.addEventListener("click", () => addToCart(parseInt(btn.dataset.id)));
  });
}

async function addToCart(itemId, qty = 1) {
  try {
    await apiRequest("POST", "/student/cart/add", { item_id: itemId, quantity: qty });
    const existing = studentCart.find(e => e.item_id === itemId);
    if (existing) existing.quantity += qty; else studentCart.push({ item_id: itemId, quantity: qty });
    renderCart();
    showMessage(document.getElementById("cartMsg"), "Added to cart", "success");
  } catch (e) {
    showMessage(document.getElementById("cartMsg"), e.message, "error");
  }
}

function renderCart() {
  const cartDiv = document.getElementById("cart-drawer");
  cartDiv.innerHTML = "";
  if (studentCart.length === 0) { cartDiv.textContent = "Cart is empty"; return; }
  const table = document.createElement("table");
  table.innerHTML = `<tr><th>Item ID</th><th>Qty</th><th>Actions</th></tr>`;
  studentCart.forEach(entry => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${entry.item_id}</td>
      <td>${entry.quantity}</td>
      <td>
        <button class="inc" data-id="${entry.item_id}">+</button>
        <button class="dec" data-id="${entry.item_id}">-</button>
        <button class="rm" data-id="${entry.item_id}">✖</button>
      </td>`;
    table.appendChild(tr);
  });
  cartDiv.appendChild(table);
  cartDiv.querySelectorAll(".inc").forEach(b => b.addEventListener("click", ev => modifyCart(+1, ev)));
  cartDiv.querySelectorAll(".dec").forEach(b => b.addEventListener("click", ev => modifyCart(-1, ev)));
  cartDiv.querySelectorAll(".rm").forEach(b => b.addEventListener("click", ev => removeFromCart(ev)));
}

async function modifyCart(delta, ev) {
  const id = parseInt(ev.target.dataset.id);
  const entry = studentCart.find(e => e.item_id === id);
  if (!entry) return;
  const newQty = entry.quantity + delta;
  if (newQty <= 0) return await removeFromCart(ev);
  try {
    await apiRequest("POST", "/student/cart/remove", { item_id: id });
    await apiRequest("POST", "/student/cart/add", { item_id: id, quantity: newQty });
    entry.quantity = newQty;
    renderCart();
  } catch (e) {
    showMessage(document.getElementById("cartMsg"), e.message, "error");
  }
}

async function removeFromCart(ev) {
  const id = parseInt(ev.target.dataset.id);
  try {
    await apiRequest("POST", "/student/cart/remove", { item_id: id });
    studentCart = studentCart.filter(e => e.item_id !== id);
    renderCart();
    showMessage(document.getElementById("cartMsg"), "Removed from cart", "success");
  } catch (e) {
    showMessage(document.getElementById("cartMsg"), e.message, "error");
  }
}

async function placeOrder(ev) {
  ev.preventDefault();
  // Using default payment method "cash"
  const method = "cash";
  try {
    const res = await apiRequest("POST", "/student/order", { payment_method: method });
    studentCart = [];
    renderCart();
    showMessage(document.getElementById("orderMsg"), `Order #${res.order_id} placed`, "success");
    loadOrderHistory();
  } catch (e) {
    showMessage(document.getElementById("orderMsg"), e.message, "error");
  }
}

async function loadOrderHistory() {
  const holder = document.getElementById("orderHistory");
  holder.innerHTML = "Loading…";
  try {
    const orders = await apiRequest("GET", "/student/orders");
    if (!orders || orders.length === 0) {
      holder.textContent = "No orders yet";
      return;
    }
    const list = document.createElement("ul");
    orders.forEach(o => {
      const li = document.createElement("li");
      li.textContent = `#${o.id} – ${o.status} – $${o.total || o.amount || 0}`;
      list.appendChild(li);
    });
    holder.innerHTML = "";
    holder.appendChild(list);
  } catch (e) {
    showMessage(holder, e.message, "error");
  }
}

// ---- Staff Dashboard -----------------------------------------------------
async function loadIncomingOrders() {
  const container = document.getElementById("incomingOrders");
  container.innerHTML = "Loading…";
  try {
    const orders = await apiRequest("GET", "/staff/orders");
    renderStaffOrders(orders);
  } catch (e) {
    showMessage(container, e.message, "error");
  }
}

function renderStaffOrders(orders) {
  const container = document.getElementById("incomingOrders");
  container.innerHTML = "";
  if (!orders || orders.length === 0) { container.textContent = "No pending orders"; return; }
  orders.forEach(o => {
    const div = document.createElement("div");
    div.className = "order-card";
    div.innerHTML = `
      <p>Order <strong>#${o.id}</strong> – Status: ${o.status}</p>
      <select data-id="${o.id}">
        <option value="pending" ${o.status==='pending'?'selected':''}>Pending</option>
        <option value="accepted" ${o.status==='accepted'?'selected':''}>Accepted</option>
        <option value="preparing" ${o.status==='preparing'?'selected':''}>Preparing</option>
        <option value="ready" ${o.status==='ready'?'selected':''}>Ready</option>
        <option value="completed" ${o.status==='completed'?'selected':''}>Completed</option>
        <option value="rejected" ${o.status==='rejected'?'selected':''}>Rejected</option>
      </select>
    `;
    container.appendChild(div);
    div.querySelector("select").addEventListener("change", async ev => {
      const newStatus = ev.target.value;
      const oid = ev.target.dataset.id;
      try {
        await apiRequest("POST", `/staff/orders/${oid}/status`, { new_status: newStatus });
        showMessage(container, "Status updated", "success");
        loadIncomingOrders();
      } catch (e) {
        showMessage(container, e.message, "error");
      }
    });
  });
}

async function loadStaffInventory() {
  const inv = document.getElementById("inventoryManagement");
  inv.innerHTML = "Loading…";
  try {
    const items = await apiRequest("GET", "/staff/inventory");
    const table = document.createElement("table");
    table.innerHTML = `<tr><th>Ingredient</th><th>Qty</th><th>Unit</th><th>Adjust</th></tr>`;
    items.forEach(it => {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td>${it.name}</td>
        <td>${it.quantity}</td>
        <td>${it.unit}</td>
        <td><input type="number" data-id="${it.id}" min="-1000" max="1000" placeholder="±" style="width:60px;" />
            <button data-id="${it.id}" class="adjBtn">Go</button></td>`;
      table.appendChild(tr);
    });
    inv.innerHTML = "";
    inv.appendChild(table);
    inv.querySelectorAll(".adjBtn").forEach(btn => btn.addEventListener("click", async ev => {
      const id = ev.target.dataset.id;
      const delta = parseInt(inv.querySelector(`input[data-id="${id}"]`).value);
      if (isNaN(delta) || delta === 0) return;
      try {
        await apiRequest("POST", "/staff/inventory/update", { ingredient_id: parseInt(id), delta });
        showMessage(inv, "Inventory updated", "success");
        loadStaffInventory();
      } catch (e) {
        showMessage(inv, e.message, "error");
      }
    }));
  } catch (e) {
    showMessage(inv, e.message, "error");
  }
}

// ---- Admin Dashboard -----------------------------------------------------
async function loadAdminDashboard() {
  const stats = document.getElementById("adminStats");
  stats.innerHTML = "Loading…";
  try {
    const data = await apiRequest("GET", "/admin/dashboard");
    stats.innerHTML = `<p>Total Users: ${data.total_users}</p>
                       <p>Total Orders: ${data.total_orders}</p>
                       <p>Low‑stock items: ${data.low_stock_items?.length || 0}</p>`;
  } catch (e) {
    showMessage(stats, e.message, "error");
  }
}

async function loadAdminUsers() {
  const ul = document.getElementById("adminUsers");
  ul.innerHTML = "Loading…";
  try {
    const users = await apiRequest("GET", "/admin/users");
    ul.innerHTML = "";
    users.forEach(u => {
      const li = document.createElement("li");
      li.textContent = `${u.id}: ${u.email} (${u.role})`;
      ul.appendChild(li);
    });
  } catch (e) {
    showMessage(ul, e.message, "error");
  }
}

async function loadAdminInventory() {
  const inv = document.getElementById("adminInventory");
  inv.innerHTML = "Loading…";
  try {
    const items = await apiRequest("GET", "/admin/inventory");
    const list = document.createElement("ul");
    items.forEach(it => {
      const li = document.createElement("li");
      li.textContent = `${it.name}: ${it.quantity} ${it.unit}`;
      list.appendChild(li);
    });
    inv.innerHTML = "";
    inv.appendChild(list);
  } catch (e) {
    showMessage(inv, e.message, "error");
  }
}

async function loadAdminSales() {
  const sales = document.getElementById("adminSales");
  sales.innerHTML = "Loading…";
  try {
    const report = await apiRequest("GET", "/admin/reports/sales");
    sales.innerHTML = `<pre>${JSON.stringify(report, null, 2)}</pre>`;
  } catch (e) {
    showMessage(sales, e.message, "error");
  }
}

// ---- Initialization -------------------------------------------------------
function initApp() {
  const token = localStorage.getItem("jwt");
  const role = localStorage.getItem("role");
  if (!token || !role) { showSection("auth-section"); return; }
  if (role === "student") {
    showSection("dashboard-student");
    loadStudentMenu();
    renderCart();
    loadOrderHistory();
  } else if (role === "staff") {
    showSection("dashboard-staff");
    loadIncomingOrders();
    loadStaffInventory();
  } else if (role === "admin") {
    showSection("dashboard-admin");
    loadAdminDashboard();
    loadAdminUsers();
    loadAdminInventory();
    loadAdminSales();
  } else {
    logout();
  }
}

// ---- Event Listeners -----------------------------------------------------
document.addEventListener("DOMContentLoaded", () => {
  const loginForm = document.getElementById("loginForm");
  if (loginForm) loginForm.addEventListener("submit", handleLogin);
  const regForm = document.getElementById("registerForm");
  if (regForm) regForm.addEventListener("submit", handleRegister);
  const logoutBtn = document.getElementById("logoutBtn");
  if (logoutBtn) logoutBtn.addEventListener("click", logout);
  const orderForm = document.getElementById("orderForm");
  if (orderForm) orderForm.addEventListener("submit", placeOrder);
  initApp();
});

// End of app.js
