import { useNavigate } from "react-router-dom";

export function Home() {
  const nav = useNavigate();
  return (
    <div className="container center">
      <div className="card" style={{ width: "100%", textAlign: "center" }}>
        <div className="huge">AMM Game</div>
        <p className="note">Simple AMM UI — create or use a pool</p>

        <div style={{ marginTop: 20 }} className="row center">
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