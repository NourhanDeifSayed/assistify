/**
 * Product Database for MediCare AI Chat
 */

export const products = [
  {
    id: 1,
    name: "Blood Pressure Monitor",
    description: "Digital BP monitor for accurate readings",
    price: 2699,
    currency: "EGP",
    benefits: [
      "FDA approved and clinically validated",
      "Large display for easy reading",
      "Stores up to 60 measurements",
      "Automatic inflation for comfort",
      "Detects irregular heartbeat",
    ],
    relatedProducts: [2, 5],
    image: "blood-pressure-monitor.png",
  },
  {
    id: 2,
    name: "Pulse Oximeter",
    description: "Finger pulse oximeter for measuring oxygen levels",
    price: 1499,
    currency: "EGP",
    benefits: [
      "Medical-grade accuracy",
      "Fast reading in 1-2 seconds",
      "Portable and lightweight",
      "Low battery indicator",
      "Perfect for home monitoring",
    ],
    relatedProducts: [1, 5],
    image: "pulse-oximeter.png",
  },
  {
    id: 3,
    name: "Digital Thermometer",
    description: "Fast temperature reading device",
    price: 899,
    currency: "EGP",
    benefits: [
      "Measures temperature in seconds",
      "High accuracy ±0.1°C",
      "Memory function for last reading",
      "Waterproof design",
      "Suitable for all ages",
    ],
    relatedProducts: [1, 2],
    image: "digital-thermometer.png",
  },
  {
    id: 4,
    name: "Smart Scale",
    description: "Digital scale with BMI calculation",
    price: 2399,
    currency: "EGP",
    benefits: [
      "Tracks weight and calculates BMI automatically",
      "Measures body fat percentage",
      "Stores up to 10 user profiles",
      "Bluetooth connectivity",
      "Mobile app integration",
    ],
    relatedProducts: [5, 1],
    image: "smart-scale.png",
  },
  {
    id: 5,
    name: "Heart Rate Monitor",
    description: "Wearable monitor for 24/7 tracking",
    price: 3899,
    currency: "EGP",
    benefits: [
      "Monitors heart rate 24/7",
      "Provides health insights",
      "Water resistant design",
      "Long battery life (7-10 days)",
      "Syncs with smartphone app",
    ],
    relatedProducts: [2, 4],
    image: "heart-rate-monitor.png",
  },
  {
    id: 6,
    name: "Glucose Monitor",
    description: "Blood glucose monitoring system",
    price: 1799,
    currency: "EGP",
    benefits: [
      "Essential for diabetes management",
      "Quick and painless testing",
      "Stores 500 test results",
      "Includes lancets and test strips",
      "Portable and easy to use",
    ],
    relatedProducts: [1, 2],
    image: "glucose-monitor.png",
  },
];

export const mockOrders = [
  {
    id: "ORD-001",
    customerEmail: "customer@example.com",
    items: [
      { productId: 2, quantity: 1, price: 1499 },
    ],
    totalPrice: 1499,
    status: "delivered",
    orderDate: "2024-11-10",
    deliveryDate: "2024-11-15",
    trackingNumber: "TRACK-001",
    tracking: {
      status: "Delivered",
      location: "Cairo, Egypt",
      estimatedDelivery: "2024-11-15",
      updates: [
        { date: "2024-11-10", status: "Order Placed", location: "Warehouse" },
        { date: "2024-11-11", status: "Processing", location: "Warehouse" },
        { date: "2024-11-12", status: "Shipped", location: "Cairo Distribution Center" },
        { date: "2024-11-15", status: "Delivered", location: "Cairo, Egypt" },
      ],
    },
  },
  {
    id: "ORD-002",
    customerEmail: "customer@example.com",
    items: [
      { productId: 1, quantity: 1, price: 2699 },
    ],
    totalPrice: 2699,
    status: "in_transit",
    orderDate: "2024-11-18",
    trackingNumber: "TRACK-002",
    tracking: {
      status: "In Transit",
      location: "Alexandria, Egypt",
      estimatedDelivery: "2024-11-22",
      updates: [
        { date: "2024-11-18", status: "Order Placed", location: "Warehouse" },
        { date: "2024-11-19", status: "Processing", location: "Warehouse" },
        { date: "2024-11-20", status: "Shipped", location: "Cairo Distribution Center" },
        { date: "2024-11-21", status: "In Transit", location: "Alexandria, Egypt" },
      ],
    },
  },
];

/**
 * Search products by name or description
 */
export function searchProducts(query: string) {
  const lowerQuery = query.toLowerCase();
  return products.filter(
    (p) =>
      p.name.toLowerCase().includes(lowerQuery) ||
      p.description.toLowerCase().includes(lowerQuery)
  );
}

/**
 * Get product details by ID
 */
export function getProductById(id: number) {
  return products.find((p) => p.id === id);
}

/**
 * Get related products
 */
export function getRelatedProducts(productId: number) {
  const product = getProductById(productId);
  if (!product) return [];
  return product.relatedProducts
    .map((id) => getProductById(id))
    .filter((p) => p !== undefined);
}

/**
 * Format product information for chat
 */
export function formatProductInfo(product: typeof products[0]) {
  return `
**${product.name}** - ${product.price} ${product.currency}
${product.description}

Benefits:
${product.benefits.map((b) => `- ${b}`).join("\n")}
  `.trim();
}

/**
 * Format order tracking information
 */
export function formatTrackingInfo(order: typeof mockOrders[0]) {
  const trackingUpdates = order.tracking.updates
    .map((u) => `• ${u.date}: ${u.status} - ${u.location}`)
    .join("\n");

  return `
**Order #${order.id}** - Tracking #${order.trackingNumber}
Status: ${order.tracking.status}
Estimated Delivery: ${order.tracking.estimatedDelivery}

Timeline:
${trackingUpdates}
  `.trim();
}

/**
 * Get all products as formatted text for LLM context
 */
export function getAllProductsContext() {
  return products
    .map((p) => `- ${p.name} (${p.price} ${p.currency}): ${p.description}`)
    .join("\n");
}
