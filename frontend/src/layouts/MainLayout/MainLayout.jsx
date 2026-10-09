import {
  Link,
  Outlet,
} from "react-router-dom";

import Header from "../../components/Header/Header";

function MainLayout() {
  return (
    <div
      className="app-shell"
      dir="rtl"
    >
      <Header />

      <main className="main-content">
        <Outlet />
      </main>

      <footer className="site-footer">
        <div className="footer-container">
          <div className="footer-brand">
            <Link
              to="/"
              className="footer-logo"
            >
              <span>مارکت</span>
              <strong>‌پلیس</strong>
            </Link>

            <p className="footer-brand-description">
              یک تجربه ساده، مطمئن و یکپارچه
              برای خرید و فروش از
              مارکت‌پلیس.
            </p>

            <div className="footer-brand-line" />
          </div>

          <div className="footer-links">
            <h3>دسترسی سریع</h3>

            <Link to="/">
              خانه
            </Link>

            <Link to="/products">
              محصولات
            </Link>

            <Link to="/cart">
              سبد خرید
            </Link>

            <Link to="/profile">
              پروفایل
            </Link>
          </div>

          <div className="footer-links">
            <h3>
              درباره مارکت‌پلیس
            </h3>

            <Link to="/about">
              درباره ما
            </Link>

            <Link to="/terms">
              قوانین و مقررات
            </Link>
          </div>

          <div className="footer-contact">
            <h3>تماس با ما</h3>

            <Link to="/contact">
              <p>
                پشتیبانی و پاسخگویی به
                سؤالات شما
              </p>
            </Link>
          </div>
        </div>

        <div className="footer-bottom">
          <p>
            تمام حقوق محفوظ است
            <span> © </span>
            <strong>
              مارکت‌پلیس
            </strong>
          </p>

          <span className="footer-bottom-note">
            ساخته‌شده برای یک تجربه خرید
            ساده و مطمئن
          </span>
        </div>
      </footer>
    </div>
  );
}

export default MainLayout;