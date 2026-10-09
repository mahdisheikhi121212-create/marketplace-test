import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { apiUrl } from "../../services/api";
import { addToCart } from "../../services/cart";

function ProductDetail() {
  const { id } = useParams();
  const navigate = useNavigate();

  const [product, setProduct] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [addedToCart, setAddedToCart] = useState(false);

  useEffect(() => {
    if (!id || id === "undefined") {
      setError("شناسه محصول نامعتبر است.");
      setLoading(false);
      return;
    }

    const fetchProduct = async () => {
      try {
        setLoading(true);
        setError("");
        setAddedToCart(false);

        const response = await fetch(
          apiUrl(`/api/products/${id}/`)
        );

        if (!response.ok) {
          throw new Error("دریافت محصول با مشکل مواجه شد.");
        }

        const data = await response.json();
        setProduct(data);
      } catch (err) {
        setError(err.message);
        setProduct(null);
      } finally {
        setLoading(false);
      }
    };

    fetchProduct();
  }, [id]);

  const handleAddToCart = () => {
    if (!product) return;

    addToCart(product);
    setAddedToCart(true);
  };

  if (loading) {
    return (
      <section dir="rtl">
        <p>در حال دریافت اطلاعات محصول...</p>
      </section>
    );
  }

  if (error) {
    return (
      <section dir="rtl">
        <h2>خطا</h2>
        <p>{error}</p>

        <Link to="/products">
          بازگشت به محصولات
        </Link>
      </section>
    );
  }

  if (!product) {
    return (
      <section dir="rtl">
        <h2>محصول پیدا نشد</h2>
        <p>این محصول وجود ندارد یا حذف شده است.</p>

        <Link to="/products">
          بازگشت به محصولات
        </Link>
      </section>
    );
  }

  return (
    <section className="product-detail" dir="rtl">
      <div className="product-detail-image">
        <span>
          {product.category_name || "تصویر محصول"}
        </span>
      </div>

      <div className="product-detail-info">
        <h2>{product.name}</h2>

        <p className="product-price">
          {Number(product.price).toLocaleString("fa-IR")} تومان
        </p>

        <p className="product-category">
          دسته‌بندی:{" "}
          {product.category_name || "نامشخص"}
        </p>

        <p className="product-description">
          {product.description}
        </p>

        <button
          className="add-to-cart-button"
          type="button"
          onClick={handleAddToCart}
        >
          افزودن به سبد خرید
        </button>

        {addedToCart && (
          <div className="cart-added-message">
            محصول با موفقیت به سبد خرید اضافه شد.
          </div>
        )}

        {addedToCart && (
          <button
            type="button"
            className="go-to-cart-button"
            onClick={() => navigate("/cart")}
          >
            مشاهده سبد خرید
          </button>
        )}
      </div>
    </section>
  );
}

export default ProductDetail;
