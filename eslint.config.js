import js from '@eslint/js';
import react from 'eslint-plugin-react';

export default [
  js.configs.recommended,
  {
    files: ['**/*.js', '**/*.jsx'],
    ignores: [
      'node_modules/**',
      'dist/**',
      'build/**',
      '**/*.min.js',
      '**/*.bundle.js',
      '__pycache__/**',
      '**/*.pyc',
      '**/*.log',
      'resources/**',
      'tools/**',
      'addons/**',
      'docs/**',
      'tests/**',
      'ultron_addons/**',
      'public/**',
      '.git/**',
      'pokedex-portfolio/dist/**',
      'pokedex-portfolio/build/**',
      '**/node_modules/**'
    ],
    plugins: {
      react,
    },
    languageOptions: {
      ecmaVersion: 'latest',
      sourceType: 'module',
      parserOptions: {
        ecmaFeatures: {
          jsx: true,
        },
      },
      globals: {
        console: 'readonly',
        process: 'readonly',
        Buffer: 'readonly',
        __dirname: 'readonly',
        __filename: 'readonly',
        module: 'readonly',
        require: 'readonly',
        exports: 'readonly',
        global: 'readonly',
        window: 'readonly',
        document: 'readonly',
        navigator: 'readonly',
      },
    },
    rules: {
      'indent': ['error', 2],
      'quotes': ['error', 'single'],
      'semi': ['error', 'always'],
      'no-unused-vars': 'warn',
      'no-console': 'warn',
      'react/react-in-jsx-scope': 'off',
      'react/prop-types': 'warn',
      ...react.configs.recommended.rules,
    },
    settings: {
      react: {
        version: 'detect',
      },
    },
  },
];
