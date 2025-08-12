import React, { useState } from 'react';

interface AboutProps {
  theme: 'red' | 'blue';
}

const About: React.FC<AboutProps> = ({ theme }) => {
  const [selectedTab, setSelectedTab] = useState<'bio' | 'journey' | 'philosophy'>('bio');

  const tabData = {
    bio: {
      title: 'TRAINER PROFILE',
      content: (
        <div className="space-y-6">
          <div className="flex items-center gap-6 mb-6">
            <div className="relative w-24 h-24">
              <div className="absolute inset-0 border-4 border-green-400 rounded-full animate-spin-slow"></div>
              <div className="absolute inset-2 bg-gradient-to-br from-gray-700 to-gray-900 rounded-full flex items-center justify-center">
                <span className="retro-text text-green-400 text-xl">AC</span>
              </div>
            </div>
            <div>
              <h3 className="retro-text text-white text-xl mb-2">ALEX CODEMASTER</h3>
              <div className="text-green-400 text-lg mb-2">FULL-STACK DEVELOPER</div>
              <div className="bg-gradient-to-r from-green-800 to-green-900 border border-green-400 rounded-full px-4 py-1 inline-block">
                <span className="retro-text text-green-400 text-xs">LVL 99</span>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-3 gap-4 mb-6">
            <div className="bg-gradient-to-br from-gray-800 to-gray-900 border border-gray-600 rounded-lg p-4 text-center hover:border-green-400 transition-colors">
              <div className="text-2xl mb-2">🏆</div>
              <div className="retro-text text-green-400 text-lg">5+</div>
              <div className="retro-text text-gray-400 text-xs">YEARS EXP</div>
            </div>
            <div className="bg-gradient-to-br from-gray-800 to-gray-900 border border-gray-600 rounded-lg p-4 text-center hover:border-green-400 transition-colors">
              <div className="text-2xl mb-2">⚡</div>
              <div className="retro-text text-green-400 text-lg">50+</div>
              <div className="retro-text text-gray-400 text-xs">PROJECTS</div>
            </div>
            <div className="bg-gradient-to-br from-gray-800 to-gray-900 border border-gray-600 rounded-lg p-4 text-center hover:border-green-400 transition-colors">
              <div className="text-2xl mb-2">🎯</div>
              <div className="retro-text text-green-400 text-lg">15+</div>
              <div className="retro-text text-gray-400 text-xs">TECH STACKS</div>
            </div>
          </div>

          <div className="space-y-4 text-gray-300 leading-relaxed">
            <p>
              Passionate full-stack developer with a love for creating elegant solutions 
              to complex problems. I specialize in building scalable web applications 
              and have a particular fondness for React, TypeScript, and modern development practices.
            </p>
            <p>
              When I'm not coding, you can find me exploring new technologies, contributing 
              to open-source projects, or sharing knowledge with the developer community.
            </p>
          </div>
        </div>
      )
    },
    journey: {
      title: 'DEVELOPER JOURNEY',
      content: (
        <div className="space-y-6">
          {[
            { year: '2019', title: 'THE BEGINNING', desc: 'Started my coding journey with Python and fell in love with programming logic', badge: 'ROOKIE' },
            { year: '2020', title: 'WEB DEVELOPMENT', desc: 'Discovered web development and dove deep into JavaScript, HTML, and CSS', badge: 'EXPLORER' },
            { year: '2021', title: 'REACT MASTERY', desc: 'Mastered React ecosystem and started building complex single-page applications', badge: 'SPECIALIST' },
            { year: '2022', title: 'FULL-STACK EVOLUTION', desc: 'Expanded into backend development with Node.js, databases, and cloud services', badge: 'EXPERT' },
            { year: '2023', title: 'SENIOR DEVELOPER', desc: 'Leading teams, architecting solutions, and mentoring junior developers', badge: 'MASTER' },
          ].map((item, index) => (
            <div key={item.year} className="flex gap-6">
              <div className="w-20 text-center">
                <div className="retro-text text-green-400 text-sm bg-black bg-opacity-60 border border-green-400 rounded-md p-2">
                  {item.year}
                </div>
              </div>
              <div className="flex-1 bg-gradient-to-br from-gray-800 to-gray-900 border border-gray-600 rounded-lg p-4">
                <h4 className="retro-text text-white text-sm mb-2">{item.title}</h4>
                <p className="text-gray-300 text-sm mb-2 leading-relaxed">{item.desc}</p>
                <div className="inline-block bg-gradient-to-r from-green-800 to-green-900 border border-green-400 rounded-full px-3 py-1">
                  <span className="retro-text text-green-400 text-xs">{item.badge}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      )
    },
    philosophy: {
      title: 'CODING PHILOSOPHY',
      content: (
        <div className="space-y-6">
          <div className="grid grid-cols-2 gap-4">
            {[
              { icon: '🎯', title: 'PRECISION', desc: 'Every line of code should have a purpose. Clean, readable, and maintainable code is not just a goal—it\'s a standard.' },
              { icon: '🚀', title: 'INNOVATION', desc: 'Staying ahead of the curve by embracing new technologies and methodologies that improve user experience and developer productivity.' },
              { icon: '🤝', title: 'COLLABORATION', desc: 'Great software is built by great teams. Communication, mentorship, and knowledge sharing are essential to success.' },
              { icon: '📚', title: 'LEARNING', desc: 'Technology evolves rapidly. Continuous learning and adaptation are not just beneficial—they\'re necessary for growth.' },
            ].map((item) => (
              <div key={item.title} className="bg-gradient-to-br from-gray-800 to-gray-900 border border-gray-600 rounded-lg p-6 text-center hover:border-green-400 transition-all hover:transform hover:-translate-y-1">
                <div className="text-3xl mb-4">{item.icon}</div>
                <h4 className="retro-text text-green-400 text-sm mb-3">{item.title}</h4>
                <p className="text-gray-300 text-sm leading-relaxed">{item.desc}</p>
              </div>
            ))}
          </div>
          
          <div className="text-center p-8 bg-black bg-opacity-30 rounded-lg border-l-4 border-green-400">
            <blockquote className="text-white text-lg italic mb-4 leading-relaxed">
              "Code is like humor. When you have to explain it, it's bad."
            </blockquote>
            <cite className="retro-text text-green-400 text-xs">- CORY HOUSE</cite>
          </div>
        </div>
      )
    }
  };

  return (
    <div className="section-content">
      <h2 className="section-title">TRAINER DATABASE</h2>
      
      {/* Tab Navigation */}
      <div className="flex justify-center gap-4 mb-8">
        {Object.keys(tabData).map((tab) => (
          <button
            key={tab}
            onClick={() => setSelectedTab(tab as keyof typeof tabData)}
            className={`px-6 py-3 rounded-lg border-2 retro-text text-xs transition-all ${
              selectedTab === tab
                ? 'bg-gradient-to-br from-green-800 to-green-900 border-green-400 text-green-400 shadow-lg shadow-green-400/30'
                : 'bg-gradient-to-br from-gray-800 to-gray-900 border-gray-600 text-gray-400 hover:border-green-400 hover:text-green-400'
            }`}
          >
            {tab.toUpperCase()}
          </button>
        ))}
      </div>
      
      {/* Content Area */}
      <div className="bg-black bg-opacity-40 border-2 border-green-400 rounded-xl p-8 min-h-96">
        <div className="flex justify-between items-center mb-8 pb-4 border-b border-green-400">
          <h3 className="retro-text text-green-400 text-lg">{tabData[selectedTab].title}</h3>
          <div className="relative w-16 h-5 bg-green-400 bg-opacity-10 border border-green-400 rounded overflow-hidden">
            <div className="absolute inset-0 bg-gradient-to-r from-transparent via-green-400 to-transparent animate-pulse"></div>
          </div>
        </div>
        
        <div className="animate-fade-in">
          {tabData[selectedTab].content}
        </div>
      </div>
    </div>
  );
};

export default About;
