import apiClient from './client';

// products
export const productService = {
  getAll: (params) => apiClient.get('/v1/products/', { params }),
  getById: (id) => apiClient.get(`/v1/products/${id}/`),
  create: (data) => apiClient.post('/v1/products/', data),
  update: (id, data) => apiClient.put(`/v1/products/${id}/`, data),
  delete: (id) => apiClient.delete(`/v1/products/${id}/`),
  getActive: () => apiClient.get('/v1/products/active/'),
  getRecommendations: (id) => apiClient.get(`/v1/products/${id}/recommendations/`),
};

// orders
export const orderService = {
  getAll: (params) => apiClient.get('/v1/orders/', { params }),
  getById: (id) => apiClient.get(`/v1/orders/${id}/`),
  create: (data) => apiClient.post('/v1/orders/', data),
  update: (id, data) => apiClient.put(`/v1/orders/${id}/`, data),
  delete: (id) => apiClient.delete(`/v1/orders/${id}/`),
  getRecent: () => apiClient.get('/v1/orders/recent/'),
  confirmPayment: (id) => apiClient.post(`/v1/orders/${id}/confirm_payment/`),
  markShipped: (id) => apiClient.post(`/v1/orders/${id}/mark_shipped/`),
  markDelivered: (id) => apiClient.post(`/v1/orders/${id}/mark_delivered/`),
};

// offers
export const offerService = {
  getAll: (params) => apiClient.get('/v1/offers/', { params }),
  getById: (id) => apiClient.get(`/v1/offers/${id}/`),
  create: (data) => apiClient.post('/v1/offers/', data),
  update: (id, data) => apiClient.put(`/v1/offers/${id}/`, data),
  delete: (id) => apiClient.delete(`/v1/offers/${id}/`),
  getActive: () => apiClient.get('/v1/offers/active/'),
};

// feedback
export const feedbackService = {
  getAll: (params) => apiClient.get('/v1/feedback/', { params }),
  getById: (id) => apiClient.get(`/v1/feedback/${id}/`),
  create: (data) => apiClient.post('/v1/feedback/', data),
  update: (id, data) => apiClient.put(`/v1/feedback/${id}/`, data),
  getAverageRating: () => apiClient.get('/v1/feedback/average_rating/'),
};

// support  tickets
export const supportTicketService = {
  getAll: (params) => apiClient.get('/v1/support-tickets/', { params }),
  getById: (id) => apiClient.get(`/v1/support-tickets/${id}/`),
  create: (data) => apiClient.post('/v1/support-tickets/', data),
  update: (id, data) => apiClient.put(`/v1/support-tickets/${id}/`, data),
  delete: (id) => apiClient.delete(`/v1/support-tickets/${id}/`),
  getOpen: () => apiClient.get('/v1/support-tickets/open/'),
  resolve: (id, data) => apiClient.post(`/v1/support-tickets/${id}/resolve/`, data),
};

// customers
export const customerService = {
  getAll: (params) => apiClient.get('/v1/customers/', { params }),
  getById: (id) => apiClient.get(`/v1/customers/${id}/`),
  create: (data) => apiClient.post('/v1/customers/', data),
  update: (id, data) => apiClient.put(`/v1/customers/${id}/`, data),
  delete: (id) => apiClient.delete(`/v1/customers/${id}/`),
  getConversations: (id) => apiClient.get(`/v1/customers/${id}/conversations/`),
  getInteractions: (id) => apiClient.get(`/v1/customers/${id}/interactions/`),
};

// conversations
export const conversationService = {
  getAll: (params) => apiClient.get('/v1/conversations/', { params }),
  getById: (id) => apiClient.get(`/v1/conversations/${id}/`),
  create: (data) => apiClient.post('/v1/conversations/', data),
  update: (id, data) => apiClient.put(`/v1/conversations/${id}/`, data),
  sendMessage: (id, data) => apiClient.post(`/v1/conversations/${id}/send_message/`, data),
  close: (id) => apiClient.post(`/v1/conversations/${id}/close/`),
};

// funnel stages
export const funnelStageService = {
  getAll: (params) => apiClient.get('/v1/funnel-stages/', { params }),
  getById: (id) => apiClient.get(`/v1/funnel-stages/${id}/`),
  getByStage: () => apiClient.get('/v1/funnel-stages/by_stage/'),
};

// shipping delays
export const shippingDelayService = {
  getAll: (params) => apiClient.get('/v1/shipping-delays/', { params }),
  getById: (id) => apiClient.get(`/v1/shipping-delays/${id}/`),
  getUnnotified: () => apiClient.get('/v1/shipping-delays/unnotified/'),
};

// wehooks
export const webhookService = {
  health: () => apiClient.get('/health/'),
};
