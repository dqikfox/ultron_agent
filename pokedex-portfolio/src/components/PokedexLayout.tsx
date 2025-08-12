import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Power, Volume2, Settings, Search } from 'lucide-react';

interface PokedexLayoutProps {
  children: React.ReactNode;
  theme: 'red' | 'blue';
  onThemeToggle: () => void;
}

const PokedexLayout: React.FC<PokedexLayoutProps> = ({ children, theme, onThemeToggle }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  const navigationItems = [
    { path: '/', label: 'HOME', icon: '🏠' },
    { path: '/about', label: 'ABOUT', icon: '👤' },
    { path: '/skills', label: 'SKILLS', icon: '⚡' },
    { path: '/projects', label: 'PROJECTS', icon: '💼' },
    { path: '/experience', label: 'EXPERIENCE', icon: '🏆' },
    { path: '/contact', label: 'CONTACT', icon: '📞' },
  ];

  const handleNavigation = (path: string) => {
    navigate(path);
    setIsMenuOpen(false);
  };

  const currentSection = navigationItems.find(item => item.path === location.pathname);

  return (
    <div className="min-h-screen p-4 flex items-center justify-center">
      <div className="pokedex-container">
        {/* Main Pokédex Body */}
        <div className={`pokedex-body ${theme === 'red' ? 'pokedex-red' : 'pokedex-blue'}`}>
          
          {/* Top Section - Control Panel */}
          <div className="pokedex-top">
            {/* Main LED Light */}
            <div className="flex items-center gap-4 mb-6">
              <div className={`led-light large ${theme === 'red' ? 'led-red' : 'led-blue'}`}>
                <div className="led-glow"></div>
              </div>
              <div className="flex gap-2">
                <div className="led-light small led-yellow"></div>
                <div className="led-light small led-green"></div>
              </div>
            </div>

            {/* Navigation Panel */}
            <div className="navigation-panel">
              <div className="nav-header">
                <h2 className="pokedex-title">ALEX CODEMASTER</h2>
                <div className="current-section">
                  {currentSection && (
                    <span className="section-indicator">
                      {currentSection.icon} {currentSection.label}
                    </span>
                  )}
                </div>
              </div>
              
              <div className="nav-buttons-grid">
                {navigationItems.map((item) => (
                  <button
                    key={item.path}
                    onClick={() => handleNavigation(item.path)}
                    className={`nav-button ${location.pathname === item.path ? 'active' : ''}`}
                  >
                    <span className="nav-icon">{item.icon}</span>
                    <span className="nav-label">{item.label}</span>
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Main Screen */}
          <div className="pokedex-screen">
            <div className="screen-border">
              <div className="screen-content">
                <div className="scan-lines"></div>
                {children}
              </div>
            </div>
          </div>

          {/* Bottom Control Panel */}
          <div className="pokedex-controls">
            {/* D-Pad Style Navigation */}
            <div className="control-section">
              <div className="d-pad">
                <div className="d-pad-center"></div>
              </div>
              <div className="control-labels">
                <span>NAVIGATE</span>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="control-section">
              <div className="action-buttons">
                <button className="action-btn btn-a" onClick={onThemeToggle}>
                  <span>A</span>
                </button>
                <button className="action-btn btn-b">
                  <span>B</span>
                </button>
              </div>
              <div className="control-labels">
                <span>A: THEME</span>
                <span>B: SELECT</span>
              </div>
            </div>

            {/* System Controls */}
            <div className="control-section">
              <div className="system-controls">
                <button className="system-btn">
                  <Power size={16} />
                </button>
                <button className="system-btn">
                  <Volume2 size={16} />
                </button>
                <button className="system-btn">
                  <Settings size={16} />
                </button>
              </div>
              <div className="control-labels">
                <span>SYSTEM</span>
              </div>
            </div>
          </div>

          {/* Speaker Grille */}
          <div className="speaker-grille">
            {Array.from({ length: 36 }, (_, i) => (
              <div key={i} className="speaker-hole"></div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default PokedexLayout;
