import pandas as pd
import json
import sys

# Read HTML file (XLS is actually HTML)
try:
    df = pd.read_html('docs/서울시+문화행사+공공서비스예약+정보.xls', encoding='utf-8')
    print("=== API SPECIFICATION ===")
    for i, table in enumerate(df):
        print(f"\n--- Table {i} ---")
        print(table.to_string())
    print("\n")
except Exception as e:
    print(f"Error reading HTML: {e}")

# Read JSON with UTF-8
try:
    # Change stdout encoding to UTF-8
    sys.stdout.reconfigure(encoding='utf-8')

    with open('docs/서울시 문화행사 공공서비스예약 정보.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    print("\n=== SAMPLE DATA STRUCTURE ===")
    print(f"Root keys: {list(data.keys())}")

    # Print first item
    for key in data.keys():
        print(f"\n--- {key} ---")
        if isinstance(data[key], dict):
            if 'list_total_count' in data[key]:
                print(f"Total count: {data[key]['list_total_count']}")
            if 'RESULT' in data[key]:
                print(f"Result: {data[key]['RESULT']}")
            if 'row' in data[key]:
                print(f"Number of rows: {len(data[key]['row'])}")
                if data[key]['row']:
                    print(f"First row keys: {list(data[key]['row'][0].keys())}")
                    print(f"First row sample:")
                    for k, v in list(data[key]['row'][0].items())[:5]:
                        print(f"  {k}: {v}")
except Exception as e:
    print(f"Error reading JSON: {e}")
    import traceback
    traceback.print_exc()
