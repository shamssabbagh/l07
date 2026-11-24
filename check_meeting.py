from gmail_service import search_emails_impl, read_email_impl
import json

queries = [
    'meeting',
    'meet',
    'interview',
    'appointment',
    'פגישה',
    'מפגש',
    'schedule',
    'zoom',
]

seen_ids = set()
results = []

for q in queries:
    msgs = search_emails_impl(q, max_results=10)
    for m in msgs:
        if m['id'] not in seen_ids:
            seen_ids.add(m['id'])
            details = read_email_impl(m['id'])
            results.append(details)

results.sort(key=lambda x: x['date'], reverse=True)

print(f"Total matching emails: {len(results)}")
for r in results[:15]:
    print("--------------------------------------------------")
    print(f"ID: {r['id']}")
    print(f"Date: {r['date']}")
    print(f"From: {r['from']}")
    print(f"Subject: {r['subject']}")
    print(f"Snippet: {r['snippet'][:150]}")
