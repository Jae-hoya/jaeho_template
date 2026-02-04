const fs = require('fs');

console.log('=== Seoul Open Data API Analysis ===\n');

const files = [
  '서울시 문화행사 공공서비스예약 정보.json',
  '서울시 문화행사 정보.json',
  '서울시 여성가족재단 행사 정보.json'
];

files.forEach(file => {
  try {
    const path = `C:/Users/skyop/jaeho_template/11.VibeCoding_for_Agent/05.MCP_Server/05.MCP_with_AWS/docs/${file}`;
    const data = JSON.parse(fs.readFileSync(path, 'utf8'));

    console.log(`\n${'='.repeat(60)}`);
    console.log(`FILE: ${file}`);
    console.log('='.repeat(60));

    console.log('\nTop-level keys:', Object.keys(data));
    console.log('Total records:', data.DATA ? data.DATA.length : 0);

    if (data.DESCRIPTION) {
      console.log('\nField Descriptions (한글 -> 영문):');
      Object.entries(data.DESCRIPTION).forEach(([key, value]) => {
        console.log(`  ${key}: ${value}`);
      });
    }

    if (data.DATA && data.DATA.length > 0) {
      console.log('\nSample Record (first):');
      console.log(JSON.stringify(data.DATA[0], null, 2));

      console.log('\nAll field names in data:');
      console.log(Object.keys(data.DATA[0]).join(', '));
    }

  } catch(e) {
    console.log(`\nError reading ${file}: ${e.message}`);
  }
});
