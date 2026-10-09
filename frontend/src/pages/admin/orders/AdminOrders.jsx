import { useEffect, useState } from "react";
import { apiRequest } from "../../../api";

function AdminOrders() {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const fetchOrders = async () => {
    const token = localStorage.getItem("access_token");

    if (!token) {
      setError(
        "برای ورود به پنل مدیریت ابتدا وارد حساب کاربری شوید."
      );
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      setError("");

      const response = await apiRequest(
        "/api/orders/admin/",
        {
          method: "GET",
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail ||
            "دریافت سفارش‌ها با خطا مواجه شد."
        );
      }

      setOrders(
        Array.isArray(data)
          ? data
          : data.results || []
      );
    } catch (err) {
      console.error(
        "خطا در دریافت سفارش‌های مدیریت:",
        err
      );

      setError(
        err.message ||
          "دریافت سفارش‌ها با خطا مواجه شد."
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchOrders();
  }, []);

  const updateShippingStatus = async (
    shippingId,
    status
  ) => {
    try {
      const response = await apiRequest(
        `/api/shipping/${shippingId}/`,
        {
          method: "PATCH",
          body: JSON.stringify({
            status,
          }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail ||
            "تغییر وضعیت ارسال با خطا مواجه شد."
        );
      }

      await fetchOrders();
    } catch (err) {
      console.error(
        "خطا در تغییر وضعیت ارسال:",
        err
      );

      setError(
        err.message ||
          "تغییر وضعیت ارسال با خطا مواجه شد."
      );
    }
  };

  const getNextShippingStatus = (status) => {
    const transitions = {
      pending: "processing",
      processing: "shipped",
      shipped: "delivered",
    };

    return transitions[status] || null;
  };

  const getOrderStatusLabel = (status) => {
    const labels = {
      pending: "در انتظار پرداخت",
      paid: "پرداخت شده",
      processing: "در حال پردازش",
      shipped: "ارسال شده",
      delivered: "تحویل شده",
      cancelled: "لغو شده",
    };

    return labels[status] || status;
  };

  const getShippingStatusLabel = (status) => {
    const labels = {
      pending: "در انتظار ارسال",
      processing: "در حال آماده‌سازی",
      shipped: "ارسال شده",
      delivered: "تحویل شده",
      returned: "مرجوع شده",
    };

    return labels[status] || status;
  };

  if (loading) {
    return (
      <section dir="rtl">
        <h2>پنل مدیریت سفارش‌ها</h2>
        <p>در حال دریافت سفارش‌ها...</p>
      </section>
    );
  }

  return (
    <section
      dir="rtl"
      style={{
        padding: "24px 0",
      }}
    >
      <h2>پنل مدیریت سفارش‌ها</h2>

      {error && (
        <p
          style={{
            color: "red",
            marginBottom: "20px",
          }}
        >
          {error}
        </p>
      )}

      {orders.length === 0 ? (
        <p>هیچ سفارشی وجود ندارد.</p>
      ) : (
        orders.map((order) => {
          const shippingAddress =
            order.shipping_address;

          const shipping =
            order.shipping;

          const nextShippingStatus =
            shipping
              ? getNextShippingStatus(
                  shipping.status
                )
              : null;

          return (
            <article
              key={order.id}
              style={{
                border: "1px solid #ddd",
                borderRadius: "12px",
                padding: "20px",
                marginBottom: "20px",
              }}
            >
              <h3>
                سفارش {order.order_number}
              </h3>

              <p>
                مشتری:{" "}
                {order.customer_name ||
                  order.customer?.username ||
                  order.customer ||
                  "—"}
              </p>

              <p>
                وضعیت سفارش:{" "}
                <strong>
                  {getOrderStatusLabel(
                    order.status
                  )}
                </strong>
              </p>

              <p>
                مبلغ کل:{" "}
                {Number(
                  order.total_price
                ).toLocaleString("fa-IR")}{" "}
                تومان
              </p>

              <p>
                تاریخ ثبت:{" "}
                {new Date(
                  order.created_at
                ).toLocaleString("fa-IR")}
              </p>

              {shippingAddress &&
                Object.keys(shippingAddress).length >
                  0 && (
                  <div>
                    <h4>آدرس ارسال</h4>

                    <p>
                      گیرنده:{" "}
                      {shippingAddress.receiver_name ||
                        "—"}
                    </p>

                    <p>
                      موبایل:{" "}
                      {shippingAddress.phone || "—"}
                    </p>

                    <p>
                      استان:{" "}
                      {shippingAddress.province || "—"}
                    </p>

                    <p>
                      شهر:{" "}
                      {shippingAddress.city || "—"}
                    </p>

                    <p>
                      آدرس:{" "}
                      {shippingAddress.address_line ||
                        "—"}
                    </p>

                    <p>
                      کد پستی:{" "}
                      {shippingAddress.postal_code ||
                        "—"}
                    </p>
                  </div>
                )}

              <div>
                <h4>وضعیت ارسال</h4>

                {shipping ? (
                  <>
                    <p>
                      وضعیت:{" "}
                      <strong>
                        {getShippingStatusLabel(
                          shipping.status
                        )}
                      </strong>
                    </p>

                    <p>
                      شرکت حمل:{" "}
                      {shipping.carrier || "—"}
                    </p>

                    <p>
                      کد رهگیری:{" "}
                      {shipping.tracking_number ||
                        "—"}
                    </p>

                    {shipping.shipped_at && (
                      <p>
                        زمان ارسال:{" "}
                        {new Date(
                          shipping.shipped_at
                        ).toLocaleString(
                          "fa-IR"
                        )}
                      </p>
                    )}

                    {shipping.delivered_at && (
                      <p>
                        زمان تحویل:{" "}
                        {new Date(
                          shipping.delivered_at
                        ).toLocaleString(
                          "fa-IR"
                        )}
                      </p>
                    )}

                    {nextShippingStatus && (
                      <button
                        type="button"
                        onClick={() =>
                          updateShippingStatus(
                            shipping.id,
                            nextShippingStatus
                          )
                        }
                        style={{
                          marginTop: "10px",
                          padding: "10px 16px",
                          cursor: "pointer",
                        }}
                      >
                        تغییر وضعیت ارسال به «
                        {getShippingStatusLabel(
                          nextShippingStatus
                        )}
                        »
                      </button>
                    )}
                  </>
                ) : (
                  <p>
                    برای این سفارش هنوز اطلاعات
                    ارسال ایجاد نشده است.
                  </p>
                )}
              </div>

              {order.items?.length > 0 && (
                <div>
                  <h4>اقلام سفارش</h4>

                  {order.items.map((item) => (
                    <div
                      key={item.id}
                      style={{
                        marginBottom: "8px",
                      }}
                    >
                      {item.product_name}
                      {" — "}
                      تعداد: {item.quantity}
                      {" — "}
                      {Number(
                        item.price_at_purchase
                      ).toLocaleString("fa-IR")}{" "}
                      تومان
                    </div>
                  ))}
                </div>
              )}
            </article>
          );
        })
      )}
    </section>
  );
}

export default AdminOrders;
