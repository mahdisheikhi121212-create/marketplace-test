import { useState } from "react";
import { useNavigate } from "react-router-dom";

import { loginUser } from "../../api";


function Login() {
  const navigate = useNavigate();

  const [username, setUsername] =
    useState("");

  const [password, setPassword] =
    useState("");

  const [
    showPassword,
    setShowPassword,
  ] = useState(false);

  const [loading, setLoading] =
    useState(false);

  const [error, setError] =
    useState("");


  const handleSubmit = async (
    event
  ) => {
    event.preventDefault();

    try {
      setLoading(true);
      setError("");

      const data =
        await loginUser(
          username,
          password
        );

      if (
        !data.access ||
        !data.refresh
      ) {
        throw new Error(
          "توکن ورود از سرور دریافت نشد."
        );
      }

      localStorage.setItem(
        "access_token",
        data.access
      );

      localStorage.setItem(
        "refresh_token",
        data.refresh
      );

      /*
       * به Header و سایر بخش‌های برنامه
       * اعلام می‌کنیم که وضعیت ورود
       * تغییر کرده است.
       */
      window.dispatchEvent(
        new Event(
          "auth-changed"
        )
      );

      navigate("/cart");
    } catch (err) {
      console.error(
        "خطا در ورود:",
        err
      );

      setError(
        err.message ||
          "ورود ناموفق بود."
      );
    } finally {
      setLoading(false);
    }
  };


  const inputStyle = {
    width: "100%",
    height: "40px",
    boxSizing: "border-box",
  };


  return (
    <section
      dir="rtl"
      style={{
        maxWidth: "420px",
        margin: "0 auto",
      }}
    >
      <h2>
        ورود به حساب
      </h2>

      <form
        onSubmit={
          handleSubmit
        }
      >
        <div>
          <label>
            نام کاربری
          </label>

          <input
            type="text"
            value={username}
            onChange={(
              event
            ) =>
              setUsername(
                event.target.value
              )
            }
            required
            autoComplete="username"
            style={inputStyle}
          />
        </div>

        <div>
          <label>
            رمز عبور
          </label>

          <div
            style={{
              position: "relative",
              width: "100%",
            }}
          >
            <input
              type={
                showPassword
                  ? "text"
                  : "password"
              }
              value={password}
              onChange={(
                event
              ) =>
                setPassword(
                  event.target.value
                )
              }
              required
              autoComplete="current-password"
              style={{
                ...inputStyle,
                paddingLeft:
                  "40px",
              }}
            />

            <button
              type="button"
              onClick={() =>
                setShowPassword(
                  (current) =>
                    !current
                )
              }
              aria-label={
                showPassword
                  ? "مخفی کردن رمز عبور"
                  : "نمایش رمز عبور"
              }
              style={{
                position: "absolute",
                left: "6px",
                top: "50%",
                transform:
                  "translateY(-50%)",
                border: "none",
                background:
                  "transparent",
                cursor: "pointer",
                fontSize: "18px",
                padding: "3px",
              }}
            >
              {showPassword
                ? "🙈"
                : "👁️"}
            </button>
          </div>
        </div>

        {error && (
          <p
            style={{
              color: "red",
            }}
          >
            {error}
          </p>
        )}

        <button
          type="submit"
          disabled={loading}
        >
          {loading
            ? "در حال ورود..."
            : "ورود"}
        </button>
      </form>
    </section>
  );
}


export default Login;