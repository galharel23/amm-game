import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { poolAPI } from "../api/client";
import type { Pool } from "../api/client";

export function PoolsList() {
  const nav = useNavigate();
  const [pools, setPools] = useState<Pool[]>([]);
  const [loading, setLoading] = useState(true);
  const [skip, setSkip] = useState(0);
  const limit = 10;
  const [total, setTotal] = useState(0);

  useEffect(() => {
    setLoading(true);
    poolAPI
      .getPools(skip, limit)
      .then((r) => {
        setPools(r.data.pools);
        setTotal(r.data.total);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [skip]);

  return (
    <div className="container">
      <div className="card">
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
          }}
        >
          <h2>Available Pools</h2>
          <button className="btn" onClick={() => nav("/create-pool")}>
            Create
          </button>
        </div>

        {loading ? (
          <p className="small">Loading pools...</p>
        ) : (
          <>
            {pools.length === 0 ? (
              <div>
                <p>No pools yet</p>
                <button className="btn" onClick={() => nav("/create-pool")}>
                  Create first pool
                </button>
              </div>
            ) : (
              <div style={{ display: "grid", gap: 10 }}>
                {pools.map((p) => (
                  <div
                    key={p.id}
                    className="card"
                    style={{
                      display: "flex",
                      justifyContent: "space-between",
                      alignItems: "center",
                    }}
                  >
                    <div>
                      <div style={{ fontWeight: 700 }}>Pool</div>
                      <div className="small">
                        X: {p.x_reserve.toFixed(2)} • Y: {p.y_reserve.toFixed(2)}
                      </div>
                      <div className="small">
                        Price X→Y: {p.price_x_in_y.toFixed(6)}
                      </div>
                    </div>
                    <div>
                      <button
                        className="btn"
                        onClick={() => nav(`/swap/${p.id}`)}
                      >
                        Use →
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </>
        )}

        <div
          style={{
            marginTop: 12,
            display: "flex",
            justifyContent: "space-between",
          }}
        >
          <button
            className="btn"
            disabled={skip === 0}
            onClick={() => setSkip(Math.max(0, skip - limit))}
          >
            ← Prev
          </button>
          <div className="small">Page {skip / limit + 1}</div>
          <button
            className="btn"
            disabled={skip + limit >= total}
            onClick={() => setSkip(skip + limit)}
          >
            Next →
          </button>
        </div>
      </div>
    </div>
  );
}