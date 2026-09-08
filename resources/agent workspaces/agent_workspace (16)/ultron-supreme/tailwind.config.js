/** @type {import('tailwindcss').Config} */
module.exports = {
	darkMode: ['class'],
	content: [
		'./pages/**/*.{ts,tsx}',
		'./components/**/*.{ts,tsx}',
		'./app/**/*.{ts,tsx}',
		'./src/**/*.{ts,tsx}',
	],
	theme: {
		container: {
			center: true,
			padding: '2rem',
			screens: {
				'2xl': '1400px',
			},
		},
		extend: {
			colors: {
				border: 'hsl(var(--border))',
				input: 'hsl(var(--input))',
				ring: 'hsl(var(--ring))',
				background: 'hsl(var(--background))',
				foreground: 'hsl(var(--foreground))',
				primary: {
					DEFAULT: '#2B5D3A',
					foreground: 'hsl(var(--primary-foreground))',
				},
				secondary: {
					DEFAULT: '#4A90E2',
					foreground: 'hsl(var(--secondary-foreground))',
				},
				accent: {
					DEFAULT: '#F5A623',
					foreground: 'hsl(var(--accent-foreground))',
				},
				destructive: {
					DEFAULT: 'hsl(var(--destructive))',
					foreground: 'hsl(var(--destructive-foreground))',
				},
				muted: {
					DEFAULT: 'hsl(var(--muted))',
					foreground: 'hsl(var(--muted-foreground))',
				},
				popover: {
					DEFAULT: 'hsl(var(--popover))',
					foreground: 'hsl(var(--popover-foreground))',
				},
				card: {
					DEFAULT: 'hsl(var(--card))',
					foreground: 'hsl(var(--card-foreground))',
				},
				ultron: {
					red: '#ff3333',
					blue: '#00d4ff',
					dark: '#0a0a0a',
					darker: '#050505',
					steel: '#1a1a1a',
					'steel-light': '#2a2a2a',
					gray: '#666666',
					success: '#00ff88',
					warning: '#ffaa00',
					error: '#ff3333',
				}
			},
			fontFamily: {
				sans: ['Inter', 'ui-sans-serif', 'system-ui', 'sans-serif'],
				heading: ['Inter', 'ui-sans-serif', 'system-ui', 'sans-serif'],
				orbitron: ['Orbitron', 'monospace'],
				roboto: ['Roboto', 'sans-serif'],
			},
			borderRadius: {
				lg: 'var(--radius)',
				md: 'calc(var(--radius) - 2px)',
				sm: 'calc(var(--radius) - 4px)',
			},
			keyframes: {
				'accordion-down': {
					from: { height: 0 },
					to: { height: 'var(--radix-accordion-content-height)' },
				},
				'accordion-up': {
					from: { height: 'var(--radix-accordion-content-height)' },
					to: { height: 0 },
				},
				pulseRed: {
					'0%, 100%': { boxShadow: '0 0 5px rgba(255, 51, 51, 0.5)' },
					'50%': { boxShadow: '0 0 20px rgba(255, 51, 51, 0.8), 0 0 30px rgba(255, 51, 51, 0.6)' },
				},
				pulseBlue: {
					'0%, 100%': { boxShadow: '0 0 5px rgba(0, 212, 255, 0.5)' },
					'50%': { boxShadow: '0 0 20px rgba(0, 212, 255, 0.8), 0 0 30px rgba(0, 212, 255, 0.6)' },
				},
				scan: {
					'0%': { left: '-100%' },
					'50%': { left: '100%' },
					'100%': { left: '100%' },
				},
				holographicShift: {
					'0%, 100%': { backgroundPosition: '0% 0%' },
					'50%': { backgroundPosition: '100% 100%' },
				},
				circuitFlow: {
					'0%': { backgroundPosition: '0% 0%, 0% 0%, 0% 0%' },
					'100%': { backgroundPosition: '200px 200px, -150px -150px, 100px 100px' },
				},
			},
			animation: {
				'accordion-down': 'accordion-down 0.2s ease-out',
				'accordion-up': 'accordion-up 0.2s ease-out',
				'pulse-red': 'pulseRed 2s ease-in-out infinite',
				'pulse-blue': 'pulseBlue 2s ease-in-out infinite',
				'scan': 'scan 3s ease-in-out infinite',
				'holographic': 'holographicShift 4s ease-in-out infinite',
				'circuit-flow': 'circuitFlow 20s linear infinite',
			},
		},
	},
	plugins: [require('tailwindcss-animate')],
}