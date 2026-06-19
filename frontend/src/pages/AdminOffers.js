import { useCallback, useEffect, useState } from "react";
import AdminLayout from "../components/AdminLayout";
import {
  fetchAdminOffers,
  createOffer,
  updateOffer,
  deleteOffer,
  fetchProducts,
} from "../services/api";
import styles from "./AdminOffers.module.css";

export default function AdminOffers() {
  const [offers, setOffers] = useState([]);
  const [productsList, setProductsList] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  // Filters state
  const [search, setSearch] = useState("");
  const [activeFilter, setActiveFilter] = useState("");
  const [page, setPage] = useState(1);
  const [totalCount, setTotalCount] = useState(0);

  // Modals state
  const [editingOffer, setEditingOffer] = useState(null);
  const [showAddModal, setShowAddModal] = useState(false);
  const [confirmDeleteOffer, setConfirmDeleteOffer] = useState(null);

  // Form states
  const [formProduct, setFormProduct] = useState("");
  const [formDiscount, setFormDiscount] = useState("");
  const [formDiscountPrice, setFormDiscountPrice] = useState("");
  const [formIsActive, setFormIsActive] = useState(true);
  const [formUntil, setFormUntil] = useState("");

  const loadOffers = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const params = {
        page,
        search,
        is_active: activeFilter,
      };
      Object.keys(params).forEach((k) => {
        if (params[k] === "") delete params[k];
      });

      const data = await fetchAdminOffers(params);
      setOffers(data.results || data);
      setTotalCount(data.count || (data.results ? data.results.length : 0));
    } catch (err) {
      setError("Failed to load offers.");
    } finally {
      setLoading(false);
    }
  }, [page, search, activeFilter]);

  const loadProductsList = async () => {
    try {
      const data = await fetchProducts();
      setProductsList(data.results || data);
    } catch (err) {
      console.error("Failed to load products list for offer dropdown:", err);
    }
  };

  useEffect(() => {
    loadOffers();
    loadProductsList();
  }, [loadOffers]);

  const openAddModal = () => {
    setFormProduct(productsList[0]?.id || "");
    setFormDiscount("");
    setFormDiscountPrice("");
    setFormIsActive(true);
    setFormUntil("");
    setShowAddModal(true);
  };

  const openEditModal = (offer) => {
    setEditingOffer(offer);
    setFormProduct(offer.product);
    setFormDiscount(offer.discount_percent);
    setFormDiscountPrice(offer.discounted_price);
    setFormIsActive(offer.is_active);
    setFormUntil(offer.valid_until || "");
  };

  const handleSaveOffer = async (e) => {
    e.preventDefault();
    if (!formProduct || !formDiscount || !formDiscountPrice) return;

    setError(null);
    setSuccess(null);

    const payload = {
      product: parseInt(formProduct),
      discount_percent: parseInt(formDiscount),
      discounted_price: parseFloat(formDiscountPrice),
      is_active: formIsActive,
      valid_until: formUntil || null,
    };

    try {
      if (editingOffer) {
        await updateOffer(editingOffer.id, payload);
        setSuccess("Offer updated successfully.");
        setEditingOffer(null);
      } else {
        await createOffer(payload);
        setSuccess("New offer created successfully.");
        setShowAddModal(false);
      }
      await loadOffers();
    } catch (err) {
      const detail = err.discounted_price?.[0] || err.valid_until?.[0] || err.detail || "Failed to save offer.";
      setError(detail);
    }
  };

  const handleDelete = async () => {
    setError(null);
    setSuccess(null);
    try {
      await deleteOffer(confirmDeleteOffer.id);
      setSuccess("Offer deleted successfully.");
      setConfirmDeleteOffer(null);
      await loadOffers();
    } catch (err) {
      setError("Failed to delete offer.");
    }
  };

  return (
    <AdminLayout title="Offers & Discounts">
      <div className={styles.container}>
        {/* Controls */}
        <div className={styles.actionsBar}>
          <div className={styles.searchBox}>
            <span>🔍</span>
            <input
              type="text"
              placeholder="Search product name..."
              value={search}
              onChange={(e) => {
                setSearch(e.target.value);
                setPage(1);
              }}
            />
          </div>

          <div className={styles.actionsRight}>
            <select
              value={activeFilter}
              onChange={(e) => {
                setActiveFilter(e.target.value);
                setPage(1);
              }}
              className={styles.statusSelect}
            >
              <option value="">All Statuses</option>
              <option value="true">Active Only</option>
              <option value="false">Inactive Only</option>
            </select>

            <button className={styles.addBtn} onClick={openAddModal}>
              ➕ Create Offer
            </button>
          </div>
        </div>

        {error && <div className={styles.errorAlert}>{error}</div>}
        {success && <div className={styles.successAlert}>{success}</div>}

        {/* Offers List */}
        {loading ? (
          <p className={styles.loading}>Loading offers...</p>
        ) : offers.length === 0 ? (
          <div className={styles.emptyState}>No discount offers found.</div>
        ) : (
          <div className={styles.tableWrapper}>
            <table className={styles.table}>
              <thead>
                <tr>
                  <th>Product</th>
                  <th>Original Price</th>
                  <th>Discount %</th>
                  <th>Discounted Price</th>
                  <th>Expires On</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {offers.map((o) => {
                  const isExpired = o.valid_until && new Date(o.valid_until) < new Date();
                  const isActive = o.is_active && !isExpired;

                  return (
                    <tr key={o.id}>
                      <td>
                        <strong>{o.product_emoji || "📦"} {o.product_name}</strong>
                        <small className={styles.productId}>Product ID: {o.product}</small>
                      </td>
                      <td>EGP {Number(o.original_price).toLocaleString()}</td>
                      <td>
                        <span className={styles.discountBadge}>-{o.discount_percent}%</span>
                      </td>
                      <td>
                        <strong className={styles.discountPrice}>
                          EGP {Number(o.discounted_price).toLocaleString()}
                        </strong>
                      </td>
                      <td>
                        {o.valid_until ? (
                          <span className={isExpired ? styles.expiredText : ""}>
                            {new Date(o.valid_until).toLocaleDateString()}
                            {isExpired && " (Expired)"}
                          </span>
                        ) : (
                          <span className={styles.noExpiry}>No Expiry</span>
                        )}
                      </td>
                      <td>
                        <span className={`${styles.statusBadge} ${isActive ? styles.active : styles.inactive}`}>
                          {isActive ? "Active" : isExpired ? "Expired" : "Inactive"}
                        </span>
                      </td>
                      <td>
                        <div className={styles.rowActions}>
                          <button className={styles.editBtn} onClick={() => openEditModal(o)}>
                            Edit
                          </button>
                          <button
                            className={styles.deleteBtn}
                            onClick={() => setConfirmDeleteOffer(o)}
                          >
                            Delete
                          </button>
                        </div>
                      </td>
                    </tr>
                  );
                })}
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

        {/* Add/Edit Offer Modal */}
        {(showAddModal || editingOffer) && (
          <div className={styles.modalOverlay} onClick={() => { setShowAddModal(false); setEditingOffer(null); }}>
            <div className={styles.modalContent} onClick={(e) => e.stopPropagation()}>
              <div className={styles.modalHeader}>
                <h2>{editingOffer ? "Edit Offer" : "Create New Offer"}</h2>
                <button className={styles.closeModal} onClick={() => { setShowAddModal(false); setEditingOffer(null); }}>✕</button>
              </div>

              <form onSubmit={handleSaveOffer} className={styles.modalForm}>
                <div className={styles.formGroup}>
                  <label>Select Product</label>
                  <select
                    value={formProduct}
                    onChange={(e) => setFormProduct(e.target.value)}
                    disabled={!!editingOffer}
                    required
                  >
                    {productsList.map((p) => (
                      <option key={p.id} value={p.id}>
                        {p.emoji || "📦"} {p.name} (EGP {p.price})
                      </option>
                    ))}
                  </select>
                </div>

                <div className={styles.formRow}>
                  <div className={styles.formGroup}>
                    <label>Discount Percentage (%)</label>
                    <input
                      type="number"
                      required
                      min="1"
                      max="100"
                      value={formDiscount}
                      onChange={(e) => setFormDiscount(e.target.value)}
                      placeholder="e.g. 20"
                    />
                  </div>

                  <div className={styles.formGroup}>
                    <label>Discounted Price (EGP)</label>
                    <input
                      type="number"
                      step="0.01"
                      required
                      value={formDiscountPrice}
                      onChange={(e) => setFormDiscountPrice(e.target.value)}
                      placeholder="e.g. 799.00"
                    />
                  </div>
                </div>

                <div className={styles.formGroup}>
                  <label>Expiration Date (Optional)</label>
                  <input
                    type="date"
                    value={formUntil}
                    onChange={(e) => setFormUntil(e.target.value)}
                  />
                </div>

                <div className={styles.checkboxGroup}>
                  <input
                    type="checkbox"
                    id="offerActive"
                    checked={formIsActive}
                    onChange={(e) => setFormIsActive(e.target.checked)}
                  />
                  <label htmlFor="offerActive">Offer is Active</label>
                </div>

                <div className={styles.formActions}>
                  <button
                    type="button"
                    className={styles.cancelBtn}
                    onClick={() => { setShowAddModal(false); setEditingOffer(null); }}
                  >
                    Cancel
                  </button>
                  <button type="submit" className={styles.saveBtn}>
                    {editingOffer ? "Save Changes" : "Create Offer"}
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}

        {/* Delete Confirmation Modal */}
        {confirmDeleteOffer && (
          <div className={styles.modalOverlay} onClick={() => setConfirmDeleteOffer(null)}>
            <div className={styles.modalContentSmall} onClick={(e) => e.stopPropagation()}>
              <h2>Delete Offer</h2>
              <p>Are you sure you want to delete this offer for <strong>{confirmDeleteOffer.product_name}</strong>? This action cannot be undone.</p>
              <div className={styles.confirmButtons}>
                <button className={styles.cancelBtn} onClick={() => setConfirmDeleteOffer(null)}>
                  Cancel
                </button>
                <button className={styles.dangerBtn} onClick={handleDelete}>
                  Delete
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </AdminLayout>
  );
}
