import { create } from 'zustand';

export const useAppStore = create((set) => ({
  // Auth state
  user: null,
  isAuthenticated: false,
  setUser: (user) => set({ user, isAuthenticated: !!user }),
  logout: () => set({ user: null, isAuthenticated: false }),

  // Products state
  products: [],
  selectedProduct: null,
  setProducts: (products) => set({ products }),
  setSelectedProduct: (product) => set({ selectedProduct: product }),

  // Orders state
  orders: [],
  currentOrder: null,
  setOrders: (orders) => set({ orders }),
  setCurrentOrder: (order) => set({ currentOrder: order }),

  // Cart state
  cart: [],
  addToCart: (product) => set((state) => ({
    cart: [...state.cart, { ...product, cartId: Date.now() }],
  })),
  removeFromCart: (cartId) => set((state) => ({
    cart: state.cart.filter((item) => item.cartId !== cartId),
  })),
  clearCart: () => set({ cart: [] }),

  // Feedback state
  feedback: [],
  setFeedback: (feedback) => set({ feedback }),

  // Support tickets state
  tickets: [],
  setTickets: (tickets) => set({ tickets }),

  // UI state
  loading: false,
  error: null,
  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error }),
  clearError: () => set({ error: null }),

  // Language state
  language: 'ar',
  setLanguage: (language) => set({ language }),

  // Funnel state
  currentFunnelStage: 'awareness',
  setCurrentFunnelStage: (stage) => set({ currentFunnelStage: stage }),
}));
