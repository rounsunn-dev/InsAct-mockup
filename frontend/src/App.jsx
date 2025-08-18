import { useEffect, useState } from "react";

function App() {
  const [data, setData] = useState(null);

  useEffect(() => {
    fetch("http://127.0.0.1:8000/ping")
      .then((res) => res.json())
      .then((data) => setData(data));
  }, []);

  return (
    <div style={{ padding: "2rem" }}>
      <h1>InsAct Mockup 🚀</h1>
      <p>Backend says: {data ? data.message : "Loading..."}</p>
    </div>
  );
}

export default App;
