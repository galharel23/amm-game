import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { poolAPI, Currency } from '../api/client';

export function CreatePool() {
  const navigate = useNavigate();
  const [currencies, setCurrencies] = useState<Currency[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [currencyX, setCurrencyX] = useState('');
  const [currencyY, setCurrencyY] = useState('');
  const [amountX, setAmountX] = useState('');
  const [amountY, setAmountY] = useState('');
  const [creating, setCreating] = useState(false);

  useEffect(() => {
    fetchCurrencies();
  }, []);

  const fetchCurrencies = async () => {
    try {
      const { data } = await poolAPI.getCurrencies(0, 100);
      setCurrencies(data.currencies);
    } catch (err) {
      setError('Failed to load currencies');
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (!currencyX || !currencyY || !amountX || !amountY) {
      setError('Please fill in all fields');
      return;
    }

    if (currencyX === currencyY) {
      setError('Please select different currencies');
      return;
    }

    try {
      setCreating(true);
      await poolAPI.createPool(currencyX, currencyY, parseFloat(amountX), parseFloat(amountY));
      navigate('/pools');
    } catch (err: any) {
      setError(err.response?.data?.detail?.detail || 'Failed to create pool');
    } finally {
      setCreating(false);
    }
  };

  if (loading) return <div className="min-h-screen flex items-center justify-center">Loading...</div>;

  return (
    <div className="min-h-screen bg-gradient-to-br from-emerald-50 to-teal-50 py-12 px-4">
      <div className="max-w-md mx-auto">
        <button onClick={() => navigate('/')} className="mb-6 text-emerald-600 hover:text-emerald-700 font-semibold">
          ← Back
        </button>

        <div className="bg-white rounded-lg shadow-lg p-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Create Pool</h1>
          <p className="text-gray-600 mb-6">Set up a new liquidity pool</p>

          {error && (
            <div className="mb-4 p-4 bg-red-50 border border-red-200 text-red-700 rounded-lg text-sm">
              {error}
            </div>
          )}

          <form onSubmit={handleCreate} className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Sell (Currency X)</label>
              <select
                value={currencyX}
                onChange={(e) => setCurrencyX(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-transparent"
              >
                <option value="">Select currency</option>
                {currencies.map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.symbol} - {c.name}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Amount</label>
              <input
                type="number"
                value={amountX}
                onChange={(e) => setAmountX(e.target.value)}
                placeholder="0.00"
                step="0.01"
                min="0"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-transparent"
              />
            </div>

            <div className="flex justify-center pt-4">
              <div className="text-2xl text-gray-400">⇅</div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Buy (Currency Y)</label>
              <select
                value={currencyY}
                onChange={(e) => setCurrencyY(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-transparent"
              >
                <option value="">Select currency</option>
                {currencies.map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.symbol} - {c.name}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Amount</label>
              <input
                type="number"
                value={amountY}
                onChange={(e) => setAmountY(e.target.value)}
                placeholder="0.00"
                step="0.01"
                min="0"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-transparent"
              />
            </div>

            <button
              type="submit"
              disabled={creating}
              className="w-full py-3 px-4 bg-emerald-500 hover:bg-emerald-600 disabled:bg-gray-400 text-white font-semibold rounded-lg transition-all duration-200"
            >
              {creating ? 'Creating...' : 'Create Pool'}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}