import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { poolAPI } from "../api/client";
import type { Pool, Currency } from "../api/client";

export function PoolsList() {
  const nav = useNavigate();

  // All pools from backend
  const [allPools, setAllPools] = useState<Pool[]>([]);
  const [loading, setLoading] = useState(true);

  // All currencies from backend
  const [currencies, setCurrencies] = useState<Currency[]>([]);

  // Selected currencies (filters)
  const [selectedCurrencyIds, setSelectedCurrencyIds] = useState<string[]>([]);

  // Frontend pagination (2 pools per page)
  const pageSize = 2;
  const [page, setPage] = useState(0);

  useEffect(() => {
    setLoading(true);
    Promise.all([
      poolAPI.getPools(0, 1000),
      poolAPI.getCurrencies(0, 1000),
    ])
      .then(([poolsRes, curRes]) => {
        setAllPools(poolsRes.data.pools);
        setCurrencies(curRes.data.currencies);
      })
      .catch(() => {
        setAllPools([]);
        setCurrencies([]);
      })
      .finally(() => setLoading(false));
  }, []);

  // Apply currency filters (if none selected, show all)
  const filteredPools =
    selectedCurrencyIds.length === 0
      ? allPools
      : allPools.filter((p) =>
          selectedCurrencyIds.some(
            (id) => id === p.currency_x_id || id === p.currency_y_id,
          ),
        );

  const totalPages = Math.max(1, Math.ceil(filteredPools.length / pageSize));

  useEffect(() => {
    if (page >= totalPages) {
      setPage(totalPages - 1);
    }
  }, [page, totalPages]);

  const visiblePools = filteredPools.slice(
    page * pageSize,
    page * pageSize + pageSize,
  );

  const toggleCurrency = (id: string) => {
    setPage(0);
    setSelectedCurrencyIds((prev) =>
      prev.includes(id) ? prev.filter((cId) => cId !== id) : [...prev, id],
    );
  };

  const clearFilters = () => {
    setSelectedCurrencyIds([]);
    setPage(0);
  };

  return (
    <div className="container center">
      <div className="card" style={{ width: "100%", maxWidth: 900 }}>
        {/* Header row with Home / title / New Pool */}
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            marginBottom: 12,
          }}
        >
          <button className="btn secondary" onClick={() => nav("/")}>
            ← Home
          </button>

          <h2 style={{ fontSize: "1.6rem", margin: 0 }}>Available Pools</h2>

          <button className="btn" onClick={() => nav("/create-pool")}>
            ➕ New Pool
          </button>
        </div>

        {/* Currency filter UI */}
        <div className="currency-filter">
          {/* NEW: label */}
          <div className="small" style={{ marginBottom: 4 }}>
            Filter by currency
          </div>

          {/* Selected currencies (chips with X) */}
          {selectedCurrencyIds.length > 0 && (
            <div className="currency-selected-row">
              {selectedCurrencyIds.map((id) => {
                const cur = currencies.find((c) => c.id === id);
                if (!cur) return null;
                return (
                  <div
                    key={id}
                    className="currency-chip currency-chip--selected"
                  >
                    <span>
                      {cur.symbol} · {cur.name}
                    </span>
                    <button
                      type="button"
                      className="currency-chip-remove"
                      onClick={() => toggleCurrency(id)}
                    >
                      ✕
                    </button>
                  </div>
                );
              })}
              <button
                type="button"
                className="currency-chip-clear"
                onClick={clearFilters}
              >
                Clear
              </button>
            </div>
          )}

          {/* List of all currencies to choose from */}
          <div className="currency-all-row">
            {currencies.map((c) => {
              const selected = selectedCurrencyIds.includes(c.id);
              return (
                <button
                  key={c.id}
                  type="button"
                  className={
                    "currency-chip" +
                    (selected ? " currency-chip--disabled" : "")
                  }
                  onClick={() => !selected && toggleCurrency(c.id)}
                >
                  {c.symbol}
                </button>
              );
            })}
          </div>
        </div>

        {/* Pools grid and pagination */}
        {loading ? (
          <p className="small">Loading pools…</p>
        ) : filteredPools.length === 0 ? (
          <div>
            <p>No pools match your selected currencies.</p>
            <button className="btn" onClick={clearFilters}>
              Clear filters
            </button>
          </div>
        ) : (
          <>
            {/* Always 2-column grid; 1 pool will keep same width as 2 */}
            <div className="pools-grid">
              {visiblePools.map((p) => (
                <div
                  key={p.id}
                  className="subcard"
                  style={{
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                  }}
                >
                  <div>
                    <div style={{ fontWeight: 800 }}>
                      {p.currency_x_symbol}/{p.currency_y_symbol}
                    </div>
                    <div className="small">
                      {p.currency_x_name} • {p.currency_y_name}
                    </div>
                    <div className="small" style={{ marginTop: 4 }}>
                      {p.currency_x_symbol} reserve: {p.x_reserve.toFixed(2)} •{" "}
                      {p.currency_y_symbol} reserve: {p.y_reserve.toFixed(2)}
                    </div>
                    <div className="small">
                      Price {p.currency_x_symbol}→{p.currency_y_symbol}:{" "}
                      {p.price_x_in_y.toFixed(6)}
                    </div>
                  </div>
                  <button
                    className="btn secondary"
                    onClick={() => nav(`/swap/${p.id}`)}
                  >
                    Use →
                  </button>
                </div>
              ))}
            </div>

            {/* Pagination (2 pools per page) */}
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                marginTop: 8,
              }}
            >
              <button
                className="btn"
                disabled={page === 0}
                onClick={() => setPage((p) => Math.max(0, p - 1))}
              >
                ← Prev
              </button>
              <div className="small">
                Page {page + 1} / {totalPages}
              </div>
              <button
                className="btn"
                disabled={page + 1 >= totalPages}
                onClick={() => setPage((p) => p + 1)}
              >
                Next →
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  );
}