import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface Currency {
  id: string;
  symbol: string;
  name: string;
  decimals: number;
  image_url: string | null;
  pools_count: number;
  created_at: string;
}

export interface Pool {
  id: string;
  x_reserve: number;
  y_reserve: number;
  K: number;
  price_x_in_y: number;
  price_y_in_x: number;
  is_active: boolean;
  created_at: string;
}

export interface SwapResponse {
  pool: Pool;
  amount_in: number;
  amount_out: number;
  price_execution: number;
}

export const poolAPI = {
  getCurrencies: (skip = 0, limit = 100) =>
    apiClient.get<{ currencies: Currency[]; total: number }>('/pools/currencies/', {
      params: { skip, limit },
    }),

  getPools: (skip = 0, limit = 100) =>
    apiClient.get<{ pools: Pool[]; total: number }>('/pools/', {
      params: { skip, limit },
    }),

  getPool: (poolId: string) =>
    apiClient.get<Pool>(`/pools/${poolId}`),

  createPool: (currencyXId: string, currencyYId: string, xInit: number, yInit: number) =>
    apiClient.post<Pool>('/pools/', {
      currency_x_id: currencyXId,
      currency_y_id: currencyYId,
      x_init: xInit,
      y_init: yInit,
    }),

  swapXForY: (poolId: string, amountIn: number, minAmountOut: number = 0) =>
    apiClient.post<SwapResponse>(`/pools/${poolId}/swap/x-for-y`, {
      amount_in: amountIn,
      min_amount_out: minAmountOut,
    }),

  swapYForX: (poolId: string, amountIn: number, minAmountOut: number = 0) =>
    apiClient.post<SwapResponse>(`/pools/${poolId}/swap/y-for-x`, {
      amount_in: amountIn,
      min_amount_out: minAmountOut,
    }),
};