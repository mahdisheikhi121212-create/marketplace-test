import "./MarketplaceAtmosphere.css";

export default function MarketplaceAtmosphere() {
  return (
    <div className="marketplace-atmosphere" aria-hidden="true">
      {/* نورهای محیطی */}
      <div className="atmosphere-glow atmosphere-glow-1" />
      <div className="atmosphere-glow atmosphere-glow-2" />
      <div className="atmosphere-glow atmosphere-glow-3" />

      {/* ذرات بسیار ظریف */}
      <div className="atmosphere-particles">
        <span>✦</span>
        <span>✧</span>
        <span>·</span>
        <span>✦</span>
        <span>·</span>
        <span>✧</span>
        <span>·</span>
        <span>✦</span>
        <span>·</span>
        <span>✧</span>
      </div>

      {/* گل‌ها */}
      <div className="atmosphere-flower flower-1">✿</div>
      <div className="atmosphere-flower flower-2">❀</div>
      <div className="atmosphere-flower flower-3">✿</div>
      <div className="atmosphere-flower flower-4">❀</div>

      {/* برگ‌ها */}
      <div className="atmosphere-leaf leaf-1">⌁</div>
      <div className="atmosphere-leaf leaf-2">⌁</div>
      <div className="atmosphere-leaf leaf-3">⌁</div>

      {/* =========================
          مشتری اول
      ========================= */}
      <div className="market-person person-1">
        <span className="person-head" />

        <span className="person-body">
          <span className="person-arm person-arm-left" />
          <span className="person-arm person-arm-right" />

          <span className="person-leg person-leg-left" />
          <span className="person-leg person-leg-right" />
        </span>

        <span className="person-bag">🛍</span>
      </div>

      {/* =========================
          مشتری دوم
      ========================= */}
      <div className="market-person person-2">
        <span className="person-head" />

        <span className="person-body">
          <span className="person-arm person-arm-left" />
          <span className="person-arm person-arm-right" />

          <span className="person-leg person-leg-left" />
          <span className="person-leg person-leg-right" />
        </span>

        <span className="person-bag">🛍</span>
      </div>

      {/* =========================
          مشتری سوم
      ========================= */}
      <div className="market-person person-3">
        <span className="person-head" />

        <span className="person-body">
          <span className="person-arm person-arm-left" />
          <span className="person-arm person-arm-right" />

          <span className="person-leg person-leg-left" />
          <span className="person-leg person-leg-right" />
        </span>
      </div>

      {/* سبدهای خرید */}
      <div className="market-cart cart-1">🛒</div>
      <div className="market-cart cart-2">🛒</div>
      <div className="market-cart cart-3">🛒</div>
    </div>
  );
}
