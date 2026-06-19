import { useCallback, useEffect, useState } from "react";
import AdminLayout from "../components/AdminLayout";
import { fetchAdminConversations, fetchConversationById } from "../services/api";
import styles from "./AdminConversations.module.css";

export default function AdminConversations() {
  const [conversations, setConversations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Filters state
  const [search, setSearch] = useState("");
  const [langFilter, setLangFilter] = useState("");
  const [purchaseFilter, setPurchaseFilter] = useState("");
  const [complaintFilter, setComplaintFilter] = useState("");
  const [authFilter, setAuthFilter] = useState("");
  const [page, setPage] = useState(1);
  const [totalCount, setTotalCount] = useState(0);

  // Selected conversation state
  const [selectedConv, setSelectedConv] = useState(null);
  const [convDetails, setConvDetails] = useState(null);
  const [loadingDetails, setLoadingDetails] = useState(false);

  const loadConversations = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const params = {
        page,
        search,
        language: langFilter,
        purchase_state: purchaseFilter,
        complaint_state: complaintFilter,
        auth_status: authFilter,
      };

      Object.keys(params).forEach((key) => {
        if (params[key] === "") delete params[key];
      });

      const data = await fetchAdminConversations(params);
      setConversations(data.results || data);
      setTotalCount(data.count || (data.results ? data.results.length : 0));
    } catch (err) {
      setError("Failed to load conversations.");
    } finally {
      setLoading(false);
    }
  }, [page, search, langFilter, purchaseFilter, complaintFilter, authFilter]);

  useEffect(() => {
    loadConversations();
  }, [loadConversations]);

  const openConversationDetails = async (conv) => {
    setSelectedConv(conv);
    setConvDetails(null);
    setLoadingDetails(true);
    try {
      const data = await fetchConversationById(conv.id);
      setConvDetails(data);
    } catch (err) {
      console.error("Failed to load conversation details:", err);
    } finally {
      setLoadingDetails(false);
    }
  };

  return (
    <AdminLayout title="Chatbot Conversations">
      <div className={styles.container}>
        {/* Controls */}
        <div className={styles.controls}>
          <div className={styles.searchBox}>
            <span>🔍</span>
            <input
              type="text"
              placeholder="Search session, email, customer name..."
              value={search}
              onChange={(e) => {
                setSearch(e.target.value);
                setPage(1);
              }}
            />
          </div>

          <div className={styles.filters}>
            <select
              value={authFilter}
              onChange={(e) => {
                setAuthFilter(e.target.value);
                setPage(1);
              }}
            >
              <option value="">All Users</option>
              <option value="authenticated">Authenticated Only</option>
              <option value="anonymous">Anonymous Only</option>
            </select>

            <select
              value={langFilter}
              onChange={(e) => {
                setLangFilter(e.target.value);
                setPage(1);
              }}
            >
              <option value="">All Languages</option>
              <option value="en">English (en)</option>
              <option value="ar">Arabic (ar)</option>
            </select>

            <select
              value={purchaseFilter}
              onChange={(e) => {
                setPurchaseFilter(e.target.value);
                setPage(1);
              }}
            >
              <option value="">Purchase Flow</option>
              <option value="idle">Idle</option>
              <option value="awaiting_address">Awaiting Address</option>
              <option value="awaiting_phone">Awaiting Phone</option>
              <option value="awaiting_email">Awaiting Email</option>
              <option value="awaiting_confirmation">Awaiting Confirm</option>
            </select>

            <select
              value={complaintFilter}
              onChange={(e) => {
                setComplaintFilter(e.target.value);
                setPage(1);
              }}
            >
              <option value="">Complaint Flow</option>
              <option value="idle">Idle</option>
              <option value="awaiting_order_confirmation">Confirm Order</option>
              <option value="awaiting_description">Awaiting Desc</option>
            </select>
          </div>
        </div>

        {error && <div className={styles.errorAlert}>{error}</div>}

        {/* Conversations List */}
        {loading ? (
          <p className={styles.loading}>Loading conversations...</p>
        ) : conversations.length === 0 ? (
          <div className={styles.emptyState}>No conversations found.</div>
        ) : (
          <div className={styles.tableWrapper}>
            <table className={styles.table}>
              <thead>
                <tr>
                  <th>ID</th>
                  <th>User / Session</th>
                  <th>Customer Name</th>
                  <th>Last Intent</th>
                  <th>Language</th>
                  <th>Flow States</th>
                  <th>Feedback Rating</th>
                  <th>Last Active</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {conversations.map((c) => (
                  <tr key={c.id}>
                    <td>{c.id}</td>
                    <td>
                      {c.user_email ? (
                        <span className={styles.authUserBadge}>{c.user_email}</span>
                      ) : (
                        <code className={styles.guestToken} title={c.session_key}>
                          Guest: {c.session_key ? c.session_key.substring(0, 10) + "..." : "Local"}
                        </code>
                      )}
                    </td>
                    <td>{c.user_name || "-"}</td>
                    <td>
                      <span className={styles.intentBadge}>{c.last_intent || "unknown"}</span>
                    </td>
                    <td>{c.language.toUpperCase()}</td>
                    <td>
                      <div className={styles.statesWrapper}>
                        {c.purchase_state && (
                          <span className={styles.purchaseStateBadge}>Cart: {c.purchase_state}</span>
                        )}
                        {c.complaint_state && c.complaint_state !== "idle" && (
                          <span className={styles.complaintStateBadge}>Ticket: {c.complaint_state}</span>
                        )}
                        {!c.purchase_state && (!c.complaint_state || c.complaint_state === "idle") && (
                          <span className={styles.idleStateBadge}>Idle</span>
                        )}
                      </div>
                    </td>
                    <td>
                      {c.feedback_rating ? (
                        <span className={styles.ratingBadge}>{"⭐".repeat(c.feedback_rating)}</span>
                      ) : (
                        <span className={styles.noFeedback}>None</span>
                      )}
                    </td>
                    <td>{new Date(c.updated_at).toLocaleString([], { dateStyle: 'short', timeStyle: 'short' })}</td>
                    <td>
                      <button
                        className={styles.viewBtn}
                        onClick={() => openConversationDetails(c)}
                      >
                        View Transcript
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

        {/* Transcript Details Modal */}
        {selectedConv && (
          <div className={styles.modalOverlay} onClick={() => setSelectedConv(null)}>
            <div className={styles.modalContent} onClick={(e) => e.stopPropagation()}>
              <div className={styles.modalHeader}>
                <h2>Conversation #{selectedConv.id} Transcript</h2>
                <button className={styles.closeModal} onClick={() => setSelectedConv(null)}>✕</button>
              </div>

              <div className={styles.modalBody}>
                {loadingDetails ? (
                  <p className={styles.loading}>Loading chat history...</p>
                ) : convDetails ? (
                  <>
                    <div className={styles.metaGrid}>
                      <div><strong>Client ID:</strong> {convDetails.session_key}</div>
                      <div><strong>Customer name:</strong> {convDetails.user_name || "Not provided"}</div>
                      <div><strong>Language:</strong> {convDetails.language.toUpperCase()}</div>
                      <div><strong>Phone:</strong> {convDetails.phone || "Not provided"}</div>
                      <div><strong>Email:</strong> {convDetails.email || "Not provided"}</div>
                      <div><strong>Address:</strong> {convDetails.address || "Not provided"}</div>
                      {convDetails.ticket_number && (
                        <div>
                          <strong>Linked Support Ticket:</strong>{" "}
                          <span className={styles.ticketLink}>{convDetails.ticket_number}</span>
                        </div>
                      )}
                      {convDetails.feedback && (
                        <div className={styles.feedbackBox}>
                          <strong>Feedback Score:</strong> {convDetails.feedback.rating}/5
                          {convDetails.feedback.comment && <p>"{convDetails.feedback.comment}"</p>}
                        </div>
                      )}
                    </div>

                    <div className={styles.chatSection}>
                      <h3>Chronological Messages</h3>
                      <div className={styles.chatTranscript}>
                        {convDetails.messages?.length === 0 ? (
                          <p className={styles.noChat}>No messages in this conversation yet.</p>
                        ) : (
                          convDetails.messages?.map((msg, i) => (
                            <div
                              key={i}
                              className={`${styles.chatMessage} ${
                                msg.role === "user" ? styles.chatUser : styles.chatAssistant
                              }`}
                            >
                              <span className={styles.chatSender}>
                                {msg.role === "user" ? "Customer" : "MediCare AI"}
                              </span>
                              <p>{msg.content}</p>
                              <span className={styles.chatTime}>
                                {new Date(msg.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                              </span>
                            </div>
                          ))
                        )}
                      </div>
                    </div>
                  </>
                ) : (
                  <p>Could not retrieve transcript.</p>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </AdminLayout>
  );
}
