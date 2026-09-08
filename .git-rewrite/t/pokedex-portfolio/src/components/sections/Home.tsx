import React, { useState, useEffect } from 'react';

interface HomeProps {
  theme: 'red' | 'blue';
}

const Home: React.FC<HomeProps> = ({ theme }) => {
  const [displayText, setDisplayText] = useState('');
  const [currentLine, setCurrentLine] = useState(0);
  const [isTyping, setIsTyping] = useState(true);

  const welcomeMessages = [
    'SYSTEM INITIALIZING...',
    'POKÉDEX DATABASE ONLINE',
    '',
    'WELCOME TO MY PORTFOLIO',
    'TRAINER: ALEX CODEMASTER',
    'DEVELOPER LVL: 99',
    '',
    'READY FOR NEW ADVENTURE!',
  ];

  useEffect(() => {
    if (currentLine < welcomeMessages.length) {
      const message = welcomeMessages[currentLine];
      let charIndex = 0;

      const typingInterval = setInterval(() => {
        if (charIndex <= message.length) {
          setDisplayText(prev => {
            const lines = prev.split('\n');
            lines[currentLine] = message.substring(0, charIndex);
            return lines.join('\n');
          });
          charIndex++;
        } else {
          clearInterval(typingInterval);
          setTimeout(() => {
            setCurrentLine(prev => prev + 1);
          }, 500);
        }
      }, 50);

      return () => clearInterval(typingInterval);
    } else {
      setIsTyping(false);
    }
  }, [currentLine]);

  return (
    <div className="section-content min-h-full flex flex-col text-green-400">
      {/* Header Display */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex gap-2">
          <div className={`w-2 h-2 rounded-full animate-pulse ${theme === 'red' ? 'bg-red-400' : 'bg-blue-400'}`}></div>
          <div className="w-2 h-2 rounded-full bg-green-400 animate-pulse"></div>
          <div className="w-2 h-2 rounded-full bg-yellow-400"></div>
        </div>
        <div className="text-xs text-green-400">
          SYSTEM TIME: 17:23:31
        </div>
      </div>

      {/* Main Content Area */}
      <div className="flex-1 flex items-center justify-center">
        <div className="terminal-window w-full max-w-2xl">
          <div className="terminal-header bg-gradient-to-r from-gray-800 to-gray-700 p-4 border-b border-green-400 flex items-center gap-4 rounded-t-lg">
            <div className="flex gap-2">
              <div className="w-3 h-3 rounded-full bg-red-500"></div>
              <div className="w-3 h-3 rounded-full bg-yellow-500"></div>
              <div className="w-3 h-3 rounded-full bg-green-500"></div>
            </div>
            <span className="retro-text text-green-400 text-xs">POKÉDEX_PORTFOLIO.EXE</span>
          </div>
          
          <div className="terminal-content bg-black bg-opacity-80 p-8 min-h-48 rounded-b-lg border-2 border-green-400 border-t-0">
            <pre className="font-mono text-green-400 text-sm leading-relaxed whitespace-pre-wrap">
{displayText}
{isTyping && <span className="animate-pulse">█</span>}
            </pre>

            {!isTyping && (
              <div className="mt-6 bg-gradient-to-br from-gray-900 to-black p-6 rounded-xl border-2 border-green-400 animate-fade-in">
                <div className="flex justify-between items-center mb-4 pb-4 border-b border-green-400">
                  <h3 className="retro-text text-white text-lg">ALEX CODEMASTER</h3>
                  <div className="font-mono text-green-400 text-sm">ID: 001337</div>
                </div>
                
                <div className="space-y-2 mb-4">
                  <div className="flex justify-between font-mono text-sm">
                    <span className="text-gray-400">SPECIALTY:</span>
                    <span className="text-green-400">FULL-STACK DEVELOPMENT</span>
                  </div>
                  <div className="flex justify-between font-mono text-sm">
                    <span className="text-gray-400">EXPERIENCE:</span>
                    <span className="text-green-400">5+ YEARS</span>
                  </div>
                  <div className="flex justify-between font-mono text-sm">
                    <span className="text-gray-400">LOCATION:</span>
                    <span className="text-green-400">SILICON VALLEY</span>
                  </div>
                  <div className="flex justify-between font-mono text-sm">
                    <span className="text-gray-400">STATUS:</span>
                    <span className="text-green-400">READY FOR HIRE</span>
                  </div>
                </div>

                <div className="mt-4">
                  <div className="retro-text text-green-400 text-xs mb-4">CURRENT TECH STACK:</div>
                  <div className="grid grid-cols-3 gap-2">
                    {['REACT', 'TYPESCRIPT', 'NODE.JS', 'PYTHON', 'DOCKER', 'AWS'].map((tech) => (
                      <div
                        key={tech}
                        className="bg-gradient-to-br from-green-800 to-green-900 border border-green-400 rounded-md p-2 text-center retro-text text-xs text-green-400 hover:shadow-lg hover:shadow-green-400/30 transition-all"
                      >
                        {tech}
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Bottom Status Bar */}
      <div className="mt-6 bg-black bg-opacity-60 border border-green-400 rounded-md p-3">
        <div className="flex justify-between items-center text-xs font-mono text-green-400">
          <span>PORTFOLIO v2.5.0</span>
          <span>READY</span>
          <span>ONLINE</span>
        </div>
      </div>
    </div>
  );
};

export default Home;
