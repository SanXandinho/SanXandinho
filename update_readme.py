import os
import json
import urllib.request
import re

TOKEN = os.environ["GH_TOKEN"]
USERNAME = os.environ["GITHUB_REPOSITORY_OWNER"]

def graphql(query):
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": query}).encode(),
        headers={"Authorization": f"bearer {TOKEN}", "Content-Type": "application/json"}
    )
    return json.loads(urllib.request.urlopen(req).read())

query = f"""
{{
  user(login: "{USERNAME}") {{
    contributionsCollection {{
      commitContributionsByRepository(maxRepositories: 100) {{
        repository {{ nameWithOwner url }}
      }}
      pullRequestContributionsByRepository(maxRepositories: 100) {{
        repository {{ nameWithOwner url }}
      }}
    }}
  }}
}}
"""

data = graphql(query)["data"]["user"]["contributionsCollection"]
repos = {}

for item in data["commitContributionsByRepository"] + data["pullRequestContributionsByRepository"]:
    r = item["repository"]
    repos[r["nameWithOwner"]] = r["url"]

lines = [f"- [{name}]({url})" for name, url in repos.items()]
new_content = "\n".join(lines[:5]) if lines else "_No recent activity._"

with open("README.md", "r", encoding="utf-8") as f:
    content = f.read()

content = re.sub(
    r"<!--START_SECTION:recent-->.*?<!--END_SECTION:recent-->",
    f"<!--START_SECTION:recent-->\n{new_content}\n<!--END_SECTION:recent-->",
    content,
    flags=re.DOTALL
)

with open("README.md", "w", encoding="utf-8") as f:
    f.write(content)
