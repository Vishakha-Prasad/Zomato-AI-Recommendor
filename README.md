# Zomato-AI-Recommendor

AI-powered restaurant recommendations using Zomato data and Groq LLM.

## Run locally

```bash
pip install -r requirements.txt
python data_pipeline/explore_and_clean_data.py  # Generate data/zomato_cleaned.csv
streamlit run app.py
```

## Deploy to Streamlit Cloud

1. Push this repo to GitHub.
2. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub.
3. Click **New app** → select repo `Zomato-AI-Recommendor`, main file `app.py`.
4. Under **Advanced settings** add secrets:
   ```
   GROQ_API_KEY = "your-groq-api-key"
   ```
5. Ensure `data/zomato_cleaned.csv` exists in the repo (or update `.gitignore` to include it for deployment).

Then click **Deploy**.