import streamlit as st
import google.generativeai as genai
from PIL import Image
import json
import re

# 페이지 설정
st.set_page_config(
    page_title="🎬 릴스 썸네일 마스터",
    page_icon="🎬",
    layout="wide"
)

# 세션 상태 초기화
if "analysis_results" not in st.session_state:
    st.session_state.analysis_results = []
if "title_results" not in st.session_state:
    st.session_state.title_results = None

# JSON 안전 추출 함수
def extract_json_safely(text):
    try:
        json_match = re.search(r"```json\s*(.*?)\s*```", text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group(1))
        code_match = re.search(r"```\s*(.*?)\s*```", text, re.DOTALL)
        if code_match:
            return json.loads(code_match.group(1))
        return json.loads(text)
    except json.JSONDecodeError:
        return {
            "오류": "파싱 실패",
            "원문": text[:200] + "..." if len(text) > 200 else text
        }

# 사이드바 - API 설정
with st.sidebar:
    st.title("⚙️ 설정")
    st.markdown("---")
    
    api_key = st.text_input(
        "🔑 Gemini API 키 입력",
        type="password",
        placeholder="AIzaSy...",
        help="aistudio.google.com에서 무료 발급"
    )
    
    model = None
    
    if api_key:
        try:
            genai.configure(api_key=api_key.strip())
            model = genai.GenerativeModel("gemini-1.5-flash")
            test_response = model.generate_content("테스트")
            st.success("✅ API 연결 성공!")
        except Exception as e:
            st.error(f"❌ API 오류: {str(e)}")
            model = None
    else:
        st.info("👆 API 키를 입력하면 시작됩니다")
        st.markdown("**📌 무료 발급 방법**")
        st.markdown("1. aistudio.google.com 접속")
        st.markdown("2. Get API Key 클릭")
        st.markdown("3. Create API Key 클릭")
        st.markdown("4. 생성된 키 복사 후 위에 입력")
    
    st.markdown("---")
    st.markdown("**📊 무료 사용량**")
    st.markdown("- 썸네일 분석: 1,500개/일")
    st.markdown("- 제목 생성: 무제한")
    st.markdown("- 총 비용: **완전 무료** 🎉")

# 메인 화면
st.title("🎬 릴스 썸네일 마스터")
st.markdown("**설득 심리학 기반 썸네일 분석 & 혁신 제목 생성 툴**")
st.markdown("---")

tab1, tab2 = st.tabs(["📊 썸네일 분석 + 혁신 제목", "✍️ 새 릴스 제목 생성"])

# 탭 1: 썸네일 분석
with tab1:
    st.header("📊 썸네일 분석 + 혁신 제목 생성")
    st.markdown("썸네일 이미지를 업로드하면 **설득 심리학 분석 + 혁신 제목 3개**를 자동으로 생성합니다")
    
    if not model:
        st.warning("⬅️ 왼쪽 사이드바에 API 키를 먼저 입력해주세요!")
    else:
        uploaded_files = st.file_uploader(
            "📁 썸네일 이미지 업로드 (여러 장 동시 가능, 캡처 이미지도 가능)",
            type=["png", "jpg", "jpeg", "webp"],
            accept_multiple_files=True
        )
        
        if uploaded_files:
            st.info(f"📁 {len(uploaded_files)}개 파일 업로드 완료")
            
            if st.button("🚀 분석 + 혁신 제목 생성 시작!", type="primary", key="analyze_btn"):
                st.session_state.analysis_results = []
                
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                generation_config = genai.GenerationConfig(
                    response_mime_type="application/json"
                )
                
                for idx, file in enumerate(uploaded_files):
                    status_text.markdown(f"⏳ **분석 중... {idx+1}/{len(uploaded_files)}**: `{file.name}`")
                    
                    try:
                        image = Image.open(file).convert("RGB")
                        
                        prompt = """
당신은 인스타그램 마케팅 전문가이자 소비자 심리학 박사입니다.
이 썸네일을 로버트 치알디니의 설득의 심리학 8원칙과 최신 신경과학을 기반으로 분석하고,
기존 제목보다 훨씬 강력한 혁신적 썸네일 제목 3개를 생성해주세요.

[혁신 제목 필수 조건]
- "이거 위험해요", "저만 몰랐나요", "꼭 보세요", "꿀팁" 같은 진부한 표현 절대 금지
- 뇌가 "이건 뭔가 다르다"고 느끼는 예상 파괴형으로 작성
- 10글자 이내로 간결하게 작성
- 인지부조화, 자이가르닉효과, 극도의구체성 기법을 각각 적용

반드시 아래 JSON 스키마 형식으로만 응답하세요:

{
  "썸네일_텍스트": "이미지에서 보이는 텍스트 (없으면 없음)",
  "콘텐츠_유형": "육아/음식/제품판매/일상/정보 중 하나",
  "설득_원칙": ["적용된 원칙1", "원칙2"],
  "클릭_점수": 8,
  "강점": "가장 강력한 요소 한 문장",
  "약점": "가장 약한 요소 한 문장",
  "혁신_제목": [
    {
      "제목": "혁신 제목 1",
      "기법": "인지부조화",
      "심리_원리": "클릭 유도 심리 메커니즘 설명"
    },
    {
      "제목": "혁신 제목 2",
      "기법": "자이가르닉효과",
      "심리_원리": "클릭 유도 심리 메커니즘 설명"
    },
    {
      "제목": "혁신 제목 3",
      "기법": "극도의구체성",
      "심리_원리": "클릭 유도 심리 메커니즘 설명"
    }
  ],
  "최우선_추천": "혁신 제목 3개 중 가장 강력한 제목 그대로 복사"
}
"""
                        
                        response = model.generate_content(
                            [prompt, image],
                            generation_config=generation_config
                        )
                        
                        if hasattr(response, 'text') and response.text:
                            result = json.loads(response.text)
                        else:
                            result = extract_json_safely(str(response))
                        
                        result["파일명"] = file.name
                        result["이미지"] = image
                        st.session_state.analysis_results.append(result)
                        
                    except Exception as e:
                        st.error(f"❌ {file.name} 분석 오류: {str(e)} - 다음 파일로 진행합니다")
                    
                    progress_bar.progress((idx + 1) / len(uploaded_files))
                
                status_text.markdown("✅ **모든 분석 완료!**")

    # 결과 표시
    if st.session_state.analysis_results:
        results = st.session_state.analysis_results
        st.markdown("---")
        st.header("📊 분석 결과")
        
        # 요약 지표
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("총 분석 완료", f"{len(results)}개")
        with col2:
            scores = [r.get("클릭_점수", 5) for r in results if isinstance(r.get("클릭_점수"), (int, float))]
            avg = sum(scores) / len(scores) if scores else 0
            st.metric("평균 클릭 점수", f"{avg:.1f}/10")
        with col3:
            high = len([r for r in results if isinstance(r.get("클릭_점수"), (int, float)) and r.get("클릭_점수", 0) >= 8])
            st.metric("고득점 썸네일", f"{high}개")
        with col4:
            types = [r.get("콘텐츠_유형", "") for r in results if r.get("콘텐츠_유형")]
            most_type = max(set(types), key=types.count) if types else "-"
            st.metric("주요 콘텐츠 유형", most_type)
        
        st.markdown("---")
        
        # 개별 결과 표시
        for i, result in enumerate(results):
            if "오류" in result:
                with st.expander(f"❌ [{i+1}] {result.get('파일명', '')} - 분석 실패"):
                    st.error("분석 중 오류가 발생했습니다.")
                continue
            
            score = result.get("클릭_점수", 0)
            score_emoji = "🔥" if score >= 8 else "✅" if score >= 6 else "⚠️"
            
            with st.expander(
                f"{score_emoji} [{i+1}] {result.get('파일명', '')} | "
                f"클릭 점수: {score}/10 | "
                f"유형: {result.get('콘텐츠_유형', '')}"
            ):
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    if "이미지" in result:
                        st.image(result["이미지"], use_container_width=True)
                
                with col2:
                    st.markdown(f"**📝 썸네일 텍스트**: `{result.get('썸네일_텍스트', '없음')}`")
                    st.markdown(f"**🎯 설득 원칙**: {', '.join(result.get('설득_원칙', []))}")
                    st.success(f"💪 **강점**: {result.get('강점', '')}")
                    st.warning(f"⚠️ **약점**: {result.get('약점', '')}")
                
                st.markdown("### 🚀 혁신 썸네일 제목 3가지")
                
                best_title = result.get("최우선_추천", "")
                
                for j, title_info in enumerate(result.get("혁신_제목", []), 1):
                    title = title_info.get("제목", "")
                    is_best = title == best_title
                    
                    if is_best:
                        st.success(f"⭐ **추천 1순위: [{title}]**")
                    else:
                        st.info(f"📌 **{j}순위: [{title}]**")
                    
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.markdown(f"- **적용 기법**: `{title_info.get('기법', '')}`")
                    with col_b:
                        st.markdown(f"- **심리 원리**: {title_info.get('심리_원리', '')}")
                    
                    if j < len(result.get("혁신_제목", [])):
                        st.markdown("---")

# 탭 2: 새 릴스 제목 생성
with tab2:
    st.header("✍️ 새 릴스 혁신 제목 생성기")
    st.markdown("릴스 내용을 간략히 입력하면 **조회수를 폭발시키는 혁신 제목 3개**를 만들어드립니다")
    
    if not model:
        st.warning("⬅️ 왼쪽 사이드바에 API 키를 먼저 입력해주세요!")
    else:
        col1, col2 = st.columns(2)
        
        with col1:
            story = st.text_area(
                "📝 릴스 내용/스토리 입력",
                placeholder="예: 인스타그램 팔로워 0명에서 3개월만에 1만명 달성한 실제 경험담",
                height=150
            )
        
        with col2:
            target = st.selectbox(
                "🎯 타겟 오디언스",
                [
                    "인스타그램 초보자 (팔로워 1천명 이하)",
                    "소상공인/사장님",
                    "직장인 부업러",
                    "20-30대 여성",
                    "육아맘",
                    "콘텐츠 크리에이터"
                ]
            )
            
            st.markdown("**💡 입력 예시**")
            st.markdown("- 팔로워 늘리는 방법 공유")
            st.markdown("- 제품 솔직 후기")
            st.markdown("- 일상 브이로그")
        
        if st.button("🎯 혁신 제목 생성!", type="primary", key="title_btn"):
            if not story.strip():
                st.warning("📝 릴스 내용을 입력해주세요!")
            else:
                with st.spinner("최고의 제목을 만들고 있습니다... ⏳"):
                    try:
                        generation_config = genai.GenerationConfig(
                            response_mime_type="application/json"
                        )
                        
                        prompt = f"""
당신은 수천만 조회수 릴스를 만드는 최고의 카피라이터입니다.

[릴스 내용]: {story}
[타겟 오디언스]: {target}

[필수 조건]
- "꿀팁", "필수", "이거 위험해요", "저만 몰랐나요", "꼭 보세요" 절대 금지
- 뇌가 "이건 뭔가 다르다"고 느끼는 예상 파괴형으로 작성
- 10글자 이내로 간결하게
- 각각 다른 심리 기법 적용

반드시 아래 JSON 스키마로만 응답하세요:

{{
  "혁신_제목": [
    {{
      "제목": "제목1",
      "기법": "인지부조화",
      "클릭_이유": "이 제목이 클릭을 유도하는 핵심 심리 원리"
    }},
    {{
      "제목": "제목2",
      "기법": "자이가르닉효과",
      "클릭_이유": "이 제목이 클릭을 유도하는 핵심 심리 원리"
    }},
    {{
      "제목": "제목3",
      "기법": "극도의구체성",
      "클릭_이유": "이 제목이 클릭을 유도하는 핵심 심리 원리"
    }}
  ],
  "최우선_추천": "3개 중 가장 강력한 제목 그대로 복사"
}}
"""
                        
                        response = model.generate_content(
                            prompt,
                            generation_config=generation_config
                        )
                        
                        if hasattr(response, 'text') and response.text:
                            result = json.loads(response.text)
                        else:
                            result = extract_json_safely(str(response))
                        
                        st.session_state.title_results = result
                        
                    except Exception as e:
                        st.error(f"❌ 오류 발생: {str(e)} - 내용을 조금 수정해서 다시 시도해주세요")

    # 결과 표시
    if st.session_state.title_results:
        result = st.session_state.title_results
        
        if "오류" in result:
            st.error("제목 생성 중 오류가 발생했습니다.")
        else:
            st.markdown("---")
            st.header("🎯 생성된 혁신 제목")
            
            best_title = result.get("최우선_추천", "")
            if best_title:
                st.success(f"⭐ **최우선 추천: [{best_title}]**")
            st.markdown("---")
            
            for j, title_info in enumerate(result.get("혁신_제목", []), 1):
                title = title_info.get("제목", "")
                is_best = title == best_title
                
                if is_best:
                    st.success(f"⭐ **추천 1순위: [{title}]**")
                else:
                    st.info(f"📌 **{j}순위: [{title}]**")
                
                col_a, col_b = st.columns(2)
                with col_a:
                    st.markdown(f"- **심리 기법**: `{title_info.get('기법', '')}`")
                with col_b:
                    st.markdown(f"- **클릭 이유**: {title_info.get('클릭_이유', '')}")
                
                if j < len(result.get("혁신_제목", [])):
                    st.markdown("---")
