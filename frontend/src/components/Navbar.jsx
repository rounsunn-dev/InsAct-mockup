function Navbar({ showBackButton = false, onBack, title = "InsAct" }) {
  return (
    <nav className="navbar">
      <div className="nav-content">
        {showBackButton && (
          <button onClick={onBack} className="back-btn">
            ← Back
          </button>
        )}
        <h1 className="nav-title">{title}</h1>
        <div className="nav-spacer"></div>
      </div>
    </nav>
  );
}

export default Navbar;