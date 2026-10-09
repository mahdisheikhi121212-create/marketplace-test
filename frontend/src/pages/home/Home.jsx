import { useEffect, useState } from "react";
import {
  Link,
  useNavigate,
} from "react-router-dom";

import {
  apiUrl,
} from "../../services/api";


function Home() {
  const navigate = useNavigate();

  const [search, setSearch] =
    useState("");

  const [suggestions, setSuggestions] =
    useState([]);

  const [
    suggestionsLoading,
    setSuggestionsLoading,
  ] = useState(false);


  const categories = [
    {
      icon: "👕",
      title: "پوشاک",
      text: "استایل و پوشاک مورد علاقه‌تان",
      className: "category-fashion",
    },
    {
      icon: "💻",
      title: "دیجیتال",
      text: "کالای دیجیتال و لوازم هوشمند",
      className: "category-digital",
    },
    {
      icon: "🏠",
      title: "خانه و زندگی",
      text: "لوازم کاربردی برای خانه",
      className: "category-home",
    },
    {
      icon: "💄",
      title: "زیبایی",
      text: "محصولات مراقبت و زیبایی",
      className: "category-beauty",
    },
  ];


  const advantages = [
    {
      number: "۱",
      title: "انتخاب بیشتر",
      text: "محصولات متنوع را در یکجا ببینید.",
    },
    {
      number: "۲",
      title: "مقایسه آسان",
      text: "قبل از خرید، گزینه‌های مختلف را راحت‌تر مقایسه کنید.",
    },
    {
      number: "۳",
      title: "خرید مطمئن‌تر",
      text: "تجربه‌ای ساده، شفاف و یکپارچه برای خرید داشته باشید.",
    },
  ];


  useEffect(() => {
    const value =
      search.trim();

    if (!value) {
      setSuggestions([]);
      setSuggestionsLoading(false);
      return;
    }

    const timer =
      setTimeout(
        async () => {
          try {
            setSuggestionsLoading(
              true
            );

            const params =
              new URLSearchParams();

            params.set(
              "search",
              value
            );

            const response =
              await fetch(
                apiUrl(
                  `/api/products/?${params.toString()}`
                )
              );

            if (!response.ok) {
              throw new Error(
                "خطا در دریافت پیشنهادهای جستجو"
              );
            }

            const data =
              await response.json();

            setSuggestions(
              (
                data.results || []
              ).slice(0, 6)
            );
          } catch (error) {
            console.error(
              "Search suggestions error:",
              error
            );

            setSuggestions([]);
          } finally {
            setSuggestionsLoading(
              false
            );
          }
        },
        300
      );

    return () =>
      clearTimeout(timer);
  }, [search]);


  const handleSearch = (
    event
  ) => {
    event.preventDefault();

    const value =
      search.trim();

    if (!value) {
      setSearch("");
      setSuggestions([]);

      navigate("/products");
      return;
    }

    setSearch("");
    setSuggestions([]);

    navigate(
      `/products?search=${encodeURIComponent(
        value
      )}`
    );
  };


  const handleSuggestionClick = (
    product
  ) => {
    setSearch("");
    setSuggestions([]);

    navigate(
      `/products/${product.id}`
    );
  };


  return (
    <section
      className="home-page"
      dir="rtl"
    >
      <section className="home-hero">
        <div className="home-hero-content">
          <span className="home-badge">
            بازار آنلاین شما
          </span>

          <h1>
            دنیای خرید و فروش،
            <br />

            <strong>
              در یکجا
            </strong>
          </h1>

          <p className="home-hero-description">
            محصولات مورد علاقه‌تان را
            پیدا کنید، مقایسه کنید و با
            تجربه‌ای ساده و آرام خرید
            کنید.
          </p>

          <div className="home-search-wrapper">
            <form
              className="home-search-box"
              onSubmit={
                handleSearch
              }
            >
              <span>⌕</span>

              <input
                type="text"
                value={search}
                onChange={(
                  event
                ) =>
                  setSearch(
                    event.target.value
                  )
                }
                placeholder="چه چیزی می‌خواهید پیدا کنید؟"
                aria-label="جستجوی محصول"
              />

              <button type="submit">
                جستجو
              </button>
            </form>

            {search.trim() && (
              <div className="home-search-suggestions">
                {suggestionsLoading ? (
                  <div className="home-search-status">
                    در حال جستجو...
                  </div>
                ) : suggestions.length >
                  0 ? (
                  suggestions.map(
                    (product) => (
                      <button
                        type="button"
                        className="home-search-suggestion"
                        key={
                          product.id
                        }
                        onClick={() =>
                          handleSuggestionClick(
                            product
                          )
                        }
                      >
                        <span className="suggestion-icon">
                          🛍️
                        </span>

                        <span className="suggestion-info">
                          <strong>
                            {
                              product.name
                            }
                          </strong>

                          {product.category_name && (
                            <small>
                              {
                                product.category_name
                              }
                            </small>
                          )}
                        </span>

                        <span className="suggestion-arrow">
                          ←
                        </span>
                      </button>
                    )
                  )
                ) : (
                  <div className="home-search-status">
                    محصولی پیدا نشد.
                  </div>
                )}
              </div>
            )}
          </div>

          <div className="home-actions">
            <Link
              to="/products"
              className="home-primary-button"
            >
              مشاهده محصولات
              <span>←</span>
            </Link>
          </div>
        </div>

        <div className="home-hero-visual">
          <div className="hero-orbit hero-orbit-one" />
          <div className="hero-orbit hero-orbit-two" />

          <div className="home-hero-card">
            <div className="home-hero-icon">
              🛍️
            </div>

            <span>
              MARKET PLACE
            </span>

            <h3>
              همه‌چیز در یکجا
            </h3>

            <p>
              یک فضای یکپارچه برای
              تجربه خرید ساده و مطمئن.
            </p>

            <div className="hero-card-stats">
              <div>
                <strong>
                  ∞
                </strong>

                <small>
                  انتخاب
                </small>
              </div>

              <div>
                <strong>
                  +
                </strong>

                <small>
                  محصول
                </small>
              </div>

              <div>
                <strong>
                  ✓
                </strong>

                <small>
                  تجربه ساده
                </small>
              </div>
            </div>
          </div>
        </div>
      </section>


      <section className="home-categories">
        <div className="home-section-heading">
          <div>
            <span>
              دسته‌بندی‌ها
            </span>

            <h2>
              چیزی که می‌خواهید را
              راحت‌تر پیدا کنید
            </h2>
          </div>

          <Link to="/products">
            مشاهده همه ←
          </Link>
        </div>

        <div className="category-grid">
          {categories.map(
            (category) => (
              <Link
                to="/products"
                className={`category-card ${category.className}`}
                key={
                  category.title
                }
              >
                <div className="category-icon">
                  {category.icon}
                </div>

                <div>
                  <h3>
                    {category.title}
                  </h3>

                  <p>
                    {category.text}
                  </p>
                </div>

                <span className="category-arrow">
                  ←
                </span>
              </Link>
            )
          )}
        </div>
      </section>


      <section className="home-advantage">
        <div className="advantage-intro">
          <span>
            چرا مارکت‌پلیس؟
          </span>

          <h2>
            فقط یک فروشگاه نیست؛
            <br />

            <strong>
              یک بازار کامل برای
              خرید و فروش است.
            </strong>
          </h2>

          <p>
            هدف ما ساختن فضایی است که
            کاربران بتوانند ساده‌تر،
            شفاف‌تر و با آرامش بیشتری
            خرید کنند.
          </p>
        </div>

        <div className="advantage-list">
          {advantages.map(
            (item) => (
              <div
                className="advantage-item"
                key={
                  item.number
                }
              >
                <strong>
                  {item.number}
                </strong>

                <div>
                  <h3>
                    {item.title}
                  </h3>

                  <p>
                    {item.text}
                  </p>
                </div>
              </div>
            )
          )}
        </div>
      </section>
    </section>
  );
}

export default Home;