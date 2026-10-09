import {
  useEffect,
  useRef,
  useState,
} from "react";

import {
  useNavigate,
} from "react-router-dom";

import {
  apiRequest,
  apiUrl,
} from "../../services/api";

import {
  clearCart,
  getCart,
} from "../../services/cart";


const CHECKOUT_IDEMPOTENCY_KEY =
  "checkout_idempotency_key";

const CHECKOUT_ORDER_KEY =
  "checkout_order_id";


function Checkout() {
  const navigate = useNavigate();

  const checkoutKeyRef =
    useRef(
      localStorage.getItem(
        CHECKOUT_IDEMPOTENCY_KEY
      ) ||
        crypto.randomUUID()
    );

  const [
    existingOrderId,
    setExistingOrderId,
  ] = useState(
    localStorage.getItem(
      CHECKOUT_ORDER_KEY
    )
  );

  const [provinces, setProvinces] =
    useState([]);

  const [cities, setCities] =
    useState([]);

  const [
    selectedProvince,
    setSelectedProvince,
  ] = useState("");

  const [
    selectedCity,
    setSelectedCity,
  ] = useState("");

  const [title, setTitle] =
    useState("");

  const [
    receiverName,
    setReceiverName,
  ] = useState("");

  const [phone, setPhone] =
    useState("");

  const [
    addressLine,
    setAddressLine,
  ] = useState("");

  const [
    postalCode,
    setPostalCode,
  ] = useState("");

  const [
    isDefault,
    setIsDefault,
  ] = useState(false);

  const [loading, setLoading] =
    useState(false);


  useEffect(() => {
    localStorage.setItem(
      CHECKOUT_IDEMPOTENCY_KEY,
      checkoutKeyRef.current
    );
  }, []);


  const readResponse =
    async (response) => {
      const text =
        await response.text();

      if (!text) {
        return {};
      }

      try {
        return JSON.parse(text);
      } catch {
        return {
          detail: text,
        };
      }
    };


  useEffect(() => {
    if (existingOrderId) {
      return;
    }

    fetch(
      apiUrl(
        "/api/locations/provinces/"
      )
    )
      .then((response) => {
        if (!response.ok) {
          throw new Error(
            "دریافت استان‌ها با خطا مواجه شد."
          );
        }

        return response.json();
      })
      .then((data) => {
        setProvinces(
          Array.isArray(data)
            ? data
            : []
        );
      })
      .catch((error) => {
        console.error(
          "خطا در دریافت استان‌ها:",
          error
        );
      });
  }, [existingOrderId]);


  useEffect(() => {
    if (existingOrderId) {
      return;
    }

    if (!selectedProvince) {
      setCities([]);
      setSelectedCity("");
      return;
    }

    fetch(
      apiUrl(
        `/api/locations/cities/?province=${selectedProvince}`
      )
    )
      .then((response) => {
        if (!response.ok) {
          throw new Error(
            "دریافت شهرها با خطا مواجه شد."
          );
        }

        return response.json();
      })
      .then((data) => {
        setCities(
          Array.isArray(data)
            ? data
            : []
        );

        setSelectedCity("");
      })
      .catch((error) => {
        console.error(
          "خطا در دریافت شهرها:",
          error
        );

        setCities([]);
      });
  }, [
    selectedProvince,
    existingOrderId,
  ]);


  const normalizeText = (
    text
  ) => {
    return String(text)
      .trim()
      .replace(/ي/g, "ی")
      .replace(/ى/g, "ی")
      .replace(/ك/g, "ک")
      .replace(/\u200c/g, " ")
      .replace(/\s+/g, " ");
  };


  const findMatchingName = (
    items,
    targetName
  ) => {
    const normalizedTarget =
      normalizeText(
        targetName
      );

    if (!normalizedTarget) {
      return null;
    }

    return (
      items.find(
        (item) =>
          normalizeText(
            item.name
          ) ===
          normalizedTarget
      ) ||
      items.find((item) => {
        const itemName =
          normalizeText(
            item.name
          );

        return (
          itemName.includes(
            normalizedTarget
          ) ||
          normalizedTarget.includes(
            itemName
          )
        );
      }) ||
      null
    );
  };


  const handleUseCurrentLocation =
    () => {
      if (
        !navigator.geolocation
      ) {
        alert(
          "مرورگر شما از مکان‌یابی پشتیبانی نمی‌کند."
        );

        return;
      }

      navigator.geolocation
        .getCurrentPosition(
          (position) => {
            const {
              latitude,
              longitude,
            } =
              position.coords;

            fetch(
              `https://nominatim.openstreetmap.org/reverse?format=jsonv2&lat=${latitude}&lon=${longitude}&zoom=10&addressdetails=1&accept-language=fa`
            )
              .then(
                (response) => {
                  if (
                    !response.ok
                  ) {
                    throw new Error(
                      "Reverse geocoding failed."
                    );
                  }

                  return response.json();
                }
              )
              .then((data) => {
                const address =
                  data.address ||
                  {};

                const provinceName =
                  normalizeText(
                    address.state ||
                      ""
                  );

                const cityName =
                  normalizeText(
                    address.city ||
                      address.town ||
                      address.municipality ||
                      address.village ||
                      ""
                  );

                const matchedProvince =
                  findMatchingName(
                    provinces,
                    provinceName
                  );

                if (
                  !matchedProvince
                ) {
                  alert(
                    `استان «${provinceName}» در فهرست Marketplace پیدا نشد.`
                  );

                  return;
                }

                setSelectedProvince(
                  String(
                    matchedProvince.id
                  )
                );

                fetch(
                  apiUrl(
                    `/api/locations/cities/?province=${matchedProvince.id}`
                  )
                )
                  .then(
                    (
                      response
                    ) => {
                      if (
                        !response.ok
                      ) {
                        throw new Error(
                          "City request failed."
                        );
                      }

                      return response.json();
                    }
                  )
                  .then(
                    (
                      provinceCities
                    ) => {
                      const safeCities =
                        Array.isArray(
                          provinceCities
                        )
                          ? provinceCities
                          : [];

                      setCities(
                        safeCities
                      );

                      const matchedCity =
                        findMatchingName(
                          safeCities,
                          cityName
                        );

                      if (
                        !matchedCity
                      ) {
                        setSelectedCity(
                          ""
                        );

                        alert(
                          `استان «${matchedProvince.name}» پیدا شد، اما شهر «${cityName}» پیدا نشد.`
                        );

                        return;
                      }

                      setSelectedCity(
                        String(
                          matchedCity.id
                        )
                      );
                    }
                  )
                  .catch(
                    (error) => {
                      console.error(
                        "خطا در دریافت شهرها:",
                        error
                      );

                      alert(
                        "استان پیدا شد، اما دریافت شهرها با خطا مواجه شد."
                      );
                    }
                  );
              })
              .catch(
                (error) => {
                  console.error(
                    "خطا در تبدیل موقعیت به آدرس:",
                    error
                  );

                  alert(
                    "موقعیت پیدا شد، اما نام استان و شهر قابل دریافت نبود."
                  );
                }
              );
          },

          (error) => {
            if (
              error.code === 1
            ) {
              alert(
                "لطفاً اجازه دسترسی به موقعیت مکانی را فعال کنید."
              );
            } else if (
              error.code === 2
            ) {
              alert(
                "موقعیت مکانی شما قابل تشخیص نیست."
              );
            } else if (
              error.code === 3
            ) {
              alert(
                "زمان دریافت موقعیت مکانی تمام شد."
              );
            } else {
              alert(
                "دریافت موقعیت مکانی با خطا مواجه شد."
              );
            }
          }
        );
    };


  const syncServerCart =
    async (localCart) => {
      const cartResponse =
        await apiRequest(
          "/api/cart/",
          {
            method: "GET",
          }
        );

      const serverCartData =
        await readResponse(
          cartResponse
        );

      if (!cartResponse.ok) {
        throw new Error(
          serverCartData.detail ||
            "دریافت سبد خرید از سرور با خطا مواجه شد."
        );
      }

      const serverItems =
        Array.isArray(
          serverCartData.items
        )
          ? serverCartData.items
          : [];

      const localProductIds =
        new Set(
          localCart.map(
            (item) =>
              Number(item.id)
          )
        );

      for (
        const serverItem
        of serverItems
      ) {
        const productId =
          Number(
            serverItem
              .product
              .id
          );

        if (
          !localProductIds.has(
            productId
          )
        ) {
          const deleteResponse =
            await apiRequest(
              `/api/cart/items/${serverItem.id}/`,
              {
                method:
                  "DELETE",
              }
            );

          if (
            !deleteResponse.ok
          ) {
            const deleteData =
              await readResponse(
                deleteResponse
              );

            throw new Error(
              deleteData.detail ||
                "حذف آیتم قدیمی از سبد سرور ناموفق بود."
            );
          }
        }
      }

      for (
        const item
        of localCart
      ) {
        const serverCartItem =
          serverItems.find(
            (
              serverItem
            ) =>
              Number(
                serverItem
                  .product
                  .id
              ) ===
              Number(
                item.id
              )
          );

        if (
          serverCartItem
        ) {
          const response =
            await apiRequest(
              `/api/cart/items/${serverCartItem.id}/`,
              {
                method:
                  "PATCH",
                body:
                  JSON.stringify(
                    {
                      quantity:
                        item.quantity,
                    }
                  ),
              }
            );

          const data =
            await readResponse(
              response
            );

          if (!response.ok) {
            throw new Error(
              data.detail ||
                data.quantity?.[0] ||
                `ویرایش محصول «${item.name}» در سبد سرور ناموفق بود.`
            );
          }
        } else {
          const response =
            await apiRequest(
              "/api/cart/items/",
              {
                method:
                  "POST",
                body:
                  JSON.stringify(
                    {
                      product_id:
                        item.id,
                      quantity:
                        item.quantity,
                    }
                  ),
              }
            );

          const data =
            await readResponse(
              response
            );

          if (!response.ok) {
            throw new Error(
              data.detail ||
                data.product_id?.[0] ||
                data.quantity?.[0] ||
                `افزودن محصول «${item.name}» به سبد سرور ناموفق بود.`
            );
          }
        }
      }
    };


  const clearServerCart =
    async () => {
      const response =
        await apiRequest(
          "/api/cart/",
          {
            method: "GET",
          }
        );

      const data =
        await readResponse(
          response
        );

      if (!response.ok) {
        throw new Error(
          data.detail ||
            "بررسی سبد سرور با خطا مواجه شد."
        );
      }

      const items =
        Array.isArray(
          data.items
        )
          ? data.items
          : [];

      for (
        const item of items
      ) {
        const deleteResponse =
          await apiRequest(
            `/api/cart/items/${item.id}/`,
            {
              method: "DELETE",
            }
          );

        if (
          !deleteResponse.ok
        ) {
          const deleteData =
            await readResponse(
              deleteResponse
            );

          throw new Error(
            deleteData.detail ||
              "پاک‌سازی سبد سرور ناموفق بود."
          );
        }
      }
    };


  const handleSubmit =
    async (event = null) => {
      if (event) {
        event.preventDefault();
      }

      if (loading) {
        return;
      }

      const hasSession =
        localStorage.getItem(
          "access_token"
        ) ||
        localStorage.getItem(
          "refresh_token"
        );

      if (!hasSession) {
        alert(
          "برای تکمیل سفارش ابتدا وارد حساب کاربری خود شوید."
        );

        navigate("/login");

        return;
      }

      const localCart =
        getCart();

      let orderId =
        localStorage.getItem(
          CHECKOUT_ORDER_KEY
        );

      if (
        !orderId &&
        !localCart.length
      ) {
        alert(
          "سبد خرید شما خالی است."
        );

        navigate("/cart");

        return;
      }

      try {
        setLoading(true);

        if (!orderId) {
          const selectedProvinceObject =
            provinces.find(
              (
                province
              ) =>
                String(
                  province.id
                ) ===
                String(
                  selectedProvince
                )
            );

          const selectedCityObject =
            cities.find(
              (city) =>
                String(
                  city.id
                ) ===
                String(
                  selectedCity
                )
            );

          if (
            !selectedProvinceObject
          ) {
            throw new Error(
              "لطفاً استان را انتخاب کنید."
            );
          }

          if (
            !selectedCityObject
          ) {
            throw new Error(
              "لطفاً شهر را انتخاب کنید."
            );
          }


          const addressResponse =
            await apiRequest(
              "/api/addresses/",
              {
                method:
                  "POST",
                body:
                  JSON.stringify(
                    {
                      title,
                      receiver_name:
                        receiverName,
                      phone,
                      province:
                        selectedProvinceObject.name,
                      city:
                        selectedCityObject.name,
                      address_line:
                        addressLine,
                      postal_code:
                        postalCode,
                      is_default:
                        isDefault,
                    }
                  ),
              }
            );

          const addressData =
            await readResponse(
              addressResponse
            );

          if (
            !addressResponse.ok
          ) {
            throw new Error(
              addressData.detail ||
                addressData
                  .title?.[0] ||
                addressData
                  .receiver_name?.[0] ||
                addressData
                  .phone?.[0] ||
                addressData
                  .province?.[0] ||
                addressData
                  .city?.[0] ||
                addressData
                  .address_line?.[0] ||
                addressData
                  .postal_code?.[0] ||
                "ثبت آدرس با خطا مواجه شد."
            );
          }

          if (
            !addressData.id
          ) {
            throw new Error(
              "آدرس ثبت شد، اما شناسه آدرس از سرور دریافت نشد."
            );
          }


          await syncServerCart(
            localCart
          );


          const orderResponse =
            await apiRequest(
              "/api/orders/",
              {
                method:
                  "POST",
                headers: {
                  "Idempotency-Key":
                    checkoutKeyRef.current,
                },
                body:
                  JSON.stringify(
                    {
                      shipping_address_id:
                        addressData.id,
                    }
                  ),
              }
            );

          const orderData =
            await readResponse(
              orderResponse
            );

          if (
            !orderResponse.ok
          ) {
            throw new Error(
              orderData.detail ||
                orderData.error ||
                orderData.message ||
                orderData
                  .shipping_address_id?.[0] ||
                "ایجاد سفارش با خطا مواجه شد."
            );
          }

          if (!orderData.id) {
            throw new Error(
              "سفارش ایجاد شد، اما شناسه سفارش از سرور دریافت نشد."
            );
          }

          orderId =
            String(
              orderData.id
            );

          localStorage.setItem(
            CHECKOUT_ORDER_KEY,
            orderId
          );

          /*
           * اگر بعد از ساخت Order،
           * Payment یا Redirect شکست بخورد،
           * صفحه فوراً وارد حالت Retry می‌شود.
           */
          setExistingOrderId(
            orderId
          );
        }


        /*
         * در Retry نیز Server Cart
         * باید خالی باشد.
         */
        await clearServerCart();


        const paymentResponse =
          await apiRequest(
            "/api/payments/",
            {
              method: "POST",
              body:
                JSON.stringify({
                  order:
                    Number(
                      orderId
                    ),
                }),
            }
          );

        const paymentData =
          await readResponse(
            paymentResponse
          );

        if (
          !paymentResponse.ok
        ) {
          throw new Error(
            paymentData.detail ||
              paymentData.order?.[0] ||
              "ایجاد پرداخت با خطا مواجه شد."
          );
        }

        if (
          !paymentData.id
        ) {
          throw new Error(
            "پرداخت ایجاد شد، اما شناسه پرداخت از سرور دریافت نشد."
          );
        }


        const redirectResponse =
          await apiRequest(
            `/api/payments/${paymentData.id}/redirect/`,
            {
              method: "GET",
            }
          );

        const redirectData =
          await readResponse(
            redirectResponse
          );

        if (
          !redirectResponse.ok
        ) {
          throw new Error(
            redirectData.detail ||
              "آدرس درگاه پرداخت دریافت نشد."
          );
        }

        if (
          !redirectData.payment_url
        ) {
          throw new Error(
            "آدرس درگاه پرداخت از سرور دریافت نشد."
          );
        }


        clearCart({
          preserveCheckoutSession: true,
        });

        window.location.href =
          redirectData.payment_url;
      } catch (error) {
        console.error(
          "خطا در تکمیل سفارش:",
          error
        );

        alert(
          error.message ||
            "تکمیل سفارش با خطا مواجه شد."
        );
      } finally {
        setLoading(false);
      }
    };


  /*
   * اگر Order قبلاً ساخته شده ولی
   * Checkout Session هنوز باقی است،
   * دیگر فرم آدرس نمایش داده نمی‌شود.
   *
   * کاربر مستقیماً پرداخت همان Order
   * را ادامه می‌دهد و Order جدیدی
   * ساخته نمی‌شود.
   */
  if (existingOrderId) {
    return (
      <section dir="rtl">
        <h2>
          تکمیل سفارش
        </h2>

        <p>
          یک سفارش پرداخت‌نشده از
          مرحله قبلی وجود دارد.
        </p>

        <p>
          برای جلوگیری از ایجاد سفارش
          تکراری، پرداخت همان سفارش
          ادامه داده می‌شود.
        </p>

        <button
          type="button"
          onClick={() =>
            handleSubmit()
          }
          disabled={loading}
        >
          {loading
            ? "در حال انتقال به درگاه..."
            : "ادامه پرداخت سفارش قبلی"}
        </button>
      </section>
    );
  }


  return (
    <section dir="rtl">
      <h2>
        تکمیل سفارش
      </h2>

      <form
        onSubmit={
          handleSubmit
        }
      >
        <div>
          <label
            htmlFor="title"
          >
            عنوان آدرس
          </label>

          <input
            id="title"
            name="title"
            type="text"
            placeholder="مثلاً خانه"
            value={title}
            onChange={(
              event
            ) =>
              setTitle(
                event.target
                  .value
              )
            }
            disabled={loading}
            required
          />
        </div>

        <div>
          <label
            htmlFor="receiver_name"
          >
            نام گیرنده
          </label>

          <input
            id="receiver_name"
            name="receiver_name"
            type="text"
            placeholder="نام و نام خانوادگی"
            value={
              receiverName
            }
            onChange={(
              event
            ) =>
              setReceiverName(
                event.target
                  .value
              )
            }
            disabled={loading}
            required
          />
        </div>

        <div>
          <label
            htmlFor="phone"
          >
            شماره موبایل
          </label>

          <input
            id="phone"
            name="phone"
            type="tel"
            placeholder="09123456789"
            value={phone}
            onChange={(
              event
            ) =>
              setPhone(
                event.target
                  .value
              )
            }
            disabled={loading}
            required
          />
        </div>

        <div>
          <label
            htmlFor="province"
          >
            استان
          </label>

          <select
            id="province"
            name="province"
            value={
              selectedProvince
            }
            onChange={(
              event
            ) =>
              setSelectedProvince(
                event.target
                  .value
              )
            }
            disabled={loading}
            required
          >
            <option value="">
              انتخاب استان
            </option>

            {provinces.map(
              (province) => (
                <option
                  key={
                    province.id
                  }
                  value={
                    province.id
                  }
                >
                  {
                    province.name
                  }
                </option>
              )
            )}
          </select>
        </div>

        <div>
          <label
            htmlFor="city"
          >
            شهر
          </label>

          <select
            id="city"
            name="city"
            value={
              selectedCity
            }
            onChange={(
              event
            ) =>
              setSelectedCity(
                event.target
                  .value
              )
            }
            disabled={
              loading ||
              !selectedProvince
            }
            required
          >
            <option value="">
              {selectedProvince
                ? "انتخاب شهر"
                : "ابتدا استان را انتخاب کنید"}
            </option>

            {cities.map(
              (city) => (
                <option
                  key={city.id}
                  value={
                    city.id
                  }
                >
                  {city.name}
                </option>
              )
            )}
          </select>
        </div>

        <div>
          <label
            htmlFor="address_line"
          >
            آدرس دقیق
          </label>

          <textarea
            id="address_line"
            name="address_line"
            rows="4"
            placeholder="آدرس کامل خود را وارد کنید"
            value={
              addressLine
            }
            onChange={(
              event
            ) =>
              setAddressLine(
                event.target
                  .value
              )
            }
            disabled={loading}
            required
          />
        </div>

        <div>
          <label
            htmlFor="postal_code"
          >
            کد پستی
          </label>

          <input
            id="postal_code"
            name="postal_code"
            type="text"
            placeholder="کد پستی ۱۰ رقمی"
            value={
              postalCode
            }
            onChange={(
              event
            ) =>
              setPostalCode(
                event.target
                  .value
              )
            }
            disabled={loading}
            required
          />
        </div>

        <div>
          <button
            type="button"
            onClick={
              handleUseCurrentLocation
            }
            disabled={loading}
          >
            استفاده از موقعیت فعلی من
          </button>
        </div>

        <div>
          <label>
            <input
              type="checkbox"
              name="is_default"
              checked={
                isDefault
              }
              onChange={(
                event
              ) =>
                setIsDefault(
                  event.target
                    .checked
                )
              }
              disabled={
                loading
              }
            />

            این آدرس، آدرس
            پیش‌فرض من باشد
          </label>
        </div>

        <button
          type="submit"
          disabled={loading}
        >
          {loading
            ? "در حال انتقال به درگاه..."
            : "ادامه و پرداخت"}
        </button>
      </form>
    </section>
  );
}


export default Checkout;