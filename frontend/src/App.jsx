import { BrowserRouter, Routes, Route } from "react-router-dom";

import MainLayout from "./layouts/MainLayout/MainLayout";

import Home from "./pages/home/Home";
import Products from "./pages/products/Products";
import ProductDetail from "./pages/products/ProductDetail";
import Cart from "./pages/cart/Cart";
import Checkout from "./pages/checkout/Checkout";
import Profile from "./pages/profile/Profile";
import Orders from "./pages/orders/Orders";
import AdminOrders from "./pages/admin-orders/AdminOrders";
import About from "./pages/about/About";
import Contact from "./pages/contact/Contact";
import Login from "./pages/login/Login";
import Register from "./pages/register/Register";
import Terms from "./pages/legal/Terms";

import MarketplaceAtmosphere from "./MarketplaceAtmosphere";

function App() {
  return (
    <BrowserRouter>
      <div className="app-shell">
        <MarketplaceAtmosphere />

        <div className="app-content">
          <Routes>
            <Route
              path="/"
              element={<MainLayout />}
            >
              <Route
                index
                element={<Home />}
              />

              <Route
                path="products"
                element={<Products />}
              />

              <Route
                path="products/:id"
                element={<ProductDetail />}
              />

              <Route
                path="cart"
                element={<Cart />}
              />

              <Route
                path="checkout"
                element={<Checkout />}
              />

              <Route
                path="profile"
                element={<Profile />}
              />

              <Route
                path="orders"
                element={<Orders />}
              />

              <Route
                path="admin/orders"
                element={<AdminOrders />}
              />

              <Route
                path="about"
                element={<About />}
              />

              <Route
                path="contact"
                element={<Contact />}
              />

              <Route
                path="login"
                element={<Login />}
              />

              <Route
                path="register"
                element={<Register />}
              />

              <Route
                path="terms"
                element={<Terms />}
              />
            </Route>
          </Routes>
        </div>
      </div>
    </BrowserRouter>
  );
}

export default App;