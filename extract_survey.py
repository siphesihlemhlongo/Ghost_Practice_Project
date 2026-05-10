import pandas as pd

df = pd.read_excel('MB Ghost Practice User Survey (Responses).xlsx')

with open('survey_summary.txt', 'w', encoding='utf-8') as f:
    f.write('=== FRUSTRATIONS ===\n')
    for x in df['What are your biggest frustrations with GP?  '].dropna().unique():
        f.write('- ' + str(x) + '\n')
    
    f.write('\n=== IMPORTANT FEATURES ===\n')
    for x in df['If we moved to a new system, what features would be most important to you?   '].dropna().unique():
        f.write('- ' + str(x) + '\n')
        
    f.write('\n=== MISSING FEATURES ===\n')
    for x in df['Are there any features you feel are missing or inadequate?  '].dropna().unique():
        f.write('- ' + str(x) + '\n')
