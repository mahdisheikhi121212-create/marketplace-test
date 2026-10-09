import API_BASE_URL, {
  apiRequest,
  loginUser,
} from "../api";

export {
  apiRequest,
  loginUser,
};

export function apiUrl(path) {
  return `${API_BASE_URL}${path}`;
}

export default API_BASE_URL;