import { Link, useNavigate } from "react-router-dom";

export const Navbar = () => {
  const navigate = useNavigate();
  const token = sessionStorage.getItem("token");

  const handleLogout = () => {
    sessionStorage.removeItem("token");
    navigate("/login");
  };

  return (
    <nav className="navbar navbar-light bg-light">
      <div className="container">
        <Link to="/" className="navbar-brand mb-0 h1 text-decoration-none">
          JWT Auth
        </Link>

        <div className="d-flex gap-2">
          {!token ? (
            <>
              <Link to="/signup" className="btn btn-outline-primary">Signup</Link>
              <Link to="/login" className="btn btn-outline-success">Login</Link>
            </>
          ) : (
            <>
              <Link to="/private" className="btn btn-outline-dark">Private</Link>
              <button onClick={handleLogout} className="btn btn-danger">
                Logout
              </button>
            </>
          )}
        </div>
      </div>
    </nav>
  );
};