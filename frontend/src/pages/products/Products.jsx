import {
  useEffect,
  useState,
} from "react";

import {
  Link,
  useLocation,
  useNavigate,
} from "react-router-dom";

import {
  apiUrl,
} from "../../services/api";


function Products() {
  const location = useLocation();
  const navigate = useNavigate();

  const getSearchFromUrl = () => {
    const params =
      new URLSearchParams(
        location.search
      );

    return params.get("search") || "";
  };

  const [products, setProducts] =
    useState([]);

  const [search, setSearch] =
    useState(
      getSearchFromUrl()
    );

  const [suggestions, setSuggestions] =
    useState([]);

  const [loading, setLoading] =
    useState(true);

  const [
    suggestionsLoading,
    setSuggestionsLoading,
  ] = useState(false);

  const [error, setError] =
    useState("");


  useEffect(() => {
    setSearch(
      getSearchFromUrl()
    );
  }, [location.search]);


  useEffect(() => {
    const fetchProducts = async () => {
      try {
        setLoading(true);
        setError("");

        const params =
          new URLSearchParams();

        if (search.trim()) {
          params.set(
            "search",
            search.trim()
          );
        }

        const queryString =
          params.toString();

        const apiPath =
          queryString
            ? `/api/products/?${queryString}`
            : "/api/products/";

        const response =
          await fetch(
            apiUrl(apiPath)
          );

        if (!response.ok) {
          throw new Error(
            "دریافت محصولات با مشکل مواجه شد."
          );
        }

        const data =
          await response.json();

        setProducts(
          data.results || []
        );
      } catch (err) {
        setError(
          err.message ||
            "دریافت محصولات با مشکل مواجه شد."
        );

        setProducts([]);
      } finally {
        setLoading(false);
      }
    };

    const timeoutId =
      setTimeout(
        fetchProducts,
        300
      );

    return () =>
      clearTimeout(timeoutId);
  }, [search]);


  useEffect(() => {
    const trimmedSearch =
      search.trim();

    if (
      trimmedSearch.length < 2
    ) {
      setSuggestions([]);
      setSuggestionsLoading(false);
      return;
    }

    const fetchSuggestions =
      async () => {
        try {
          setSuggestionsLoading(
            true
          );

          const params =
            new URLSearchParams();

          params.set(
            "search",
            trimmedSearch
          );

          const response =
            await fetch(
              apiUrl(
                `/api/products/?${params.toString()}`
              )
            );

          if (!response.ok) {
            throw new Error(
              "دریافت پیشنهادها با مشکل مواجه شد."
            );
          }

          const data =
            await response.json();

          setSuggestions(
            (
              data.results || []
            ).slice(0, 6)
          );
        } catch {
          setSuggestions([]);
        } finally {
          setSuggestionsLoading(
            false
          );
        }
      };

    const timeoutId =
      setTimeout(
        fetchSuggestions,
        300
      );

    return () =>
      clearTimeout(timeoutId);
  }, [search]);


  const handleSearchChange = (
    event
  ) => {
    const value =
      event.target.value;

    setSearch(value);

    const params =
      new URLSearchParams();

    if (value.trim()) {
      params.set(
        "search",
        value.trim()
      );
    }

    const queryString =
      params.toString();

    navigate(
      queryString
        ? `/products?${queryString}`
        : "/products",
      {
        replace: true,
      }
    );
  };


  const handleSuggestionClick =
    () => {
      setSuggestions([]);
    };


  return (
    <section
      className="products-page"
      dir="rtl"
    >
      <div className="products-heading">
        <div>
          <span className="section-eyebrow">
            Marketplace
          </span>

          <h2>محصولات</h2>

          <p>
            مجموعه‌ای از محصولات
            فروشگاه‌های مختلف را بررسی
            کنید و محصول مناسب خودتان
            را پیدا کنید.
          </p>
        </div>

        <div className="products-count">
          <strong>
            {products.length}
          </strong>

          <span>محصول</span>
        </div>
      </div>

      <div className="products-toolbar">
        <div className="products-search">
          <span>⌕</span>

          <input
            type="text"
            placeholder="جستجوی محصول..."
            aria-label="جستجوی محصول"
            value={search}
            onChange={
              handleSearchChange
            }
          />

          {search.trim().length >=
            2 && (
            <div className="search-suggestions">
              {suggestionsLoading && (
                <div className="search-suggestion-status">
                  در حال جستجو...
                </div>
              )}

              {!suggestionsLoading &&
                suggestions.length >
                  0 && (
                  <>
                    {suggestions.map(
                      (product) => (
                        <Link
                          key={
                            product.id
                          }
                          to={`/products/${product.id}`}
                          className="search-suggestion"
                          onClick={
                            handleSuggestionClick
                          }
                        >
                          <span className="search-suggestion-name">
                            {
                              product.name
                            }
                          </span>

                          {product.category_name && (
                            <span className="search-suggestion-category">
                              {
                                product.category_name
                              }
                            </span>
                          )}
                        </Link>
                      )
                    )}
                  </>
                )}

              {!suggestionsLoading &&
                suggestions.length ===
                  0 && (
                  <div className="search-suggestion-status">
                    محصولی پیدا نشد.
                  </div>
                )}
            </div>
          )}
        </div>
      </div>

      {loading && (
        <p>
          در حال دریافت محصولات...
        </p>
      )}

      {error && (
        <p>{error}</p>
      )}

      {!loading &&
        !error &&
        products.length === 0 && (
          <p>
            محصولی پیدا نشد.
          </p>
        )}

      {!loading &&
        !error &&
        products.length > 0 && (
          <div className="products-grid">
            {products.map(
              (product) => (
                <article
                  className="product-card"
                  key={product.id}
                >
                  <div className="product-image">
                    <span>
                      {product.category_name ||
                        "تصویر محصول"}
                    </span>

                    <span className="product-category">
                      {
                        product.category_name
                      }
                    </span>
                  </div>

                  <div className="product-card-body">
                    <div className="product-shop">
                      Marketplace
                    </div>

                    <h3>
                      {product.name}
                    </h3>

                    <div className="product-meta">
                      <span>
                        دسته‌بندی:{" "}
                        {product.category_name ||
                          "نامشخص"}
                      </span>
                    </div>

                    <div className="product-card-footer">
                      <div className="product-price">
                        {Number(
                          product.price
                        ).toLocaleString(
                          "fa-IR"
                        )}{" "}
                        تومان
                      </div>

                      <Link
                        to={`/products/${product.id}`}
                        className="product-button"
                      >
                        مشاهده محصول
                      </Link>
                    </div>
                  </div>
                </article>
              )
            )}
          </div>
        )}
    </section>
  );
}

export default Products;