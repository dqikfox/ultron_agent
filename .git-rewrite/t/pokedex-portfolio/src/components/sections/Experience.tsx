import React, { useState } from 'react';
import { Calendar, MapPin, Trophy, Star } from 'lucide-react';

interface ExperienceProps {
  theme: 'red' | 'blue';
}

interface Experience {
  id: number;
  company: string;
  position: string;
  location: string;
  period: string;
  type: 'work' | 'freelance' | 'education' | 'achievement';
  status: 'current' | 'completed';
  description: string;
  achievements: string[];
  technologies: string[];
  badges: string[];
  color: string;
  icon: string;
}

const Experience: React.FC<ExperienceProps> = ({ theme }) => {
  const [selectedExp, setSelectedExp] = useState<Experience | null>(null);
  const [filter, setFilter] = useState<'all' | 'work' | 'freelance' | 'education' | 'achievement'>('all');

  const experiences: Experience[] = [
    {
      id: 1,
      company: 'TechCorp Solutions',
      position: 'Senior Full-Stack Developer',
      location: 'San Francisco, CA',
      period: '2022 - Present',
      type: 'work',
      status: 'current',
      description: 'Leading development of scalable web applications and mentoring junior developers. Architecting cloud-native solutions and implementing DevOps best practices.',
      achievements: [
        'Led team of 5 developers on major product redesign',
        'Reduced application load time by 40% through optimization',
        'Implemented CI/CD pipeline reducing deployment time by 60%',
        'Mentored 3 junior developers to mid-level positions',
        'Designed microservices architecture serving 100K+ users'
      ],
      technologies: ['React', 'TypeScript', 'Node.js', 'AWS', 'Docker', 'Kubernetes', 'PostgreSQL'],
      badges: ['Team Leader', 'Performance Optimizer', 'Mentor', 'Cloud Architect'],
      color: '#3b82f6',
      icon: '🏢'
    },
    {
      id: 2,
      company: 'StartupHub Inc.',
      position: 'Full-Stack Developer',
      location: 'Austin, TX',
      period: '2020 - 2022',
      type: 'work',
      status: 'completed',
      description: 'Developed MVP and core features for a growing startup. Built entire frontend and backend infrastructure from scratch using modern technologies.',
      achievements: [
        'Built MVP from concept to launch in 3 months',
        'Developed real-time chat system for 10K+ users',
        'Implemented payment processing with 99.9% uptime',
        'Created responsive design supporting 5+ devices',
        'Optimized database queries improving performance by 50%'
      ],
      technologies: ['Vue.js', 'Python', 'Django', 'Redis', 'PostgreSQL', 'Stripe', 'Heroku'],
      badges: ['MVP Builder', 'Startup Pioneer', 'Full-Stack', 'Payment Integration'],
      color: '#10b981',
      icon: '🚀'
    },
    {
      id: 3,
      company: 'Digital Agency Pro',
      position: 'Frontend Developer',
      location: 'Remote',
      period: '2019 - 2020',
      type: 'work',
      status: 'completed',
      description: 'Specialized in creating stunning client websites and web applications. Collaborated with designers to bring creative visions to life with pixel-perfect implementations.',
      achievements: [
        'Delivered 25+ client projects with 100% satisfaction',
        'Reduced development time by 30% with reusable components',
        'Implemented responsive designs for major e-commerce sites',
        'Created interactive animations increasing user engagement',
        'Mentored design team on technical feasibility'
      ],
      technologies: ['JavaScript', 'React', 'SCSS', 'Webpack', 'Figma', 'Adobe XD'],
      badges: ['Client Satisfaction', 'Design Implementation', 'E-commerce Specialist'],
      color: '#f59e0b',
      icon: '🎨'
    },
    {
      id: 4,
      company: 'Freelance Developer',
      position: 'Independent Contractor',
      location: 'Various',
      period: '2018 - 2019',
      type: 'freelance',
      status: 'completed',
      description: 'Provided custom web development solutions for small businesses and startups. Built websites, web applications, and provided technical consulting.',
      achievements: [
        'Completed 15+ freelance projects successfully',
        'Built e-commerce platforms for 5 small businesses',
        'Provided technical consulting for startup launches',
        'Developed custom CMS solutions',
        'Maintained 5-star rating across all platforms'
      ],
      technologies: ['WordPress', 'PHP', 'MySQL', 'JavaScript', 'Bootstrap', 'WooCommerce'],
      badges: ['Entrepreneur', 'Small Business Helper', 'CMS Expert', '5-Star Rating'],
      color: '#8b5cf6',
      icon: '💼'
    },
    {
      id: 5,
      company: 'State University',
      position: 'Computer Science Degree',
      location: 'California',
      period: '2016 - 2020',
      type: 'education',
      status: 'completed',
      description: 'Bachelor of Science in Computer Science with focus on software engineering and web technologies. Graduated Magna Cum Laude with 3.8 GPA.',
      achievements: [
        'Graduated Magna Cum Laude (GPA: 3.8/4.0)',
        'President of Computer Science Club',
        'Won 3 hackathons during university',
        'Teaching Assistant for Web Development course',
        'Published research paper on web performance'
      ],
      technologies: ['Java', 'Python', 'C++', 'JavaScript', 'SQL', 'Data Structures', 'Algorithms'],
      badges: ['Magna Cum Laude', 'Hackathon Winner', 'Research Published', 'Teaching Assistant'],
      color: '#ef4444',
      icon: '🎓'
    },
    {
      id: 6,
      company: 'Open Source Contributions',
      position: 'Community Contributor',
      location: 'Global',
      period: '2019 - Present',
      type: 'achievement',
      status: 'current',
      description: 'Active contributor to open source projects and maintainer of popular development tools. Passionate about giving back to the developer community.',
      achievements: [
        '500+ contributions across GitHub projects',
        'Maintainer of 3 popular open source libraries',
        '2K+ stars on personal repositories',
        'Speaker at 5 developer conferences',
        'Published 20+ technical articles'
      ],
      technologies: ['JavaScript', 'TypeScript', 'React', 'Node.js', 'Python', 'Documentation'],
      badges: ['Open Source Hero', 'Community Leader', 'Conference Speaker', 'Technical Writer'],
      color: '#06b6d4',
      icon: '🌟'
    }
  ];

  const filteredExperiences = experiences.filter(exp => 
    filter === 'all' || exp.type === filter
  );

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'work': return '🏢';
      case 'freelance': return '💼';
      case 'education': return '🎓';
      case 'achievement': return '🏆';
      default: return '⭐';
    }
  };

  const getTypeColor = (type: string) => {
    switch (type) {
      case 'work': return '#3b82f6';
      case 'freelance': return '#8b5cf6';
      case 'education': return '#ef4444';
      case 'achievement': return '#10b981';
      default: return '#6b7280';
    }
  };

  return (
    <div className="section-content">
      <h2 className="section-title">ACHIEVEMENT HALL</h2>
      
      {/* Filter Badges */}
      <div className="flex flex-wrap justify-center gap-4 mb-8">
        {['all', 'work', 'freelance', 'education', 'achievement'].map((filterType) => (
          <button
            key={filterType}
            onClick={() => setFilter(filterType as any)}
            className={`flex items-center gap-2 px-6 py-3 rounded-full border-2 retro-text text-xs transition-all ${
              filter === filterType
                ? 'border-green-400 shadow-lg shadow-green-400/30'
                : 'border-gray-600 hover:border-green-400'
            }`}
            style={{
              background: filter === filterType 
                ? `linear-gradient(145deg, ${getTypeColor(filterType)}40, transparent)`
                : 'linear-gradient(145deg, #1f2937, #111827)',
              color: filter === filterType ? '#fff' : '#9ca3af'
            }}
          >
            <span className="text-base">{getTypeIcon(filterType)}</span>
            <span>{filterType.toUpperCase()}</span>
          </button>
        ))}
      </div>

      {/* Experience Timeline */}
      <div className="relative max-w-4xl mx-auto">
        {/* Timeline Line */}
        <div className="absolute left-1/2 transform -translate-x-1/2 w-1 h-full bg-gradient-to-b from-green-400 via-transparent to-green-400 hidden md:block"></div>

        <div className="space-y-8">
          {filteredExperiences.map((exp, index) => (
            <div
              key={exp.id}
              className={`flex items-center ${index % 2 === 0 ? 'md:flex-row' : 'md:flex-row-reverse'} gap-8`}
            >
              {/* Timeline Badge */}
              <div className="relative z-10 mx-8 md:mx-0">
                <div 
                  className="w-20 h-20 rounded-full border-4 flex items-center justify-center cursor-pointer transition-all hover:scale-110"
                  style={{ 
                    borderColor: exp.color,
                    background: `linear-gradient(145deg, #1f2937, #111827)`,
                    boxShadow: `0 0 20px ${exp.color}40`
                  }}
                  onClick={() => setSelectedExp(exp)}
                >
                  <span className="text-2xl">{exp.icon}</span>
                  {exp.status === 'current' && (
                    <div className="absolute -top-2 -right-2 bg-red-500 text-white text-xs retro-text px-2 py-1 rounded-full border-2 border-white animate-pulse">
                      NOW
                    </div>
                  )}
                </div>
              </div>

              {/* Experience Card */}
              <div 
                className="flex-1 max-w-lg bg-gradient-to-br from-gray-800 to-gray-900 border-2 border-gray-600 rounded-xl p-6 cursor-pointer transition-all hover:border-green-400 hover:transform hover:-translate-y-1"
                onClick={() => setSelectedExp(exp)}
              >
                <div className="mb-4">
                  <h3 className="retro-text text-white text-sm mb-1">{exp.position}</h3>
                  <div className="text-green-400 font-semibold mb-2">{exp.company}</div>
                  <div className="flex flex-col md:flex-row md:items-center gap-2 text-sm text-gray-400">
                    <div className="flex items-center gap-1">
                      <Calendar size={14} />
                      <span>{exp.period}</span>
                    </div>
                    <div className="flex items-center gap-1">
                      <MapPin size={14} />
                      <span>{exp.location}</span>
                    </div>
                  </div>
                </div>
                
                <p className="text-gray-300 text-sm mb-4 leading-relaxed">{exp.description}</p>
                
                <div className="mb-4">
                  <h4 className="retro-text text-green-400 text-xs mb-2">KEY ACHIEVEMENTS</h4>
                  <ul className="space-y-1">
                    {exp.achievements.slice(0, 3).map((achievement, i) => (
                      <li key={i} className="bg-green-400 bg-opacity-10 border-l-2 border-green-400 p-2 text-sm">
                        {achievement}
                      </li>
                    ))}
                    {exp.achievements.length > 3 && (
                      <li className="text-gray-400 italic text-sm">+{exp.achievements.length - 3} more achievements...</li>
                    )}
                  </ul>
                </div>
                
                <div className="mb-4">
                  <h4 className="retro-text text-green-400 text-xs mb-2">TECHNOLOGIES</h4>
                  <div className="flex flex-wrap gap-1">
                    {exp.technologies.slice(0, 4).map((tech) => (
                      <span 
                        key={tech} 
                        className="px-2 py-1 rounded border retro-text text-xs"
                        style={{ 
                          background: `linear-gradient(145deg, ${exp.color}40, transparent)`,
                          borderColor: exp.color,
                          color: '#fff'
                        }}
                      >
                        {tech}
                      </span>
                    ))}
                    {exp.technologies.length > 4 && (
                      <span className="px-2 py-1 rounded border border-gray-600 retro-text text-xs text-gray-400">
                        +{exp.technologies.length - 4}
                      </span>
                    )}
                  </div>
                </div>
                
                <div>
                  <h4 className="retro-text text-green-400 text-xs mb-2">BADGES EARNED</h4>
                  <div className="grid grid-cols-2 gap-1">
                    {exp.badges.map((badge) => (
                      <div key={badge} className="flex items-center gap-1 bg-gradient-to-r from-gray-700 to-gray-800 border border-yellow-500 rounded p-1">
                        <Trophy size={10} className="text-yellow-500" />
                        <span className="retro-text text-xs text-yellow-500">{badge}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Experience Detail Modal */}
      {selectedExp && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-80 flex items-center justify-center z-50 p-4"
          onClick={() => setSelectedExp(null)}
        >
          <div 
            className="bg-gradient-to-br from-gray-800 to-gray-900 border-2 border-green-400 rounded-xl w-full max-w-4xl max-h-[90vh] overflow-y-auto"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex flex-col md:flex-row items-center gap-4 p-6 border-b border-gray-600">
              <div 
                className="w-20 h-20 rounded-full border-4 flex items-center justify-center"
                style={{ 
                  borderColor: selectedExp.color,
                  background: `linear-gradient(145deg, ${selectedExp.color}40, transparent)`
                }}
              >
                <span className="text-3xl">{selectedExp.icon}</span>
              </div>
              <div className="flex-1 text-center md:text-left">
                <h3 className="retro-text text-green-400 text-lg">{selectedExp.position}</h3>
                <div className="text-white text-xl mb-2">{selectedExp.company}</div>
                <div className="flex flex-col md:flex-row gap-4 text-gray-400">
                  <span>{selectedExp.period}</span>
                  <span>{selectedExp.location}</span>
                </div>
              </div>
              <button 
                className="w-10 h-10 rounded-full border-2 border-red-500 text-red-500 hover:bg-red-500 hover:text-white transition-colors"
                onClick={() => setSelectedExp(null)}
              >
                ✕
              </button>
            </div>
            
            <div className="p-6 space-y-6 text-gray-300">
              <div>
                <h4 className="retro-text text-green-400 text-sm mb-3">MISSION DESCRIPTION</h4>
                <p className="leading-relaxed">{selectedExp.description}</p>
              </div>
              
              <div>
                <h4 className="retro-text text-green-400 text-sm mb-3">ACHIEVEMENTS UNLOCKED</h4>
                <div className="space-y-3">
                  {selectedExp.achievements.map((achievement, index) => (
                    <div key={index} className="flex items-center gap-4 bg-green-400 bg-opacity-10 border-l-4 border-green-400 p-4 rounded-r">
                      <Star size={16} className="text-yellow-400 flex-shrink-0" />
                      <span>{achievement}</span>
                    </div>
                  ))}
                </div>
              </div>
              
              <div>
                <h4 className="retro-text text-green-400 text-sm mb-3">TECH ARSENAL</h4>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                  {selectedExp.technologies.map((tech) => (
                    <div 
                      key={tech} 
                      className="bg-gradient-to-br from-gray-700 to-gray-800 border border-green-400 rounded-lg p-3 text-center retro-text text-xs text-green-400 hover:shadow-lg hover:shadow-green-400/30 transition-all"
                    >
                      {tech}
                    </div>
                  ))}
                </div>
              </div>
              
              <div>
                <h4 className="retro-text text-green-400 text-sm mb-3">BADGES COLLECTION</h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {selectedExp.badges.map((badge) => (
                    <div 
                      key={badge} 
                      className="bg-gradient-to-r from-gray-700 to-gray-800 border-2 border-yellow-400 rounded-xl p-4 text-center hover:shadow-lg hover:shadow-yellow-400/30 transition-all"
                    >
                      <Trophy size={20} className="text-yellow-400 mx-auto mb-2" />
                      <span className="retro-text text-xs text-white">{badge}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Experience;
