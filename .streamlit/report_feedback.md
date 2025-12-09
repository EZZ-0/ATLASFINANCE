
📊 Research Evaluation: What's Viable vs Not
Based on the R&D reports and our current engine state:
✅ VIABLE & ACHIEVABLE (Do These)
Feature	Effort	Why It Works
Redis caching	Low ($20/mo)	Solves rate limits permanently
Basic SEO pages	Medium	Each stock gets a page, Google indexes
Freemium tier	Low	Just add limits to current features
Product Hunt launch	Free	Already built, just needs polish
Watchlist	Medium	st.session_state already exists
AI Summary (GPT)	Low ($30/mo)	Just API call + prompt template
⚠️ VIABLE BUT REQUIRES EFFORT (Phase 2)
Feature	Effort	Challenge
Arabic RTL interface	High	Needs full UI rewrite
Tadawul stocks	Medium	Need data source (Argaam?)
Stock screener	Medium	DB needed for filtering
Portfolio tracking	High	Requires user auth
NL search (ChatGPT style)	High	LangChain + intent parsing
❌ NOT VIABLE NOW (Skip)
Feature	Why Not
React/Next.js migration	3+ months work, no revenue yet
Mobile app	Needs React first
Real-time WebSockets	Overkill for current scale
Backtesting engine	Complex, not core value
Options flow	Expensive data, niche audience
🚀 Streamlit Alternatives: Prices & Options
Option 1: Stay on Streamlit (RECOMMENDED for now)
Hosting	Price	Limits
Streamlit Cloud (Free)	$0	1GB RAM, sleeps after 7 days
Streamlit Cloud (Teams)	$250/mo	Always on, custom domain
Heroku	$7-25/mo	Eco dynos, reliable
Railway	$5-20/mo	Easy deploy, good DX
Render	$7/mo	Free tier available
Option 2: Hybrid (Streamlit + FastAPI Backend)
Setup	Price	Benefits
Streamlit + Railway API	$15-40/mo	Separates concerns
Streamlit + Supabase	$25/mo	Adds user auth + DB
Option 3: Full Migration (NOT YET)
Framework	Price	Timeline
Next.js + Vercel	$0-20/mo	3-6 months work
React + AWS	$50-200/mo	4-6 months work
VERDICT: Stay on Streamlit for MVP. Add Redis ($20/mo) for caching. Migrate only after revenue.
📋 What's Left Before Launch
Critical (Must Have)
Task	Status	Time
Rate limiting fix	✅ DONE	-
All 20 issues fixed	✅ DONE	-
Final manual test pass	⏳ Pending	1-2 hours
Remove any remaining bugs	⏳	Based on test
Nice to Have (Can launch without)
Task	Priority	Time
Watchlist feature	Medium	4-6 hours
Basic SEO meta tags	Medium	2 hours
Landing page polish	Low	2 hours
Error message cleanup	Low	1 hour
Post-Launch (Phase 2)
Task	Priority
Redis caching	High
Pro tier / paywall	High
AI summary feature	Medium
Tadawul stocks	Medium
Arabic interface	Low
💡 My Honest Take
The research is good but ambitious - Focus on 20% that gives 80% value
KSA market is real opportunity - But needs Tadawul data source first
Don't migrate from Streamlit yet - Get users first, then worry about scale
Redis is the real fix - For $20/mo you solve caching permanently
AI summary is easy win - One API call, huge perceived value
Recommended next step: Run the final manual test, fix any remaining bugs, then deploy to Streamlit Cloud or Railway. Add paid features after you have 100+ users.
Want me to run the test checklist now, or focus on something else?