import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

export const Private = () => {
  const navigate = useNavigate();
  const backendUrl = import.meta.env.VITE_BACKEND_URL;

  const [data, setData] = useState(null);
  const [msg, setMsg] = useState("Loading...");

  useEffect(() => {
    const token = sessionStorage.getItem("token");

    
    if (!token) {
      navigate("/login");
      return;
    }

    const loadPrivate = async () => {
      try {
        const resp = await fetch(`${backendUrl}/api/private`, {
          headers: {
            Authorization: `Bearer ${token}`
          }
        });

        const payload = await resp.json();

        if (!resp.ok) {
          
          sessionStorage.removeItem("token");
          navigate("/login");
          return;
        }

        setData(payload);
        setMsg(null);
      } catch (err) {
        setMsg("Network error");
      }
    };

    loadPrivate();
  }, [backendUrl, navigate]);

  return (
    <div className="container py-4">
      <h2>Private</h2>

      {msg && <div className="alert alert-info">{msg}</div>}

      {data && (
        <div className="card p-3">
          <p className="mb-1"><strong>Message:</strong> {data.msg}</p>
          <p className="mb-0"><strong>User:</strong> {data.user?.email}</p>
        </div>
      )}
    </div>
  );
};