import { useCallback, useEffect, useState } from "react";
import AdminLayout from "../components/AdminLayout";
import { fetchAdminReviews, fetchAdminConversationFeedback } from "../services/api";
import styles from "./AdminReviews.module.css";

export default function AdminReviews() {
  const [activeTab, setActiveTab] = useState("product"); // 'product' or 'chat'
  const [reviews, setReviews] = useState([]);
  const [feedbackList, setFeedbackList] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Filters state
  const [search, setSearch] = useState("");
  const [ratingFilter, setRatingFilter] = useState("");
  const [page, setPage] = useState(1);
  const [totalCount, setTotalCount] = useState(0);

  const loadReviewsData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const params = {
        page,
        search,
        rating: ratingFilter,
      };
      Object.keys(params).forEach((k) => {
        if (params[k] === "") delete params[k];
      });

      if (activeTab === "product") {
        const data = await fetchAdminReviews(params);
        setReviews(data.results || data);
        setTotalCount(data.count || (data.results ? data.results.length : 0));
      } else {
        const data = await fetchAdminConversationFeedback(params);
        setFeedbackList(data.results || data);
        setTotalCount(data.count || (data.results ? data.results.length : 0));
      }
    } catch (err) {
      setError("Failed to load feedback data.");
    } finally {
      setLoading(false);
    }
  }, [activeTab, page, search, ratingFilter]);

  useEffect(() => {
    loadReviewsData();
  }, [loadReviewsData]);

  // Calculations for summary stats
  const averageRating =
    activeTab === "product"
      ? reviews.length > 0
        ? (reviews.reduce((sum, r) => sum + r.rating, 0) / reviews.length).toFixed(1)
        : "0.0"
      : feedbackList.length > 0
      ? (feedbackList.reduce((sum, f) => sum + f.rating, 0) / feedbackList.length).toFixed(1)
      : "0.0";

  return (
    <AdminLayout title="Reviews & Feedback">
      <div className={styles.container}>
        {/* Navigation Tabs */}
        <div className={styles.tabs}>
          <button
            className={`${styles.tabBtn} ${activeTab === "product" ? styles.tabActive : ""}`}
            onClick={() => {
              setActiveTab("product");
              setPage(1);
              setSearch("");
              setRatingFilter("");
            }}
          >
            📦 Product Reviews
          </button>
          <button
            className={`${styles.tabBtn} ${activeTab === "chat" ? styles.tabActive : ""}`}
            onClick={() => {
              setActiveTab("chat");
              setPage(1);
              setSearch("");
              setRatingFilter("");
            }}
          >
            💬 Chatbot Feedback
          </button>
        </div>

        {/* Rating Summaries Card */}
        <div className={styles.summaryCard}>
          <div className={styles.summaryVal}>
            <h2>{averageRating} ★</h2>
            <span>Average Score</span>
          </div>

          <div className={styles.summaryStats}>
            <div>
              <strong>Total Records:</strong> {totalCount}
            </div>
            <div>
              <strong>Type:</strong> {activeTab === "product" ? "Order Reviews" : "Conversation Feedback"}
            </div>
          </div>
        </div>

        {/* Controls */}
        <div className={styles.controls}>
          <div className={styles.searchBox}>
            <span>🔍</span>
            <input
              type="text"
              placeholder="Search comments, emails, orders..."
              value={search}
              onChange={(e) => {
                setSearch(e.target.value);
                setPage(1);
              }}
            />
          </div>

          <div className={styles.filters}>
            <select
              value={ratingFilter}
              onChange={(e) => {
                setRatingFilter(e.target.value);
                setPage(1);
              }}
            >
              <option value="">All Ratings</option>
              <option value="5">5 Stars</option>
              <option value="4">4 Stars</option>
              <option value="3">3 Stars</option>
              <option value="2">2 Stars</option>
              <option value="1">1 Star</option>
            </select>
          </div>
        </div>

        {error && <div className={styles.errorAlert}>{error}</div>}

        {/* Data list */}
        {loading ? (
          <p className={styles.loading}>Loading reviews...</p>
        ) : activeTab === "product" ? (
          /* Product reviews list */
          reviews.length === 0 ? (
            <div className={styles.emptyState}>No product reviews found.</div>
          ) : (
            <div className={styles.tableWrapper}>
              <table className={styles.table}>
                <thead>
                  <tr>
                    <th>Order No</th>
                    <th>Customer</th>
                    <th>Product Items</th>
                    <th>Rating</th>
                    <th>Comment</th>
                    <th>Date</th>
                  </tr>
                </thead>
                <tbody>
                  {reviews.map((r) => (
                    <tr key={r.id}>
                      <td><strong>{r.order_number}</strong></td>
                      <td>{r.user_email || "Anonymous"}</td>
                      <td>
                        <div className={styles.products}>
                          {r.products?.map((item, idx) => (
                            <span key={idx}>
                              {item.product_emoji || "📦"} {item.product_name}
                            </span>
                          ))}
                        </div>
                      </td>
                      <td>
                        <span className={styles.ratingBadge}>{"★".repeat(r.rating)}</span>
                      </td>
                      <td className={styles.commentCell}>{r.comment || <span className={styles.noText}>No comment left</span>}</td>
                      <td>{new Date(r.created_at).toLocaleDateString()}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )
        ) : (
          /* Chatbot feedback list */
          feedbackList.length === 0 ? (
            <div className={styles.emptyState}>No chatbot feedback found.</div>
          ) : (
            <div className={styles.tableWrapper}>
              <table className={styles.table}>
                <thead>
                  <tr>
                    <th>Session/Conversation</th>
                    <th>Customer</th>
                    <th>Rating</th>
                    <th>Comment</th>
                    <th>Date</th>
                  </tr>
                </thead>
                <tbody>
                  {feedbackList.map((f) => (
                    <tr key={f.id}>
                      <td><strong>Conv #{f.conversation || f.conversation_id}</strong></td>
                      <td>{f.conversation_email || "Anonymous"}</td>
                      <td>
                        <span className={styles.ratingBadge}>{"★".repeat(f.rating)}</span>
                      </td>
                      <td className={styles.commentCell}>{f.comment || <span className={styles.noText}>No comment left</span>}</td>
                      <td>{new Date(f.created_at).toLocaleDateString()}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )
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
      </div>
    </AdminLayout>
  );
}
