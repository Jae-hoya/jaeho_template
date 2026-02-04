-------------------------------------------------------------------------------------------------------------------------------
Test (db를 위한 docker를 반드시 켜야한다.)
의사를 위한 대출 상품을 추천해줘

2025년 금리 알려줘
-------------------------------------------------------------------------------------------------------------------------------

내 상위 디렉토리를 가져오는 권한을 주기 위함
/add-dir (클로드 코드)
chmod -R 777 /path/to/parent_directory (안되는듯? 그냥 경로 주고 해달라 하면 된다)


-------------------------------------------------------------------------------------------------------------------------------
만약, 잘 안된다면 구현, 오류, 문제해결 레포트를 받고,
ultrathinking 해서 해결해달라고 하는것도 방법이다. 

이 레포트 내용들을 모르니, 해결하는동안 다른 클로드 창에서 

레포트md들을 읽고 정확히 무엇이 문제인지 알려줘. 간단히 요약 (코드 수정 하지 마.) 

받는게 좋다.



입력:
레포트(md파일들)을 바탕으로 문제를 해결해줘. 
ultrathink

참조:
@ ~ 파일
@ ~ 파일
-------------------------------------------------------------------------------------------------------------------------------
입력:
테스트 해줘. 가상환경은 C:\Users\skyop\jaeho_template\dotenv_windows 을 사용하면 돼.



-------------------------------------------------------------------------------------------------------------------------------

입력:
프로젝트:
이미 구현된 hybrid_search.py를 tool로 사용하는 agent를 만들어줘

https://github.com/vercel-labs/ai-sdk-preview-python-streaming.git clone 해서 프론트엔드를 이걸로 활용해

요구사항:
- 가상환경은 C:\Users\skyop\jaeho_template\dotenv_windows 을 사용
- clone하면 weather tool이 있을텐데 이것을 제거
- hybrid search를 import해서 tool로 사용해
- web search tool을 tavily을 이용해서 구현: https://docs.tavily.com/documentation/api-reference/endpoint/search

참고: 
../LangGraph_RAG 와 ../ hybrid_search 에서 파일을 읽고 맥락을 파악해.

-------------------------------------------------------------------------------------------------------------------------------

1) 백엔드 띄우기 (이미 실행 중이면 생략)
cd .\11.VibeCoding_for_Agent\Agenctic_RAG\

C:\Users\skyop\jaeho_template\dotenv_windows\Scripts\python.exe -m uvicorn api.index:app --reload --app-dir "ai-sdk-preview-python-streaming"


npm install -g pnpm
pnpm --version
pnpm dev


2) 프론트엔드 실행
일단 가상환경없이 설치해야할것들
npm install -g pnpm
pnpm --version
pnpm dev


경로 이동 후!
cd C:\Users\skyop\jaeho_template\11.VibeCoding_for_Agent\Agenctic_RAG\ai-sdk-preview-python-streaming 
pnpm install
pnpm dev



3) 브라우저에서 접속  
http://localhost:3000