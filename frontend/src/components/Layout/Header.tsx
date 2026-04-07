import { Link } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';

export function Header() {
  const { user, isAuthenticated, logout } = useAuth();

  return (
    <header className="bg-white shadow-sm">
      <nav className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <Link to="/" className="text-2xl font-bold text-primary-600">
            Handwerker Platform
          </Link>

          <div className="flex items-center gap-6">
            {isAuthenticated ? (
              <>
                <Link to="/search" className="text-gray-700 hover:text-primary-600">
                  Find Craftsmen
                </Link>
                {user?.role === 'homeowner' && (
                  <Link to="/bookings" className="text-gray-700 hover:text-primary-600">
                    My Bookings
                  </Link>
                )}
                {user?.role === 'craftsman' && (
                  <>
                    <Link to="/bookings" className="text-gray-700 hover:text-primary-600">
                      Bookings
                    </Link>
                    <Link to="/profile" className="text-gray-700 hover:text-primary-600">
                      Profile
                    </Link>
                  </>
                )}
                <Link to="/messages" className="text-gray-700 hover:text-primary-600">
                  Messages
                </Link>
                <div className="flex items-center gap-3">
                  <span className="text-sm text-gray-600">{user?.full_name}</span>
                  <button
                    onClick={logout}
                    className="text-sm text-gray-700 hover:text-primary-600"
                  >
                    Logout
                  </button>
                </div>
              </>
            ) : (
              <>
                <Link to="/search" className="text-gray-700 hover:text-primary-600">
                  Find Craftsmen
                </Link>
                <Link
                  to="/login"
                  className="text-gray-700 hover:text-primary-600"
                >
                  Login
                </Link>
                <Link
                  to="/register"
                  className="bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700"
                >
                  Register
                </Link>
              </>
            )}
          </div>
        </div>
      </nav>
    </header>
  );
}
