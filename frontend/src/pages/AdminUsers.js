import { useCallback, useEffect, useState } from "react";
import AdminLayout from "../components/AdminLayout";
import { useAuth } from "../context/AuthContext";
import { fetchAdminUsers, updateAdminUser } from "../services/api";
import styles from "./AdminUsers.module.css";

export default function AdminUsers() {
  const { user: currentAdmin } = useAuth();
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  // Filters state
  const [search, setSearch] = useState("");
  const [roleFilter, setRoleFilter] = useState("");
  const [activeFilter, setActiveFilter] = useState("");
  const [staffFilter, setStaffFilter] = useState("");
  const [page, setPage] = useState(1);
  const [totalCount, setTotalCount] = useState(0);

  // Detail / edit modal state
  const [selectedUser, setSelectedUser] = useState(null);
  const [editRole, setEditRole] = useState("customer");
  const [editIsStaff, setEditIsStaff] = useState(false);
  const [editIsSuperuser, setEditIsSuperuser] = useState(false);
  const [editIsActive, setEditIsActive] = useState(true);
  const [editPhone, setEditPhone] = useState("");
  const [editAddress, setEditAddress] = useState("");
  const [savingUser, setSavingUser] = useState(false);

  const loadUsers = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const params = {
        page,
        search,
        role: roleFilter,
        is_active: activeFilter,
        is_staff: staffFilter,
      };

      Object.keys(params).forEach((key) => {
        if (params[key] === "") delete params[key];
      });

      const data = await fetchAdminUsers(params);
      setUsers(data.results || data);
      setTotalCount(data.count || (data.results ? data.results.length : 0));
    } catch (err) {
      setError(err.detail || "Failed to load registered users.");
    } finally {
      setLoading(false);
    }
  }, [page, search, roleFilter, activeFilter, staffFilter]);

  useEffect(() => {
    loadUsers();
  }, [loadUsers]);

  const openUserDetails = (user) => {
    setSelectedUser(user);
    setEditRole(user.role);
    setEditIsStaff(user.is_staff);
    setEditIsSuperuser(user.is_superuser);
    setEditIsActive(user.is_active);
    setEditPhone(user.phone || "");
    setEditAddress(user.address || "");
  };

  const handleSaveUser = async (e) => {
    e.preventDefault();
    setSavingUser(true);
    setError(null);
    setSuccess(null);

    const payload = {
      role: editRole,
      is_staff: editIsStaff,
      is_superuser: editIsSuperuser,
      is_active: editIsActive,
      phone: editPhone,
      address: editAddress,
    };

    try {
      await updateAdminUser(selectedUser.id, payload);
      setSuccess(`User '${selectedUser.email}' updated successfully.`);
      setSelectedUser(null);
      await loadUsers();
    } catch (err) {
      setError(err.detail || "Failed to update user details.");
    } finally {
      setSavingUser(false);
    }
  };

  const isRequesterSuperuser = currentAdmin?.is_superuser;

  return (
    <AdminLayout title="Users & Customers">
      <div className={styles.container}>
        {/* Controls */}
        <div className={styles.controls}>
          <div className={styles.searchBox}>
            <span>🔍</span>
            <input
              type="text"
              placeholder="Search username, email, ID..."
              value={search}
              onChange={(e) => {
                setSearch(e.target.value);
                setPage(1);
              }}
            />
          </div>

          <div className={styles.filters}>
            <select
              value={roleFilter}
              onChange={(e) => {
                setRoleFilter(e.target.value);
                setPage(1);
              }}
            >
              <option value="">All Roles</option>
              <option value="customer">Customer</option>
              <option value="admin">Admin</option>
            </select>

            <select
              value={activeFilter}
              onChange={(e) => {
                setActiveFilter(e.target.value);
                setPage(1);
              }}
            >
              <option value="">All Statuses</option>
              <option value="true">Active Only</option>
              <option value="false">Deactivated Only</option>
            </select>

            <select
              value={staffFilter}
              onChange={(e) => {
                setStaffFilter(e.target.value);
                setPage(1);
              }}
            >
              <option value="">Staff Status</option>
              <option value="true">Staff Only</option>
              <option value="false">Non-Staff Only</option>
            </select>
          </div>
        </div>

        {error && <div className={styles.errorAlert}>{error}</div>}
        {success && <div className={styles.successAlert}>{success}</div>}

        {/* User Table */}
        {loading ? (
          <p className={styles.loading}>Loading users...</p>
        ) : users.length === 0 ? (
          <div className={styles.emptyState}>No users found.</div>
        ) : (
          <div className={styles.tableWrapper}>
            <table className={styles.table}>
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Username</th>
                  <th>Email</th>
                  <th>Role</th>
                  <th>Staff Status</th>
                  <th>Account Status</th>
                  <th>Joined Date</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {users.map((u) => (
                  <tr key={u.id} className={!u.is_active ? styles.inactiveRow : ""}>
                    <td>{u.id}</td>
                    <td><strong>{u.username}</strong></td>
                    <td>{u.email}</td>
                    <td>
                      <span className={`${styles.roleBadge} ${styles[u.role]}`}>
                        {u.role === "admin" ? "Admin" : "Customer"}
                      </span>
                    </td>
                    <td>
                      <span className={`${styles.boolBadge} ${u.is_staff ? styles.yes : styles.no}`}>
                        {u.is_staff ? "Staff" : "Normal"}
                      </span>
                      {u.is_superuser && (
                        <span className={styles.superuserBadge}>Superuser</span>
                      )}
                    </td>
                    <td>
                      <span className={`${styles.statusBadge} ${u.is_active ? styles.active : styles.inactive}`}>
                        {u.is_active ? "Active" : "Deactivated"}
                      </span>
                    </td>
                    <td>{new Date(u.date_joined).toLocaleDateString()}</td>
                    <td>
                      <button
                        className={styles.viewBtn}
                        onClick={() => openUserDetails(u)}
                      >
                        Inspect / Edit
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* Pagination */}
        {totalCount > 10 && (
          <div className={styles.pagination}>
            <button
              disabled={page === 1}
              onClick={() => setPage((p) => p - 1)}
            >
              Previous
            </button>
            <span>Page {page} of {Math.ceil(totalCount / 10)}</span>
            <button
              disabled={page >= Math.ceil(totalCount / 10)}
              onClick={() => setPage((p) => p + 1)}
            >
              Next
            </button>
          </div>
        )}

        {/* User Inspect / Edit Modal */}
        {selectedUser && (
          <div className={styles.modalOverlay} onClick={() => setSelectedUser(null)}>
            <div className={styles.modalContent} onClick={(e) => e.stopPropagation()}>
              <div className={styles.modalHeader}>
                <h2>Inspect User: {selectedUser.username}</h2>
                <button className={styles.closeModal} onClick={() => setSelectedUser(null)}>✕</button>
              </div>

              <div className={styles.modalBody}>
                {/* User Summary */}
                <div className={styles.userSummary}>
                  <div className={styles.summaryItem}>
                    <strong>Username:</strong> {selectedUser.username}
                  </div>
                  <div className={styles.summaryItem}>
                    <strong>Email:</strong> {selectedUser.email}
                  </div>
                  <div className={styles.summaryItem}>
                    <strong>Joined:</strong> {new Date(selectedUser.date_joined).toLocaleString()}
                  </div>
                </div>

                {/* Edit Form */}
                <form onSubmit={handleSaveUser} className={styles.editForm}>
                  <h3>Modify Account Settings</h3>

                  <div className={styles.formRow}>
                    <div className={styles.formGroup}>
                      <label>Role</label>
                      <select
                        value={editRole}
                        onChange={(e) => setEditRole(e.target.value)}
                        disabled={selectedUser.is_superuser && !isRequesterSuperuser}
                      >
                        <option value="customer">Customer</option>
                        <option value="admin">Admin</option>
                      </select>
                    </div>

                    <div className={styles.formGroup}>
                      <label>Phone Number</label>
                      <input
                        type="text"
                        value={editPhone}
                        onChange={(e) => setEditPhone(e.target.value)}
                        placeholder="e.g. 01012345678"
                      />
                    </div>
                  </div>

                  <div className={styles.formGroup}>
                    <label>Default Address</label>
                    <textarea
                      rows="2"
                      value={editAddress}
                      onChange={(e) => setEditAddress(e.target.value)}
                      placeholder="Street name, Building No, City..."
                    ></textarea>
                  </div>

                  <div className={styles.checkboxes}>
                    <div className={styles.checkboxGroup}>
                      <input
                        type="checkbox"
                        id="editIsActive"
                        checked={editIsActive}
                        onChange={(e) => setEditIsActive(e.target.checked)}
                        disabled={selectedUser.is_superuser && !isRequesterSuperuser}
                      />
                      <label htmlFor="editIsActive">Account is Active</label>
                    </div>

                    <div className={styles.checkboxGroup}>
                      <input
                        type="checkbox"
                        id="editIsStaff"
                        checked={editIsStaff}
                        onChange={(e) => setEditIsStaff(e.target.checked)}
                        disabled={!isRequesterSuperuser}
                      />
                      <label htmlFor="editIsStaff" className={!isRequesterSuperuser ? styles.disabledLabel : ""}>
                        Staff Status {!isRequesterSuperuser && "(Superusers only)"}
                      </label>
                    </div>

                    <div className={styles.checkboxGroup}>
                      <input
                        type="checkbox"
                        id="editIsSuperuser"
                        checked={editIsSuperuser}
                        onChange={(e) => setEditIsSuperuser(e.target.checked)}
                        disabled={!isRequesterSuperuser}
                      />
                      <label htmlFor="editIsSuperuser" className={!isRequesterSuperuser ? styles.disabledLabel : ""}>
                        Superuser Privilege {!isRequesterSuperuser && "(Superusers only)"}
                      </label>
                    </div>
                  </div>

                  <div className={styles.formActions}>
                    <button
                      type="button"
                      className={styles.cancelBtn}
                      onClick={() => setSelectedUser(null)}
                    >
                      Cancel
                    </button>
                    <button type="submit" className={styles.saveBtn} disabled={savingUser}>
                      {savingUser ? "Saving..." : "Save Details"}
                    </button>
                  </div>
                </form>
              </div>
            </div>
          </div>
        )}
      </div>
    </AdminLayout>
  );
}
