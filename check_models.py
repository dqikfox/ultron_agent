import requests
try:
    response = requests.get('http://localhost:11434/api/tags', timeout=5)
    models = response.json().get('models', [])
    print('Available models:')
    for model in models:
        print(f'  - {model["name"]}')
    ultron_models = [m for m in models if 'ultron' in m['name'].lower()]
    if ultron_models:
        print(f'\nFound Ultron models: {[m["name"] for m in ultron_models]}')
    else:
        print('\nNo Ultron models found. You may need to pull gerard/ultron:latest')
except Exception as e:
    print(f'Error: {e}')
