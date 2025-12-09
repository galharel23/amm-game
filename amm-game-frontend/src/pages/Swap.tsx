import { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { poolAPI, Pool } from '../api/client';

export function Swap() {
  const navigate = useNavigate();
  const { poolId } = useParams<{ poolId: string }>();
  const [pool, setPool] = useState<Pool | null>(null);
  const [loading, setLoading] = useState(true);
  const [amountIn, setAmountIn] = useState('');
  const [amountOut, setAmountOut] = useState(0);
  const [swapDirection, setSwapDirection] = useState<'x-to-y' | 'y-to-x'>('x-to-y');
  const [slippage, setSlippage] = useState(0.5);
  const [swapping, setSwapping] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);

  useEffect(() => {
    if (poolId) fetchPool();
  }, [poolId]);

  const fetchPool = async () => {
    try {
      setLoading(true);
      const { data } = await poolAPI.getPool(poolId!);
      setPool(data);
    } catch (err) {
      setError('Failed to load pool');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (!pool || !amountIn) {
      setAmountOut(0);
      return;
    }

    const amount = parseFloat(amountIn);
    if (isNaN(amount) || amount <= 0) {
      setAmountOut(0);
      return;
    }

    if (swapDirection === 'x-to-y') {
      const xNew = pool.x_reserve + amount;
      const yNew = pool.K / xNew;
      const output = pool.y_reserve - yNew;
      setAmountOut(Math.max(0, output));
    } else {
      const yNew = pool.y_reserve + amount;
      const xNew = pool.K / yNew;
      const output = pool.x_reserve - xNew;
      setAmountOut(Math.max(0, output));
    }
  }, [amountIn, swapDirection, pool]);

  const handleSwap = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess(false);

    if (!poolId || !amountIn) {
      setError('Please enter an amount');
      return;
    }

    const amount = parseFloat(amountIn);
    const minAmountOut = amountOut * (1 - slippage / 100);

    try {
      setSwapping(true);
      if (swapDirection === 'x-to-y') {
        await poolAPI.swapXForY(poolId, amount, minAmountOut);
      } else {
        await poolAPI.swapYForX(poolId, amount, minAmountOut);
      }
      setSuccess(true);
      setAmountIn('');
      fetchPool();
      setTimeout(() => setSuccess(false), 3000);
    } catch (err: any) {
      setError(err.response?.data?.detail?.detail || 'Swap failed');
    } finally {
      setSwapping(false);
    }
  };

  if (loading) return <div className="min-h-screen flex items-center justify-center">Loading pool...</div>;
  if (!pool) return <div className="min-h-screen flex items-center justify-center">Pool not found</div>;

  return (
    <div className="min-h-screen bg-gradient-to-br from-emerald-50 to-teal-50 py-12 px-4">
      <div className="max-w-md mx-auto">
        <button onClick={() => navigate('/pools')} className="mb-6 text-emerald-600 hover:text-emerald-700 font-semibold">
          ← Back
        </button>

        <div className="bg-white rounded-lg shadow-lg p-8">
          <h1 className="text-2xl font-bold text-gray-900 mb-2">Swap</h1>
          <p className="text-gray-600 mb-6">Trade tokens instantly</p>

          {success && (
            <div className="mb-4 p-4 bg-green-50 border border-green-200 text-green-700 rounded-lg text-sm">
              ✅ Swap successful!
            </div>
          )}

          {error && (
            <div className="mb-4 p-4 bg-red-50 border border-red-200 text-red-700 rounded-lg text-sm">
              {error}
            </div>
          )}

          <form onSubmit={handleSwap} className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Sell</label>
              <div className="flex gap-2">
                <input
                  type="number"
                  value={amountIn}
                  onChange={(e) => setAmountIn(e.target.value)}
                  placeholder="0"
                  step="0.01"
                  min="0"
                  className="flex-1 px-4 py-3 text-2xl border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-transparent"
                />
                <div className="flex items-center px-4 py-3 bg-gray-100 rounded-lg font-semibold text-gray-700">
                  {swapDirection === 'x-to-y' ? 'X' : 'Y'}
                </div>
              </div>
            </div>

            <div className="flex justify-center">
              <button
                type="button"
                onClick={() => setSwapDirection(swapDirection === 'x-to-y' ? 'y-to-x' : 'x-to-y')}
                className="p-2 bg-gray-100 hover:bg-gray-200 rounded-full transition-all duration-200"
              >
                <div className="text-2xl">⇅</div>
              </button>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Buy</label>
              <div className="flex gap-2">
                <input
                  type="number"
                  value={amountOut.toFixed(8)}
                  readOnly
                  placeholder="0"
                  className="flex-1 px-4 py-3 text-2xl border border-gray-300 rounded-lg bg-gray-50 text-gray-600"
                />
                <div className="flex items-center px-4 py-3 bg-gray-100 rounded-lg font-semibold text-gray-700">
                  {swapDirection === 'x-to-y' ? 'Y' : 'X'}
                </div>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Slippage: {slippage.toFixed(1)}%
              </label>
              <input
                type="range"
                min="0"
                max="5"
                step="0.1"
                value={slippage}
                onChange={(e) => setSlippage(parseFloat(e.target.value))}
                className="w-full"
              />
            </div>

            <div className="bg-gray-50 rounded-lg p-4 space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-600">Price X→Y:</span>
                <span className="font-semibold">{pool.price_x_in_y.toFixed(6)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">X Reserve:</span>
                <span className="font-semibold">{pool.x_reserve.toFixed(2)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Y Reserve:</span>
                <span className="font-semibold">{pool.y_reserve.toFixed(2)}</span>
              </div>
            </div>

            <button
              type="submit"
              disabled={swapping || !amountIn}
              className="w-full py-3 px-4 bg-emerald-500 hover:bg-emerald-600 disabled:bg-gray-400 text-white font-semibold rounded-lg transition-all duration-200"
            >
              {swapping ? 'Swapping...' : 'Swap'}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}