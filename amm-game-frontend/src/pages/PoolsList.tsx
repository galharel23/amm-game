import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { poolAPI, Pool } from '../api/client';

export function PoolsList() {
  const navigate = useNavigate();
  const [pools, setPools] = useState<Pool[]>([]);
  const [loading, setLoading] = useState(true);
  const [skip, setSkip] = useState(0);
  const [total, setTotal] = useState(0);
  const limit = 10;

  useEffect(() => {
    fetchPools();
  }, [skip]);

  const fetchPools = async () => {
    try {
      setLoading(true);
      const { data } = await poolAPI.getPools(skip, limit);
      setPools(data.pools);
      setTotal(data.total);
    } catch (err) {
      console.error('Failed to load pools', err);
    } finally {
      setLoading(false);
    }
  };

  const totalPages = Math.ceil(total / limit);
  const currentPage = skip / limit + 1;

  return (
    <div className="min-h-screen bg-gradient-to-br from-emerald-50 to-teal-50 py-12 px-4">
      <div className="max-w-2xl mx-auto">
        <button onClick={() => navigate('/')} className="mb-6 text-emerald-600 hover:text-emerald-700 font-semibold">
          ← Back
        </button>

        <h1 className="text-3xl font-bold text-gray-900 mb-8">Available Pools</h1>

        {loading ? (
          <div className="text-center py-12">Loading pools...</div>
        ) : pools.length === 0 ? (
          <div className="text-center py-12 bg-white rounded-lg shadow">
            <p className="text-gray-600 mb-4">No pools available yet</p>
            <button onClick={() => navigate('/create-pool')} className="text-emerald-600 hover:text-emerald-700 font-semibold">
              Create the first pool →
            </button>
          </div>
        ) : (
          <>
            <div className="space-y-4 mb-8">
              {pools.map((pool) => (
                <button
                  key={pool.id}
                  onClick={() => navigate(`/swap/${pool.id}`)}
                  className="w-full text-left bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-all duration-200 border-2 border-transparent hover:border-emerald-500"
                >
                  <div className="flex justify-between items-center">
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900">Pool</h3>
                      <p className="text-sm text-gray-600 mt-2">
                        X: {pool.x_reserve.toFixed(2)} | Y: {pool.y_reserve.toFixed(2)}
                      </p>
                      <p className="text-sm text-gray-600">
                        Price X→Y: {pool.price_x_in_y.toFixed(4)}
                      </p>
                    </div>
                    <div className="text-emerald-600 text-2xl">→</div>
                  </div>
                </button>
              ))}
            </div>

            {totalPages > 1 && (
              <div className="flex justify-between items-center bg-white rounded-lg shadow p-4">
                <button
                  onClick={() => setSkip(Math.max(0, skip - limit))}
                  disabled={skip === 0}
                  className="px-4 py-2 bg-emerald-500 text-white rounded-lg disabled:bg-gray-300 hover:bg-emerald-600"
                >
                  ← Previous
                </button>

                <div className="text-gray-600">
                  Page {currentPage} of {totalPages}
                </div>

                <button
                  onClick={() => setSkip(skip + limit)}
                  disabled={currentPage >= totalPages}
                  className="px-4 py-2 bg-emerald-500 text-white rounded-lg disabled:bg-gray-300 hover:bg-emerald-600"
                >
                  Next →
                </button>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}