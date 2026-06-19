const BASE_URL = "http://localhost:8000/api/v1";

function getToken() {
  return localStorage.getItem("access_token");
}

async function request(path, options = {}) {
  const token = getToken();
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...options.headers,
    },
    ...options,
  });
  const data = await res.json();
  if (!res.ok) throw data;
  return data;
}

export async function register({ username, email, password, password2, role }) {
  return request("/auth/register/", {
    method: "POST",
    body: JSON.stringify({ username, email, password, password2, role }),
  });
}

export async function login({ email, password }) {
  const data = await request("/auth/login/", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
  localStorage.setItem("access_token", data.access);
  localStorage.setItem("refresh_token", data.refresh);
  return data;
}

export function logout() {
  localStorage.removeItem("access_token");
  localStorage.removeItem("refresh_token");
}

export async function getMe() {
  return request("/auth/me/");
}

export async function fetchProducts(search = "") {
  const q = search ? `?search=${encodeURIComponent(search)}` : "";
  return request(`/products/${q}`);
}

export async function fetchProductById(id) {
  return request(`/products/${id}/`);
}

export async function fetchOffers() {
  return request("/products/offers/");
}

export async function placeOrder({ customerEmail, paymentMethod, deliveryAddress, phone, items }) {
  return request("/orders/", {
    method: "POST",
    body: JSON.stringify({
      customer_email: customerEmail,
      payment_method: paymentMethod,
      delivery_address: deliveryAddress,
      phone,
      items,
    }),
  });
}

export async function fetchMyOrders() {
  return request("/orders/list/");
}

export async function fetchOrderByNumber(orderNumber) {
  return request(`/orders/${orderNumber}/`);
}

export async function submitReview({ orderId, rating, comment }) {
  return request("/orders/reviews/create/", {
    method: "POST",
    body: JSON.stringify({ order: orderId, rating, comment }),
  });
}

export async function sendChatMessage(message, conversationId = null) {
  const data = await request("/chat/", {
    method: "POST",
    body: JSON.stringify({
      message,
      conversation_id: conversationId,
    }),
  });

  return {
    reply: data.reply,
    conversationId: data.conversation_id,
  };
}

export async function fetchAnalytics() {
  return request("/chat/analytics/");
}

export async function submitConversationFeedback({ conversationId, rating, comment }) {
  return request("/chat/feedback/", {
    method: "POST",
    body: JSON.stringify({
      conversation_id: conversationId,
      rating,
      comment,
    }),
  });
}

export async function fetchAdminOrders() {
  return request("/orders/list/");
}

export async function updateOrderStatus({
  orderNumber,
  status,
  location,
  trackingNumber = "",
}) {
  const payload = {
    status,
    location,
  };

  if (trackingNumber) {
    payload.tracking_number = trackingNumber;
  }

  return request(
    `/orders/${encodeURIComponent(orderNumber)}/status/`,
    {
      method: "PATCH",
      body: JSON.stringify(payload),
    }
  );
}

// Admin Support Tickets
export async function fetchAdminTickets(params = {}) {
  const query = new URLSearchParams(params).toString();
  return request(`/support/tickets/?${query}`);
}

export async function fetchTicketByNumber(ticketNumber) {
  return request(`/support/tickets/${encodeURIComponent(ticketNumber)}/`);
}

export async function replyToTicket(ticketNumber, { response, status }) {
  return request(`/support/tickets/${encodeURIComponent(ticketNumber)}/reply/`, {
    method: "POST",
    body: JSON.stringify({ response, status }),
  });
}

// Admin Users
export async function fetchAdminUsers(params = {}) {
  const query = new URLSearchParams(params).toString();
  return request(`/auth/admin/users/?${query}`);
}

export async function updateAdminUser(id, data) {
  return request(`/auth/admin/users/${id}/`, {
    method: "PATCH",
    body: JSON.stringify(data),
  });
}

// Admin Conversations
export async function fetchAdminConversations(params = {}) {
  const query = new URLSearchParams(params).toString();
  return request(`/chat/admin/conversations/?${query}`);
}

export async function fetchConversationById(id) {
  return request(`/chat/admin/conversations/${id}/`);
}

// Admin Reviews & Conversation Feedback
export async function fetchAdminReviews(params = {}) {
  const query = new URLSearchParams(params).toString();
  return request(`/orders/reviews/admin/?${query}`);
}

export async function fetchAdminConversationFeedback(params = {}) {
  const query = new URLSearchParams(params).toString();
  return request(`/chat/feedback/?${query}`);
}

// Admin Offers
export async function fetchAdminOffers(params = {}) {
  const query = new URLSearchParams(params).toString();
  return request(`/products/admin/offers/?${query}`);
}

export async function createOffer(data) {
  return request("/products/admin/offers/", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function updateOffer(id, data) {
  return request(`/products/admin/offers/${id}/`, {
    method: "PATCH",
    body: JSON.stringify(data),
  });
}

export async function deleteOffer(id) {
  return request(`/products/admin/offers/${id}/`, {
    method: "DELETE",
  });
}

// Admin FAQ / Knowledge Base
export async function fetchAdminFAQs(params = {}) {
  const query = new URLSearchParams(params).toString();
  return request(`/support/faq/?${query}`);
}

export async function createFAQ(data) {
  return request("/support/faq/", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function updateFAQ(id, data) {
  return request(`/support/faq/${id}/`, {
    method: "PATCH",
    body: JSON.stringify(data),
  });
}

export async function deleteFAQ(id) {
  return request(`/support/faq/${id}/`, {
    method: "DELETE",
  });
}

// Admin Product Actions
export async function adminCreateProduct(data) {
  return request("/products/", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function adminUpdateProduct(id, data) {
  return request(`/products/${id}/`, {
    method: "PATCH",
    body: JSON.stringify(data),
  });
}

export async function adminDeactivateProduct(id) {
  return request(`/products/${id}/`, {
    method: "DELETE",
  });
}