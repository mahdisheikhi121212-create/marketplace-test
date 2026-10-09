
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import {
  getCart,
  updateCartQuantity,
  removeFromCart,
  clearCart,
  getCartTotal,
} from "../../services/cart";

function Cart() {
  const [cart, setCart] = useState([]);

  useEffect(() => {
    setCart(getCart());
  }, []);

  const handleIncrease = (productId, quantity) => {
    const updatedCart = updateCartQuantity(
      productId,
      quantity + 1
    );

    setCart(updatedCart);
  };

  const handleDecrease = (productId, quantity) => {
    const updatedCart = updateCartQuantity(
      productId,
      quantity - 1
    );

    setCart(updatedCart);
  };

  const handleRemove = (productId) => {
    const updatedCart = removeFromCart(productId);
    setCart(updatedCart);
  };

  const handleClear = () => {
    clearCart();
    setCart([]);
  };

  const total = getCartTotal(cart);

  if (cart.length === 0) {
    return (
      <section className="cart-page" dir="rtl">
        <div className="cart-empty">
          <span className="section-eyebrow">
            Marketplace
          </span>

          <h2>سبد خرید شما خالی است</h2>

          <p>
            هنوز محصولی به سبد خرید اضافه نکرده‌اید.
          </p>

          <Link
            to="/products"
            className="cart-primary-button"
          >
            مشاهده محصولات
          </Link>
        </div>
      </section>
    );
  }

  return (
    <section className="cart-page" dir="rtl">
      <div className="cart-heading">
        <div>
          <span className="section-eyebrow">
            Marketplace
          </span>

          <h2>سبد خرید</h2>

          <p>
            محصولات انتخاب‌شده خود را بررسی و مدیریت کنید.
          </p>
        </div>

        <button
          type="button"
          className="cart-clear-button"
          onClick={handleClear}
        >
          خالی کردن سبد
        </button>
      </div>

      <div className="cart-layout">
        <div className="cart-items">
          {cart.map((item) => (
            <article
              className="cart-item"
              key={item.id}
            >
              <div className="cart-item-image">
                <span>
                  {item.category_name || "محصول"}
                </span>
              </div>

              <div className="cart-item-info">
                <span className="cart-item-category">
                  {item.category_name ||
                    "دسته‌بندی نامشخص"}
                </span>

                <h3>{item.name}</h3>

                <p>
                  {Number(item.price).toLocaleString(
                    "fa-IR"
                  )}{" "}
                  تومان
                </p>
              </div>

              <div className="cart-item-controls">
                <div className="quantity-control">
                  <button
                    type="button"
                    onClick={() =>
                      handleIncrease(
                        item.id,
                        item.quantity
                      )
                    }
                  >
                    +
                  </button>

                  <span>{item.quantity}</span>

                  <button
                    type="button"
                    onClick={() =>
                      handleDecrease(
                        item.id,
                        item.quantity
                      )
                    }
                  >
                    −
                  </button>
                </div>

                <strong>
                  {(
                    Number(item.price) * item.quantity
                  ).toLocaleString("fa-IR")}{" "}
                  تومان
                </strong>

                <button
                  type="button"
                  className="cart-remove-button"
                  onClick={() =>
                    handleRemove(item.id)
                  }
                >
                  حذف
                </button>
              </div>
            </article>
          ))}
        </div>

        <aside className="cart-summary">
          <h3>خلاصه سفارش</h3>

          <div className="cart-summary-row">
            <span>تعداد کالا</span>

            <strong>
              {cart.reduce(
                (count, item) =>
                  count + item.quantity,
                0
              )}
            </strong>
          </div>

          <div className="cart-summary-row cart-total-row">
            <span>مبلغ کل</span>

            <strong>
              {total.toLocaleString("fa-IR")} تومان
            </strong>
          </div>

          <Link
            to="/checkout"
            className="cart-checkout-button"
          >
            ادامه و پرداخت
          </Link>

          <Link
            to="/products"
            className="cart-continue-button"
          >
            ادامه خرید
          </Link>
        </aside>
      </div>
    </section>
  );
}

export default Cart;
