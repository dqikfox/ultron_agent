import React, { useState } from 'react';
import { ExternalLink, Github, Search, Filter } from 'lucide-react';

interface ProjectsProps {
  theme: 'red' | 'blue';
}

interface Project {
  id: number;
  name: string;
  type: string;
  category: string;
  description: string;
  longDescription: string;
  technologies: string[];
  status: 'completed' | 'in-progress' | 'beta';
  demoUrl?: string;
  githubUrl?: string;
  features: string[];
  stats: {
    lines: string;
    commits: string;
    duration: string;
  };
  color: string;
  icon: string;
}

const Projects: React.FC<ProjectsProps> = ({ theme }) => {
  const [selectedProject, setSelectedProject] = useState<Project | null>(null);
  const [filter, setFilter] = useState<'all' | 'web' | 'mobile' | 'api' | 'tool'>('all');
  const [searchTerm, setSearchTerm] = useState('');

  const projects: Project[] = [
    {
      id: 1,
      name: 'E-Commerce Platform',
      type: 'Full-Stack Web App',
      category: 'web',
      description: 'Modern e-commerce platform with React, Node.js, and Stripe integration',
      longDescription: 'A comprehensive e-commerce solution featuring user authentication, product catalog, shopping cart, payment processing, and admin dashboard. Built with scalability and user experience in mind.',
      technologies: ['React', 'TypeScript', 'Node.js', 'PostgreSQL', 'Stripe', 'Redis', 'Docker'],
      status: 'completed',
      demoUrl: 'https://demo-ecommerce.com',
      githubUrl: 'https://github.com/alexcodemaster/ecommerce-platform',
      features: [
        'User authentication & authorization',
        'Product catalog with search & filters',
        'Shopping cart & checkout process',
        'Payment processing with Stripe',
        'Admin dashboard for inventory management',
        'Real-time notifications',
        'Mobile-responsive design'
      ],
      stats: { lines: '25K+', commits: '150+', duration: '4 months' },
      color: '#3b82f6',
      icon: '🛒'
    },
    {
      id: 2,
      name: 'Task Management API',
      type: 'REST API Service',
      category: 'api',
      description: 'Scalable task management API with team collaboration features',
      longDescription: 'A robust REST API for task management applications with features like team collaboration, project organization, real-time updates, and comprehensive analytics.',
      technologies: ['Python', 'FastAPI', 'PostgreSQL', 'Redis', 'Docker', 'JWT', 'WebSocket'],
      status: 'completed',
      githubUrl: 'https://github.com/alexcodemaster/task-api',
      features: [
        'RESTful API design with FastAPI',
        'JWT-based authentication',
        'Real-time updates via WebSocket',
        'Team and project management',
        'Task analytics and reporting',
        'Rate limiting and caching',
        'Comprehensive API documentation'
      ],
      stats: { lines: '15K+', commits: '95+', duration: '3 months' },
      color: '#10b981',
      icon: '📋'
    },
    {
      id: 3,
      name: 'DevTools Dashboard',
      type: 'Developer Tools',
      category: 'tool',
      description: 'Comprehensive developer dashboard for monitoring and analytics',
      longDescription: 'A powerful dashboard for developers to monitor application performance, track API usage, manage deployments, and analyze user behavior with beautiful visualizations.',
      technologies: ['React', 'D3.js', 'Node.js', 'MongoDB', 'Socket.io', 'Chart.js', 'Express'],
      status: 'in-progress',
      demoUrl: 'https://devtools-dashboard.com',
      githubUrl: 'https://github.com/alexcodemaster/devtools-dashboard',
      features: [
        'Real-time performance monitoring',
        'API usage analytics',
        'Custom dashboard creation',
        'Alert system for critical events',
        'Data visualization with D3.js',
        'Multi-project support',
        'Export and reporting features'
      ],
      stats: { lines: '35K+', commits: '200+', duration: '6 months' },
      color: '#8b5cf6',
      icon: '📊'
    },
    {
      id: 4,
      name: 'Social Media App',
      type: 'Mobile Application',
      category: 'mobile',
      description: 'Cross-platform social media app with React Native',
      longDescription: 'A feature-rich social media application built with React Native, featuring user profiles, post sharing, real-time messaging, and advanced privacy controls.',
      technologies: ['React Native', 'TypeScript', 'Firebase', 'Redux', 'Expo', 'AsyncStorage'],
      status: 'beta',
      githubUrl: 'https://github.com/alexcodemaster/social-app',
      features: [
        'User profiles and authentication',
        'Post creation with media support',
        'Real-time messaging system',
        'News feed with infinite scroll',
        'Push notifications',
        'Privacy settings and blocking',
        'Cross-platform compatibility'
      ],
      stats: { lines: '28K+', commits: '180+', duration: '5 months' },
      color: '#f59e0b',
      icon: '📱'
    },
    {
      id: 5,
      name: 'AI Code Assistant',
      type: 'VS Code Extension',
      category: 'tool',
      description: 'AI-powered code completion and refactoring tool',
      longDescription: 'An intelligent VS Code extension that provides AI-powered code suggestions, automatic refactoring, and smart code analysis to boost developer productivity.',
      technologies: ['TypeScript', 'VS Code API', 'OpenAI API', 'Webpack', 'Jest'],
      status: 'completed',
      githubUrl: 'https://github.com/alexcodemaster/ai-code-assistant',
      features: [
        'AI-powered code completion',
        'Automatic code refactoring',
        'Smart error detection',
        'Code quality analysis',
        'Multiple language support',
        'Custom snippets generation',
        'Integration with popular frameworks'
      ],
      stats: { lines: '12K+', commits: '85+', duration: '2 months' },
      color: '#ef4444',
      icon: '🤖'
    },
    {
      id: 6,
      name: 'Crypto Portfolio Tracker',
      type: 'Web Application',
      category: 'web',
      description: 'Real-time cryptocurrency portfolio tracking and analysis',
      longDescription: 'A comprehensive cryptocurrency portfolio tracker with real-time price updates, profit/loss analysis, market insights, and automated trading alerts.',
      technologies: ['Vue.js', 'Vuex', 'Node.js', 'WebSocket', 'Chart.js', 'Express', 'MongoDB'],
      status: 'completed',
      demoUrl: 'https://crypto-tracker-demo.com',
      githubUrl: 'https://github.com/alexcodemaster/crypto-tracker',
      features: [
        'Real-time price tracking',
        'Portfolio performance analysis',
        'Market trend visualization',
        'Price alerts and notifications',
        'Multi-exchange support',
        'Historical data analysis',
        'Dark/light theme toggle'
      ],
      stats: { lines: '22K+', commits: '140+', duration: '3.5 months' },
      color: '#06b6d4',
      icon: '₿'
    }
  ];

  const filteredProjects = projects.filter(project => {
    const matchesFilter = filter === 'all' || project.category === filter;
    const matchesSearch = project.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                          project.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
                          project.technologies.some(tech => tech.toLowerCase().includes(searchTerm.toLowerCase()));
    return matchesFilter && matchesSearch;
  });

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return '#10b981';
      case 'in-progress': return '#f59e0b';
      case 'beta': return '#3b82f6';
      default: return '#6b7280';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'completed': return 'CAPTURED';
      case 'in-progress': return 'EVOLVING';
      case 'beta': return 'TRAINING';
      default: return 'UNKNOWN';
    }
  };

  return (
    <div className="section-content">
      <h2 className="section-title">PROJECT DATABASE</h2>
      
      {/* Search and Filter Controls */}
      <div className="flex flex-col md:flex-row gap-4 justify-center mb-8">
        <div className="relative">
          <Search size={16} className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400" />
          <input
            type="text"
            placeholder="Search projects..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="bg-black bg-opacity-50 border-2 border-gray-600 rounded-lg pl-12 pr-4 py-3 text-green-400 font-mono focus:border-green-400 focus:outline-none focus:shadow-lg focus:shadow-green-400/30 transition-all"
          />
        </div>
        
        <div className="relative">
          <Filter size={16} className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400" />
          <select
            value={filter}
            onChange={(e) => setFilter(e.target.value as any)}
            className="bg-black bg-opacity-50 border-2 border-gray-600 rounded-lg pl-12 pr-8 py-3 text-green-400 font-mono focus:border-green-400 focus:outline-none appearance-none cursor-pointer"
          >
            <option value="all">ALL TYPES</option>
            <option value="web">WEB TYPE</option>
            <option value="mobile">MOBILE TYPE</option>
            <option value="api">API TYPE</option>
            <option value="tool">TOOL TYPE</option>
          </select>
        </div>
      </div>

      {/* Projects Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
        {filteredProjects.map((project, index) => (
          <div
            key={project.id}
            className="bg-gradient-to-br from-gray-800 to-gray-900 border-2 border-gray-600 rounded-xl p-6 cursor-pointer transition-all hover:border-green-400 hover:transform hover:-translate-y-2 hover:shadow-xl"
            onClick={() => setSelectedProject(project)}
            style={{ animationDelay: `${index * 0.1}s` }}
          >
            <div className="flex justify-between items-start mb-4">
              <div className="text-3xl">{project.icon}</div>
              <div 
                className="retro-text text-xs px-3 py-1 rounded-full border"
                style={{ 
                  color: getStatusColor(project.status),
                  borderColor: getStatusColor(project.status)
                }}
              >
                {getStatusText(project.status)}
              </div>
            </div>
            
            <div className="mb-4">
              <h3 className="retro-text text-white text-sm mb-2">{project.name}</h3>
              <div className="text-gray-400 text-sm mb-3">{project.type}</div>
              <p className="text-gray-300 text-sm leading-relaxed">{project.description}</p>
            </div>
            
            <div className="flex flex-wrap gap-2 mb-4">
              {project.technologies.slice(0, 3).map((tech) => (
                <span 
                  key={tech} 
                  className="px-2 py-1 rounded border retro-text text-xs text-white"
                  style={{ 
                    background: `linear-gradient(145deg, ${project.color}40, transparent)`,
                    borderColor: project.color
                  }}
                >
                  {tech}
                </span>
              ))}
              {project.technologies.length > 3 && (
                <span className="px-2 py-1 rounded border border-gray-600 retro-text text-xs text-gray-400">
                  +{project.technologies.length - 3}
                </span>
              )}
            </div>
            
            <div className="grid grid-cols-3 gap-4 pt-4 border-t border-gray-600">
              <div className="text-center">
                <div className="retro-text text-xs mb-1" style={{ color: project.color }}>
                  {project.stats.lines}
                </div>
                <div className="retro-text text-xs text-gray-400">LINES</div>
              </div>
              <div className="text-center">
                <div className="retro-text text-xs mb-1" style={{ color: project.color }}>
                  {project.stats.commits}
                </div>
                <div className="retro-text text-xs text-gray-400">COMMITS</div>
              </div>
              <div className="text-center">
                <div className="retro-text text-xs mb-1" style={{ color: project.color }}>
                  {project.stats.duration}
                </div>
                <div className="retro-text text-xs text-gray-400">DURATION</div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Project Detail Modal */}
      {selectedProject && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-80 flex items-center justify-center z-50 p-4"
          onClick={() => setSelectedProject(null)}
        >
          <div 
            className="bg-gradient-to-br from-gray-800 to-gray-900 border-2 border-green-400 rounded-xl w-full max-w-4xl max-h-[90vh] overflow-y-auto"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex justify-between items-center p-6 border-b border-gray-600">
              <div className="flex items-center gap-4">
                <span className="text-3xl">{selectedProject.icon}</span>
                <div>
                  <h3 className="retro-text text-green-400 text-lg">{selectedProject.name}</h3>
                  <div className="text-gray-400">{selectedProject.type}</div>
                </div>
              </div>
              <button 
                className="w-10 h-10 rounded-full border-2 border-red-500 text-red-500 hover:bg-red-500 hover:text-white transition-colors"
                onClick={() => setSelectedProject(null)}
              >
                ✕
              </button>
            </div>
            
            <div className="p-6 space-y-6 text-gray-300">
              <div>
                <h4 className="retro-text text-green-400 text-sm mb-3">DESCRIPTION</h4>
                <p className="leading-relaxed">{selectedProject.longDescription}</p>
              </div>
              
              <div>
                <h4 className="retro-text text-green-400 text-sm mb-3">TECH STACK</h4>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
                  {selectedProject.technologies.map((tech) => (
                    <div 
                      key={tech} 
                      className="bg-gradient-to-br from-gray-700 to-gray-800 border border-green-400 rounded-md p-2 text-center retro-text text-xs text-green-400"
                    >
                      {tech}
                    </div>
                  ))}
                </div>
              </div>
              
              <div>
                <h4 className="retro-text text-green-400 text-sm mb-3">FEATURES</h4>
                <ul className="space-y-2">
                  {selectedProject.features.map((feature, index) => (
                    <li key={index} className="bg-green-400 bg-opacity-10 border-l-4 border-green-400 p-3 rounded-r">
                      {feature}
                    </li>
                  ))}
                </ul>
              </div>
              
              <div className="flex flex-col md:flex-row gap-4 justify-center">
                {selectedProject.demoUrl && (
                  <a 
                    href={selectedProject.demoUrl} 
                    target="_blank" 
                    rel="noopener noreferrer" 
                    className="flex items-center justify-center gap-2 bg-gradient-to-r from-blue-600 to-blue-700 border-2 border-blue-500 rounded-lg px-6 py-3 text-white retro-text text-xs hover:from-blue-700 hover:to-blue-800 transition-all"
                  >
                    <ExternalLink size={16} />
                    <span>LIVE DEMO</span>
                  </a>
                )}
                {selectedProject.githubUrl && (
                  <a 
                    href={selectedProject.githubUrl} 
                    target="_blank" 
                    rel="noopener noreferrer" 
                    className="flex items-center justify-center gap-2 bg-gradient-to-r from-gray-600 to-gray-700 border-2 border-gray-500 rounded-lg px-6 py-3 text-white retro-text text-xs hover:from-gray-700 hover:to-gray-800 transition-all"
                  >
                    <Github size={16} />
                    <span>SOURCE CODE</span>
                  </a>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Projects;
