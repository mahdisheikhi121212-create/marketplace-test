import { useState } from "react";
import { useNavigate } from "react-router-dom";

import { loginUser } from "../../api";

function Login() {
    const navigate = useNavigate();

    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [showPassword, setShowPassword] = useState(false);
    const [error, setError] = useState("");
    const [isLoading, setIsLoading] = useState(false);

    const handleSubmit = async (event) => {
        event.preventDefault();

        setError("");

        if (!username.trim()) {
            setError("لطفاً نام کاربری را وارد کنید.");
            return;
        }

        if (!password) {
            setError("لطفاً رمز عبور را وارد کنید.");
            return;
        }

        setIsLoading(true);

        try {
            const data = await loginUser(
                username,
                password
            );

            localStorage.setItem(
                "access_token",
                data.access
            );

            localStorage.setItem(
                "refresh_token",
                data.refresh
            );

            navigate("/");

        } catch (error) {
            setError(error.message);

        } finally {
            setIsLoading(false);
        }
    };

    return (
        <main dir="rtl">
            <section>
                <h1>ورود به حساب کاربری</h1>

                <p>
                    برای ادامه وارد حساب کاربری خود شوید.
                </p>

                <form onSubmit={handleSubmit}>
                    <div>
                        <label htmlFor="username">
                            نام کاربری
                        </label>

                        <input
                            id="username"
                            name="username"
                            type="text"
                            value={username}
                            onChange={(event) =>
                                setUsername(event.target.value)
                            }
                            autoComplete="username"
                            disabled={isLoading}
                        />
                    </div>

                    <div>
                        <label htmlFor="password">
                            رمز عبور
                        </label>

                        <div
                            style={{
                                position: "relative",
                                width: "100%",
                            }}
                        >
                            <input
                                id="password"
                                name="password"
                                type={
                                    showPassword
                                        ? "text"
                                        : "password"
                                }
                                value={password}
                                onChange={(event) =>
                                    setPassword(
                                        event.target.value
                                    )
                                }
                                autoComplete="current-password"
                                disabled={isLoading}
                                style={{
                                    width: "100%",
                                    boxSizing: "border-box",
                                    paddingLeft: "40px",
                                }}
                            />

                            <button
                                type="button"
                                onClick={() =>
                                    setShowPassword(
                                        (current) => !current
                                    )
                                }
                                disabled={isLoading}
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
                        <p role="alert">
                            {error}
                        </p>
                    )}

                    <button
                        type="submit"
                        disabled={isLoading}
                    >
                        {isLoading
                            ? "در حال ورود..."
                            : "ورود"}
                    </button>
                </form>
            </section>
        </main>
    );
}

export default Login;