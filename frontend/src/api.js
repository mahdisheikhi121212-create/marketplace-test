const API_BASE_URL =
    import.meta.env.VITE_API_BASE_URL ||
    "http://127.0.0.1:8000";


export async function loginUser(
    username,
    password
) {
    const response = await fetch(
        `${API_BASE_URL}/api/auth/login/`,
        {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                username,
                password,
            }),
        }
    );

    const data = await response.json();

    if (!response.ok) {
        throw new Error(
            data.detail ||
            data.error ||
            "ورود ناموفق بود."
        );
    }

    return data;
}


async function refreshAccessToken() {
    const refreshToken =
        localStorage.getItem("refresh_token");

    if (!refreshToken) {
        return null;
    }

    const response = await fetch(
        `${API_BASE_URL}/api/auth/token/refresh/`,
        {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                refresh: refreshToken,
            }),
        }
    );

    if (!response.ok) {
        localStorage.removeItem("access_token");
        localStorage.removeItem("refresh_token");

        return null;
    }

    const data = await response.json();

    localStorage.setItem(
        "access_token",
        data.access
    );

    if (data.refresh) {
        localStorage.setItem(
            "refresh_token",
            data.refresh
        );
    }

    return data.access;
}


export async function apiRequest(
    endpoint,
    options = {}
) {
    let accessToken =
        localStorage.getItem("access_token");

    const makeRequest = async (token) => {
        const headers = {
            "Content-Type": "application/json",
            ...options.headers,
        };

        if (token) {
            headers.Authorization =
                `Bearer ${token}`;
        }

        return fetch(
            `${API_BASE_URL}${endpoint}`,
            {
                ...options,
                headers,
            }
        );
    };

    let response =
        await makeRequest(accessToken);

    if (
        response.status === 401 &&
        localStorage.getItem("refresh_token")
    ) {
        accessToken =
            await refreshAccessToken();

        if (accessToken) {
            response =
                await makeRequest(accessToken);
        }
    }

    return response;
}


export default API_BASE_URL;
