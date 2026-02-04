import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('docs/서울시 문화행사 공공서비스예약 정보.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print('=== Complete JSON Structure (first 5000 chars) ===')
print(json.dumps(data, ensure_ascii=False, indent=2)[:5000])

print('\n\n=== Summary ===')
if 'DATA' in data:
    print(f"Number of items in DATA: {len(data['DATA'])}")
    if data['DATA']:
        print(f"\nFirst item:")
        print(json.dumps(data['DATA'][0], ensure_ascii=False, indent=2))
