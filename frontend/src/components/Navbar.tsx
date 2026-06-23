import { Link } from 'react-router-dom';
import { Brain, Plus, Settings } from 'lucide-react';

export function Navbar() {
  return (
    <nav className="navbar">
      <Link to="/" className="navbar-brand">
        <Brain size={28} />
        <span>Market Research AI</span>
      </Link>
      <div className="navbar-actions">
        <button className="btn btn-secondary btn-sm">
          <Settings size={16} />
          Settings
        </button>
      </div>
    </nav>
  );
}
