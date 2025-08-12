import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import PokedexLayout from './components/PokedexLayout';
import Home from './components/sections/Home';
import About from './components/sections/About';
import Skills from './components/sections/Skills';
import Projects from './components/sections/Projects';
import Experience from './components/sections/Experience';
import Contact from './components/sections/Contact';
import './App.css';

function App() {
  const [isLoading, setIsLoading] = useState(true);
  const [theme, setTheme] = useState<'red' | 'blue'>('red');

  useEffect(() => {
    // Simulate initial loading with Pokéball animation
    const timer = setTimeout(() => {
      setIsLoading(false);
    }, 2000);

    return () => clearTimeout(timer);
  }, []);

  const toggleTheme = () => {
    setTheme(prev => prev === 'red' ? 'blue' : 'red');
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-red-600 to-red-800 flex items-center justify-center">
        <div className="loading-container">
          <div className="pokeball-spinner">
            <div className="pokeball">
              <div className="pokeball-top"></div>
              <div className="pokeball-middle"></div>
              <div className="pokeball-bottom"></div>
            </div>
          </div>
          <div className="loading-text">Loading Portfolio...</div>
        </div>
      </div>
    );
  }

  return (
    <Router>
      <div className={`min-h-screen transition-all duration-500 ${
        theme === 'red' 
          ? 'bg-gradient-to-br from-red-600 via-red-700 to-red-800' 
          : 'bg-gradient-to-br from-blue-600 via-blue-700 to-blue-800'
      }`}>
        <PokedexLayout theme={theme} onThemeToggle={toggleTheme}>
          <Routes>
            <Route path="/" element={<Home theme={theme} />} />
            <Route path="/about" element={<About theme={theme} />} />
            <Route path="/skills" element={<Skills theme={theme} />} />
            <Route path="/projects" element={<Projects theme={theme} />} />
            <Route path="/experience" element={<Experience theme={theme} />} />
            <Route path="/contact" element={<Contact theme={theme} />} />
          </Routes>
        </PokedexLayout>
      </div>
    </Router>
  );
}

export default App;
