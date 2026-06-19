import { BrowserRouter, Routes, Route } from "react-router-dom";
import { CartProvider } from "./context/CartContext";
import { AuthProvider } from "./context/AuthContext";
import Navbar from "./components/Navbar";
import ChatWidget from "./components/ChatWidget";
import AdminRoute from "./components/AdminRoute";

import Home from "./pages/Home";
import Products from "./pages/Products";
import Integrations from "./pages/Integrations";
import Cart from "./pages/Cart";
import Payment from "./pages/Payment";
import Confirmation from "./pages/Confirmation";
import Tracking from "./pages/Tracking";
import Review from "./pages/Review";
import Offers from "./pages/Offers";
import ChatPage from "./pages/ChatPage";
import Analytics from "./pages/Analytics";
import AdminOrders from "./pages/AdminOrders";
import AdminProducts from "./pages/AdminProducts";
import AdminTickets from "./pages/AdminTickets";
import AdminUsers from "./pages/AdminUsers";
import AdminConversations from "./pages/AdminConversations";
import AdminReviews from "./pages/AdminReviews";
import AdminOffers from "./pages/AdminOffers";
import AdminFAQ from "./pages/AdminFAQ";

export default function App() {
  return (
    <AuthProvider>
      <CartProvider>
        <BrowserRouter>
          <Navbar />
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/products" element={<Products />} />
            <Route path="/integrations" element={<Integrations />} />
            <Route path="/cart" element={<Cart />} />
            <Route path="/payment" element={<Payment />} />
            <Route path="/confirmation" element={<Confirmation />} />
            <Route path="/tracking" element={<Tracking />} />
            <Route path="/review" element={<Review />} />
            <Route path="/offers" element={<Offers />} />
            <Route path="/chat" element={<ChatPage />} />

            {/* Admin Routes */}
            <Route
              path="/analytics"
              element={
                <AdminRoute>
                  <Analytics />
                </AdminRoute>
              }
            />
            <Route
              path="/admin/orders"
              element={
                <AdminRoute>
                  <AdminOrders />
                </AdminRoute>
              }
            />
            <Route
              path="/admin/products"
              element={
                <AdminRoute>
                  <AdminProducts />
                </AdminRoute>
              }
            />
            <Route
              path="/admin/tickets"
              element={
                <AdminRoute>
                  <AdminTickets />
                </AdminRoute>
              }
            />
            <Route
              path="/admin/users"
              element={
                <AdminRoute>
                  <AdminUsers />
                </AdminRoute>
              }
            />
            <Route
              path="/admin/conversations"
              element={
                <AdminRoute>
                  <AdminConversations />
                </AdminRoute>
              }
            />
            <Route
              path="/admin/reviews"
              element={
                <AdminRoute>
                  <AdminReviews />
                </AdminRoute>
              }
            />
            <Route
              path="/admin/offers"
              element={
                <AdminRoute>
                  <AdminOffers />
                </AdminRoute>
              }
            />
            <Route
              path="/admin/faq"
              element={
                <AdminRoute>
                  <AdminFAQ />
                </AdminRoute>
              }
            />
          </Routes>
          <ChatWidget />
        </BrowserRouter>
      </CartProvider>
    </AuthProvider>
  );
}