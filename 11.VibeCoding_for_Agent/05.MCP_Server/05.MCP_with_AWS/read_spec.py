import pandas as pd
import json

# Read XLS
try:
    df = pd.read_excel('docs/서울시+문화행사+공공서비스예약+정보.xls', engine='xlrd')
    print("=== API SPECIFICATION ===")
    print(df.to_string())
    print("\n")
except Exception as e:
    print(f"Error reading XLS: {e}")

# Read JSON
try:
    with open('docs/서울시 문화행사 공공서비스예약 정보.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    print("\n=== SAMPLE DATA (first item) ===")
    if isinstance(data, dict) and 'culturalSpaceInfo' in data:
        print(json.dumps(data['culturalSpaceInfo'], ensure_ascii=False, indent=2)[:3000])
    else:
        print(json.dumps(data, ensure_ascii=False, indent=2)[:3000])
except Exception as e:
    print(f"Error reading JSON: {e}")
