import { useCallback, useEffect, useState } from "react";
import AdminLayout from "../components/AdminLayout";
import { fetchAdminTickets, replyToTicket, fetchConversationById } from "../services/api";
import styles from "./AdminTickets.module.css";

const ISSUE_LABELS = {
  damaged_item: "Damaged Item",
  missing_item: "Missing Item",
  delayed_order: "Delayed Order",
  wrong_item: "Wrong Item",
  refund_request: "Refund Request",
  other: "Other",
};

const PRIORITY_LABELS = {
  low: "Low",
  medium: "Medium",
  high: "High",
  urgent: "Urgent",
};

const STATUS_LABELS = {
  open: "Open",
  in_progress: "In Progress",
  waiting_for_customer: "Waiting for Customer",
  resolved: "Resolved",
  closed: "Closed",
};

export default function AdminTickets() {
  const [tickets, setTickets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  // Filters state
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [priorityFilter, setPriorityFilter] = useState("");
  const [categoryFilter, setCategoryFilter] = useState("");
  const [page, setPage] = useState(1);
  const [totalCount, setTotalCount] = useState(0);

  // Modal / Details state
  const [selectedTicket, setSelectedTicket] = useState(null);
  const [conversation, setConversation] = useState(null);
  const [loadingConv, setLoadingConv] = useState(false);
  const [replyText, setReplyText] = useState("");
  const [replyStatus, setReplyStatus] = useState("in_progress");
  const [submittingReply, setSubmittingReply] = useState(false);

  const loadTickets = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const params = {
        page,
        search,
        status: statusFilter,
        priority: priorityFilter,
        category: categoryFilter,
      };
      // Clean empty params
      Object.keys(params).forEach((key) => {
        if (!params[key]) delete params[key];
      });

      const data = await fetchAdminTickets(params);
      setTickets(data.results || data);
      setTotalCount(data.count || (data.results ? data.results.length : 0));
    } catch (err) {
      setError(err.detail || "Failed to load support tickets.");
    } finally {
      setLoading(false);
    }
  }, [page, search, statusFilter, priorityFilter, categoryFilter]);

  useEffect(() => {
    loadTickets();
  }, [loadTickets]);

  const openTicketDetails = async (ticket) => {
    setSelectedTicket(ticket);
    setReplyText(ticket.admin_response || "");
    setReplyStatus(ticket.status === "open" ? "in_progress" : ticket.status);
    setConversation(null);

    if (ticket.conversation) {
      setLoadingConv(true);
      try {
        const data = await fetchConversationById(ticket.conversation);
        setConversation(data);
      } catch (err) {
        console.error("Failed to load conversation history:", err);
      } finally {
        setLoadingConv(false);
      }
    }
  };

  const handleReplySubmit = async (e) => {
    e.preventDefault();
    if (!replyText.trim()) return;

    setSubmittingReply(true);
    setError(null);
    setSuccess(null);

    try {
      const updatedTicket = await replyToTicket(selectedTicket.ticket_number, {
        response: replyText.trim(),
        status: replyStatus,
      });
      setSuccess(`Ticket ${selectedTicket.ticket_number} updated successfully.`);
      setSelectedTicket(updatedTicket);
      await loadTickets();
      // Close modal
      setSelectedTicket(null);
    } catch (err) {
      setError(err.detail || "Failed to submit response.");
    } finally {
      setSubmittingReply(false);
    }
  };

  const markAsResolved = async () => {
    setSubmittingReply(true);
    setError(null);
    setSuccess(null);
    try {
      const updatedTicket = await replyToTicket(selectedTicket.ticket_number, {
        response: replyText.trim() || "Ticket marked as resolved by admin.",
        status: "resolved",
      });
      setSuccess(`Ticket ${selectedTicket.ticket_number} resolved successfully.`);
      setSelectedTicket(updatedTicket);
      await loadTickets();
      setSelectedTicket(null);
    } catch (err) {
      setError(err.detail || "Failed to resolve ticket.");
    } finally {
      setSubmittingReply(false);
    }
  };

  return (
    <AdminLayout title="Support Tickets">
      <div className={styles.container}>
        {/* Search & Filter Controls */}
        <div className={styles.controls}>
          <div className={styles.searchBox}>
            <span>🔍</span>
            <input
              type="text"
              placeholder="Search ticket number, customer, description..."
              value={search}
              onChange={(e) => {
                setSearch(e.target.value);
                setPage(1);
              }}
            />
          </div>

          <div className={styles.filters}>
            <select
              value={statusFilter}
              onChange={(e) => {
                setStatusFilter(e.target.value);
                setPage(1);
              }}
            >
              <option value="">All Statuses</option>
              {Object.entries(STATUS_LABELS).map(([k, v]) => (
                <option key={k} value={k}>{v}</option>
              ))}
            </select>

            <select
              value={priorityFilter}
              onChange={(e) => {
                setPriorityFilter(e.target.value);
                setPage(1);
              }}
            >
              <option value="">All Priorities</option>
              {Object.entries(PRIORITY_LABELS).map(([k, v]) => (
                <option key={k} value={k}>{v}</option>
              ))}
            </select>

            <select
              value={categoryFilter}
              onChange={(e) => {
                setCategoryFilter(e.target.value);
                setPage(1);
              }}
            >
              <option value="">All Categories</option>
              {Object.entries(ISSUE_LABELS).map(([k, v]) => (
                <option key={k} value={k}>{v}</option>
              ))}
            </select>
          </div>
        </div>

        {error && <div className={styles.errorAlert}>{error}</div>}
        {success && <div className={styles.successAlert}>{success}</div>}

        {/* Tickets List */}
        {loading ? (
          <p className={styles.loading}>Loading tickets...</p>
        ) : tickets.length === 0 ? (
          <div className={styles.emptyState}>No support tickets found.</div>
        ) : (
          <div className={styles.tableWrapper}>
            <table className={styles.table}>
              <thead>
                <tr>
                  <th>Ticket Number</th>
                  <th>Customer</th>
                  <th>Category</th>
                  <th>Subject/Issue</th>
                  <th>Priority</th>
                  <th>Status</th>
                  <th>Created At</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {tickets.map((t) => (
                  <tr key={t.id}>
                    <td><strong>{t.ticket_number}</strong></td>
                    <td>{t.user_email || "Anonymous"}</td>
                    <td>
                      <span className={styles.categoryBadge}>
                        {ISSUE_LABELS[t.issue_type] || t.issue_type}
                      </span>
                    </td>
                    <td className={styles.descCell}>{t.description}</td>
                    <td>
                      <span className={`${styles.priority} ${styles[`priority_${t.priority}`]}`}>
                        {PRIORITY_LABELS[t.priority] || t.priority}
                      </span>
                    </td>
                    <td>
                      <span className={`${styles.status} ${styles[`status_${t.status}`]}`}>
                        {STATUS_LABELS[t.status] || t.status}
                      </span>
                    </td>
                    <td>{new Date(t.created_at).toLocaleDateString()}</td>
                    <td>
                      <button
                        className={styles.viewBtn}
                        onClick={() => openTicketDetails(t)}
                      >
                        Details / Reply
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

        {/* Details / Reply Modal */}
        {selectedTicket && (
          <div className={styles.modalOverlay} onClick={() => setSelectedTicket(null)}>
            <div className={styles.modalContent} onClick={(e) => e.stopPropagation()}>
              <div className={styles.modalHeader}>
                <h2>Ticket {selectedTicket.ticket_number} Details</h2>
                <button className={styles.closeModal} onClick={() => setSelectedTicket(null)}>✕</button>
              </div>

              <div className={styles.modalBody}>
                <div className={styles.detailGrid}>
                  <div>
                    <strong>Customer:</strong> {selectedTicket.user_email || "Anonymous"}
                  </div>
                  <div>
                    <strong>Category:</strong> {ISSUE_LABELS[selectedTicket.issue_type] || selectedTicket.issue_type}
                  </div>
                  <div>
                    <strong>Priority:</strong> {PRIORITY_LABELS[selectedTicket.priority] || selectedTicket.priority}
                  </div>
                  <div>
                    <strong>Status:</strong> {STATUS_LABELS[selectedTicket.status] || selectedTicket.status}
                  </div>
                  {selectedTicket.order_number && (
                    <div>
                      <strong>Linked Order:</strong> {selectedTicket.order_number}
                    </div>
                  )}
                  {selectedTicket.resolved_at && (
                    <div>
                      <strong>Resolved At:</strong> {new Date(selectedTicket.resolved_at).toLocaleString()}
                    </div>
                  )}
                  {selectedTicket.assigned_to_email && (
                    <div>
                      <strong>Assigned Admin:</strong> {selectedTicket.assigned_to_email}
                    </div>
                  )}
                </div>

                <div className={styles.complaintSection}>
                  <h3>Full Complaint Description</h3>
                  <div className={styles.complaintText}>{selectedTicket.description}</div>
                </div>

                {/* Conversation History */}
                {selectedTicket.conversation && (
                  <div className={styles.chatSection}>
                    <h3>Attached Conversation History</h3>
                    {loadingConv ? (
                      <p>Loading chat history...</p>
                    ) : conversation ? (
                      <div className={styles.chatTranscript}>
                        {conversation.messages?.map((msg, i) => (
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
                        ))}
                      </div>
                    ) : (
                      <p className={styles.noChat}>Could not load chat history.</p>
                    )}
                  </div>
                )}

                {/* Reply Form */}
                <form onSubmit={handleReplySubmit} className={styles.replyForm}>
                  <h3>Add Admin Reply & Update Status</h3>

                  <div className={styles.formGroup}>
                    <label>Admin Reply</label>
                    <textarea
                      placeholder="Type your response to the customer here..."
                      value={replyText}
                      onChange={(e) => setReplyText(e.target.value)}
                      rows="4"
                      required
                    ></textarea>
                  </div>

                  <div className={styles.formRow}>
                    <div className={styles.formGroup}>
                      <label>Update Status</label>
                      <select
                        value={replyStatus}
                        onChange={(e) => setReplyStatus(e.target.value)}
                      >
                        <option value="in_progress">In Progress</option>
                        <option value="waiting_for_customer">Waiting for Customer</option>
                        <option value="closed">Closed</option>
                      </select>
                    </div>

                    <div className={styles.formButtons}>
                      <button
                        type="button"
                        className={styles.resolveBtn}
                        onClick={markAsResolved}
                        disabled={submittingReply}
                      >
                        {submittingReply ? "Resolving..." : "Mark as Resolved"}
                      </button>

                      <button
                        type="submit"
                        className={styles.submitBtn}
                        disabled={submittingReply}
                      >
                        {submittingReply ? "Submitting..." : "Send Response"}
                      </button>
                    </div>
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
