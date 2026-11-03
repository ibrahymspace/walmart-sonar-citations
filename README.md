# walmart-sonar-citations

One Perplexity Sonar call about Walmart, sent through OpenRouter. Prints the answer text and
every citation URL from the response's citation field (never from the answer text).

```bash
pip install -r requirements.txt
# put your key after OPENROUTER_API_KEY= in .env (git-ignored)
python main.py            # live call
python main.py --sample   # same printing code on openrouter_sonar_sample_response.json
```
