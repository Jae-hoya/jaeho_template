aws mcp git clone
git clone https://github.com/awslabs/mcp.git

데이터
https://data.seoul.go.kr/dataList/OA-2269/S/1/datasetView.do
https://data.seoul.go.kr/dataList/OA-2208/S/1/datasetView.do

(sheet의 json과 openapi 명세서)
---
구현체를 따라하고 싶으면 cloning을 해서 조사를 시키고, 이것을 바탕으로 구현을 시키면 된다.
조사시킨 결과를 바탕으로 새로운 mcp server를 자동으로 생성하는 agentic한 프로세스를 claude code의 커맨드 기반으로 만들 수 있다.
이 만들어 놓은 커맨드 기반으로 mcp server를 자동으로 만들고 사용해보자!

@mcp/ 를 분석해서 레포트를 작성해 주세요

1. 어떤식으로 하위 mcp server들을 관리하는지 조사해주세요.
2. @mcp\src\amazon-bedrock-agentcore-mcp-server/  를 분석해서 mcp server를 하나의 구조로 정리해 주세요

-----------------------------------------------------------------------------------------------------------------------
https://github.com/awslabs/mcp/tree/cookiecutters cookiecutter 템플릿을 만들어줘 (git 준다음에!)

그리고 그 밖에 cookiecutter 관리 리포트가 필요해.
-----------------------------------------------------------------------------------------------------------------------
입력: (template_opencode_codex/ template_claudecode 둘다 하기)

template/ 디렉토리에 만들고, 만들때에는 @Cookiecutter_Management_Analysis.md 를 참고해서 새로운 mcp server를 만들 때 사용할 수 있게 도와줘

프로젝트 이름은 "data-seoul-mcp" 이고, 네이밍 컨벤션은 분석되있는 레포트파일을 그대로 참고해.
내가 바꾸려고 하는 api는 아래 정보를 붙여 넣었어


<문화행사정보 api 개요>
문화행사정보는 시민들이 쉽게 문화행사 일정과 위치를 확인할 수 있도록 서울시 내에 있는 문화행사 정보, 문화공간 현황, 행사 장소명, 문화공간에 가기 위한 대중교통 이용 안내 등의 문화행사 및 관련 정보를 상세히 제공합니다. 시민들은 장르별로 구분된 문화공간 현황과 함께 원하는 문화행사가 열리는 장소와 행사 기간을 확인하실 수 있습니다. 또한, 문화행사가 열리는 곳 인근 교통 정보를 확인하실 수 있습니다. OpenAPI로 서비스하고 있습니다

개방데이터 정보
개방데이터 목록	주요 데이터 항목	제공 방식
서울시 문화행사 공공서비스예약 정보 
서울시 여성가족재단 행사 정보 
서울시 문화행사 정보 

주요 데이터 항목
총 데이터 건수,  요청결과 코드,  요청결과 메시지,  자치구코드,  자치구명,  장르명,  분류코드,  분류코드 명,  코드별 개수,  문화행사코드,  시작일자,  종료일자,  장소,  문화행사코드 등	

</문화행사정보 api 개요>

참고: mcp server 들의 모음을 monorepo에 관리하는 프로젝트를 할거야/ "/mcp" 프로젝트를 따라할거야
@AWS_MCP_Servers_Analysis_Report.md 


---
상황에따라
dockerfile은 사용하지 않을거야 참고해.


---

만든 README.md에서, cursor연동 및
uvx를 사용하는 부분과 동시에 로컬 파일을 바로 실행하는 방법을 가이드 하는 부분을 추가 해줘.

예시:

{
  "mcpServers": {
    "seoul-culture-events": {
      "command": "uv",
      "args": [
        "--directory",
        "/PATH/",
        "run",
        "python"
      ],
      "env": {
        "SEOUL_API_KEY": "...",
        "SEOUL_API_BASE_URL": "...",
      }    
    }
  } 
}

command, args를 조심해서 틀리지 않게 작성해줘


-----------------------------------------------------------------------------------------------------------------------

입력:               template_cladecode or template_opencode_codex
@template_cladecode/ 를 조회해서 서울시 문화행사 mcp server를 관리하는 프로젝트에 대해 문서를 작성해 -> README.md, Claude.md

<문화행사정보 api 개요>
문화행사정보는 시민들이 쉽게 문화행사 일정과 위치를 확인할 수 있도록 서울시 내에 있는 문화행사 정보, 문화공간 현황, 행사 장소명, 문화공간에 가기 위한 대중교통 이용 안내 등의 문화행사 및 관련 정보를 상세히 제공합니다. 시민들은 장르별로 구분된 문화공간 현황과 함께 원하는 문화행사가 열리는 장소와 행사 기간을 확인하실 수 있습니다. 또한, 문화행사가 열리는 곳 인근 교통 정보를 확인하실 수 있습니다. OpenAPI로 서비스하고 있습니다

개방데이터 정보
개방데이터 목록	주요 데이터 항목	제공 방식

서울시 문화행사 공공서비스예약 정보 
서울시 여성가족재단 행사 정보 
서울시 문화행사 정보 



주요 데이터 항목
총 데이터 건수,  요청결과 코드,  요청결과 메시지,  자치구코드,  자치구명,  장르명,  분류코드,  분류코드 명,  코드별 개수,  문화행사코드,  시작일자,  종료일자,  장소,  문화행사코드 등	

</문화행사정보 api 개요>

-----------------------------------------------------------------------------------------------------------------------
(CLAUDE.md)를 못만들었을때
@template/ 아래의 코드 관련 내용을 분석해서 프로젝트 구조, 개발 명령어를 추가해줘

개발 방식도 추가하는데,
- TDD 기반으로 개발할 것
- atomic 단위로 commit, commit할 때에는 관련있는 파일만 add 할것
- 절대 git push 하지 말것


-----------------------------------------------------------------------------------------------------------------------

slash command를 잘 만들기 위해서 claude code docs에 가서

입력:
shalsh command를 만들어줘
이름은 "/add-mcp-server"

먼저 cookiecutter 명령어를 사용해서 템플릿을 사용한 다음에 파일을 수정해서 mcp server를 구현해줘

나는 api 명세서를 파일로 제공할거야. 파일은 xls(명세서), 그리고 예시 데이터를 제공할거야.


opencode의 경우:
https://opencode.ai/docs/commands/



참조:
claude의 경우:
https://code.claude.com/docs/en/skills
https://docs.claude.com/en/docs/claude-code/slash-commands#custom-slash-commands

------
/add-mcp-server  가 1개인데 이걸 그대로 tool로 구현하는 간단한 implement를 수행해
참조할 api spec: @docs/서울시+문화행사+정보.xls

예시: @docs/서울시 문화행사 정보.json
이건 일종의 테스트라고 보면 돼