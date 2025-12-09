import { useNavigate } from 'react-router-dom';

export function Home() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-gradient-to-br from-emerald-50 to-teal-50 flex items-center justify-center px-4">
      <div className="max-w-md w-full space-y-8 text-center">
        <div>
          <h1 className="text-4xl font-bold text-gray-900">AMM Game</h1>
          <p className="mt-2 text-gray-600">Swap tokens instantly</p>
        </div>

        <div className="space-y-4">
          <button
            onClick={() => navigate('/create-pool')}
            className="w-full py-4 px-6 bg-emerald-500 hover:bg-emerald-600 text-white font-semibold rounded-lg shadow-lg transition-all duration-200 transform hover:scale-105"
          >
            ➕ Create a Pool
          </button>

          <button
            onClick={() => navigate('/pools')}
            className="w-full py-4 px-6 bg-blue-500 hover:bg-blue-600 text-white font-semibold rounded-lg shadow-lg transition-all duration-200 transform hover:scale-105"
          >
            🔄 Use a Pool
          </button>
        </div>

        <div className="text-sm text-gray-500 mt-12">
          <p>Constant-product AMM</p>
        </div>
      </div>
    </div>
  );
}