import os
import openai
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# ✅ 자동 주제 생성 함수
def generate_topics():
    prompt = '''
너는 'Hello Healthy' 유튜브 채널의 작가야.

다음 조건을 만족하는 **숏폼 건강 콘텐츠 주제**를 4개 만들어줘:

- 건강과 라이프스타일 중심 (예: 간, 췌장, 집중력, 염증, 피로, 순환 등)
- '질환'보단 '회복템', '부스팅', '컨디션 관리' 같은 단어 위주
- 40~60대를 은근히 겨냥하지만, 2030이 봐도 흥미로운 제목
- 짧고 직관적인 문장 / 핵심 키워드 포함 / 12~20자 이내
- 말투는 트렌디하고 시사형 or 팁형 느낌

예시:
- 점심 먹고 나면 바로 피곤한 이유
- 에너지 레벨이 다른 사람들의 비밀
- 간이 보내는 작은 신호, 무시하지 마세요
- 커큐민이 몸에 미치는 뜻밖의 변화

그런 주제 4개만 깔끔하게 리스트로 줘.
    '''
    res = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.8
    )
    lines = res['choices'][0]['message']['content'].strip().split("\n")
    return [line.strip("-•● ").strip() for line in lines if line.strip()]

# ✅ 논문 검색용 키워드 추출 함수
def get_search_query(topic):
    return f"{topic} site:ncbi.nlm.nih.gov"

# ✅ PubMed에서 논문 제목 & 초록 수집
def fetch_pubmed_abstract(query):
    headers = {"User-Agent": "Mozilla/5.0"}
    search_url = f"https://www.google.com/search?q={query}"
    try:
        res = requests.get(search_url, headers=headers)
        soup = BeautifulSoup(res.text, 'html.parser')
        for link in soup.select('a'):
            href = link.get('href')
            if href and 'ncbi.nlm.nih.gov' in href:
                real_url = href.split("&")[0].replace("/url?q=", "")
                page = requests.get(real_url, headers=headers)
                detail = BeautifulSoup(page.text, 'html.parser')
                title = detail.find('h1')
                abstract = detail.find('div', class_='abstract')
                if title and abstract:
                    return (title.get_text().strip(), abstract.get_text().strip())
    except Exception as e:
        return ("", "")
    return ("", "")

# ✅ GPT에게 헬로헬씨 스타일 대본 생성 요청
def generate_script(topic, paper_title):
    system_prompt = """
너는 'Hello Healthy'라는 유튜브 숏폼 채널의 콘텐츠 작가야.

이 채널은 겉으로는 전 연령을 위한 건강 정보를 다루지만, 실제 타깃은 40~60대야.  
단, 그 사실이 영상에 드러나면 안 돼. 시청자에게는 2030도 즐겨보는 ‘젊고 트렌디한 자기관리 콘텐츠’처럼 느껴져야 해.

---

🎯 채널 컨셉은 ‘중년 건강’이 아닌 **‘스마트한 자기관리’**다.

- “질병 치료”가 아니라 “컨디션 최적화”
- “갱년기 관리” 대신 “에너지 레벨 조절”
- “노화 방지” 대신 “퍼포먼스 부스팅”
- “영양제 추천” 대신 “몸 기능 치트키”

❌ ‘질환’, ‘증상’, ‘고지혈증’, ‘노화’, ‘갱년기’ 같은 말은 사용하지 마.  
✅ 대신 ‘회복템’, ‘부스팅’, ‘에너지 효율’, ‘컨디션 리셋’, ‘셀프 체크’, ‘몸의 사용설명서’ 같은 표현을 써줘.

---

📦 콘텐츠 전략은 다음과 같아:

1. **도입**: 일상에서 흔히 겪는 상태(피로, 집중력 저하, 붓기 등)를 문제처럼 제시  
2. **중반**: 논문 출처 기반으로 몸에서 벌어지는 메커니즘을 설명 (논문 제목만 괄호로 간단히 표기)  
3. **후반**: 음식, 습관, 운동 루틴 등을 팁처럼 정리해 보여줌  
4. **마무리**: ‘당신도 이 팁으로 몸이 달라질 수 있다’는 식의 조용한 암시로 끝냄

✳️ 포인트:  
– ‘정보 전달’이 아니라 ‘생산성 향상 팁’처럼 보여줘  
– 마치 스마트워치를 분석하듯, 몸의 신호를 기술처럼 다뤄  
– 모든 문장은 또박또박, 친절하지만 권위적이지 않게  
– 어투는 의사 선생님 말투 ❌, **스마트한 선배** 혹은 **건강 데이터 분석가** 느낌으로

---

🎨 영상의 분위기는 ‘따뜻함’보다 **깔끔하고 미니멀한 인포그래픽 스타일**이야.

- 흰색, 회색 배경에 포인트 컬러 하나
- 간결한 키워드, 통계, 인포그래픽
- 모든 설명은 과하지 않게, 정보 중심으로

---

🧠 전체 문체는 ‘나레이션 스크립트’용이야.

- 너무 문어체는 금지
- 자연스럽고 리듬감 있는 말하기 문장
- 자막용 하이라이트 키워드가 잘 살아야 함

---

너는 지금부터 **헬로헬씨(Hello Healthy)** 콘텐츠의 세계관에 맞는 스크립트를 작성하는 작가야.  
한 편당 길이는 약 90초 분량으로 작성하고, 시청자에게 “아, 이거 나도 해봐야겠다”는 느낌이 들게 만드는 게 핵심이야.
"""
    user_prompt = f"""
주제: {topic}

논문 제목: {paper_title} (괄호로 간단히 넣어줘)
"""
    res = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.7
    )
    return res['choices'][0]['message']['content']

# ✅ 실행 함수
def main():
    topics = generate_topics()
    for idx, topic in enumerate(topics):
        print(f"\n📌 [{idx+1}] 주제: {topic}")
        search_query = get_search_query(topic)
        paper_title, _ = fetch_pubmed_abstract(search_query)
        if not paper_title:
            paper_title = "Harvard Med. (임의 논문 제목)"

        script = generate_script(topic, paper_title)
        filename = f"hello_healthy_script_{idx+1}.txt"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"# {topic}\n")
            f.write(f"(참고: {paper_title})\n\n")
            f.write(script)
        print(f"✅ 저장 완료: {filename}")

if __name__ == "__main__":
    main()

