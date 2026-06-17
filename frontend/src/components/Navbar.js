import { useEffect, useState } from "react";
import { Link, useLocation } from "react-router-dom";
import { useCart } from "../context/CartContext";
import { getMe, logout } from "../services/api";
import AuthModal from "./AuthModal";
import styles from "./Navbar.module.css";

export default function Navbar() {
  const { cart } = useCart();
  const location = useLocation();

  const [showAuth, setShowAuth] = useState(false);
  const [user, setUser] = useState(null);
  const [loadingUser, setLoadingUser] = useState(true);

  const navLinks = [
    { to: "/", label: "Home" },
    { to: "/products", label: "Products" },
    { to: "/integrations", label: "Integrations" },
    { to: "/chat", label: "Support" },
  ];

  useEffect(() => {
    let isMounted = true;

    async function loadCurrentUser() {
      const token = localStorage.getItem("access_token");

      if (!token) {
        if (isMounted) {
          setUser(null);
          setLoadingUser(false);
        }
        return;
      }

      try {
        const data = await getMe();
        if (isMounted) {
          setUser(data.user || data);
        }
      } catch (error) {
        logout();
        if (isMounted) {
          setUser(null);
        }
      } finally {
        if (isMounted) {
          setLoadingUser(false);
        }
      }
    }

    loadCurrentUser();

    return () => {
      isMounted = false;
    };
  }, []);

  function handleAuthSuccess(authenticatedUser) {
    setUser(authenticatedUser);
    setShowAuth(false);
  }

  function handleLogout() {
    logout();
    setUser(null);
  }

  const isAdmin =
    user?.is_staff ||
    user?.is_superuser ||
    user?.role === "admin";

  return (
    <>
      <nav className={styles.navbar}>
        <div className={`container ${styles.inner}`}>
          <Link to="/" className={styles.logo}>
            <span className={styles.logoIcon}>🏥</span>
            <span className={styles.logoText}>MediCare AI</span>
          </Link>

          <div className={styles.links}>
            {navLinks.map((link) => (
              <Link
                key={link.to}
                to={link.to}
                className={`${styles.link} ${
                  location.pathname === link.to
                    ? styles.active
                    : ""
                }`}
              >
                {link.label}
              </Link>
            ))}

            {isAdmin && (
              <>
                <Link
                  to="/analytics"
                  className={`${styles.link} ${
                    location.pathname === "/analytics"
                      ? styles.active
                      : ""
                  }`}
                >
                  Analytics
                </Link>
                <Link
                  to="/admin/orders"
                  className={`${styles.link} ${
                    location.pathname === "/admin/orders"
                      ? styles.active
                      : ""
                  }`}
                >
                  Orders
                </Link>
              </>
            )}
          </div>

          <div className={styles.actions}>
            <Link to="/cart" className={styles.cartBtn}>
              🛒
              {cart.length > 0 && (
                <span className={styles.cartBadge}>
                  {cart.length}
                </span>
              )}
            </Link>

            {!loadingUser && !user && (
              <button
                className={styles.signInBtn}
                onClick={() => setShowAuth(true)}
              >
                Sign In
              </button>
            )}

            {!loadingUser && user && (
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: "12px",
                }}
              >
                <div
                  style={{
                    display: "flex",
                    flexDirection: "column",
                    textAlign: "right",
                  }}
                >
                  <strong style={{ fontSize: "13px" }}>
                    {user.email}
                  </strong>
                  <span
                    style={{
                      fontSize: "12px",
                      color: "#667085",
                    }}
                  >
                    {isAdmin
                      ? "Admin"
                      : user.role || "Customer"}
                  </span>
                </div>

                <button
                  className={styles.signInBtn}
                  onClick={handleLogout}
                >
                  Logout
                </button>
              </div>
            )}
          </div>
        </div>
      </nav>

      {showAuth && (
        <AuthModal
          onClose={() => setShowAuth(false)}
          onAuthSuccess={handleAuthSuccess}
        />
      )}
    </>
  );
}