import { useState } from "react";
import { NavLink, Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import styles from "./AdminLayout.module.css";

export default function AdminLayout({ children, title }) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  const handleLogout = () => {
    logout();
    navigate("/");
  };

  const navItems = [
    { path: "/analytics", label: "Dashboard", icon: "📊" },
    { path: "/admin/orders", label: "Orders", icon: "📦" },
    { path: "/admin/products", label: "Products", icon: "🩺" },
    { path: "/admin/tickets", label: "Support Tickets", icon: "🎫" },
    { path: "/admin/users", label: "Users & Customers", icon: "👥" },
    { path: "/admin/conversations", label: "Conversations", icon: "💬" },
    { path: "/admin/reviews", label: "Reviews & Feedback", icon: "⭐" },
    { path: "/admin/offers", label: "Offers & Discounts", icon: "🏷️" },
    { path: "/admin/faq", label: "FAQ & KB", icon: "💡" },
  ];

  const adminEmail = user?.email || "admin@assistify.com";
  const firstLetter = adminEmail.charAt(0).toUpperCase();

  return (
    <div className={styles.layout}>
      {/* Sidebar */}
      <aside className={`${styles.sidebar} ${isSidebarOpen ? styles.sidebarOpen : ""}`}>
        <div className={styles.sidebarHeader}>
          <span className={styles.logoIcon}>⚡</span>
          <span className={styles.logoText}>Assistify Admin</span>
          <button
            className={styles.closeBtn}
            onClick={() => setIsSidebarOpen(false)}
            aria-label="Close menu"
          >
            ✕
          </button>
        </div>

        <nav className={styles.nav}>
          {navItems.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                `${styles.navLink} ${isActive ? styles.navLinkActive : ""}`
              }
              onClick={() => setIsSidebarOpen(false)}
            >
              <span className={styles.navIcon}>{item.icon}</span>
              <span>{item.label}</span>
            </NavLink>
          ))}
        </nav>

        <div className={styles.sidebarFooter}>
          <div className={styles.adminProfile}>
            <div className={styles.avatar}>{firstLetter}</div>
            <div className={styles.adminInfo}>
              <span className={styles.adminEmail} title={adminEmail}>
                {adminEmail}
              </span>
              <span className={styles.adminRole}>Administrator</span>
            </div>
          </div>
          <button className={styles.logoutBtn} onClick={handleLogout}>
            <span>🚪</span> Logout
          </button>
        </div>
      </aside>

      {/* Main Container */}
      <div className={styles.main}>
        <header className={styles.header}>
          <div className={styles.headerLeft}>
            <button
              className={styles.menuToggle}
              onClick={() => setIsSidebarOpen(!isSidebarOpen)}
              aria-label="Toggle menu"
            >
              ☰
            </button>
            <h1 className={styles.pageTitle}>{title}</h1>
          </div>
          <Link to="/" className={styles.viewSiteBtn}>
            View Site
          </Link>
        </header>

        <main className={styles.content}>
          <div className={styles.contentInner}>{children}</div>
        </main>
      </div>
    </div>
  );
}
