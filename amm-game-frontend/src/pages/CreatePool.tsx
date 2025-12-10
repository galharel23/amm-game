import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { poolAPI } from "../api/client";
import type { Currency } from "../api/client";

export function CreatePool() {
  const nav = useNavigate();
  const [currencies, setCurrencies] = useState<Currency[]>([]);
  const [loading, setLoading] = useState(true);
  const [cx, setCx] = useState("");
  const [cy, setCy] = useState("");
  const [xamt, setXamt] = useState("");
  const [yamt, setYamt] = useState("");
  const [err, setErr] = useState("");

  useEffect(() => {
    poolAPI
      .getCurrencies()
      .then((r) => setCurrencies(r.data.currencies))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErr("");
    if (!cx || !cy) {
      setErr("Choose two currencies");
      return;
    }
    if (cx === cy) {
      setErr("Currencies must differ");
      return;
    }
    try {
      await poolAPI.createPool(
        cx,
        cy,
        parseFloat(xamt || "0"),
        parseFloat(yamt || "0")
      );
      nav("/pools");
    } catch (e: any) {
      setErr(e?.response?.data?.detail?.detail || "Failed to create pool");
    }
  };

  return (
    <div className="container">
      <div className="card">
        <h2>Create Pool</h2>
        {loading ? (
          <p className="small">Loading currencies...</p>
        ) : (
          <form onSubmit={submit} style={{ display: "grid", gap: 10 }}>
            <div>
              <label className="small">Currency X</label>
              <select
                className="input"
                value={cx}
                onChange={(e) => setCx(e.target.value)}
              >
                <option value="">-- select --</option>
                {currencies.map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.symbol} — {c.name}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="small">Amount X</label>
              <input
                className="input"
                value={xamt}
                onChange={(e) => setXamt(e.target.value)}
                placeholder="1000"
              />
            </div>

            <div>
              <label className="small">Currency Y</label>
              <select
                className="input"
                value={cy}
                onChange={(e) => setCy(e.target.value)}
              >
                <option value="">-- select --</option>
                {currencies.map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.symbol} — {c.name}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="small">Amount Y</label>
              <input
                className="input"
                value={yamt}
                onChange={(e) => setYamt(e.target.value)}
                placeholder="5000"
              />
            </div>

            {err && <div style={{ color: "#a00" }}>{err}</div>}

            <div style={{ display: "flex", gap: 10 }}>
              <button type="submit" className="btn">
                Create Pool
              </button>
              <button
                type="button"
                className="btn secondary"
                onClick={() => nav("/")}
              >
                Cancel
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
}