import axios from "axios";

const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

export const apiClient = axios.create({
  baseURL: API_BASE,
  headers: { "Content-Type": "application/json" },
});

export type Currency = {
  id: string;
  symbol: string;
  name: string;
  decimals: number;
  image_url?: string | null;
  pools_count: number;
  created_at: string;
};

export type Pool = {
  id: string;
  x_reserve: number;
  y_reserve: number;
  K: number;
  price_x_in_y: number;
  price_y_in_x: number;
  is_active: boolean;
  created_at: string;
};

export const poolAPI = {
  getCurrencies: (skip = 0, limit = 100) =>
    apiClient.get<{ currencies: Currency[]; total: number }>("/pools/currencies/", { params: { skip, limit } }),
  getPools: (skip = 0, limit = 100) =>
    apiClient.get<{ pools: Pool[]; total: number }>("/pools/", { params: { skip, limit } }),
  getPool: (id: string) => apiClient.get<Pool>(`/pools/${id}`),
  createPool: (cx: string, cy: string, x_init: number, y_init: number) =>
    apiClient.post<Pool>("/pools/", { currency_x_id: cx, currency_y_id: cy, x_init, y_init }),
  swapXForY: (poolId: string, amount_in: number, min_amount_out = 0) =>
    apiClient.post(`/pools/${poolId}/swap/x-for-y`, { amount_in, min_amount_out }),
  swapYForX: (poolId: string, amount_in: number, min_amount_out = 0) =>
    apiClient.post(`/pools/${poolId}/swap/y-for-x`, { amount_in, min_amount_out }),
};