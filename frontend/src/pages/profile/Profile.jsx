import { useEffect, useState } from "react";
import { apiRequest } from "../../services/api";

function Profile() {
  const [profile, setProfile] = useState(null);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        setLoading(true);
        setError("");

        const response = await apiRequest(
          "/api/auth/profile/",
          {
            method: "GET",
          }
        );

        const data = await response.json();

        if (!response.ok) {
          throw new Error(
            data.detail ||
              "دریافت اطلاعات پروفایل با خطا مواجه شد."
          );
        }

        setProfile(data);
      } catch (err) {
        setError(
          err.message ||
            "دریافت اطلاعات پروفایل با خطا مواجه شد."
        );
      } finally {
        setLoading(false);
      }
    };

    fetchProfile();
  }, []);

  const getRoleLabel = (role) => {
    const roles = {
      admin: "مدیر",
      seller: "فروشنده",
      customer: "مشتری",
      user: "کاربر",
    };

    return roles[role] || role || "نامشخص";
  };

  if (loading) {
    return (
      <section dir="rtl">
        <h2>پروفایل من</h2>
        <p>در حال دریافت اطلاعات پروفایل...</p>
      </section>
    );
  }

  if (error) {
    return (
      <section dir="rtl">
        <h2>پروفایل من</h2>

        <p style={{ color: "red" }}>
          {error}
        </p>
      </section>
    );
  }

  return (
    <section
      dir="rtl"
      style={{
        maxWidth: "520px",
        margin: "0 auto",
      }}
    >
      <h2>پروفایل من</h2>

      <p>
        <strong>نام کاربری:</strong>{" "}
        {profile?.username || "—"}
      </p>

      <p>
        <strong>ایمیل:</strong>{" "}
        {profile?.email || "—"}
      </p>

      <p>
        <strong>نوع حساب:</strong>{" "}
        {getRoleLabel(profile?.role)}
      </p>
    </section>
  );
}

export default Profile;