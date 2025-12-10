import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Home } from './pages/Home';
import { CreatePool } from './pages/CreatePool';
import { PoolsList } from './pages/PoolsList';
import { Swap } from './pages/Swap';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/create-pool" element={<CreatePool />} />
        <Route path="/pools" element={<PoolsList />} />
        <Route path="/swap/:poolId" element={<Swap />} />
        <Route path="*" element={<Navigate to="/" />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;