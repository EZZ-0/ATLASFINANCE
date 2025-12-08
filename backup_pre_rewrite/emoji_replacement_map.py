# EMOJI REMOVAL - COMPREHENSIVE REPLACEMENT MAP
# Run this to see all emojis that need replacing

EMOJI_REPLACEMENTS = {
    # Extract tab
    'st.button("🔍 Extract Data"': 'st.button("Extract Data"',
    '❌ {result': '✗ {result',  # Or remove entirely
    '✅ Data extracted': 'Data extracted',
    '✅ Loaded:': 'Loaded:',
    '⚠️ Please enter': 'Please enter',
    'ℹ️ Using CURRENT': 'Using CURRENT',
    '✅ DCF analysis complete': 'DCF analysis complete',
    'ℹ️ This analysis reverse': 'This analysis reverse',
    'ℹ️ Consensus recommendations': 'Consensus recommendations',
    'ℹ️ This company does not': 'This company does not',
    '👈 **Get Started:**': '**Get Started:**',
    
    # Sub-tabs
    '"💵 Income Statement"': '"Income Statement"',
    '"🏦 Balance Sheet"': '"Balance Sheet"',
    '"💸 Cash Flow"': '"Cash Flow"',
    
    # Info messages
    'ℹ️ Historical data': 'Historical data',
    'ℹ️ Showing **': 'Showing **',
    '⚠️ Ratios returned': 'Warning: Ratios returned',
    'ℹ️ **Quarterly Data': 'Quarterly Data',
    'ℹ️ **Annual Data**': 'Annual Data',
    '❌ DCF failed': 'DCF failed',
    
    # Technical tab
    'ℹ️ Comprehensive technical': 'Comprehensive technical',
    '✅ Golden Cross:': 'Golden Cross:',
    '⚠️ Death Cross:': 'Death Cross:',
    '⚠️ Overbought': 'Overbought',
    '💡 Oversold': 'Oversold',
    'ℹ️ Neutral Zone': 'Neutral Zone',
    '✅ Bullish Crossover': 'Bullish Crossover',
    '⚠️ Bearish Crossover': 'Bearish Crossover',
    '✅ High Volume': 'High Volume',
    '⚠️ Low Volume': 'Low Volume',
    'ℹ️ Normal Volume': 'Normal Volume',
    
    # Forensic
    'ℹ️ Advanced forensic': 'Advanced forensic accounting models...',
    '⚠️ {beneish': '{beneish',
    
    # Options
    'ℹ️ Analyze options': 'Analyze options market sentiment...',
    
    # News
    '⚠️ {news_data': '{news_data',
    '📖 {read_time}': '{read_time}',
    '💡 How to enable': 'How to enable NewsAPI',
    '❌ {news_data': '{news_data',
    '💡 Tip: Make sure': 'Tip: Make sure',
    
    # Helper
    'st.button("ℹ️"': 'st.button("i"',  # Info button
}

print("="*60)
print("EMOJI REPLACEMENTS NEEDED")
print("="*60)
print(f"\nTotal replacements: {len(EMOJI_REPLACEMENTS)}")
print("\nMost critical:")
for emoji, replacement in list(EMOJI_REPLACEMENTS.items())[:10]:
    print(f"  {emoji[:30]}... → {replacement[:30]}...")


