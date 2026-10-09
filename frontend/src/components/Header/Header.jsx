import { useEffect, useState } from "react";
import {
  Link,
  NavLink,
  useNavigate,
} from "react-router-dom";

import {
  apiRequest,
  apiUrl,
} from "../../services/api";

function Header() {
  const [search, setSearch] = useState("");
  const [suggestions, setSuggestions] = useState([]);
  const [suggestionsLoading, setSuggestionsLoading] =
    useState(false);

  const [isAuthenticated, setIsAuthenticated] =
    useState(
      Boolean(
        localStorage.getItem("access_token") ||
          localStorage.getItem("refresh_token")
      )
    );

  const [isStaff, setIsStaff] = useState(false);

  const navigate = useNavigate();

  useEffect(() => {
    const checkAuth = async () => {
      const accessToken =
        localStorage.getItem("access_token");

      const refreshToken =
        localStorage.getItem("refresh_token");

      if (!accessToken && !refreshToken) {
        setIsAuthenticated(false);
        setIsStaff(false);
        return;
      }

      try {
        const response = await apiRequest(
          "/api/auth/me/",
          {
            method: "GET",
          }
        );

        if (!response.ok) {
          setIsAuthenticated(false);
          setIsStaff(false);
          return;
        }

        const data = await response.json();

        setIsAuthenticated(true);
        setIsStaff(data.is_staff === true);
      } catch (error) {
        console.error(
          "خطا در دریافت اطلاعات کاربر:",
          error
        );

        setIsAuthenticated(false);
        setIsStaff(false);
      }
    };

    checkAuth();

    window.addEventListener(
      "storage",
      checkAuth
    );

    window.addEventListener(
      "auth-changed",
      checkAuth
    );

    return () => {
      window.removeEventListener(
        "storage",
        checkAuth
      );

      window.removeEventListener(
        "auth-changed",
        checkAuth
      );
    };
  }, []);

  useEffect(() => {
    const value = search.trim();

    if (!value) {
      setSuggestions([]);
      setSuggestionsLoading(false);
      return;
    }

    const controller = new AbortController();

    const fetchSuggestions = async () => {
      try {
        setSuggestionsLoading(true);

        const params = new URLSearchParams();
        params.set("search", value);

        const response = await fetch(
          apiUrl(
            `/api/products/?${params.toString()}`
          ),
          {
            signal: controller.signal,
          }
        );

        if (!response.ok) {
          throw new Error(
            "دریافت نتایج جستجو انجام نشد."
          );
        }

        const data = await response.json();

        setSuggestions(
          (data.results || []).slice(0, 5)
        );
      } catch (error) {
        if (error.name !== "AbortError") {
          setSuggestions([]);
        }
      } finally {
        if (!controller.signal.aborted) {
          setSuggestionsLoading(false);
        }
      }
    };

    const timer = setTimeout(
      fetchSuggestions,
      250
    );

    return () => {
      clearTimeout(timer);
      controller.abort();
    };
  }, [search]);

  const handleSearch = (event) => {
    event.preventDefault();

    const value = search.trim();

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

  const handleSuggestionClick = (productId) => {
    setSearch("");
    setSuggestions([]);

    navigate(`/products/${productId}`);
  };

  const handleLogout = () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");

    setIsAuthenticated(false);
    setIsStaff(false);

    window.dispatchEvent(
      new Event("auth-changed")
    );

    navigate("/login");
  };

  return (
    <header
      className="site-header"
      dir="rtl"
    >
      <div className="header-container">
        <Link
          to="/"
          className="site-logo"
        >
          مارکت‌پلیس
        </Link>

        <nav className="main-nav">
          <NavLink
            to="/"
            end
          >
            خانه
          </NavLink>

          <NavLink to="/products">
            محصولات
          </NavLink>
        </nav>

        <div className="header-search-wrapper">
          <form
            className="header-search"
            onSubmit={handleSearch}
          >
            <span>⌕</span>

            <input
              type="text"
              value={search}
              onChange={(event) =>
                setSearch(event.target.value)
              }
              placeholder="جستجوی محصول..."
              aria-label="جستجوی محصول"
              autoComplete="off"
            />

            <button type="submit">
              جستجو
            </button>
          </form>

          {search.trim() && (
            <div className="header-search-suggestions">
              {suggestionsLoading && (
                <div className="header-search-status">
                  در حال جستجو...
                </div>
              )}

              {!suggestionsLoading &&
                suggestions.length === 0 && (
                  <div className="header-search-status">
                    محصولی پیدا نشد.
                  </div>
                )}

              {!suggestionsLoading &&
                suggestions.map((product) => (
                  <button
                    type="button"
                    className="header-search-suggestion"
                    key={product.id}
                    onClick={() =>
                      handleSuggestionClick(
                        product.id
                      )
                    }
                  >
                    <span className="header-search-suggestion-name">
                      {product.name}
                    </span>

                    <span className="header-search-suggestion-category">
                      {product.category_name ||
                        "محصول"}
                    </span>
                  </button>
                ))}

              {!suggestionsLoading &&
                suggestions.length > 0 && (
                  <button
                    type="button"
                    className="header-search-all"
                    onClick={handleSearch}
                  >
                    مشاهده همه نتایج
                  </button>
                )}
            </div>
          )}
        </div>

        <div className="header-actions">
          <NavLink
            to="/cart"
            className="header-action"
          >
            🛒
            <span>سبد خرید</span>
          </NavLink>

          {isAuthenticated && (
            <>
              <NavLink
                to="/orders"
                className="header-profile"
              >
                سفارش‌های من
              </NavLink>

              {isStaff && (
                <NavLink
                  to="/admin/orders"
                  className="header-profile"
                >
                  مدیریت سفارش‌ها
                </NavLink>
              )}

              <NavLink
                to="/profile"
                className="header-profile"
              >
                پروفایل
              </NavLink>

              <button
                type="button"
                className="header-profile"
                onClick={handleLogout}
              >
                خروج از حساب کاربری
              </button>
            </>
          )}

          {!isAuthenticated && (
            <>
              <NavLink
                to="/login"
                className="header-profile"
              >
                ورود
              </NavLink>

              <NavLink
                to="/register"
                className="header-profile"
              >
                ثبت‌نام
              </NavLink>
            </>
          )}
        </div>
      </div>
    </header>
  );
}

export default Header;