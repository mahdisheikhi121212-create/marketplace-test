import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { apiUrl } from "../../services/api";

function Register() {
  const navigate = useNavigate();

  const [form, setForm] = useState({
    username: "",
    password: "",
    email: "",
    phone: "",
  });

  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleChange = (event) => {
    const name = event.target.name;
    const value = event.target.value;

    setForm({
      ...form,
      [name]: value,
    });

    setError("");
  };

  const getUsernameStatus = (username) => {
    if (username.length === 0) {
      return "";
    }

    if (username.length < 3) {
      return "نام کاربری باید حداقل ۳ کاراکتر باشد.";
    }

    if (username.length > 30) {
      return "نام کاربری نمی‌تواند بیشتر از ۳۰ کاراکتر باشد.";
    }

    if (!/^[A-Za-z]/.test(username)) {
      return "نام کاربری باید با یک حرف انگلیسی شروع شود.";
    }

    if (!/^[A-Za-z0-9_-]+$/.test(username)) {
      return "فقط حروف انگلیسی، اعداد، _ و - مجاز هستند.";
    }

    return "نام کاربری قابل قبول است.";
  };

  const getPasswordStatus = (password) => {
    if (password.length === 0) {
      return "";
    }

    if (password.length < 12) {
      return "رمز عبور ضعیف است؛ حداقل ۱۲ کاراکتر لازم است.";
    }

    if (!/[A-Z]/.test(password)) {
      return "حداقل یک حرف انگلیسی بزرگ لازم است.";
    }

    if (!/[a-z]/.test(password)) {
      return "حداقل یک حرف انگلیسی کوچک لازم است.";
    }

    if (!/[0-9]/.test(password)) {
      return "حداقل یک عدد لازم است.";
    }

    if (!/[!@#$%^&*(),.?":{}|<>_\-+=/\\[\];'`~]/.test(password)) {
      return "حداقل یک کاراکتر ویژه مثل ! یا @ یا # لازم است.";
    }

    return "رمز عبور قابل قبول و قوی است.";
  };

  const usernameMessage = getUsernameStatus(form.username);
  const passwordMessage = getPasswordStatus(form.password);

  const usernameValid =
    form.username.length >= 3 &&
    form.username.length <= 30 &&
    /^[A-Za-z][A-Za-z0-9_-]*$/.test(form.username);

  const passwordValid =
    form.password.length >= 12 &&
    /[A-Z]/.test(form.password) &&
    /[a-z]/.test(form.password) &&
    /[0-9]/.test(form.password) &&
    /[!@#$%^&*(),.?":{}|<>_\-+=/\\[\];'`~]/.test(
      form.password
    );

  const inputStyle = {
    width: "100%",
    height: "40px",
    boxSizing: "border-box",
  };

  const handleSubmit = async (event) => {
    event.preventDefault();

    if (!usernameValid) {
      setError("لطفاً یک نام کاربری معتبر وارد کنید.");
      return;
    }

    if (!passwordValid) {
      setError("لطفاً یک رمز عبور قوی وارد کنید.");
      return;
    }

    setLoading(true);
    setError("");

    try {
      const response = await fetch(
        apiUrl("/api/customers/register/"),
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(form),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.username?.[0] ||
            data.password?.[0] ||
            data.email?.[0] ||
            data.phone?.[0] ||
            data.detail ||
            "ثبت‌نام انجام نشد."
        );
      }

      navigate("/login");
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <section
      dir="rtl"
      style={{
        maxWidth: "420px",
        margin: "0 auto",
      }}
    >
      <h2>ثبت‌نام</h2>

      <form onSubmit={handleSubmit}>
        <div>
          <label>نام کاربری</label>

          <input
            type="text"
            name="username"
            value={form.username}
            onChange={handleChange}
            required
            minLength={3}
            maxLength={30}
            autoComplete="username"
            style={inputStyle}
          />

          <p>
            ۳ تا ۳۰ کاراکتر؛ فقط حروف انگلیسی، عدد، _ و -؛
            شروع با حرف انگلیسی.
          </p>

          {form.username && usernameValid && (
            <p style={{ color: "green" }}>
              ✓ نام کاربری تأیید شد.
            </p>
          )}

          {form.username && !usernameValid && (
            <p style={{ color: "red" }}>
              ✗ نام کاربری تأیید نشد.
              <br />
              {usernameMessage}
            </p>
          )}
        </div>

        <div>
          <label>رمز عبور</label>

          <div
            style={{
              position: "relative",
              width: "100%",
            }}
          >
            <input
              type={showPassword ? "text" : "password"}
              name="password"
              value={form.password}
              onChange={handleChange}
              required
              minLength={12}
              autoComplete="new-password"
              style={{
                ...inputStyle,
                paddingLeft: "40px",
              }}
            />

            <button
              type="button"
              onClick={() =>
                setShowPassword((current) => !current)
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
                transform: "translateY(-50%)",
                border: "none",
                background: "transparent",
                cursor: "pointer",
                fontSize: "18px",
                padding: "3px",
              }}
            >
              {showPassword ? "🙈" : "👁️"}
            </button>
          </div>

          <p>
            حداقل ۱۲ کاراکتر؛ شامل حرف انگلیسی بزرگ،
            حرف انگلیسی کوچک، عدد و کاراکتر ویژه.
          </p>

          {form.password && passwordValid && (
            <p style={{ color: "green" }}>
              ✓ رمز عبور قوی و تأیید شد.
            </p>
          )}

          {form.password && !passwordValid && (
            <p style={{ color: "red" }}>
              ✗ رمز عبور تأیید نشد.
              <br />
              {passwordMessage}
            </p>
          )}
        </div>

        <div>
          <label>ایمیل</label>

          <input
            type="email"
            name="email"
            value={form.email}
            onChange={handleChange}
            autoComplete="email"
            style={inputStyle}
          />
        </div>

        <div>
          <label>شماره تلفن</label>

          <input
            type="text"
            name="phone"
            value={form.phone}
            onChange={handleChange}
            autoComplete="tel"
            style={inputStyle}
          />
        </div>

        {error && (
          <p style={{ color: "red" }}>
            {error}
          </p>
        )}

        <button
          type="submit"
          disabled={
            loading ||
            !usernameValid ||
            !passwordValid
          }
        >
          {loading
            ? "در حال ثبت‌نام..."
            : "ثبت‌نام"}
        </button>
      </form>
    </section>
  );
}

export default Register;
