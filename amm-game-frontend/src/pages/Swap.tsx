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
  const [status, setStatus] = useState<string>("");

  useEffect(() => {
    if (!poolId) return;
    (async () => {
      setLoading(true);
      try {
        const r = await poolAPI.getPool(poolId);
        setPool(r.data);
      } catch {
        setPool(null);
      } finally {
        setLoading(false);
      }
    })();
  }, [poolId]);

  // Derived symbols for UI
  const sellSymbol =
    direction === "x-to-y"
      ? pool?.currency_x_symbol ?? "X"
      : pool?.currency_y_symbol ?? "Y";
  const buySymbol =
    direction === "x-to-y"
      ? pool?.currency_y_symbol ?? "Y"
      : pool?.currency_x_symbol ?? "X";

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
    if (!poolId) return;
    setStatus("");
    try {
      const amt = parseFloat(amountIn);
      if (!amt || amt <= 0) {
        setStatus("Enter a positive amount");
        return;
      }

      // No slippage UI: always send min_amount_out = 0 (or use default)
      if (direction === "x-to-y") {
        await poolAPI.swapXForY(poolId, amt, 0);
      } else {
        await poolAPI.swapYForX(poolId, amt, 0);
      }

      setStatus("Swap executed");
      setAmountIn("");
    } catch (err: any) {
      setStatus(err?.response?.data?.detail?.detail || "Swap failed");
    }
  };

  if (loading)
    return (
      <div className="container center">
        <div className="card">Loading pool…</div>
      </div>
    );
  if (!pool)
    return (
      <div className="container center">
        <div className="card">Pool not found</div>
      </div>
    );

  return (
    <div className="container center">
      <div className="card" style={{ width: "100%", maxWidth: 720 }}>
        <button className="btn secondary" onClick={() => nav("/pools")}>
          ← Back
        </button>
        <h2 style={{ marginTop: 12, fontSize: "1.8rem" }}>
          Swap {pool.currency_x_symbol}/{pool.currency_y_symbol}
        </h2>
        <p className="small" style={{ marginBottom: 16 }}>
          Current price {pool.currency_x_symbol}→{pool.currency_y_symbol}:{" "}
          {pool.price_x_in_y.toFixed(6)}
        </p>

        <form onSubmit={doSwap} style={{ display: "grid", gap: 16 }}>
          <div>
            <label className="small">
              Sell amount ({sellSymbol})
            </label>
            <input
              className="input"
              value={amountIn}
              onChange={(e) => setAmountIn(e.target.value)}
              placeholder="0.0"
            />
          </div>

          <div style={{ textAlign: "center" }}>
            <button
              type="button"
              className="btn secondary"
              onClick={() =>
                setDirection(direction === "x-to-y" ? "y-to-x" : "x-to-y")
              }
            >
              ⇅ Switch direction
            </button>
          </div>

          <div>
            <label className="small">
              Receive (est.) ({buySymbol})
            </label>
            <input className="input" value={amountOut.toFixed(8)} readOnly />
          </div>

          {/* Status only, no slippage controls */}
          {status && (
            <div
              className="small"
              style={{ color: status.includes("failed") ? "red" : "green" }}
            >
              {status}
            </div>
          )}

          <button type="submit" className="btn">
            Swap
          </button>
        </form>
      </div>
    </div>
  );
}