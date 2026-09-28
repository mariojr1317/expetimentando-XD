from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title='Universal App Runner', version='0.1.0')

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=False,
    allow_methods=['*'],
    allow_headers=['*'],
)

@app.get('/')
def root():
    return {'name': 'Universal App Runner', 'version': '0.1.0', 'status': 'development'}

@app.get('/health')
def health():
    return {'status': 'ok'}

@app.get('/api/capabilities')
def capabilities():
    return {
        'exe': {'available': False, 'reason': 'isolated runner not implemented'},
        'apk': {'available': False, 'reason': 'Android runner not implemented'},
        'webrtc': {'available': False, 'reason': 'streaming not implemented'},
    }