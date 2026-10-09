import { useEffect, useState } from "react";

import { apiRequest } from "../../api";


function Me() {
    const [user, setUser] = useState(null);
    const [error, setError] = useState("");
    const [isLoading, setIsLoading] = useState(true);


    useEffect(() => {
        async function loadUser() {
            try {
                const response = await apiRequest(
                    "/api/auth/me/"
                );

                const data = await response.json();

                if (!response.ok) {
                    throw new Error(
                        data.detail ||
                        "دریافت اطلاعات کاربر ناموفق بود."
                    );
                }

                setUser(data);

            } catch (error) {
                setError(error.message);

            } finally {
                setIsLoading(false);
            }
        }

        loadUser();
    }, []);


    if (isLoading) {
        return (
            <main dir="rtl">
                <h1>در حال دریافت اطلاعات...</h1>
            </main>
        );
    }


    if (error) {
        return (
            <main dir="rtl">
                <h1>خطا</h1>
                <p role="alert">
                    {error}
                </p>
            </main>
        );
    }


    return (
        <main dir="rtl">
            <h1>اطلاعات کاربر</h1>

            <p>
                نام کاربری: {user.username}
            </p>

            <p>
                ایمیل: {user.email || "ثبت نشده"}
            </p>

            <p>
                شناسه کاربر: {user.id}
            </p>
        </main>
    );
}


export default Me;
