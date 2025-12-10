import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { poolAPI } from "../api/client";

export function Swap() {
  const nav = useNavigate();
  const { poolId } = useParams<{ poolId: string }>();
  const [pool, setPool] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [amountIn, setAmountIn] = useState("");
  const [amountOut, setAmountOut] = useState(0);
  const [direction, setDirection] = useState<"x-to-y" | "y-to-x">("x-to-y");
  const [slippage, setSlippage] = useState(0.5);
  const [status, setStatus] = useState<string>("");

  useEffect(() => {
    if (poolId) fetchPool();
  }, [poolId]);

  const fetchPool = async () => {
    setLoading(true);
    try {
      const r = await poolAPI.getPool(poolId!);
      setPool(r.data);
    } catch (e) {
      setPool(null);
    }
    setLoading(false);
  };

  useEffect(() => {
    if (!pool) {
      setAmountOut(0);
      return;
    }
    const amt = parseFloat(amountIn || "0");
    if (!amt || amt <= 0) {
      setAmountOut(0);
      return;
    }
    if (direction === "x-to-y") {
      const xNew = pool.x_reserve + amt;
      const yNew = pool.K / xNew;
      setAmountOut(Math.max(0, pool.y_reserve - yNew));
    } else {
      const yNew = pool.y_reserve + amt;
      const xNew = pool.K / yNew;
      setAmountOut(Math.max(0, pool.x_reserve - xNew));
    }
  }, [amountIn, direction, pool]);

  const doSwap = async (e: React.FormEvent) => {
    e.preventDefault();
    setStatus("");
    try {
      if (!poolId) return;
      const amt = parseFloat(amountIn);
      const min_out = amountOut * (1 - slippage / 100);
      if (direction === "x-to-y") {
        await poolAPI.swapXForY(poolId, amt, min_out);
      } else {
        await poolAPI.swapYForX(poolId, amt, min_out);
      }
      setStatus("Swap executed");
      setAmountIn("");
      fetchPool();
    } catch (err: any) {
      setStatus(err?.response?.data?.detail?.detail || "Swap failed");
    }
  };

  if (loading)
    return (
      <div className="container center">
        <div className="card">Loading...</div>
      </div>
    );
  if (!pool)
    return (
      <div className="container center">
        <div className="card">Pool not found</div>
      </div>
    );

  return (
    <div className="container">
      <div className="card">
        <button className="btn secondary" onClick={() => nav("/pools")}>
          ← Back
        </button>
        <h3 style={{ marginTop: 8 }}>Swap</h3>
        <p className="small">Pool price X→Y: {pool.price_x_in_y.toFixed(6)}</p>

        <form
          onSubmit={doSwap}
          style={{ display: "grid", gap: 10, marginTop: 10 }}
        >
          <div>
            <label className="small">Sell amount</label>
            <input
              className="input"
              value={amountIn}
              onChange={(e) => setAmountIn(e.target.value)}
            />
          </div>

          <div className="center">
            <button
              type="button"
              className="btn"
              onClick={() =>
                setDirection(direction === "x-to-y" ? "y-to-x" : "x-to-y")
              }
            >
              ⇅ Switch
            </button>
          </div>

          <div>
            <label className="small">Receive (estimated)</label>
            <input
              className="input"
              value={amountOut.toFixed(8)}
              readOnly
            />
          </div>

          <div>
            <label className="small">Slippage ({slippage}%)</label>
            <input
              type="range"
              min={0}
              max={5}
              step={0.1}
              value={slippage}
              onChange={(e) => setSlippage(parseFloat(e.target.value))}
            />
          </div>

          {status && (
            <div
              className="small"
              style={{
                color: status.includes("failed") ? "red" : "green",
              }}
            >
              {status}
            </div>
          )}

          <button className="btn" type="submit">
            Swap
          </button>
        </form>
      </div>
    </div>
  );
}