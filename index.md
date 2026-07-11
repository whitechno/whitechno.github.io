---
layout: default
---

# Oleg White

Data scientist and ML/AI engineer. I build intelligent systems for data
processing and analytics — machine learning products, RAG and agentic AI,
and distributed data infrastructure.

[GitHub](https://github.com/whitechno) ·
[LinkedIn](https://www.linkedin.com/in/olegwhite/) ·
[Twitter](https://x.com/whitechno)

## Posts

{% assign posts = site.pages
   | where_exp: "p", "p.dir contains '/blog/'"
   | where_exp: "p", "p.date"
   | sort: "date" | reverse %}
{% for post in posts %}
- {{ post.date | date: "%Y-%m-%d" }} · [{{ post.title }}]({{ post.url | relative_url }})
{% endfor %}
