import { useCallback, useEffect, useState } from "react";
import AdminLayout from "../components/AdminLayout";
import {
  fetchProducts,
  adminCreateProduct,
  adminUpdateProduct,
  adminDeactivateProduct,
} from "../services/api";
import styles from "./AdminProducts.module.css";

const CATEGORIES = ["Devices", "Wellness", "Diagnostics", "Other"];

export default function AdminProducts() {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  const [search, setSearch] = useState("");
  const [categoryFilter, setCategoryFilter] = useState("");
  const [activeFilter, setActiveFilter] = useState("");
  const [stockFilter, setStockFilter] = useState("");
  const [minPrice, setMinPrice] = useState("");
  const [maxPrice, setMaxPrice] = useState("");
  const [ordering, setOrdering] = useState("id");
  const [page, setPage] = useState(1);
  const [totalCount, setTotalCount] = useState(0);

  const [editingProduct, setEditingProduct] = useState(null);
  const [showAddModal, setShowAddModal] = useState(false);
  const [confirmDeleteProduct, setConfirmDeleteProduct] = useState(null);

  const [formName, setFormName] = useState("");
  const [formDesc, setFormDesc] = useState("");
  const [formCategory, setFormCategory] = useState("Devices");
  const [formPrice, setFormPrice] = useState("");
  const [formStock, setFormStock] = useState("");
  const [formEmoji, setFormEmoji] = useState("📦");
  const [formImage, setFormImage] = useState("");
  const [formIsActive, setFormIsActive] = useState(true);
  const [formBenefits, setFormBenefits] = useState("");

  const loadProducts = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const params = {
        page,
        search,
        category: categoryFilter,
        is_active: activeFilter,
        stock_status: stockFilter,
        min_price: minPrice,
        max_price: maxPrice,
        ordering,
      };

      Object.keys(params).forEach((key) => {
        if (params[key] === "") delete params[key];
      });

      const queryParams = new URLSearchParams(params).toString();
      const token = localStorage.getItem("access_token");
      const res = await fetch(`http://localhost:8000/api/v1/products/?${queryParams}`, {
        headers: {
          "Content-Type": "application/json",
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
      });
      const responseData = await res.json();
      if (!res.ok) throw responseData;

      setProducts(responseData.results || responseData);
      setTotalCount(responseData.count || (responseData.results ? responseData.results.length : 0));
    } catch (err) {
      setError(err.detail || "Failed to load products.");
    } finally {
      setLoading(false);
    }
  }, [page, search, categoryFilter, activeFilter, stockFilter, minPrice, maxPrice, ordering]);

  useEffect(() => {
    loadProducts();
  }, [loadProducts]);

  const openAddModal = () => {
    setFormName("");
    setFormDesc("");
    setFormCategory("Devices");
    setFormPrice("");
    setFormStock("");
    setFormEmoji("📦");
    setFormImage("");
    setFormIsActive(true);
    setFormBenefits("");
    setShowAddModal(true);
  };

  const openEditModal = (product) => {
    setEditingProduct(product);
    setFormName(product.name);
    setFormDesc(product.description);
    setFormCategory(product.category || "Devices");
    setFormPrice(product.price);
    setFormStock(product.stock ?? 10);
    setFormEmoji(product.emoji || "📦");
    setFormImage(product.image || "");
    setFormIsActive(product.is_active);
    setFormBenefits(product.benefits ? product.benefits.map((b) => b.text).join("\n") : "");
  };

  const handleSaveProduct = async (e) => {
    e.preventDefault();
    if (!formName.trim() || !formPrice || formStock === "") return;

    setError(null);
    setSuccess(null);

    const payload = {
      name: formName.trim(),
      description: formDesc.trim(),
      category: formCategory,
      price: parseFloat(formPrice),
      stock: parseInt(formStock),
      emoji: formEmoji,
      image: formImage.trim(),
      is_active: formIsActive,
      benefits: formBenefits.split("\n").map((b) => b.trim()).filter((b) => b),
    };

    try {
      if (editingProduct) {
        await adminUpdateProduct(editingProduct.id, payload);
        setSuccess(`Product '${formName}' updated successfully.`);
        setEditingProduct(null);
      } else {
        await adminCreateProduct(payload);
        setSuccess(`Product '${formName}' created successfully.`);
        setShowAddModal(false);
      }
      await loadProducts();
    } catch (err) {
      setError(err.detail || err.message || "Failed to save product.");
    }
  };

  const handleDeactivate = async () => {
    setError(null);
    setSuccess(null);
    try {
      await adminDeactivateProduct(confirmDeleteProduct.id);
      setSuccess(`Product '${confirmDeleteProduct.name}' deactivated successfully.`);
      setConfirmDeleteProduct(null);
      await loadProducts();
    } catch (err) {
      setError("Failed to deactivate product.");
    }
  };

  const handleStockAdjust = async (product, amount) => {
    const newStock = Math.max(0, (product.stock ?? 0) + amount);
    try {
      await adminUpdateProduct(product.id, { stock: newStock });
      await loadProducts();
    } catch (err) {
      setError("Failed to adjust stock.");
    }
  };

  return (
    <AdminLayout title="Products Management">
      <div className={styles.container}>
        <div className={styles.actionsBar}>
          <div className={styles.searchBox}>
            <span>🔍</span>
            <input
              type="text"
              placeholder="Search product name, category, ID..."
              value={search}
              onChange={(e) => {
                setSearch(e.target.value);
                setPage(1);
              }}
            />
          </div>

          <button className={styles.addBtn} onClick={openAddModal}>
            ➕ Add New Product
          </button>
        </div>

        <div className={styles.filterGrid}>
          <select
            value={categoryFilter}
            onChange={(e) => {
              setCategoryFilter(e.target.value);
              setPage(1);
            }}
          >
            <option value="">All Categories</option>
            {CATEGORIES.map((c) => (
              <option key={c} value={c}>{c}</option>
            ))}
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
            <option value="false">Inactive Only</option>
          </select>

          <select
            value={stockFilter}
            onChange={(e) => {
              setStockFilter(e.target.value);
              setPage(1);
            }}
          >
            <option value="">All Stock Levels</option>
            <option value="instock">In Stock</option>
            <option value="outofstock">Out of Stock</option>
          </select>

          <div className={styles.priceRange}>
            <input
              type="number"
              placeholder="Min EGP"
              value={minPrice}
              onChange={(e) => {
                setMinPrice(e.target.value);
                setPage(1);
              }}
            />
            <span>-</span>
            <input
              type="number"
              placeholder="Max EGP"
              value={maxPrice}
              onChange={(e) => {
                setMaxPrice(e.target.value);
                setPage(1);
              }}
            />
          </div>

          <select
            value={ordering}
            onChange={(e) => {
              setOrdering(e.target.value);
              setPage(1);
            }}
          >
            <option value="id">Sort by: Default</option>
            <option value="name">Name (A-Z)</option>
            <option value="-name">Name (Z-A)</option>
            <option value="price">Price (Low to High)</option>
            <option value="-price">Price (High to Low)</option>
            <option value="stock">Stock (Low to High)</option>
            <option value="-stock">Stock (High to Low)</option>
          </select>
        </div>

        {error && <div className={styles.errorAlert}>{error}</div>}
        {success && <div className={styles.successAlert}>{success}</div>}

        {loading ? (
          <p className={styles.loading}>Loading products...</p>
        ) : products.length === 0 ? (
          <div className={styles.emptyState}>No products found.</div>
        ) : (
          <div className={styles.tableWrapper}>
            <table className={styles.table}>
              <thead>
                <tr>
                  <th>Emoji/Image</th>
                  <th>Product Name</th>
                  <th>Category</th>
                  <th>Price</th>
                  <th>Stock Count</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {products.map((p) => {
                  const isOutOfStock = (p.stock ?? 0) <= 0;
                  return (
                    <tr key={p.id} className={!p.is_active ? styles.inactiveRow : ""}>
                      <td className={styles.emojiCell}>
                        {p.image ? (
                          <img src={p.image} alt={p.name} className={styles.productImg} />
                        ) : (
                          <span className={styles.largeEmoji}>{p.emoji || "📦"}</span>
                        )}
                      </td>
                      <td>
                        <strong>{p.name}</strong>
                        <small className={styles.productId}>ID: {p.id}</small>
                      </td>
                      <td>
                        <span className={styles.catBadge}>{p.category || "Devices"}</span>
                      </td>
                      <td>EGP {Number(p.price).toLocaleString()}</td>
                      <td>
                        <div className={styles.stockControl}>
                          <button onClick={() => handleStockAdjust(p, -1)}>-</button>
                          <span className={isOutOfStock ? styles.outOfStock : ""}>
                            {p.stock ?? 0} {isOutOfStock && "(Out of Stock)"}
                          </span>
                          <button onClick={() => handleStockAdjust(p, 1)}>+</button>
                        </div>
                      </td>
                      <td>
                        <span className={`${styles.statusBadge} ${p.is_active ? styles.active : styles.inactive}`}>
                          {p.is_active ? "Active" : "Inactive"}
                        </span>
                      </td>
                      <td>
                        <div className={styles.rowActions}>
                          <button className={styles.editBtn} onClick={() => openEditModal(p)}>
                            Edit
                          </button>
                          {p.is_active && (
                            <button
                              className={styles.deactivateBtn}
                              onClick={() => setConfirmDeleteProduct(p)}
                            >
                              Deactivate
                            </button>
                          )}
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}

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

        {(showAddModal || editingProduct) && (
          <div className={styles.modalOverlay} onClick={() => { setShowAddModal(false); setEditingProduct(null); }}>
            <div className={styles.modalContent} onClick={(e) => e.stopPropagation()}>
              <div className={styles.modalHeader}>
                <h2>{editingProduct ? "Edit Product" : "Add New Product"}</h2>
                <button className={styles.closeModal} onClick={() => { setShowAddModal(false); setEditingProduct(null); }}>✕</button>
              </div>

              <form onSubmit={handleSaveProduct} className={styles.modalForm}>
                <div className={styles.formGroup}>
                  <label>Product Name</label>
                  <input
                    type="text"
                    required
                    value={formName}
                    onChange={(e) => setFormName(e.target.value)}
                  />
                </div>

                <div className={styles.formRow}>
                  <div className={styles.formGroup}>
                    <label>Category</label>
                    <select value={formCategory} onChange={(e) => setFormCategory(e.target.value)}>
                      {CATEGORIES.map((c) => (
                        <option key={c} value={c}>{c}</option>
                      ))}
                    </select>
                  </div>

                  <div className={styles.formGroup}>
                    <label>Emoji Icon</label>
                    <input
                      type="text"
                      maxLength="4"
                      value={formEmoji}
                      onChange={(e) => setFormEmoji(e.target.value)}
                    />
                  </div>
                </div>

                <div className={styles.formRow}>
                  <div className={styles.formGroup}>
                    <label>Price (EGP)</label>
                    <input
                      type="number"
                      step="0.01"
                      required
                      value={formPrice}
                      onChange={(e) => setFormPrice(e.target.value)}
                    />
                  </div>

                  <div className={styles.formGroup}>
                    <label>Stock Quantity</label>
                    <input
                      type="number"
                      required
                      value={formStock}
                      onChange={(e) => setFormStock(e.target.value)}
                    />
                  </div>
                </div>

                <div className={styles.formGroup}>
                  <label>Image URL (Optional)</label>
                  <input
                    type="text"
                    value={formImage}
                    onChange={(e) => setFormImage(e.target.value)}
                    placeholder="https://example.com/image.png"
                  />
                </div>

                <div className={styles.formGroup}>
                  <label>Description</label>
                  <textarea
                    rows="3"
                    required
                    value={formDesc}
                    onChange={(e) => setFormDesc(e.target.value)}
                  ></textarea>
                </div>

                <div className={styles.formGroup}>
                  <label>Benefits (One per line)</label>
                  <textarea
                    rows="3"
                    value={formBenefits}
                    onChange={(e) => setFormBenefits(e.target.value)}
                    placeholder="FDA Approved&#10;Highly Accurate"
                  ></textarea>
                </div>

                <div className={styles.checkboxGroup}>
                  <input
                    type="checkbox"
                    id="formIsActive"
                    checked={formIsActive}
                    onChange={(e) => setFormIsActive(e.target.checked)}
                  />
                  <label htmlFor="formIsActive">Product is Active</label>
                </div>

                <div className={styles.formActions}>
                  <button
                    type="button"
                    className={styles.cancelBtn}
                    onClick={() => { setShowAddModal(false); setEditingProduct(null); }}
                  >
                    Cancel
                  </button>
                  <button type="submit" className={styles.saveBtn}>
                    {editingProduct ? "Save Changes" : "Create Product"}
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}

        {confirmDeleteProduct && (
          <div className={styles.modalOverlay} onClick={() => setConfirmDeleteProduct(null)}>
            <div className={styles.modalContentSmall} onClick={(e) => e.stopPropagation()}>
              <h2>Deactivate Product</h2>
              <p>Are you sure you want to deactivate <strong>{confirmDeleteProduct.name}</strong>? It will be hidden from the store catalog and recommendations.</p>
              <div className={styles.confirmButtons}>
                <button className={styles.cancelBtn} onClick={() => setConfirmDeleteProduct(null)}>
                  Cancel
                </button>
                <button className={styles.dangerBtn} onClick={handleDeactivate}>
                  Deactivate
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </AdminLayout>
  );
}