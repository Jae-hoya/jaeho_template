#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pandas as pd
import json

# Read HTML file (Excel file is actually HTML format)
print("Reading HTML-formatted Excel file...")
df = pd.read_html('docs/서울시+문화행사+공공서비스예약+정보.xls', encoding='utf-8')[0]

print('Shape:', df.shape)
print('\nColumns:')
for col in df.columns:
    print(f'  {col}')

print('\nAll data as JSON:')
import json
# Reset index and convert to records
records = df.to_dict(orient='records')
for i, record in enumerate(records):
    print(f'\nRow {i}:')
    print(json.dumps(record, ensure_ascii=False, indent=2))
