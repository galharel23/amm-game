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

  // NEW: state for "add currency" form
  const [newSymbol, setNewSymbol] = useState("");
  const [newName, setNewName] = useState("");
  const [newImageUrl, setNewImageUrl] = useState("");
  const [newErr, setNewErr] = useState("");
  const [creatingCurrency, setCreatingCurrency] = useState(false);

  // NEW: control popup visibility
  const [showNewCurrencyModal, setShowNewCurrencyModal] = useState(false);

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
    // ...existing validation & pool creation logic...
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

  // NEW: submit handler for creating a new currency
  const submitNewCurrency = async (e: React.FormEvent) => {
    e.preventDefault();
    setNewErr("");

    const symbol = newSymbol.trim();
    const name = newName.trim();

    if (!symbol || !name) {
      setNewErr("Symbol and name are required");
      return;
    }

    try {
      setCreatingCurrency(true);
      const res = await poolAPI.createCurrency(
        symbol,
        name,
        newImageUrl.trim() || undefined
      );

      // Add to local list so it appears in dropdowns immediately
      setCurrencies((prev) => [...prev, res.data]);

      // Optionally preselect in X or Y if empty
      if (!cx) setCx(res.data.id);
      else if (!cy) setCy(res.data.id);

      // Clear form
      setNewSymbol("");
      setNewName("");
      setNewImageUrl("");
      setNewErr("");

      // close popup on success
      setShowNewCurrencyModal(false);
    } catch (e: any) {
      setNewErr(e?.response?.data?.detail?.detail || "Failed to create currency");
    } finally {
      setCreatingCurrency(false);
    }
  };

  if (loading) {
    return (
      <div className="container center">
        <div className="card">Loading…</div>
      </div>
    );
  }

  return (
    <div className="container center">
      <div className="card" style={{ width: "100%", maxWidth: 720 }}>
        <h2 style={{ fontSize: "1.8rem", marginBottom: 8 }}>Create Pool</h2>
        <p className="small" style={{ marginBottom: 20 }}>
          Select two currencies and set their initial reserves.
        </p>

        {/* --- Pool form --- */}
        <form onSubmit={submit} style={{ display: "grid", gap: 16 }}>
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

          <div
            style={{
              display: "flex",
              gap: 12,
              marginTop: 8,
              justifyContent: "space-between",
            }}
          >
            <div style={{ display: "flex", gap: 12 }}>
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

            {/* Button to open popup */}
            <button
              type="button"
              className="btn secondary"
              onClick={() => setShowNewCurrencyModal(true)}
            >
              + Add new currency
            </button>
          </div>
        </form>
      </div>

      {/* --- New currency modal popup --- */}
      {showNewCurrencyModal && (
        <div className="modal-backdrop">
          <div className="modal-card">
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                marginBottom: 8,
              }}
            >
              <h3 style={{ fontSize: "1.2rem", margin: 0 }}>Add new currency</h3>
              <button
                type="button"
                className="modal-close-btn"
                onClick={() => setShowNewCurrencyModal(false)}
              >
                ✕
              </button>
            </div>

            <p className="small" style={{ marginBottom: 12 }}>
              Create a new currency; it will appear in the lists above.
            </p>

            <form
              onSubmit={submitNewCurrency}
              style={{ display: "grid", gap: 12 }}
            >
              <div>
                <label className="small">Symbol</label>
                <input
                  className="input"
                  value={newSymbol}
                  onChange={(e) => setNewSymbol(e.target.value)}
                  placeholder="e.g. BTC"
                />
              </div>

              <div>
                <label className="small">Name</label>
                <input
                  className="input"
                  value={newName}
                  onChange={(e) => setNewName(e.target.value)}
                  placeholder="e.g. Bitcoin"
                />
              </div>

              <div>
                <label className="small">Image URL (optional)</label>
                <input
                  className="input"
                  value={newImageUrl}
                  onChange={(e) => setNewImageUrl(e.target.value)}
                  placeholder="https://example.com/logo.png"
                />
              </div>

              {newErr && <div style={{ color: "#a00" }}>{newErr}</div>}

              <div style={{ display: "flex", gap: 12, marginTop: 4 }}>
                <button
                  type="submit"
                  className="btn"
                  disabled={creatingCurrency}
                >
                  {creatingCurrency ? "Adding…" : "Add currency"}
                </button>
                <button
                  type="button"
                  className="btn secondary"
                  onClick={() => setShowNewCurrencyModal(false)}
                >
                  Close
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}