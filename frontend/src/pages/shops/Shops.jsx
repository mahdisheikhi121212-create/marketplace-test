import { Link } from "react-router-dom";

const shops = [
  {
    id: 1,
    name: "فروشگاه آریا",
    category: "پوشاک",
    description: "فروش انواع پوشاک با کیفیت و مناسب برای استفاده روزمره.",
    rating: "۴.۸",
    products: "۱۲۸",
    color: "shop-card-green",
  },
  {
    id: 2,
    name: "دیجیتال‌سنتر",
    category: "دیجیتال",
    description: "محصولات دیجیتال و لوازم جانبی برای زندگی هوشمندتر.",
    rating: "۴.۷",
    products: "۹۶",
    color: "shop-card-blue",
  },
  {
    id: 3,
    name: "خانه و زندگی",
    category: "خانه و زندگی",
    description: "محصولات کاربردی و زیبا برای خانه‌ای آرام‌تر و دلنشین‌تر.",
    rating: "۴.۹",
    products: "۷۴",
    color: "shop-card-gold",
  },
  {
    id: 4,
    name: "زیبایی‌خانه",
    category: "زیبایی",
    description: "محصولات منتخب حوزه زیبایی و مراقبت شخصی.",
    rating: "۴.۶",
    products: "۸۵",
    color: "shop-card-pink",
  },
];

function Shops() {
  return (
    <section className="shops-page" dir="rtl">
      <div className="shops-heading">
        <div>
          <span className="section-eyebrow">MARKETPLACE</span>

          <h2>فروشگاه‌ها</h2>

          <p>
            فروشگاه‌های مختلف را ببینید، مقایسه کنید و با خیال راحت
            فروشنده مورد نظرتان را انتخاب کنید.
          </p>
        </div>

        <div className="shops-count">
          <strong>{shops.length}</strong>
          <span>فروشگاه فعال</span>
        </div>
      </div>

      <div className="shops-grid">
        {shops.map((shop) => (
          <article className="shop-card" key={shop.id}>
            <div className={`shop-card-cover ${shop.color}`}>
              <div className="shop-logo">
                {shop.name.charAt(0)}
              </div>

              <span className="shop-category">
                {shop.category}
              </span>
            </div>

            <div className="shop-card-body">
              <div className="shop-title-row">
                <div>
                  <h3>{shop.name}</h3>
                  <span className="shop-status">● فعال</span>
                </div>

                <div className="shop-rating">
                  ★ {shop.rating}
                </div>
              </div>

              <p className="shop-description">
                {shop.description}
              </p>

              <div className="shop-meta">
                <span>
                  <strong>{shop.products}</strong>
                  محصول
                </span>

                <span>فروشگاه معتبر</span>
              </div>

              <Link
                to={`/shops/${shop.id}`}
                className="shop-button"
              >
                مشاهده فروشگاه
                <span>←</span>
              </Link>
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}

export default Shops;