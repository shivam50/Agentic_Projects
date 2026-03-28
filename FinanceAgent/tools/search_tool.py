from duckduckgo_search import DDGS

def research_merchant(merchant_name):
    """Searches the web for context on a merchant."""
    print(f"🔍 Investigator is looking up: {merchant_name}...")
    
    with DDGS() as ddgs:
        # We search for the merchant and keywords like 'scam' or 'hq'
        results = ddgs.text(f"{merchant_name} official website or customer support", max_results=2)
        
        if not results:
            return "No web info found."
            
        # Combine the top 2 snippets into a short string to save tokens
        blob = ""
        for r in results:
            blob += f"Info: {r['body']}\n"
        return blob[:500] # Keep it short!