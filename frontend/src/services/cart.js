const CART_KEY = "marketplace_cart";

const CHECKOUT_IDEMPOTENCY_KEY =
  "checkout_idempotency_key";

const CHECKOUT_ORDER_KEY =
  "checkout_order_id";


export function resetCheckoutSession() {
  localStorage.removeItem(
    CHECKOUT_IDEMPOTENCY_KEY
  );

  localStorage.removeItem(
    CHECKOUT_ORDER_KEY
  );
}


export function getCart() {
  try {
    const cart =
      localStorage.getItem(CART_KEY);

    return cart
      ? JSON.parse(cart)
      : [];
  } catch {
    return [];
  }
}


export function saveCart(cart) {
  localStorage.setItem(
    CART_KEY,
    JSON.stringify(cart)
  );

  resetCheckoutSession();
}


export function addToCart(product) {
  const cart = getCart();

  const existingItem = cart.find(
    (item) =>
      item.id === product.id
  );

  if (existingItem) {
    existingItem.quantity += 1;
  } else {
    cart.push({
      id: product.id,
      name: product.name,
      price: product.price,
      category_name:
        product.category_name,
      quantity: 1,
    });
  }

  saveCart(cart);

  return cart;
}


export function updateCartQuantity(
  productId,
  quantity
) {
  const cart = getCart();

  const updatedCart = cart
    .map((item) =>
      item.id === productId
        ? {
            ...item,
            quantity:
              Number(quantity),
          }
        : item
    )
    .filter(
      (item) =>
        item.quantity > 0
    );

  saveCart(updatedCart);

  return updatedCart;
}


export function removeFromCart(
  productId
) {
  const cart = getCart();

  const updatedCart =
    cart.filter(
      (item) =>
        item.id !== productId
    );

  saveCart(updatedCart);

  return updatedCart;
}


export function clearCart(
  options = {}
) {
  const {
    preserveCheckoutSession = false,
  } = options;

  localStorage.removeItem(
    CART_KEY
  );

  if (!preserveCheckoutSession) {
    resetCheckoutSession();
  }
}


export function getCartTotal(
  cart = getCart()
) {
  return cart.reduce(
    (total, item) =>
      total +
      Number(item.price) *
        item.quantity,
    0
  );
}


export function getCartCount(
  cart = getCart()
) {
  return cart.reduce(
    (total, item) =>
      total + item.quantity,
    0
  );
}