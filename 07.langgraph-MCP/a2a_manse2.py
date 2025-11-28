from datetime import datetime, timedelta
from typing import Dict, List, Any
from dataclasses import dataclass
import re
import os
import sys
from pathlib import Path
import asyncio  # ✅ 운영용에서 cancel/stream 관리 위해 추가

from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field
from langgraph.prebuilt import create_react_agent
from langchain.chat_models import init_chat_model
from langgraph.graph.state import CompiledStateGraph
from langchain_core.messages import AIMessage, HumanMessage

# A2A  패키지만 사용
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.server.tasks import (
    BasePushNotificationSender,
    InMemoryPushNotificationConfigStore,
    InMemoryTaskStore,
    TaskUpdater,
)
from a2a.types import (
    AgentCard,
    AgentCapabilities,
    AgentSkill,
    TaskState,
    TextPart,
    DataPart,
    Part,
)
from a2a.utils import new_agent_text_message, new_task
from a2a.utils.errors import ServerError
import httpx
import uvicorn

# --- 사주 관련 클래스 (기존 코드 유지) ---
@dataclass
class SajuPillar:
    heavenly_stem: str
    earthly_branch: str
    def __str__(self):
        return f"{self.heavenly_stem}{self.earthly_branch}"

@dataclass
class SajuChart:
    year_pillar: SajuPillar
    month_pillar: SajuPillar
    day_pillar: SajuPillar
    hour_pillar: SajuPillar
    birth_info: Dict
    age: int
    korean_age: int
    current_datetime: str
    is_leap_month: bool

    def get_day_master(self) -> str:
        return self.day_pillar.heavenly_stem

class SajuCalculator:
    def __init__(self):
        self.heavenly_stems = ["갑", "을", "병", "정", "무", "기", "경", "신", "임", "계"]
        self.earthly_branches = ["자", "축", "인", "묘", "진", "사", "오", "미", "신", "유", "술", "해"]
        self.five_elements = {
            "갑": "목", "을": "목",
            "병": "화", "정": "화", 
            "무": "토", "기": "토",
            "경": "금", "신": "금",
            "임": "수", "계": "수",
            "자": "수", "축": "토", "인": "목", "묘": "목",
            "진": "토", "사": "화", "오": "화", "미": "토",
            "신": "금", "유": "금", "술": "토", "해": "수"
        }
        self.ten_gods_mapping = {
            "목": {"목": ["비견", "겁재"], "화": ["식신", "상관"], "토": ["편재", "정재"], "금": ["편관", "정관"], "수": ["편인", "정인"]},
            "화": {"화": ["비견", "겁재"], "토": ["식신", "상관"], "금": ["편재", "정재"], "수": ["편관", "정관"], "목": ["편인", "정인"]},
            "토": {"토": ["비견", "겁재"], "금": ["식신", "상관"], "수": ["편재", "정재"], "목": ["편관", "정관"], "화": ["편인", "정인"]},
            "금": {"금": ["비견", "겁재"], "수": ["식신", "상관"], "목": ["편재", "정재"], "화": ["편관", "정관"], "토": ["편인", "정인"]},
            "수": {"수": ["비견", "겁재"], "목": ["식신", "상관"], "화": ["편재", "정재"], "토": ["편관", "정관"], "금": ["편인", "정인"]}
        }
        self.hidden_stems = {
            "자": [("계", 100)],
            "축": [("기", 60), ("계", 30), ("신", 10)],
            "인": [("갑", 60), ("병", 30), ("무", 10)],
            "묘": [("을", 100)],
            "진": [("무", 60), ("을", 30), ("계", 10)],
            "사": [("병", 60), ("무", 30), ("경", 10)],
            "오": [("정", 70), ("기", 30)],
            "미": [("기", 60), ("정", 30), ("을", 10)],
            "신": [("경", 60), ("임", 30), ("무", 10)],
            "유": [("신", 100)],
            "술": [("무", 60), ("신", 30), ("정", 10)],
            "해": [("임", 70), ("갑", 30)]
        }
        self.DAY_PILLAR_BASE_STEM = 5
        self.DAY_PILLAR_BASE_BRANCH = 1
        self.DAY_PILLAR_BASE_DAYS = (datetime(1995, 8, 26) - datetime(1900, 1, 1)).days
        self.monthly_stems = ["병", "정", "무", "기", "경", "신", "임", "계", "갑", "을"]
        
        self.leap_months = {
            1900: 8, 1903: 5, 1906: 4, 1909: 2, 1911: 6, 1914: 5, 1917: 2, 1919: 7,
            1922: 5, 1925: 4, 1928: 2, 1930: 6, 1933: 5, 1936: 3, 1938: 7, 1941: 6,
            1944: 4, 1947: 2, 1949: 7, 1952: 5, 1955: 3, 1957: 8, 1960: 6, 1963: 4,
            1966: 3, 1968: 7, 1971: 5, 1974: 4, 1976: 8, 1979: 6, 1982: 4, 1984: 10,
            1987: 6, 1990: 5, 1993: 3, 1995: 8, 1998: 5, 2001: 4, 2004: 2, 2006: 7,
            2009: 5, 2012: 4, 2014: 9, 2017: 6, 2020: 4, 2023: 2, 2025: 6, 2028: 5,
            2031: 3, 2033: 11, 2036: 6, 2039: 5, 2042: 2, 2044: 7, 2047: 5, 2050: 3,
            2052: 8, 2055: 6, 2058: 4, 2061: 3, 2063: 7, 2066: 5, 2069: 4, 2071: 8,
            2074: 6, 2077: 4, 2080: 3, 2082: 7, 2085: 5, 2088: 4, 2090: 8, 2093: 6,
            2096: 4, 2099: 2
        }

    def _is_leap_month(self, year: int, month: int) -> bool:
        return year in self.leap_months and self.leap_months[year] == month

    def _calculate_international_age(self, birthdate: datetime, now: datetime) -> int:
        age = now.year - birthdate.year
        if (now.month, now.day) < (birthdate.month, birthdate.day):
            age -= 1
        return age

    def _calculate_korean_age(self, birthdate: datetime, now: datetime) -> int:
        return now.year - birthdate.year + 1

    def calculate_saju(self, year: int, month: int, day: int, hour: int, minute: int = 0, is_male: bool = True, is_leap_month: bool = False) -> SajuChart:
        birth_datetime = datetime(year, month, day, hour, minute) - timedelta(minutes=32, seconds=1)
        base_date = datetime(1900, 1, 1)
        days_diff = (birth_datetime.date() - base_date.date()).days
        now = datetime.now()
        age = self._calculate_international_age(birth_datetime, now)
        korean_age = self._calculate_korean_age(birth_datetime, now)
        year_pillar = self._calculate_year_pillar(year)
        month_pillar = self._calculate_month_pillar_improved(year, month, day, is_leap_month)
        day_pillar = self._calculate_day_pillar(days_diff)
        hour_pillar = self._calculate_hour_pillar_improved(day_pillar.heavenly_stem, hour, minute)
        birth_info = {
            "year": year, "month": month, "day": day, 
            "hour": hour, "minute": minute,
            "is_male": is_male,
            "birth_datetime": birth_datetime,
            "is_leap_month": is_leap_month
        }
        return SajuChart(
            year_pillar, month_pillar, day_pillar, hour_pillar, 
            birth_info,
            age=age,
            korean_age=korean_age,
            current_datetime=now.strftime("%Y-%m-%d %H:%M:%S"),
            is_leap_month=is_leap_month
        )

    def _calculate_year_pillar(self, year: int) -> SajuPillar:
        base_year = 1984
        year_diff = year - base_year
        stem_index = year_diff % 10
        branch_index = year_diff % 12
        return SajuPillar(self.heavenly_stems[stem_index], self.earthly_branches[branch_index])

    def _calculate_month_pillar_improved(self, year: int, month: int, day: int, is_leap_month: bool = False) -> SajuPillar:
        month_branch_index = self._get_month_branch_by_solar_terms(year, month, day, is_leap_month)    
        year_stem_index = (year - 1984) % 10
        month_stem_base_table = [2, 4, 6, 8, 0, 2, 4, 6, 8, 0]
        month_stem_base = month_stem_base_table[year_stem_index]
        month_stem_index = (month_stem_base + ((month_branch_index + 12 - 2) % 12)) % 10
        month_stem = self.heavenly_stems[month_stem_index]
        return SajuPillar(month_stem, self.earthly_branches[month_branch_index])

    def _get_month_branch_by_solar_terms(self, year: int, month: int, day: int, is_leap_month: bool = False) -> int:
        if is_leap_month:
            month += 1
            if month > 12:
                month = 1
                year += 1
        solar_terms = [
            (2, 4, 2), (3, 6, 3), (4, 5, 4), (5, 6, 5), (6, 6, 6), (7, 7, 7),
            (8, 8, 8), (9, 8, 9), (10, 8, 10), (11, 7, 11), (12, 7, 0), (1, 6, 1),
        ]
        m, d = month, day
        for i in range(len(solar_terms)):
            sm, sd, idx = solar_terms[i]
            if (m, d) < (sm, sd):
                return solar_terms[i-1][2] if i > 0 else solar_terms[-1][2]
        return solar_terms[-2][2]

    def _calculate_day_pillar(self, days_diff: int) -> SajuPillar:
        base_stem = (self.DAY_PILLAR_BASE_STEM - self.DAY_PILLAR_BASE_DAYS) % 10
        base_branch = (self.DAY_PILLAR_BASE_BRANCH - self.DAY_PILLAR_BASE_DAYS) % 12
        stem_index = (base_stem + days_diff) % 10
        branch_index = (base_branch + days_diff) % 12
        return SajuPillar(self.heavenly_stems[stem_index], self.earthly_branches[branch_index])

    def _calculate_hour_pillar_improved(self, day_stem: str, hour: int, minute: int = 0) -> SajuPillar:
        hour_branches = ["자", "축", "인", "묘", "진", "사", "오", "미", "신", "유", "술", "해"]
        total_minutes = hour * 60 + minute - 32
        if total_minutes >= 23 * 60 or total_minutes < 1 * 60: branch_idx = 0
        elif total_minutes < 3 * 60: branch_idx = 1
        elif total_minutes < 5 * 60: branch_idx = 2
        elif total_minutes < 7 * 60: branch_idx = 3
        elif total_minutes < 9 * 60: branch_idx = 4
        elif total_minutes < 11 * 60: branch_idx = 5
        elif total_minutes < 13 * 60: branch_idx = 6
        elif total_minutes < 15 * 60: branch_idx = 7
        elif total_minutes < 17 * 60: branch_idx = 8
        elif total_minutes < 19 * 60: branch_idx = 9
        elif total_minutes < 21 * 60: branch_idx = 10
        else: branch_idx = 11
        hour_branch = hour_branches[branch_idx]
        day_stem_idx = self.heavenly_stems.index(day_stem)
        if day_stem_idx in [0, 5]: hour_stem_base = 0
        elif day_stem_idx in [1, 6]: hour_stem_base = 2
        elif day_stem_idx in [2, 7]: hour_stem_base = 4
        elif day_stem_idx in [3, 8]: hour_stem_base = 6
        else: hour_stem_base = 8
        hour_stem_idx = (hour_stem_base + branch_idx) % 10
        return SajuPillar(self.heavenly_stems[hour_stem_idx], hour_branch)

    def analyze_ten_gods(self, saju_chart: SajuChart) -> Dict[str, List[str]]:
        day_master = saju_chart.get_day_master()
        day_master_element = self.five_elements[day_master]
        ten_gods = {"년주": [], "월주": [], "일주": [], "시주": []}
        pillars = [
            ("년주", saju_chart.year_pillar),
            ("월주", saju_chart.month_pillar), 
            ("일주", saju_chart.day_pillar),
            ("시주", saju_chart.hour_pillar)
        ]
        for pillar_name, pillar in pillars:
            stem_element = self.five_elements[pillar.heavenly_stem]
            if pillar.heavenly_stem != day_master:
                god_types = self.ten_gods_mapping[day_master_element][stem_element]
                stem_idx = self.heavenly_stems.index(pillar.heavenly_stem)
                day_idx = self.heavenly_stems.index(day_master)
                if (stem_idx % 2) == (day_idx % 2):
                    ten_gods[pillar_name].append(f"천간:{god_types[0]}")
                else:
                    ten_gods[pillar_name].append(f"천간:{god_types[1]}")
            hidden_stems = self.hidden_stems[pillar.earthly_branch]
            for hidden_stem, strength in hidden_stems:
                if hidden_stem != day_master:
                    hidden_element = self.five_elements[hidden_stem]
                    god_types = self.ten_gods_mapping[day_master_element][hidden_element]
                    hidden_idx = self.heavenly_stems.index(hidden_stem)
                    day_idx = self.heavenly_stems.index(day_master)
                    if (hidden_idx % 2) == (day_idx % 2):
                        ten_gods[pillar_name].append(f"지지:{god_types[0]}({strength}%)")
                    else:
                        ten_gods[pillar_name].append(f"지지:{god_types[1]}({strength}%)")
        return ten_gods

    def calculate_great_fortune_improved(self, saju_chart: SajuChart) -> List[Dict]:
        birth_info = saju_chart.birth_info
        year = birth_info["year"]
        month = birth_info["month"]
        day = birth_info["day"]
        is_male = birth_info["is_male"]
        year_stem = saju_chart.year_pillar.heavenly_stem
        year_stem_idx = self.heavenly_stems.index(year_stem)
        is_yang_year = (year_stem_idx % 2 == 0)
        if (is_yang_year and is_male) or (not is_yang_year and not is_male):
            direction = 1
        else:
            direction = -1
        start_age = self._calculate_precise_start_age(year, month, day, direction)
        month_stem_idx = self.heavenly_stems.index(saju_chart.month_pillar.heavenly_stem)
        month_branch_idx = self.earthly_branches.index(saju_chart.month_pillar.earthly_branch)
        great_fortunes = []
        for i in range(8):
            age = start_age + (i * 10)
            stem_idx = (month_stem_idx + (direction * (i + 1))) % 10
            branch_idx = (month_branch_idx + (direction * (i + 1))) % 12
            great_fortunes.append({
                "age": age,
                "pillar": f"{self.heavenly_stems[stem_idx]}{self.earthly_branches[branch_idx]}",
                "years": f"{year + age}년 ~ {year + age + 9}년"
            })
        return great_fortunes

    def _calculate_precise_start_age(self, year: int, month: int, day: int, direction: int) -> int:
        base_age = 6
        if day > 15:
            adjustment = 1 if direction == 1 else -1
        else:
            adjustment = 0
        return max(1, base_age + adjustment)

    def get_element_strength(self, saju_chart: SajuChart) -> Dict[str, int]:
        elements = {"목": 0, "화": 0, "토": 0, "금": 0, "수": 0}
        pillars = [
            saju_chart.year_pillar.heavenly_stem, saju_chart.year_pillar.earthly_branch,
            saju_chart.month_pillar.heavenly_stem, saju_chart.month_pillar.earthly_branch,
            saju_chart.day_pillar.heavenly_stem, saju_chart.day_pillar.earthly_branch,
            saju_chart.hour_pillar.heavenly_stem, saju_chart.hour_pillar.earthly_branch,
        ]
        wuxing_map = {
            '목': ['갑', '을', '인', '묘'],
            '화': ['병', '정', '사', '오'],
            '토': ['무', '기', '진', '술', '축', '미'],
            '금': ['경', '신', '신', '유'],
            '수': ['임', '계', '자', '해'],
        }
        char2wuxing = {}
        for k, v in wuxing_map.items():
            for ch in v:
                char2wuxing[ch] = k
        for ch in pillars:
            element = char2wuxing.get(ch)
            if element:
                elements[element] += 1
            else:
                raise ValueError(f"오행 매핑표에 없는 글자: {ch}")
        return elements

def format_saju_analysis(saju_chart: SajuChart, calculator: SajuCalculator) -> str:
    analysis = []
    analysis.append("=== 사주팔자 ===")
    analysis.append(f"년주(年柱): {saju_chart.year_pillar}")
    analysis.append(f"월주(月柱): {saju_chart.month_pillar}")
    analysis.append(f"일주(日柱): {saju_chart.day_pillar}")
    analysis.append(f"시주(時柱): {saju_chart.hour_pillar}")
    analysis.append(f"일간(日干): {saju_chart.get_day_master()}")
    analysis.append(f"현재 나이: {saju_chart.age}세 / 한국식 나이: {saju_chart.korean_age}세")
    analysis.append(f"기준 시점: {saju_chart.current_datetime}")
    if saju_chart.is_leap_month:
        analysis.append("⚠️ 윤달 출생자입니다 (월간 계산이 조정되었습니다)")
    analysis.append("")
    elements = calculator.get_element_strength(saju_chart)
    analysis.append("=== 오행 강약 (8점 만점) ===")
    for element, strength in elements.items():
        analysis.append(f"{element}: {strength}점")
    analysis.append("")
    ten_gods = calculator.analyze_ten_gods(saju_chart)
    analysis.append("=== 십신 분석 ===")
    for pillar_name, gods in ten_gods.items():
        if gods:
            analysis.append(f"{pillar_name}: {', '.join(gods)}")
    analysis.append("")
    great_fortunes = calculator.calculate_great_fortune_improved(saju_chart)
    analysis.append("=== 대운 (정밀 계산) ===")
    for gf in great_fortunes[:4]:
        analysis.append(f"{gf['age']}세: {gf['pillar']} ({gf['years']})")
    return "\n".join(analysis)

def parse_input(text: str) -> Dict:
    numbers = [int(n) for n in re.findall(r'\d+', text)]
    is_male = not ("여" in text or "여자" in text)
    is_leap_month = "윤" in text or "윤달" in text or "윤월" in text
    try:
        params = {
            "year": numbers[0],
            "month": numbers[1],
            "day": numbers[2],
            "hour": numbers[3] if len(numbers) > 3 else 0,
            "minute": numbers[4] if len(numbers) > 4 else 0,
            "is_male": is_male,
            "is_leap_month": is_leap_month,
        }
        if ("오후" in text or "pm" in text.lower()) and params["hour"] <= 12:
            params["hour"] += 12
            if params["hour"] == 24:
                params["hour"] = 12
        if ("오전" in text or "am" in text.lower()) and params["hour"] == 12:
            params["hour"] = 0
        return params
    except IndexError:
        return None

# 사주 계산기 인스턴스
saju_calculator = SajuCalculator()

# --- LangChain 도구 정의 ---
class CalculateSajuInput(BaseModel):
    year: int = Field(description="출생년도 (1900-2100)")
    month: int = Field(description="출생월 (1-12)")
    day: int = Field(description="출생일 (1-31)")
    hour: int = Field(default=0, description="출생시간 (0-23, 기본값: 0)")
    minute: int = Field(default=0, description="출생분 (0-59, 기본값: 0)")
    is_male: bool = Field(default=True, description="성별 (True: 남자, False: 여자)")
    is_leap_month: bool = Field(default=False, description="윤달 출생 여부")

async def calculate_saju_tool(
    year: int,
    month: int,
    day: int,
    hour: int = 0,
    minute: int = 0,
    is_male: bool = True,
    is_leap_month: bool = False
) -> str:
    """생년월일시와 성별을 입력받아 사주팔자를 계산하고 분석합니다."""
    try:
        if not (1900 <= year <= 2100):
            return "오류: 출생년도는 1900-2100년 사이여야 합니다."
        if not (1 <= month <= 12):
            return "오류: 출생월은 1-12 사이여야 합니다."
        if not (1 <= day <= 31):
            return "오류: 출생일은 1-31 사이여야 합니다."
        if not (0 <= hour <= 23):
            return "오류: 출생시간은 0-23 사이여야 합니다."
        if not (0 <= minute <= 59):
            return "오류: 출생분은 0-59 사이여야 합니다."
        
        chart = saju_calculator.calculate_saju(
            year=year,
            month=month,
            day=day,
            hour=hour,
            minute=minute,
            is_male=is_male,
            is_leap_month=is_leap_month
        )
        
        return format_saju_analysis(chart, saju_calculator)
        
    except Exception as e:
        return f"사주 계산 중 오류가 발생했습니다: {str(e)}"

class ParseSajuInputInput(BaseModel):
    text: str = Field(description="자연어로 입력된 생년월일시 정보 (예: '1995년 8월 26일 오후 3시 30분 남자')")

async def parse_saju_input_tool(text: str) -> str:
    """자연어로 입력된 생년월일시 정보를 파싱합니다."""
    try:
        if not text:
            return "오류: 파싱할 텍스트가 입력되지 않았습니다."
        
        parsed = parse_input(text)
        if parsed is None:
            return "오류: 입력 형식을 확인해 주세요. '년, 월, 일' 정보가 필요합니다.\n예: 1995년 3월 28일 12시 30분 남자\n윤달: 1995년 윤8월 28일 12시 30분 남자"
        
        import json
        result = json.dumps(parsed, ensure_ascii=False, indent=2)
        return f"파싱 결과:\n{result}"
        
    except Exception as e:
        return f"자연어 파싱 중 오류가 발생했습니다: {str(e)}"

# LangChain 도구 생성
calculate_saju_langchain_tool = StructuredTool.from_function(
    func=calculate_saju_tool,
    name="calculate_saju",
    description="생년월일시와 성별을 입력받아 사주팔자를 계산하고 분석합니다.",
    args_schema=CalculateSajuInput,
)

parse_saju_input_langchain_tool = StructuredTool.from_function(
    func=parse_saju_input_tool,
    name="parse_saju_input",
    description="자연어로 입력된 생년월일시 정보를 파싱합니다.",
    args_schema=ParseSajuInputInput,
)

# --- LangGraph Agent 생성 ---
async def create_saju_agent() -> CompiledStateGraph:
    """사주 분석 에이전트를 생성합니다."""
    model = init_chat_model(
        model="openai:gpt-4o",
        temperature=0.1,
        api_key=os.getenv("OPENAI_API_KEY"),
    )
    
    tools = [calculate_saju_langchain_tool, parse_saju_input_langchain_tool]
    
    agent = create_react_agent(
        model=model,
        tools=tools,
        prompt="""
        당신은 사주(四柱) 분석 전문가입니다.
        사용자의 생년월일시 정보를 받아 사주팔자를 계산하고 분석해주세요.
        
        사용 가능한 도구:
        - calculate_saju: 생년월일시와 성별을 입력받아 사주팔자를 계산하고 분석합니다.
        - parse_saju_input: 자연어로 입력된 생년월일시 정보를 파싱합니다.
        
        사용자가 자연어로 생년월일시를 입력하면, 먼저 parse_saju_input으로 파싱한 후,
        calculate_saju로 사주를 계산해주세요.
        """,
    )
    
    return agent

# --- LangGraph를 A2A로 래핑하는 Executor (리팩터링 버전) ---
class LangGraphA2AExecutor(AgentExecutor):
    """LangGraph Agent를 A2A AgentExecutor로 래핑"""

    def __init__(self, graph: CompiledStateGraph):
        self.graph = graph
        # task.id 기준으로 실행 중인 asyncio.Task 관리
        self._running_tasks: Dict[str, asyncio.Task] = {}

    async def _run_graph(
        self,
        task,
        updater: TaskUpdater,
        query: str,
    ) -> None:
        """LangGraph astream을 돌면서 A2A 이벤트로 스트리밍 전송"""
        config = {"configurable": {"thread_id": str(task.id)}}
        messages = [HumanMessage(content=query)] if query else []

        last_text = ""

        try:
            async for chunk in self.graph.astream({"messages": messages}, config=config):
                if isinstance(chunk, dict) and "messages" in chunk:
                    for msg in chunk["messages"]:
                        if isinstance(msg, AIMessage) and isinstance(msg.content, str):
                            new_text = msg.content
                            if not new_text:
                                continue

                            # 전체 누적 텍스트 기준으로 delta 계산 (안전하게)
                            if new_text == last_text:
                                continue

                            if new_text.startswith(last_text):
                                delta = new_text[len(last_text):]
                            else:
                                # 혹시라도 전체가 다시 써지는 경우엔 전체를 한 번 더 보냄
                                delta = new_text

                            last_text = new_text

                            if delta:
                                await updater.update_status(
                                    TaskState.working,
                                    new_agent_text_message(delta, task.context_id, task.id),
                                )

            # 최종 결과 artifact 저장 + complete
            if last_text:
                await updater.add_artifact([
                    Part(root=TextPart(text=last_text))
                ])
            await updater.complete()

        except asyncio.CancelledError:
            # cancel() 쪽에서 상태 업데이트를 책임지고 있으므로 여기서는 조용히 패스
            raise

    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        query = context.get_user_input()

        # Task 확보 (가능하면 DefaultRequestHandler가 만든 current_task 사용)
        task = context.current_task
        if not task:
            task = new_task(context.message)
            await event_queue.enqueue_event(task)

        updater = TaskUpdater(event_queue, task.id, task.context_id)

        await updater.update_status(TaskState.submitted)

        try:
            await updater.start_work()

            # LangGraph 실행을 별도 Task로 관리 (cancel 지원)
            run_task = asyncio.create_task(
                self._run_graph(task, updater, query)
            )
            self._running_tasks[task.id] = run_task

            try:
                await run_task
            except asyncio.CancelledError:
                # cancel() 에서 이미 failed 상태로 바꿨다고 가정
                raise

        except asyncio.CancelledError:
            # 사용자 취소인 경우 별도 처리 필요 없으면 그냥 종료
            pass

        except Exception as e:
            error_msg = f"실행 중 오류 발생: {str(e)}"
            await updater.failed(
                message=new_agent_text_message(error_msg, task.context_id, task.id)
            )
            raise ServerError() from e

        finally:
            # 실행 끝난 Task 정리
            self._running_tasks.pop(task.id, None)

    async def cancel(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        """실행 중인 LangGraph Task 취소"""
        task = context.current_task
        if not task:
            return

        run_task = self._running_tasks.get(task.id)
        if run_task and not run_task.done():
            run_task.cancel()

        updater = TaskUpdater(event_queue, task.id, task.context_id)
        # A2A에 canceled 상태가 따로 없다면 failed로 처리
        await updater.failed(
            message=new_agent_text_message(
                "요청이 취소되었습니다.",
                task.context_id,
                task.id,
            )
        )

# --- A2A 서버 실행 ---
def main():
    """A2A 서버를 시작합니다."""

    async def setup_and_run():
        print("🚀 사주 분석 A2A 서버 시작 중...")

        # LangGraph Agent 생성
        graph = await create_saju_agent()

        # Agent Card 생성
        skills = [
            AgentSkill(
                id="saju_analysis",
                name="사주 분석",
                description="생년월일시를 기반으로 사주팔자를 계산하고 분석합니다",
                tags=["사주", "명리학", "운세"],
                examples=["1995년 8월 26일 오후 3시 30분 남자 사주를 봐주세요"],
            )
        ]

        host = "0.0.0.0"
        port = 8106

        agent_card = AgentCard(
            name="사주 분석 에이전트",
            description="생년월일시를 기반으로 사주팔자를 계산하고 분석하는 A2A 에이전트",
            url=f"http://{host}:{port}",
            version="1.0.0",
            default_input_modes=["text/plain", "application/json"],
            default_output_modes=["text/plain", "application/json"],
            capabilities=AgentCapabilities(
                streaming=True,
                push_notifications=False,
            ),
            skills=skills,
        )

        # A2A 서버 구성
        http_client = httpx.AsyncClient()
        push_config_store = InMemoryPushNotificationConfigStore()
        push_sender = BasePushNotificationSender(
            httpx_client=http_client,
            config_store=push_config_store
        )

        request_handler = DefaultRequestHandler(
            agent_executor=LangGraphA2AExecutor(graph=graph),
            task_store=InMemoryTaskStore(),
            push_config_store=push_config_store,
            push_sender=push_sender,
        )

        server = A2AStarletteApplication(
            agent_card=agent_card,
            http_handler=request_handler
        )

        app = server.build()

        # httpx 클라이언트 정리용 shutdown 훅
        @app.on_event("shutdown")
        async def _shutdown_http_client():
            await http_client.aclose()

        # Health check 추가
        from starlette.routing import Route
        from starlette.responses import JSONResponse

        async def health_check(request):
            return JSONResponse({"status": "healthy", "agent": agent_card.name})

        app.router.routes.append(Route("/health", health_check, methods=["GET"]))

        print(f"✅ A2A 서버 시작 완료: http://{host}:{port}")
        print(f"📋 Agent Card: http://{host}:{port}/.well-known/agent-card.json")
        print(f"🏥 Health Check: http://{host}:{port}/health")
        print("\n서버가 실행 중입니다. 종료하려면 Ctrl+C를 누르세요.")

        # uvicorn 실행
        config = uvicorn.Config(app, host=host, port=port, log_level="info")
        server_instance = uvicorn.Server(config)
        await server_instance.serve()

    asyncio.run(setup_and_run())

if __name__ == "__main__":
    from dotenv import load_dotenv

    # .env 파일 로드
    load_dotenv()

    main()
