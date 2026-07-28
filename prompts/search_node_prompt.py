search_prompt = """
Analyze the following title for the topic "{topic}" and use DDG web search tools(ddg_web_search,ddg_fetch_page) to find comprehensive, 
up-to-date information. For each title, generate a concise summary of findings and include relevant links. 
Focus on data, statistics, recent events, and verifiable facts, avoiding subjective opinions. 
The output should be structured as a JSON list where each element has "title", "summary", and "links".

Title : {title}

Return the result as a JSON list: [{{ "title": "...", "summary": "...", "links": [...] }}]
"""