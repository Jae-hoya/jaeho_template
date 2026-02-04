"""Setup validation script"""
import sys
import os

# Windows UTF-8 encoding fix
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

print('=' * 80)
print('LangGraph RAG 환경 검증')
print('=' * 80)

# 1. Python 버전
print(f'\n1. Python 버전: {sys.version}')

# 2. 필수 패키지
print('\n2. 필수 패키지 확인:')
packages = {
    'streamlit': 'Streamlit',
    'langgraph': 'LangGraph',
    'langchain': 'LangChain',
    'langchain_openai': 'LangChain OpenAI',
    'openai': 'OpenAI',
    'psycopg': 'Psycopg',
    'pandas': 'Pandas',
    'numpy': 'NumPy'
}

for module_name, display_name in packages.items():
    try:
        mod = __import__(module_name)
        version = getattr(mod, '__version__', 'unknown')
        print(f'   ✓ {display_name}: {version}')
    except ImportError:
        print(f'   ✗ {display_name}: 설치 필요')

# 3. 프로젝트 모듈
print('\n3. 프로젝트 모듈 확인:')
try:
    from search_app.database import Database
    print('   ✓ search_app.database')
except Exception as e:
    print(f'   ✗ search_app.database: {e}')

try:
    from search_app.hybrid_search import HybridSearch
    print('   ✓ search_app.hybrid_search')
except Exception as e:
    print(f'   ✗ search_app.hybrid_search: {e}')

try:
    from search_app.config import Config
    print('   ✓ search_app.config')
except Exception as e:
    print(f'   ✗ search_app.config: {e}')

# 4. 환경 변수
print('\n4. 환경 변수 확인:')
from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv('OPENAI_API_KEY')
db_url = os.getenv('DATABASE_URL')

if api_key:
    print(f'   ✓ OPENAI_API_KEY: {api_key[:10]}...')
else:
    print('   ✗ OPENAI_API_KEY: 설정 필요 (.env 파일)')

if db_url:
    print(f'   ✓ DATABASE_URL: {db_url[:30]}...')
else:
    print('   ✗ DATABASE_URL: 설정 필요 (.env 파일)')

# 5. 파일 존재 확인
print('\n5. 필수 파일 확인:')
files = {
    'streamlit_app.py': 'Streamlit 앱',
    'langgraph_rag.py': 'LangGraph RAG',
    'loan_products.json': '대출 상품 데이터',
    '.env': '환경 변수 파일'
}

for filename, description in files.items():
    if os.path.exists(filename):
        size = os.path.getsize(filename)
        print(f'   ✓ {description}: {size:,} bytes')
    else:
        print(f'   ✗ {description}: 파일 없음')

# 6. Streamlit 앱 구문 검사
print('\n6. Streamlit 앱 구문 검사:')
import ast
try:
    with open('streamlit_app.py', 'r', encoding='utf-8') as f:
        ast.parse(f.read())
    print('   ✓ streamlit_app.py 구문 정상')
except SyntaxError as e:
    print(f'   ✗ 구문 에러: {e}')

# 7. 실행 가능 여부
print('\n7. 실행 가능 여부:')
if api_key and db_url and os.path.exists('streamlit_app.py'):
    print('   ✓ Streamlit 앱 실행 가능!')
    print('\n실행 명령어:')
    print('   streamlit run streamlit_app.py')
else:
    print('   ✗ 설정이 완료되지 않았습니다.')
    if not api_key:
        print('      - .env 파일에 OPENAI_API_KEY 설정 필요')
    if not db_url:
        print('      - .env 파일에 DATABASE_URL 설정 필요')

print('\n' + '=' * 80)
