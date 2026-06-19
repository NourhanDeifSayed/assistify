import { useCallback, useEffect, useState } from "react";
import AdminLayout from "../components/AdminLayout";
import {
  fetchAdminFAQs,
  createFAQ,
  updateFAQ,
  deleteFAQ,
} from "../services/api";
import styles from "./AdminFAQ.module.css";

const PRESET_CATEGORIES = [
  "General",
  "Ordering & Shipping",
  "Products & Stock",
  "Returns & Refunds",
  "Technical Support",
  "Other"
];

export default function AdminFAQ() {
  const [faqs, setFaqs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  // Filters state
  const [search, setSearch] = useState("");
  const [categoryFilter, setCategoryFilter] = useState("");
  const [publishFilter, setPublishFilter] = useState("");
  const [page, setPage] = useState(1);
  const [totalCount, setTotalCount] = useState(0);

  // Modals state
  const [editingFaq, setEditingFaq] = useState(null);
  const [showAddModal, setShowAddModal] = useState(false);
  const [confirmDeleteFaq, setConfirmDeleteFaq] = useState(null);

  // Form states
  const [formQuestion, setFormQuestion] = useState("");
  const [formAnswer, setFormAnswer] = useState("");
  const [formCategory, setFormCategory] = useState("General");
  const [formCustomCategory, setFormCustomCategory] = useState("");
  const [formKeywords, setFormKeywords] = useState("");
  const [formDisplayOrder, setFormDisplayOrder] = useState(0);
  const [formIsPublished, setFormIsPublished] = useState(true);

  // Dynamic unique categories from all FAQs
  const [allCategories, setAllCategories] = useState([]);

  const loadFAQs = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const params = {
        page,
        search,
      };

      if (categoryFilter) {
        params.category = categoryFilter;
      }
      if (publishFilter) {
        params.is_published = publishFilter;
      }

      const data = await fetchAdminFAQs(params);
      setFaqs(data.results || data);
      setTotalCount(data.count || (data.results ? data.results.length : 0));

      // Fetch all FAQs once (without filter) to extract all unique categories for filtering
      const allData = await fetchAdminFAQs({ page: 1 });
      const uniqueCats = Array.from(
        new Set((allData.results || allData || []).map((f) => f.category))
      ).filter(Boolean);
      setAllCategories(uniqueCats);
    } catch (err) {
      setError("Failed to load FAQs.");
    } finally {
      setLoading(false);
    }
  }, [page, search, categoryFilter, publishFilter]);

  useEffect(() => {
    loadFAQs();
  }, [loadFAQs]);

  const openAddModal = () => {
    setFormQuestion("");
    setFormAnswer("");
    setFormCategory("General");
    setFormCustomCategory("");
    setFormKeywords("");
    setFormDisplayOrder(0);
    setFormIsPublished(true);
    setShowAddModal(true);
  };

  const openEditModal = (faq) => {
    setEditingFaq(faq);
    setFormQuestion(faq.question);
    setFormAnswer(faq.answer);
    
    if (PRESET_CATEGORIES.includes(faq.category)) {
      setFormCategory(faq.category);
      setFormCustomCategory("");
    } else {
      setFormCategory("Other");
      setFormCustomCategory(faq.category);
    }
    
    setFormKeywords(faq.keywords || "");
    setFormDisplayOrder(faq.display_order);
    setFormIsPublished(faq.is_published);
  };

  const handleSaveFAQ = async (e) => {
    e.preventDefault();
    if (!formQuestion.trim() || !formAnswer.trim()) return;

    setError(null);
    setSuccess(null);

    const finalCategory =
      formCategory === "Other" ? formCustomCategory.trim() : formCategory;

    if (!finalCategory) {
      setError("Category is required.");
      return;
    }

    const payload = {
      question: formQuestion.trim(),
      answer: formAnswer.trim(),
      category: finalCategory,
      keywords: formKeywords.trim(),
      display_order: parseInt(formDisplayOrder) || 0,
      is_published: formIsPublished,
    };

    try {
      if (editingFaq) {
        await updateFAQ(editingFaq.id, payload);
        setSuccess("FAQ updated successfully.");
        setEditingFaq(null);
      } else {
        await createFAQ(payload);
        setSuccess("FAQ created successfully.");
        setShowAddModal(false);
        setPage(1);
      }
      loadFAQs();
    } catch (err) {
      setError(
        err.detail || err.message || "An error occurred while saving the FAQ."
      );
    }
  };

  const handleDeleteConfirm = async () => {
    if (!confirmDeleteFaq) return;
    setError(null);
    setSuccess(null);
    try {
      await deleteFAQ(confirmDeleteFaq.id);
      setSuccess("FAQ deleted successfully.");
      setConfirmDeleteFaq(null);
      if (faqs.length === 1 && page > 1) {
        setPage((p) => p - 1);
      } else {
        loadFAQs();
      }
    } catch (err) {
      setError("Failed to delete FAQ.");
      setConfirmDeleteFaq(null);
    }
  };

  const handleTogglePublish = async (faq) => {
    try {
      await updateFAQ(faq.id, { is_published: !faq.is_published });
      setSuccess(`FAQ status updated successfully.`);
      loadFAQs();
    } catch (err) {
      setError("Failed to update status.");
    }
  };

  return (
    <AdminLayout title="FAQ & Knowledge Base">
      <div className={styles.container}>
        {/* Alerts */}
        {error && <div className={styles.errorAlert}>⚠️ {error}</div>}
        {success && <div className={styles.successAlert}>✅ {success}</div>}

        {/* Actions & Filters */}
        <div className={styles.actionsBar}>
          <div className={styles.searchBox}>
            <span>🔍</span>
            <input
              type="text"
              placeholder="Search FAQ question, answer, keywords..."
              value={search}
              onChange={(e) => {
                setSearch(e.target.value);
                setPage(1);
              }}
            />
          </div>

          <div className={styles.actionsRight}>
            <select
              className={styles.statusSelect}
              value={categoryFilter}
              onChange={(e) => {
                setCategoryFilter(e.target.value);
                setPage(1);
              }}
            >
              <option value="">All Categories</option>
              {Array.from(new Set([...PRESET_CATEGORIES.filter(c => c !== "Other"), ...allCategories]))
                .sort()
                .map((cat) => (
                  <option key={cat} value={cat}>
                    {cat}
                  </option>
                ))}
            </select>

            <select
              className={styles.statusSelect}
              value={publishFilter}
              onChange={(e) => {
                setPublishFilter(e.target.value);
                setPage(1);
              }}
            >
              <option value="">All Statuses</option>
              <option value="true">Published</option>
              <option value="false">Draft</option>
            </select>

            <button className={styles.addBtn} onClick={openAddModal}>
              + Add FAQ
            </button>
          </div>
        </div>

        {/* Table view */}
        {loading ? (
          <div className={styles.loading}>Loading FAQs...</div>
        ) : faqs.length === 0 ? (
          <div className={styles.emptyState}>No FAQs found.</div>
        ) : (
          <div className={styles.tableWrapper}>
            <table className={styles.table}>
              <thead>
                <tr>
                  <th style={{ width: "80px" }}>Order</th>
                  <th style={{ width: "150px" }}>Category</th>
                  <th>Question & Answer</th>
                  <th style={{ width: "150px" }}>Status</th>
                  <th style={{ width: "180px" }}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {faqs.map((f) => (
                  <tr key={f.id}>
                    <td>
                      <span className={styles.orderBadge}>{f.display_order}</span>
                    </td>
                    <td>
                      <span className={styles.categoryBadge}>{f.category}</span>
                    </td>
                    <td>
                      <div className={styles.qaBlock}>
                        <strong className={styles.questionText}>Q: {f.question}</strong>
                        <p className={styles.answerText}>{f.answer}</p>
                        {f.keywords && (
                          <div className={styles.keywordsList}>
                            {f.keywords.split(",").map((kw, idx) => (
                              <span key={idx} className={styles.keywordTag}>
                                {kw.trim()}
                              </span>
                            ))}
                          </div>
                        )}
                      </div>
                    </td>
                    <td>
                      <span
                        className={`${styles.statusBadge} ${
                          f.is_published ? styles.active : styles.inactive
                        }`}
                        onClick={() => handleTogglePublish(f)}
                        style={{ cursor: "pointer" }}
                        title="Click to toggle status"
                      >
                        {f.is_published ? "Published" : "Draft"}
                      </span>
                    </td>
                    <td>
                      <div className={styles.rowActions}>
                        <button className={styles.editBtn} onClick={() => openEditModal(f)}>
                          Edit
                        </button>
                        <button
                          className={styles.deleteBtn}
                          onClick={() => setConfirmDeleteFaq(f)}
                        >
                          Delete
                        </button>
                      </div>
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
            <span>
              Page {page} of {Math.ceil(totalCount / 10)}
            </span>
            <button
              disabled={page >= Math.ceil(totalCount / 10)}
              onClick={() => setPage((p) => p + 1)}
            >
              Next
            </button>
          </div>
        )}

        {/* Add/Edit FAQ Modal */}
        {(showAddModal || editingFaq) && (
          <div
            className={styles.modalOverlay}
            onClick={() => {
              setShowAddModal(false);
              setEditingFaq(null);
            }}
          >
            <div className={styles.modalContent} onClick={(e) => e.stopPropagation()}>
              <div className={styles.modalHeader}>
                <h2>{editingFaq ? "Edit FAQ" : "Create New FAQ"}</h2>
                <button
                  className={styles.closeModal}
                  onClick={() => {
                    setShowAddModal(false);
                    setEditingFaq(null);
                  }}
                >
                  ✕
                </button>
              </div>

              <form onSubmit={handleSaveFAQ} className={styles.modalForm}>
                <div className={styles.formGroup}>
                  <label>Category</label>
                  <select
                    value={formCategory}
                    onChange={(e) => setFormCategory(e.target.value)}
                    required
                  >
                    {PRESET_CATEGORIES.map((cat) => (
                      <option key={cat} value={cat}>
                        {cat}
                      </option>
                    ))}
                  </select>
                </div>

                {formCategory === "Other" && (
                  <div className={styles.formGroup}>
                    <label>Custom Category Name</label>
                    <input
                      type="text"
                      placeholder="Enter custom category"
                      value={formCustomCategory}
                      onChange={(e) => setFormCustomCategory(e.target.value)}
                      required
                    />
                  </div>
                )}

                <div className={styles.formGroup}>
                  <label>Question</label>
                  <input
                    type="text"
                    placeholder="Enter question"
                    value={formQuestion}
                    onChange={(e) => setFormQuestion(e.target.value)}
                    required
                  />
                </div>

                <div className={styles.formGroup}>
                  <label>Answer</label>
                  <textarea
                    rows={4}
                    placeholder="Enter answer"
                    value={formAnswer}
                    onChange={(e) => setFormAnswer(e.target.value)}
                    required
                  />
                </div>

                <div className={styles.formGroup}>
                  <label>Keywords (Comma separated)</label>
                  <input
                    type="text"
                    placeholder="shipping, cost, delivery"
                    value={formKeywords}
                    onChange={(e) => setFormKeywords(e.target.value)}
                  />
                </div>

                <div className={styles.formRow}>
                  <div className={styles.formGroup}>
                    <label>Display Order (Priority)</label>
                    <input
                      type="number"
                      min="0"
                      value={formDisplayOrder}
                      onChange={(e) => setFormDisplayOrder(e.target.value)}
                    />
                  </div>

                  <div className={styles.checkboxGroup} style={{ marginTop: "24px" }}>
                    <input
                      type="checkbox"
                      id="formIsPublished"
                      checked={formIsPublished}
                      onChange={(e) => setFormIsPublished(e.target.checked)}
                    />
                    <label htmlFor="formIsPublished">Publish instantly</label>
                  </div>
                </div>

                <div className={styles.formActions}>
                  <button
                    type="button"
                    className={styles.cancelBtn}
                    onClick={() => {
                      setShowAddModal(false);
                      setEditingFaq(null);
                    }}
                  >
                    Cancel
                  </button>
                  <button type="submit" className={styles.saveBtn}>
                    {editingFaq ? "Save Changes" : "Create FAQ"}
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}

        {/* Delete Confirmation Modal */}
        {confirmDeleteFaq && (
          <div
            className={styles.modalOverlay}
            onClick={() => setConfirmDeleteFaq(null)}
          >
            <div className={styles.modalContentSmall} onClick={(e) => e.stopPropagation()}>
              <h3>Confirm Delete</h3>
              <p>
                Are you sure you want to delete the FAQ:{" "}
                <strong>"{confirmDeleteFaq.question}"</strong>? This action cannot be
                undone.
              </p>
              <div className={styles.confirmButtons}>
                <button
                  className={styles.cancelBtn}
                  onClick={() => setConfirmDeleteFaq(null)}
                >
                  Cancel
                </button>
                <button className={styles.dangerBtn} onClick={handleDeleteConfirm}>
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
