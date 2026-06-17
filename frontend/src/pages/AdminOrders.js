import { useCallback, useEffect, useState } from "react";
import {
  fetchAdminOrders,
  updateOrderStatus,
} from "../services/api";
import styles from "./AdminOrders.module.css";

const STATUS_LABELS = {
  placed: "Placed",
  processing: "Processing",
  shipped: "Shipped",
  in_transit: "In Transit",
  delivered: "Delivered",
  cancelled: "Cancelled",
};

const NEXT_STATUSES = {
  placed: ["processing", "cancelled"],
  processing: ["shipped", "cancelled"],
  shipped: ["in_transit", "cancelled"],
  in_transit: ["delivered", "cancelled"],
  delivered: [],
  cancelled: [],
};

function formatCurrency(value) {
  return new Intl.NumberFormat("en-EG", {
    style: "currency",
    currency: "EGP",
  }).format(Number(value || 0));
}

function formatDate(value) {
  if (!value) {
    return "-";
  }
  return new Date(value).toLocaleString();
}

function getErrorMessage(error) {
  if (typeof error?.detail === "string") {
    return error.detail;
  }
  if (error?.status?.[0]) {
    return error.status[0];
  }
  if (error?.tracking_number?.[0]) {
    return error.tracking_number[0];
  }
  if (error?.location?.[0]) {
    return error.location[0];
  }
  return "Unable to complete the request.";
}

export default function AdminOrders() {
  const [orders, setOrders] = useState([]);
  const [drafts, setDrafts] = useState({});
  const [loading, setLoading] = useState(true);
  const [updatingOrder, setUpdatingOrder] = useState(null);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  const loadOrders = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const data = await fetchAdminOrders();
      const orderList = Array.isArray(data)
        ? data
        : data.results || [];
      setOrders(orderList);

      const initialDrafts = {};
      orderList.forEach((order) => {
        const availableStatuses =
          NEXT_STATUSES[order.status] || [];
        initialDrafts[order.order_number] = {
          status: availableStatuses[0] || "",
          location: "Warehouse",
          trackingNumber: "",
        };
      });
      setDrafts(initialDrafts);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadOrders();
  }, [loadOrders]);

  function updateDraft(orderNumber, field, value) {
    setDrafts((currentDrafts) => ({
      ...currentDrafts,
      [orderNumber]: {
        ...currentDrafts[orderNumber],
        [field]: value,
      },
    }));
  }

  async function handleStatusUpdate(order) {
    const draft = drafts[order.order_number];

    if (!draft?.status) {
      return;
    }

    if (!draft.location.trim()) {
      setError("Location is required.");
      return;
    }

    if (
      draft.status === "shipped" &&
      !draft.trackingNumber.trim() &&
      !order.tracking_number
    ) {
      setError(
        "Tracking number is required when the order is shipped."
      );
      return;
    }

    setError(null);
    setSuccess(null);
    setUpdatingOrder(order.order_number);

    try {
      await updateOrderStatus({
        orderNumber: order.order_number,
        status: draft.status,
        location: draft.location.trim(),
        trackingNumber: draft.trackingNumber.trim(),
      });

      setSuccess(
        `${order.order_number} updated successfully.`
      );
      await loadOrders();
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setUpdatingOrder(null);
    }
  }

  if (loading) {
    return (
      <main className={styles.page}>
        <div className="container">
          <p className={styles.message}>
            Loading orders...
          </p>
        </div>
      </main>
    );
  }

  return (
    <main className={styles.page}>
      <div className="container">
        <div className={styles.header}>
          <div>
            <p className={styles.eyebrow}>
              Assistify Administration
            </p>
            <h1>Orders Management</h1>
            <p className={styles.subtitle}>
              Review orders and update delivery progress.
            </p>
          </div>
          <button
            className={styles.refreshButton}
            onClick={loadOrders}
          >
            Refresh
          </button>
        </div>

        {error && (
          <div className={styles.error}>
            {error}
          </div>
        )}

        {success && (
          <div className={styles.success}>
            {success}
          </div>
        )}

        <div className={styles.summary}>
          <div className={styles.summaryCard}>
            <span>Total Orders</span>
            <strong>{orders.length}</strong>
          </div>

          <div className={styles.summaryCard}>
            <span>Placed</span>
            <strong>
              {
                orders.filter(
                  (order) => order.status === "placed"
                ).length
              }
            </strong>
          </div>

          <div className={styles.summaryCard}>
            <span>Delivered</span>
            <strong>
              {
                orders.filter(
                  (order) => order.status === "delivered"
                ).length
              }
            </strong>
          </div>

          <div className={styles.summaryCard}>
            <span>Revenue</span>
            <strong>
              {formatCurrency(
                orders.reduce(
                  (total, order) =>
                    total + Number(order.total || 0),
                  0
                )
              )}
            </strong>
          </div>
        </div>

        <div className={styles.tableWrapper}>
          <table className={styles.table}>
            <thead>
              <tr>
                <th>Order</th>
                <th>Customer</th>
                <th>Products</th>
                <th>Total</th>
                <th>Current Status</th>
                <th>Created</th>
                <th>Update Status</th>
              </tr>
            </thead>

            <tbody>
              {orders.map((order) => {
                const availableStatuses =
                  NEXT_STATUSES[order.status] || [];
                const draft =
                  drafts[order.order_number] || {};
                const isFinal =
                  availableStatuses.length === 0;

                return (
                  <tr key={order.order_number}>
                    <td>
                      <strong>
                        {order.order_number}
                      </strong>
                      {order.tracking_number && (
                        <small>
                          Tracking:{" "}
                          {order.tracking_number}
                        </small>
                      )}
                    </td>

                    <td>
                      {order.customer_email}
                    </td>

                    <td>
                      <div className={styles.products}>
                        {order.items?.map((item) => (
                          <span key={item.id}>
                            {item.product_emoji || "📦"}{" "}
                            {item.product_name} ×{" "}
                            {item.quantity}
                          </span>
                        ))}
                      </div>
                    </td>

                    <td>
                      {formatCurrency(order.total)}
                    </td>

                    <td>
                      <span
                        className={`${styles.status} ${
                          styles[
                            `status_${order.status}`
                          ] || ""
                        }`}
                      >
                        {STATUS_LABELS[order.status] ||
                          order.status}
                      </span>
                    </td>

                    <td>
                      {formatDate(order.created_at)}
                    </td>

                    <td>
                      {isFinal ? (
                        <span className={styles.finalStatus}>
                          No further updates
                        </span>
                      ) : (
                        <div className={styles.updateArea}>
                          <select
                            value={draft.status || ""}
                            onChange={(event) =>
                              updateDraft(
                                order.order_number,
                                "status",
                                event.target.value
                              )
                            }
                          >
                            {availableStatuses.map(
                              (status) => (
                                <option
                                  value={status}
                                  key={status}
                                >
                                  {STATUS_LABELS[status]}
                                </option>
                              )
                            )}
                          </select>

                          <input
                            type="text"
                            placeholder="Location"
                            value={draft.location || ""}
                            onChange={(event) =>
                              updateDraft(
                                order.order_number,
                                "location",
                                event.target.value
                              )
                            }
                          />

                          {draft.status === "shipped" && (
                            <input
                              type="text"
                              placeholder="Tracking number"
                              value={
                                draft.trackingNumber || ""
                              }
                              onChange={(event) =>
                                updateDraft(
                                  order.order_number,
                                  "trackingNumber",
                                  event.target.value
                                )
                              }
                            />
                          )}

                          <button
                            onClick={() =>
                              handleStatusUpdate(order)
                            }
                            disabled={
                              updatingOrder ===
                              order.order_number
                            }
                          >
                            {updatingOrder ===
                            order.order_number
                              ? "Updating..."
                              : "Update"}
                          </button>
                        </div>
                      )}
                    </td>
                  </tr>
                );
              })}

              {orders.length === 0 && (
                <tr>
                  <td
                    colSpan="7"
                    className={styles.empty}
                  >
                    No orders found.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </main>
  );
}