import React, { useState, useEffect } from 'react';
import { Send, Mail, Phone, MapPin, Github, Linkedin, Twitter, MessageSquare } from 'lucide-react';

interface ContactProps {
  theme: 'red' | 'blue';
}

const Contact: React.FC<ContactProps> = ({ theme }) => {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    subject: '',
    message: ''
  });
  const [isTransmitting, setIsTransmitting] = useState(false);
  const [transmissionStatus, setTransmissionStatus] = useState<'idle' | 'sending' | 'success' | 'error'>('idle');
  const [signalStrength, setSignalStrength] = useState(0);

  // Simulate signal strength animation
  useEffect(() => {
    const interval = setInterval(() => {
      setSignalStrength(prev => (prev >= 4 ? 1 : prev + 1));
    }, 800);

    return () => clearInterval(interval);
  }, []);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    setFormData(prev => ({
      ...prev,
      [e.target.name]: e.target.value
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsTransmitting(true);
    setTransmissionStatus('sending');

    // Simulate form submission
    await new Promise(resolve => setTimeout(resolve, 3000));

    // Simulate success (in real app, handle actual form submission here)
    setTransmissionStatus('success');
    setIsTransmitting(false);

    // Reset form after success
    setTimeout(() => {
      setFormData({ name: '', email: '', subject: '', message: '' });
      setTransmissionStatus('idle');
    }, 3000);
  };

  const contactMethods = [
    {
      icon: <Mail size={20} />,
      label: 'EMAIL',
      value: 'alex.codemaster@email.com',
      href: 'mailto:alex.codemaster@email.com',
      color: '#3b82f6'
    },
    {
      icon: <Phone size={20} />,
      label: 'PHONE',
      value: '+1 (555) 123-4567',
      href: 'tel:+15551234567',
      color: '#10b981'
    },
    {
      icon: <MapPin size={20} />,
      label: 'LOCATION',
      value: 'San Francisco, CA',
      href: 'https://maps.google.com/?q=San Francisco, CA',
      color: '#f59e0b'
    },
    {
      icon: <MessageSquare size={20} />,
      label: 'TELEGRAM',
      value: '@alexcodemaster',
      href: 'https://t.me/alexcodemaster',
      color: '#06b6d4'
    }
  ];

  const socialLinks = [
    {
      icon: <Github size={24} />,
      label: 'GitHub',
      href: 'https://github.com/alexcodemaster',
      color: '#24292e'
    },
    {
      icon: <Linkedin size={24} />,
      label: 'LinkedIn',
      href: 'https://linkedin.com/in/alexcodemaster',
      color: '#0077b5'
    },
    {
      icon: <Twitter size={24} />,
      label: 'Twitter',
      href: 'https://twitter.com/alexcodemaster',
      color: '#1da1f2'
    }
  ];

  return (
    <div className="section-content">
      <h2 className="section-title">COMMUNICATION CENTER</h2>
      
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 max-w-6xl mx-auto">
        {/* Main Communication Panel */}
        <div className="lg:col-span-2 bg-gradient-to-br from-gray-800 to-gray-900 border-2 border-green-400 rounded-xl p-6">
          <div className="flex justify-between items-center mb-6 pb-4 border-b border-gray-600">
            <div className="flex items-center gap-4">
              <div className="retro-text text-gray-400 text-xs">SIGNAL</div>
              <div className="flex gap-1 items-end h-5">
                {Array.from({ length: 4 }, (_, i) => (
                  <div
                    key={i}
                    className={`w-1 bg-gray-600 transition-all ${
                      i < signalStrength ? 'bg-green-400 shadow-lg shadow-green-400/50' : ''
                    }`}
                    style={{ height: `${(i + 1) * 25}%` }}
                  ></div>
                ))}
              </div>
            </div>
            <div className="flex items-center gap-2">
              <div 
                className={`w-3 h-3 rounded-full transition-all ${
                  transmissionStatus === 'idle' ? 'bg-green-400 shadow-lg shadow-green-400/50' :
                  transmissionStatus === 'sending' ? 'bg-yellow-400 shadow-lg shadow-yellow-400/50 animate-pulse' :
                  transmissionStatus === 'success' ? 'bg-green-400 shadow-lg shadow-green-400/50' :
                  'bg-red-400 shadow-lg shadow-red-400/50'
                }`}
              ></div>
              <span className="retro-text text-xs text-gray-300">
                {transmissionStatus === 'idle' && 'READY'}
                {transmissionStatus === 'sending' && 'SENDING'}
                {transmissionStatus === 'success' && 'SENT'}
                {transmissionStatus === 'error' && 'ERROR'}
              </span>
            </div>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="flex justify-between items-center mb-6">
              <h3 className="retro-text text-green-400 text-lg">MESSAGE TRANSMISSION</h3>
              <div className="font-mono text-gray-400 text-sm bg-black bg-opacity-50 px-3 py-1 rounded border border-gray-600">
                ID: MSG-{Date.now().toString().slice(-6)}
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label htmlFor="name" className="block retro-text text-green-400 text-xs mb-2">SENDER NAME</label>
                <input
                  type="text"
                  id="name"
                  name="name"
                  value={formData.name}
                  onChange={handleInputChange}
                  required
                  disabled={isTransmitting}
                  className="w-full bg-black bg-opacity-50 border-2 border-gray-600 rounded-lg p-3 text-gray-300 font-mono focus:border-green-400 focus:outline-none focus:shadow-lg focus:shadow-green-400/30 transition-all disabled:opacity-60"
                  placeholder="Enter your name..."
                />
              </div>

              <div>
                <label htmlFor="email" className="block retro-text text-green-400 text-xs mb-2">SENDER EMAIL</label>
                <input
                  type="email"
                  id="email"
                  name="email"
                  value={formData.email}
                  onChange={handleInputChange}
                  required
                  disabled={isTransmitting}
                  className="w-full bg-black bg-opacity-50 border-2 border-gray-600 rounded-lg p-3 text-gray-300 font-mono focus:border-green-400 focus:outline-none focus:shadow-lg focus:shadow-green-400/30 transition-all disabled:opacity-60"
                  placeholder="Enter your email..."
                />
              </div>

              <div className="md:col-span-2">
                <label htmlFor="subject" className="block retro-text text-green-400 text-xs mb-2">MESSAGE SUBJECT</label>
                <input
                  type="text"
                  id="subject"
                  name="subject"
                  value={formData.subject}
                  onChange={handleInputChange}
                  required
                  disabled={isTransmitting}
                  className="w-full bg-black bg-opacity-50 border-2 border-gray-600 rounded-lg p-3 text-gray-300 font-mono focus:border-green-400 focus:outline-none focus:shadow-lg focus:shadow-green-400/30 transition-all disabled:opacity-60"
                  placeholder="Enter message subject..."
                />
              </div>

              <div className="md:col-span-2">
                <label htmlFor="message" className="block retro-text text-green-400 text-xs mb-2">MESSAGE CONTENT</label>
                <textarea
                  id="message"
                  name="message"
                  value={formData.message}
                  onChange={handleInputChange}
                  required
                  disabled={isTransmitting}
                  rows={6}
                  className="w-full bg-black bg-opacity-50 border-2 border-gray-600 rounded-lg p-3 text-gray-300 font-mono focus:border-green-400 focus:outline-none focus:shadow-lg focus:shadow-green-400/30 transition-all resize-none disabled:opacity-60"
                  placeholder="Enter your message content..."
                ></textarea>
              </div>
            </div>

            <button
              type="submit"
              disabled={isTransmitting}
              className={`w-full border-2 rounded-lg p-4 retro-text text-sm transition-all flex items-center justify-center gap-3 relative overflow-hidden ${
                isTransmitting
                  ? 'bg-gradient-to-r from-yellow-600 to-yellow-700 border-yellow-500 text-black'
                  : 'bg-gradient-to-r from-green-600 to-green-700 border-green-400 text-black hover:from-green-700 hover:to-green-800 hover:shadow-xl hover:-translate-y-1'
              } disabled:cursor-not-allowed`}
            >
              <Send size={16} />
              <span>{isTransmitting ? 'TRANSMITTING...' : 'TRANSMIT MESSAGE'}</span>
              {isTransmitting && (
                <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/30 to-transparent animate-pulse"></div>
              )}
            </button>
          </form>

          {transmissionStatus === 'success' && (
            <div className="mt-6 flex items-center gap-4 bg-green-400 bg-opacity-10 border-2 border-green-400 rounded-lg p-4 animate-fade-in">
              <div className="w-10 h-10 bg-green-400 rounded-full flex items-center justify-center text-black font-bold text-xl">
                ✓
              </div>
              <div>
                <h4 className="retro-text text-green-400 text-sm mb-1">TRANSMISSION SUCCESSFUL</h4>
                <p className="text-gray-300 text-sm">Your message has been received. Response incoming within 24 hours.</p>
              </div>
            </div>
          )}
        </div>

        {/* Contact Methods & Info */}
        <div className="space-y-6">
          {/* Direct Communication Channels */}
          <div className="bg-gradient-to-br from-gray-800 to-gray-900 border-2 border-gray-600 rounded-xl p-6">
            <h3 className="retro-text text-green-400 text-sm text-center mb-6">DIRECT CHANNELS</h3>
            <div className="space-y-3">
              {contactMethods.map((method, index) => (
                <a
                  key={method.label}
                  href={method.href}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center gap-3 bg-gradient-to-r from-gray-700 to-gray-800 border border-gray-600 rounded-lg p-3 hover:border-green-400 transition-all hover:transform hover:translate-x-1"
                  style={{ animationDelay: `${index * 0.1}s` }}
                >
                  <div 
                    className="w-10 h-10 rounded-lg flex items-center justify-center text-white border"
                    style={{ 
                      background: `linear-gradient(145deg, ${method.color}40, transparent)`,
                      borderColor: method.color
                    }}
                  >
                    {method.icon}
                  </div>
                  <div className="flex-1">
                    <div className="retro-text text-xs mb-1" style={{ color: method.color }}>
                      {method.label}
                    </div>
                    <div className="text-gray-300 text-sm">{method.value}</div>
                  </div>
                  <div 
                    className="w-2 h-2 rounded-full animate-pulse"
                    style={{ backgroundColor: method.color, boxShadow: `0 0 6px ${method.color}` }}
                  ></div>
                </a>
              ))}
            </div>
          </div>

          {/* Social Networks */}
          <div className="bg-gradient-to-br from-gray-800 to-gray-900 border-2 border-gray-600 rounded-xl p-6">
            <h4 className="retro-text text-green-400 text-sm text-center mb-4">SOCIAL NETWORKS</h4>
            <div className="space-y-2">
              {socialLinks.map((social) => (
                <a
                  key={social.label}
                  href={social.href}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center gap-3 bg-gradient-to-r from-gray-700 to-gray-800 border border-gray-600 rounded-lg p-3 hover:transform hover:-translate-y-1 transition-all"
                  style={{ 
                    borderColor: social.color,
                    background: `linear-gradient(145deg, ${social.color}20, transparent)` 
                  }}
                  title={social.label}
                >
                  <span style={{ color: social.color }}>{social.icon}</span>
                  <span className="retro-text text-xs text-white">{social.label}</span>
                </a>
              ))}
            </div>
          </div>

          {/* Availability Status */}
          <div className="bg-gradient-to-br from-gray-800 to-gray-900 border-2 border-gray-600 rounded-xl p-6">
            <h4 className="retro-text text-green-400 text-sm text-center mb-4">AVAILABILITY STATUS</h4>
            <div className="space-y-4">
              <div className="flex items-center justify-center gap-2">
                <div className="w-3 h-3 bg-green-400 rounded-full animate-pulse shadow-lg shadow-green-400/50"></div>
                <span className="retro-text text-green-400 text-xs">ONLINE</span>
              </div>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-400">Avg Response Time:</span>
                  <span className="text-gray-300 font-semibold">2-4 hours</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Timezone:</span>
                  <span className="text-gray-300 font-semibold">PST (UTC-8)</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Contact;
