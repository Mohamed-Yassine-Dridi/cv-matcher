import requests


def is_valid_for_tunisian(job):
    nationality_items = job.get("nationalities", []) or []

    # Empty list means "Any Nationality"
    if not nationality_items:
        return True

    nationality_names = [
        str(n.get("constant_name", "")).strip().lower()
        for n in nationality_items
        if n.get("constant_name")
    ]

    has_tunisia = any(
        "tunisia" in name or "tunisian" in name
        for name in nationality_names
    )

    return has_tunisia


def stream_opportunities(max_pages=15, region_choice="any", duration_choice="any"):
    api_url = "https://gis-api.aiesec.org/graphql"

    my_token = "e316ebe109dd84ed16734e5161a2d236d0a7e6daf499941f7c110078e3c75493"
    headers = {
        "Content-Type": "application/json",
        "Authorization": my_token
    }

    region_map = {
        "europe": 1629,
        "americas": 1628,
        "asia": 1627,
        "mea": 1630
    }

    for page in range(1, max_pages + 1):
        filters = {"programmes": [8]}

        if region_choice in region_map:
            filters["regions"] = [region_map[region_choice]]

        if duration_choice != "any":
            filters["duration_type"] = duration_choice

        print(f"Scraping Page {page} with filters: {filters}")

        payload = {
            "operationName": "GetAllOpportunitiesQuery",
            "query": """
            query GetAllOpportunitiesQuery($page: Int, $per_page: Int, $filters: OpportunityFilter) {
              allOpportunity(page: $page, per_page: $per_page, filters: $filters) {
                data {
                  id
                  title
                  description
                  skills { option }
                  nationalities { constant_name }
                }
              }
            }
            """,
            "variables": {
                "page": page,
                "per_page": 50,
                "filters": filters
            }
        }

        try:
            response = requests.post(api_url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            data = response.json()

            if "errors" in data:
                print(f"GraphQL Error on page {page}: {data['errors']}")
                break

            jobs_list = data.get("data", {}).get("allOpportunity", {}).get("data", [])

            if not jobs_list:
                break

            opportunities = []

            for job in jobs_list:
                nationality_items = job.get("nationalities", []) or []
                nationality_names = [
                    str(n.get("constant_name", "")).strip()
                    for n in nationality_items
                    if n.get("constant_name")
                ]

                print(f"Job: {job.get('title', 'Unknown Title')} | Nationalities: {nationality_names}")

                if not is_valid_for_tunisian(job):
                    print("=> REJECTED")
                    continue

                print("=> KEPT")

                title = job.get("title", "Unknown Title")

                skills_data = job.get("skills", [])
                skill_names = [s.get("option", "") for s in skills_data if s.get("option")]
                skills_string = ", ".join(skill_names)

                raw_desc = job.get("description", "")
                short_desc = raw_desc[:300] if raw_desc else ""

                ai_optimized_text = (
                    f"Role: {title}. "
                    f"Required Skills: {skills_string}. "
                    f"Context: {short_desc}"
                )

                opportunities.append({
                    "title": title,
                    "text": ai_optimized_text,
                    "url": f"https://aiesec.org/opportunity/global-talent/{job.get('id')}"
                })

            yield opportunities

        except Exception as e:
            print(f"API Connection Error on page {page}: {e}")
            break