지금 보면 랜딩부분에에 langdering_url 입력하는것도 두개라서 하나로 줄여야 할거같아. 
RAG 자료 업로드
문서 업로드 후 자동 인덱싱되어 카피 생성 시 근거로 활용됩니다. 
이부분도 자료 업로드로 바꾸고,
대화 입력은 오른쪽 Generation 영역에서 진행됩니다. objective/channel/language는 프롬프트 문맥으로 자동 추론됩니다.
PromptSection.vue
스타일만 고르고, 나머지는 대화형 브리프로 처리합니다.
[Pasted ~3 lines] 
GenerationSection.vue
대화형 흐름과 생성 결과를 함께 보여줍니다.PRD 구조대로 `.vue` 파일 기반으로 구성한 랜딩/대화형 생성 화면입니다.
LangChain/LangGraph는 백엔드에서 실행되고, 이 화면은 API 결과를 대화형으로 확인하는 프론트입니다. 
이부분도 다 제거해야 할거같아.
왜냐하면 실무에 쓰일거를 생각하면 이런건 없는데 맞는거같아.

파일 업로드 실패가. 자료업로드 밑에도 출력이 되었으면 좋겠어
자료 업로드 완료 (일부 실패)
업로드: 성공 0/1, 실패 1
실패 파일: 2026년 2월 10일 10시 회의 _ connect ai란.docx(DOC_CONVERSION_FAILED)
인덱싱: 성공 문서가 없어 건너뜀
문구가 나와


----

이미지 pdf가 rag가 안돼.

----
0.1에서는 프론트적으로 변경
0.2에서는 버전관리 및, 백엔드 랭그래프 구현 변경
0.3에서는 완전한 랭그래프 형식으로 변경, docling붙여달라고 했으며, 추가적인 버전관리 요구

----
- 이미지(.png/.jpg/.jpeg/.webp) 처리: DocumentConverter 기본 파이프라인 사용
  - 현재 런타임 로그 기준으로 *RapidOCR(ONNX)*가 동작
  - 실제 로드 모델:
    - ch_PP-OCRv4_det_infer.onnx (텍스트 영역 검출)
    - ch_ppocr_mobile_v2.0_cls_infer.onnx (각도/방향 분류)
    - ch_PP-OCRv4_rec_infer.onnx (문자 인식)
- PDF 처리: 기본 변환 + PDF 전용 OCR 변환을 비교해서 더 나은 텍스트 채택
  - PDF 전용 OCR은 EasyOCR(ko,en) 우선, 없으면 RapidOCR fallback
  - EasyOCR 모델 캐시:
    - craft_mlt_25k.pth
    - korean_g2.pth
    - latin_g2.pth

- 이미지 변환 경로: app/integrations/docling_client.py:13  
  - DocumentConverter() 기본 컨버터(self._converter) 사용
- EasyOCR 설정은 현재 PDF 전용 OCR 컨버터에만 붙어 있음: app/integrations/docling_client.py:73
- 실제 로드되는 이미지 OCR 모델(로그/파일 기준):
  - ch_PP-OCRv4_det_infer.onnx (검출)
  - ch_ppocr_mobile_v2.0_cls_infer.onnx (방향 분류)
  - ch_PP-OCRv4_rec_infer.onnx (인식)
즉, 현재 이미지 OCR 모델은 RapidOCR + PP-OCRv4 ONNX 모델이라고 보면 됩니다. 

---------------
EasyOCR을 고정해서 사용하는게 좋다면, 더 좋다면 그렇게 바꿔줘.
------------------
지금 이미지처리에서 easy_ocr을 하니까, 시간이 오래걸려서 타임아웃이 발생해

----
@requirements.txt 를 보면 docling이 없는데 파싱을 위해서는 이게 있어야 하는거 아냐? 버전관리가 추가로 필요할 거같아.

---------------------
결국에는 jpg, png파일도 내가 처리해야하는데,  small-docling 256m vision model을 사용할 수는 없는거야? GPU를 사용하는것을 당연하게 생각하고 있어.

--------------------------
처리 하는데 시간이 좀 오래걸리는거 같아. 처리중... 옆에 동그랗게 돌아가는 표시 넣어주면 좋을 거 같아

----------------------------
대화형 로그는 토글형식으로 접었다 폈다해줘
----------------------------

생성에 있어서 메일 начис흡맞 등 추 속의 0.8% 클릭 열쇠 이렇게 말도 안되는 결과가 가끔 나오기도 해

이미지 올렸을때, 이미지 인식이 안되는거 같음
(음 일단 png파일을 읽었을때 source파일에 png파일이 없음)
그리고 문제는, sources에 이전에 선택한 파일들이 계속 들어감. 제너레이션 초기화혀먼서 이게 다 없어져야 하는거 아닌가..? 하는 생각