import { useEffect, useState } from "react";

import { apiRequest } from "../../services/api";

import {
  resetCheckoutSession,
} from "../../services/cart";


const CHECKOUT_ORDER_KEY =
  "checkout_order_id";


function Orders() {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchOrders = async () => {
      const accessToken =
        localStorage.getItem("access_token");

      const refreshToken =
        localStorage.getItem("refresh_token");

      if (!accessToken && !refreshToken) {
        setError(
          "برای مشاهده سفارش‌ها ابتدا وارد حساب کاربری خود شوید."
        );

        setLoading(false);

        return;
      }

      try {
        setLoading(true);
        setError("");

        const response = await apiRequest(
          "/api/orders/list/",
          {
            method: "GET",
          }
        );

        const data =
          await response.json();

        if (!response.ok) {
          throw new Error(
            data.detail ||
              "دریافت سفارش‌ها با خطا مواجه شد."
          );
        }

        const safeOrders =
          Array.isArray(data)
            ? data
            : [];

        setOrders(safeOrders);

        const checkoutOrderId =
          localStorage.getItem(
            CHECKOUT_ORDER_KEY
          );

        if (checkoutOrderId) {
          const checkoutOrder =
            safeOrders.find(
              (order) =>
                String(order.id) ===
                String(checkoutOrderId)
            );

          const completedStatuses = [
            "paid",
            "processing",
            "shipped",
            "delivered",
            "cancelled",
          ];

          if (
            checkoutOrder &&
            completedStatuses.includes(
              checkoutOrder.status
            )
          ) {
            resetCheckoutSession();
          }
        }
      } catch (err) {
        console.error(
          "خطا در دریافت سفارش‌ها:",
          err
        );

        setError(
          err.message ||
            "دریافت سفارش‌ها با خطا مواجه شد."
        );

        setOrders([]);
      } finally {
        setLoading(false);
      }
    };

    fetchOrders();
  }, []);


  const getOrderStatus = (status) => {
    const statusMap = {
      created: "ایجاد شده",
      pending: "در انتظار پرداخت",
      paid: "پرداخت شده",
      processing: "در حال پردازش",
      shipped: "ارسال شده",
      delivered: "تحویل داده شده",
      cancelled: "لغو شده",
      failed: "ناموفق",
    };

    return statusMap[status] || status;
  };


  const getShippingStatus = (status) => {
    const statusMap = {
      pending: "در انتظار ارسال",
      processing: "در حال آماده‌سازی",
      shipped: "ارسال شده",
      delivered: "تحویل داده شده",
      returned: "مرجوع شده",
    };

    return statusMap[status] || status;
  };


  if (loading) {
    return (
      <section dir="rtl">
        <h2>سفارش‌های من</h2>

        <p>
          در حال دریافت سفارش‌ها...
        </p>
      </section>
    );
  }


  if (error) {
    return (
      <section dir="rtl">
        <h2>سفارش‌های من</h2>

        <p style={{ color: "red" }}>
          {error}
        </p>
      </section>
    );
  }


  if (orders.length === 0) {
    return (
      <section dir="rtl">
        <h2>سفارش‌های من</h2>

        <p>
          هنوز سفارشی ثبت نشده است.
        </p>
      </section>
    );
  }


  return (
    <section dir="rtl">
      <h2>سفارش‌های من</h2>

      {orders.map((order) => {
        const shippingAddress =
          order.shipping_address;

        const shipping =
          order.shipping;

        return (
          <article
            key={order.id}
            style={{
              border: "1px solid #ddd",
              borderRadius: "10px",
              padding: "16px",
              marginBottom: "16px",
            }}
          >
            <h3>
              سفارش {order.order_number}
            </h3>

            <p>
              وضعیت سفارش:{" "}
              {getOrderStatus(
                order.status
              )}
            </p>

            <p>
              مبلغ کل:{" "}
              {Number(
                order.total_price
              ).toLocaleString(
                "fa-IR"
              )}{" "}
              تومان
            </p>

            <p>
              تاریخ ثبت:{" "}
              {new Date(
                order.created_at
              ).toLocaleString(
                "fa-IR"
              )}
            </p>

            {shipping && (
              <div>
                <h4>
                  وضعیت ارسال
                </h4>

                <p>
                  وضعیت:{" "}
                  {getShippingStatus(
                    shipping.status
                  )}
                </p>

                {shipping.carrier && (
                  <p>
                    شرکت حمل‌ونقل:{" "}
                    {shipping.carrier}
                  </p>
                )}

                {shipping.tracking_number && (
                  <p>
                    کد رهگیری:{" "}
                    {shipping.tracking_number}
                  </p>
                )}
              </div>
            )}

            {shippingAddress && (
              <div>
                <h4>
                  آدرس ارسال
                </h4>

                <p>
                  عنوان:{" "}
                  {shippingAddress.title ||
                    "—"}
                </p>

                <p>
                  گیرنده:{" "}
                  {shippingAddress
                    .receiver_name ||
                    "—"}
                </p>

                <p>
                  موبایل:{" "}
                  {shippingAddress.phone ||
                    "—"}
                </p>

                <p>
                  استان:{" "}
                  {shippingAddress.province ||
                    "—"}
                </p>

                <p>
                  شهر:{" "}
                  {shippingAddress.city ||
                    "—"}
                </p>

                <p>
                  آدرس:{" "}
                  {shippingAddress
                    .address_line ||
                    "—"}
                </p>

                <p>
                  کد پستی:{" "}
                  {shippingAddress
                    .postal_code ||
                    "—"}
                </p>
              </div>
            )}

            {order.items?.length > 0 && (
              <div>
                <h4>
                  اقلام سفارش
                </h4>

                {order.items.map(
                  (item) => (
                    <div key={item.id}>
                      <span>
                        {item.product_name}
                      </span>

                      {" — "}

                      <span>
                        تعداد:{" "}
                        {item.quantity}
                      </span>

                      {" — "}

                      <span>
                        {Number(
                          item.price_at_purchase
                        ).toLocaleString(
                          "fa-IR"
                        )}{" "}
                        تومان
                      </span>
                    </div>
                  )
                )}
              </div>
            )}

            {order.history?.length > 0 && (
              <div>
                <h4>
                  تاریخچه سفارش
                </h4>

                {order.history.map(
                  (history) => (
                    <div key={history.id}>
                      <p>
                        وضعیت:{" "}
                        {getOrderStatus(
                          history.status
                        )}
                      </p>

                      {history.description && (
                        <p>
                          {history.description}
                        </p>
                      )}

                      <p>
                        {new Date(
                          history.created_at
                        ).toLocaleString(
                          "fa-IR"
                        )}
                      </p>
                    </div>
                  )
                )}
              </div>
            )}
          </article>
        );
      })}
    </section>
  );
}


export default Orders;