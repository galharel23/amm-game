import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { poolAPI } from "../api/client";

export function Home() {
  const nav = useNavigate();
  const [poolsCount, setPoolsCount] = useState<number | null>(null);
  const [currenciesCount, setCurrenciesCount] = useState<number | null>(null);

  useEffect(() => {
    // Fetch small stats from backend to prove integration
    poolAPI
      .getPools(0, 1)
      .then((r) => setPoolsCount(r.data.total))
      .catch(() => setPoolsCount(null));

    poolAPI
      .getCurrencies(0, 1)
      .then((r) => setCurrenciesCount(r.data.total))
      .catch(() => setCurrenciesCount(null));
  }, []);

  return (
    <div className="container center">
      <div
        className="card"
        style={{
          width: "100%",
          maxWidth: 420, // was 780, keep it small like the global .card
          textAlign: "center",
        }}
      >
        <div className="huge">AMM Game</div>

        <p className="note" style={{ marginTop: 10 }}>
          Simple AMM UI — create or use a liquidity pool connected to your backend.
        </p>

        {/* Live backend stats */}
        <div style={{ marginTop: 20 }} className="small">
          {poolsCount !== null && currenciesCount !== null ? (
            <span>
              {poolsCount} pools • {currenciesCount} currencies (live from backend)
            </span>
          ) : (
            <span>Loading stats from backend…</span>
          )}
        </div>

        <div style={{ marginTop: 32 }} className="row">
          <button className="btn" onClick={() => nav("/create-pool")}>
            ➕ Create a Pool
          </button>
          <button className="btn secondary" onClick={() => nav("/pools")}>
            🔄 Use a Pool
          </button>
        </div>
      </div>
    </div>
  );
}