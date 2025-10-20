# MarketSignalsAI

System Architecture
1. Buy / Sell Signal Generation
1.1 Technical / Historical Price Analysis
Retrieves monthly, weekly, daily, and hourly prices for the past 24 periods using Yahoo Finance.
Generates 512×512 price chart images.
Sends a structured prompt(see 4.) + image set to the Technical AI Agent.
Receives a technical Buy / Sell recommendation.
Future versions will integrate a custom deep-learning model for pattern-based signal recognition.

1.2 Market Sentiment Analysis
Uses the Sentiment AI Agent to determine:
Overall market sentiment (Positive / Neutral / Negative)
Ticker sentiment for the specific stock, ETF, or crypto (Positive / Neutral / Negative)
Sentiment data are merged with technical signals to finalize actionable insights.
See for reference 
https://chatgpt.com/business/ai-for-finance
https://polygon.io/blog/sentiment-analysis-with-ticker-news-api-insights

1.3 Signal Logic
Condition	Technical Signal	Market Sentiment	Portfolio Condition	Action
Buy	BUY	Positive or Neutral (both global & ticker)	Allowed	✅ Generate Buy Signal
Sell	SELL	—	Allowed	✅ Generate Sell Signal

2. Portfolio Manager AI Agent
Starts with $10,000 virtual balance.
Tracks current open positions.
Allocates capital as
Allocation = Available_Cash / (Total_Tickers - Active_Positions)
Prevents duplicate buys.
Authorizes buys or sells when signal conditions are met.

3. Fundamental Analysis (Value Investing Core)
Inspired by Warren Buffett-style long-term value investing:
Operates on a manually curated list of ~10 tickers (stocks + ETFs).
Evaluates company fundamentals, long-term prospects, and fair-value indicators.
Intended to complement short-term signals with fundamental confidence weighting.

4. AI Agent Prompts
Custom, reusable generic prompts will guide:
Technical AI Agent → chart pattern recognition, trend identification
Sentiment AI Agent → news / social sentiment interpretation
(These will be defined externally for modular integration.)

5. Flask Trading Signal Server
Built with Python + Flask.
Runs hourly to evaluate and emit Buy/Sell signals.
Sends email notifications on actionable events.
Future feature: record signals to Ethereum blockchain for public verification of performance and model integrity.

🧠 Planned Enhancements
Custom CNN / Transformer-based model for multi-timeframe technical analysis
Fine-tuned sentiment classifier for financial news and social data. 
Persistent PostgreSQL(https://www.tigerdata.com/) / SQLite trade log
Blockchain-anchored signal verification
Web dashboard for visualization and manual input
Integration with broker APIs for paper and live trading




