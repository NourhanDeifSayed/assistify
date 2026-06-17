import { useEffect, useMemo, useState } from "react";
import { fetchAnalytics } from "../services/api";
import styles from "./Analytics.module.css";

function formatCurrency(value) {
  return new Intl.NumberFormat("en-EG", {
    style: "currency",
    currency: "EGP",
    maximumFractionDigits: 2,
  }).format(Number(value || 0));
}

function formatStatus(status) {
  return String(status || "")
    .replaceAll("_", " ")
    .replace(/\b\w/g, (letter) => letter.toUpperCase());
}

export default function Analytics() {
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let isMounted = true;

    async function loadAnalytics() {
      try {
        setLoading(true);
        setError("");
        const data = await fetchAnalytics();
        if (isMounted) {
          setAnalytics(data);
        }
      } catch (err) {
        if (isMounted) {
          setError(
            err?.detail ||
              "Unable to load analytics. Please sign in with an admin account."
          );
        }
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    }

    loadAnalytics();

    return () => {
      isMounted = false;
    };
  }, []);

  const maximumDailyOrders = useMemo(() => {
    if (!analytics?.daily_trends?.length) {
      return 1;
    }
    return Math.max(
      ...analytics.daily_trends.map((item) => item.orders),
      1
    );
  }, [analytics]);

  if (loading) {
    return (
      <main className={styles.page}>
        <div className={styles.messageCard}>
          Loading analytics...
        </div>
      </main>
    );
  }

  if (error) {
    return (
      <main className={styles.page}>
        <div className={styles.errorCard}>
          <h2>Analytics could not be loaded</h2>
          <p>{error}</p>
        </div>
      </main>
    );
  }

  const overview = analytics?.overview || {};
  const last30Days = analytics?.last_30_days || {};
  const dailyTrends = analytics?.daily_trends || [];
  const topProducts = analytics?.top_products || [];
  const ordersByStatus = analytics?.orders_by_status || {};
  const ticketsByStatus = analytics?.tickets_by_status || {};
  const feedbackDistribution = analytics?.feedback_distribution || {};

  const overviewCards = [
    {
      label: "Total Conversations",
      value: overview.total_conversations || 0,
    },
    {
      label: "Conversations With Orders",
      value: overview.conversations_with_orders || 0,
    },
    {
      label: "Total Orders",
      value: overview.total_orders || 0,
    },
    {
      label: "Total Revenue",
      value: formatCurrency(overview.total_revenue),
    },
    {
      label: "Conversion Rate",
      value: `${overview.conversation_to_order_rate || 0}%`,
    },
    {
      label: "Average Rating",
      value: `${overview.average_feedback_rating || 0} / 5`,
    },
    {
      label: "Total Tickets",
      value: overview.total_tickets || 0,
    },
    {
      label: "Active Tickets",
      value: overview.active_tickets || 0,
    },
  ];

  return (
    <main className={styles.page}>
      <header className={styles.header}>
        <div>
          <p className={styles.eyebrow}>Assistify Administration</p>
          <h1>Analytics Dashboard</h1>
          <p>
            Monitor conversations, orders, revenue, support tickets,
            and customer feedback.
          </p>
        </div>
      </header>

      <section className={styles.cardsGrid}>
        {overviewCards.map((card) => (
          <article className={styles.statCard} key={card.label}>
            <span>{card.label}</span>
            <strong>{card.value}</strong>
          </article>
        ))}
      </section>

      <section className={styles.section}>
        <div className={styles.sectionHeading}>
          <div>
            <h2>Last 30 Days</h2>
            <p>Recent activity across the platform.</p>
          </div>
        </div>

        <div className={styles.recentGrid}>
          <div>
            <span>Conversations</span>
            <strong>{last30Days.conversations || 0}</strong>
          </div>

          <div>
            <span>Orders</span>
            <strong>{last30Days.orders || 0}</strong>
          </div>

          <div>
            <span>Support Tickets</span>
            <strong>{last30Days.tickets || 0}</strong>
          </div>
        </div>
      </section>

      <section className={styles.section}>
        <div className={styles.sectionHeading}>
          <div>
            <h2>Daily Trends</h2>
            <p>Orders and revenue during the last seven days.</p>
          </div>
        </div>

        <div className={styles.trends}>
          {dailyTrends.map((item) => {
            const orderWidth =
              (item.orders / maximumDailyOrders) * 100;

            return (
              <article
                className={styles.trendRow}
                key={item.date}
              >
                <div className={styles.trendDate}>
                  <strong>{item.date}</strong>
                  <span>
                    {item.conversations} conversations
                  </span>
                </div>

                <div className={styles.barArea}>
                  <div className={styles.barTrack}>
                    <div
                      className={styles.barFill}
                      style={{ width: `${orderWidth}%` }}
                    />
                  </div>

                  <span>
                    {item.orders} orders ·{" "}
                    {formatCurrency(item.revenue)}
                  </span>
                </div>

                <div className={styles.ticketCount}>
                  {item.tickets} tickets
                </div>
              </article>
            );
          })}
        </div>
      </section>

      <section className={styles.twoColumnGrid}>
        <article className={styles.section}>
          <div className={styles.sectionHeading}>
            <div>
              <h2>Order Status</h2>
              <p>Current order distribution.</p>
            </div>
          </div>

          <div className={styles.statusList}>
            {Object.entries(ordersByStatus).map(
              ([status, count]) => (
                <div key={status}>
                  <span>{formatStatus(status)}</span>
                  <strong>{count}</strong>
                </div>
              )
            )}
          </div>
        </article>

        <article className={styles.section}>
          <div className={styles.sectionHeading}>
            <div>
              <h2>Ticket Status</h2>
              <p>Support ticket distribution.</p>
            </div>
          </div>

          <div className={styles.statusList}>
            {Object.entries(ticketsByStatus).map(
              ([status, count]) => (
                <div key={status}>
                  <span>{formatStatus(status)}</span>
                  <strong>{count}</strong>
                </div>
              )
            )}

            {Object.keys(ticketsByStatus).length === 0 && (
              <p className={styles.emptyText}>
                No support tickets are available.
              </p>
            )}
          </div>
        </article>
      </section>

      <section className={styles.section}>
        <div className={styles.sectionHeading}>
          <div>
            <h2>Top Products</h2>
            <p>Products ranked by units sold and revenue.</p>
          </div>
        </div>

        <div className={styles.tableWrapper}>
          <table className={styles.table}>
            <thead>
              <tr>
                <th>Product</th>
                <th>Units Sold</th>
                <th>Orders</th>
                <th>Revenue</th>
              </tr>
            </thead>

            <tbody>
              {topProducts.map((product) => (
                <tr key={product.product}>
                  <td>{product.product}</td>
                  <td>{product.units_sold}</td>
                  <td>{product.orders_count}</td>
                  <td>{formatCurrency(product.revenue)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <section className={styles.section}>
        <div className={styles.sectionHeading}>
          <div>
            <h2>Feedback Distribution</h2>
            <p>Conversation ratings submitted by customers.</p>
          </div>
        </div>

        <div className={styles.feedbackGrid}>
          {[1, 2, 3, 4, 5].map((rating) => (
            <div key={rating}>
              <span>{rating} Star</span>
              <strong>
                {feedbackDistribution[String(rating)] || 0}
              </strong>
            </div>
          ))}
        </div>
      </section>
    </main>
  );
}