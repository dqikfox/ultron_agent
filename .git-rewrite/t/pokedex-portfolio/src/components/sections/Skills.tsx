import React, { useState, useEffect } from 'react';

interface SkillsProps {
  theme: 'red' | 'blue';
}

interface Skill {
  name: string;
  level: number;
  type: string;
  color: string;
  experience: string;
  description: string;
  icon: string;
}

const Skills: React.FC<SkillsProps> = ({ theme }) => {
  const [selectedCategory, setSelectedCategory] = useState<'frontend' | 'backend' | 'tools' | 'soft'>('frontend');
  const [animatingBars, setAnimatingBars] = useState(false);

  const skillCategories = {
    frontend: {
      title: 'FRONTEND TYPE',
      color: '#3b82f6',
      icon: '🎨',
      skills: [
        { name: 'React', level: 95, type: 'Electric', color: '#61dafb', experience: '4+ years', description: 'Advanced component architecture and state management', icon: '⚛️' },
        { name: 'TypeScript', level: 90, type: 'Psychic', color: '#3178c6', experience: '3+ years', description: 'Type-safe development and advanced patterns', icon: '📘' },
        { name: 'Next.js', level: 85, type: 'Dark', color: '#000000', experience: '2+ years', description: 'Server-side rendering and full-stack applications', icon: '▲' },
        { name: 'TailwindCSS', level: 92, type: 'Flying', color: '#06b6d4', experience: '3+ years', description: 'Responsive design and component styling', icon: '🎨' },
        { name: 'JavaScript', level: 93, type: 'Normal', color: '#f7df1e', experience: '5+ years', description: 'ES6+, async programming, and modern APIs', icon: '📜' },
        { name: 'CSS/SCSS', level: 88, type: 'Fairy', color: '#ff69b4', experience: '5+ years', description: 'Advanced animations and responsive layouts', icon: '🎭' }
      ]
    },
    backend: {
      title: 'BACKEND TYPE',
      color: '#10b981',
      icon: '⚙️',
      skills: [
        { name: 'Node.js', level: 87, type: 'Grass', color: '#339933', experience: '3+ years', description: 'REST APIs, microservices, and async operations', icon: '🟢' },
        { name: 'Python', level: 89, type: 'Poison', color: '#3776ab', experience: '4+ years', description: 'Django, FastAPI, and data processing', icon: '🐍' },
        { name: 'PostgreSQL', level: 83, type: 'Water', color: '#336791', experience: '3+ years', description: 'Complex queries and database optimization', icon: '🐘' },
        { name: 'MongoDB', level: 81, type: 'Ground', color: '#47a248', experience: '2+ years', description: 'NoSQL design and aggregation pipelines', icon: '🍃' },
        { name: 'GraphQL', level: 76, type: 'Steel', color: '#e10098', experience: '2+ years', description: 'Schema design and resolver optimization', icon: '🔗' },
        { name: 'Redis', level: 74, type: 'Fire', color: '#dc382d', experience: '2+ years', description: 'Caching strategies and session management', icon: '🔥' }
      ]
    },
    tools: {
      title: 'DEVOPS TYPE',
      color: '#8b5cf6',
      icon: '🛠️',
      skills: [
        { name: 'Docker', level: 86, type: 'Ice', color: '#2496ed', experience: '3+ years', description: 'Containerization and multi-stage builds', icon: '🐳' },
        { name: 'AWS', level: 82, type: 'Electric', color: '#ff9900', experience: '2+ years', description: 'EC2, S3, Lambda, and CloudFormation', icon: '☁️' },
        { name: 'Git', level: 94, type: 'Normal', color: '#f05032', experience: '5+ years', description: 'Advanced workflows and collaboration', icon: '📚' },
        { name: 'Jest', level: 85, type: 'Fighting', color: '#c21325', experience: '3+ years', description: 'Unit testing and test-driven development', icon: '🧪' },
        { name: 'Webpack', level: 78, type: 'Rock', color: '#8dd6f9', experience: '3+ years', description: 'Module bundling and build optimization', icon: '📦' },
        { name: 'Linux', level: 80, type: 'Bug', color: '#fcc624', experience: '4+ years', description: 'System administration and shell scripting', icon: '🐧' }
      ]
    },
    soft: {
      title: 'LEADERSHIP TYPE',
      color: '#f59e0b',
      icon: '👥',
      skills: [
        { name: 'Team Leadership', level: 88, type: 'Dragon', color: '#7c3aed', experience: '2+ years', description: 'Mentoring developers and project coordination', icon: '👑' },
        { name: 'Problem Solving', level: 92, type: 'Psychic', color: '#ec4899', experience: '5+ years', description: 'Complex debugging and architectural decisions', icon: '🧩' },
        { name: 'Communication', level: 89, type: 'Normal', color: '#6b7280', experience: '5+ years', description: 'Technical writing and stakeholder management', icon: '💬' },
        { name: 'Code Review', level: 91, type: 'Steel', color: '#64748b', experience: '3+ years', description: 'Quality assurance and knowledge sharing', icon: '🔍' },
        { name: 'Agile/Scrum', level: 84, type: 'Fighting', color: '#dc2626', experience: '3+ years', description: 'Sprint planning and iterative development', icon: '⚡' },
        { name: 'Mentoring', level: 86, type: 'Fairy', color: '#f472b6', experience: '2+ years', description: 'Junior developer guidance and training', icon: '🌟' }
      ]
    }
  };

  useEffect(() => {
    setAnimatingBars(true);
    const timer = setTimeout(() => setAnimatingBars(false), 1000);
    return () => clearTimeout(timer);
  }, [selectedCategory]);

  const currentSkills = skillCategories[selectedCategory];

  return (
    <div className="section-content">
      <h2 className="section-title">SKILL DATABASE</h2>
      
      {/* Category Selection */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        {Object.entries(skillCategories).map(([key, category]) => (
          <button
            key={key}
            onClick={() => setSelectedCategory(key as keyof typeof skillCategories)}
            className={`p-4 rounded-xl border-2 transition-all ${
              selectedCategory === key
                ? 'border-green-400 shadow-lg shadow-green-400/30'
                : 'border-gray-600 hover:border-green-400'
            }`}
            style={{
              background: selectedCategory === key 
                ? `linear-gradient(145deg, ${category.color}20, transparent)`
                : 'linear-gradient(145deg, #1f2937, #111827)'
            }}
          >
            <div className="text-2xl mb-2">{category.icon}</div>
            <div className="retro-text text-xs text-white">{category.title}</div>
          </button>
        ))}
      </div>

      {/* Skills Display */}
      <div className="bg-black bg-opacity-40 border-2 border-green-400 rounded-xl p-8">
        <div className="flex justify-between items-center mb-8 pb-4 border-b border-green-400">
          <h3 className="retro-text text-green-400 text-lg">
            {currentSkills.icon} {currentSkills.title}
          </h3>
          <div className="retro-text text-gray-400 text-xs bg-black bg-opacity-50 px-4 py-2 rounded border border-gray-600">
            {currentSkills.skills.length} ABILITIES DISCOVERED
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {currentSkills.skills.map((skill, index) => (
            <div
              key={skill.name}
              className="bg-gradient-to-br from-gray-800 to-gray-900 border-2 border-gray-600 rounded-xl p-6 hover:border-green-400 transition-all hover:transform hover:-translate-y-1"
              style={{ animationDelay: `${index * 0.1}s` }}
            >
              {/* Skill Header */}
              <div className="flex justify-between items-center mb-4">
                <div className="flex items-center gap-3">
                  <span className="text-2xl">{skill.icon}</span>
                  <div>
                    <h4 className="retro-text text-white text-sm">{skill.name}</h4>
                    <span className="retro-text text-xs uppercase" style={{ color: skill.color }}>
                      {skill.type} TYPE
                    </span>
                  </div>
                </div>
                <div 
                  className="px-3 py-1 rounded-full border retro-text text-xs text-white"
                  style={{ 
                    background: `linear-gradient(145deg, ${skill.color}40, transparent)`,
                    borderColor: skill.color,
                    textShadow: `0 0 8px ${skill.color}`
                  }}
                >
                  LVL {skill.level}
                </div>
              </div>

              {/* Experience Bar */}
              <div className="mb-4">
                <div className="flex justify-between mb-2 retro-text text-xs">
                  <span className="text-gray-400">EXPERIENCE:</span>
                  <span style={{ color: skill.color }}>{skill.experience}</span>
                </div>
                <div className="flex items-center gap-4">
                  <div className="flex-1 h-5 bg-black bg-opacity-50 border border-gray-600 rounded-full overflow-hidden">
                    <div 
                      className={`h-full rounded-full transition-all duration-1000 relative ${animatingBars ? 'w-0' : ''}`}
                      style={{ 
                        width: animatingBars ? '0%' : `${skill.level}%`,
                        background: `linear-gradient(90deg, ${skill.color}, transparent)`
                      }}
                    >
                      <div 
                        className="absolute top-0 left-0 right-0 h-1/2 bg-gradient-to-r from-transparent via-white via-transparent"
                        style={{ animation: 'shine 2s ease-in-out infinite' }}
                      ></div>
                    </div>
                  </div>
                  <span className="retro-text text-xs min-w-[40px] text-right" style={{ color: skill.color }}>
                    {skill.level}%
                  </span>
                </div>
              </div>

              {/* Skill Description */}
              <div className="mb-4">
                <p className="text-gray-300 text-sm leading-relaxed">{skill.description}</p>
              </div>

              {/* Power Indicators */}
              <div className="flex justify-center gap-2">
                {Array.from({ length: 5 }, (_, i) => (
                  <div
                    key={i}
                    className={`w-3 h-3 rounded-full border transition-all ${
                      i < Math.floor(skill.level / 20)
                        ? 'border-green-400 shadow-lg'
                        : 'border-gray-600'
                    }`}
                    style={{
                      background: i < Math.floor(skill.level / 20) ? skill.color : 'transparent',
                      boxShadow: i < Math.floor(skill.level / 20) ? `0 0 8px ${skill.color}` : 'none'
                    }}
                  ></div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Skills;
