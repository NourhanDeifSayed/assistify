import { Navigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function AdminRoute({ children }) {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div style={{ display: "flex", justifyContent: "center", alignItems: "center", minHeight: "100vh", background: "#f5f9ff" }}>
        <div style={{ display: "flex", gap: "6px" }}>
          <span className="loading-dot"></span>
          <span className="loading-dot"></span>
          <span className="loading-dot"></span>
        </div>
      </div>
    );
  }

  if (!user) {
    return <Navigate to="/" replace />;
  }

  const isAdmin =
    user.is_staff ||
    user.is_superuser ||
    user.role === "admin";

  if (!isAdmin) {
    return (
      <div style={{ display: "flex", flexDirection: "column", justifyContent: "center", alignItems: "center", minHeight: "80vh", padding: "24px", textAlign: "center" }}>
        <h1 style={{ fontSize: "64px", marginBottom: "16px" }}>🚫</h1>
        <h2 style={{ fontSize: "28px", color: "var(--text)", marginBottom: "8px" }}>Access Denied</h2>
        <p style={{ color: "var(--text-muted)", maxWidth: "480px", marginBottom: "24px" }}>
          You do not have administrative permissions to view this page. If you believe this is an error, please sign in with an administrator account.
        </p>
        <a href="/" className="btn-primary">Back to Home</a>
      </div>
    );
  }

  return children;
}
