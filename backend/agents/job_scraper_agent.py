import asyncio
import aiohttp
import ssl
from datetime import datetime
from typing import List, Dict
import os

class JobScraperAgent:
    """Real Job Scraper using Adzuna API"""

    def __init__(self):
        self.name = "Job Scraper"
        self.adzuna_app_id = os.getenv("ADZUNA_APP_ID", "17f1be01")
        self.adzuna_app_key = os.getenv("ADZUNA_APP_KEY", "1e4d1f9a78950983d2e04aab1667cd00")
        self.base_url = "https://api.adzuna.com/v1/api/jobs"

    async def search_jobs(self, filters: Dict) -> List[Dict]:
        """Search real jobs via Adzuna API"""

        job_title = filters.get("job_title", "")
        location = filters.get("location", "")
        min_salary = filters.get("min_salary", 0)
        max_salary = filters.get("max_salary", 0)
        keywords = filters.get("keywords", [])
        max_results = filters.get("max_results", 20)

        print(f"\n🎯 Searching Adzuna for '{job_title}' in '{location}'...")

        # Build search query
        what = job_title
        if keywords:
            what = f"{job_title} {' '.join(keywords)}"

        # Detect country
        country = "gb"
        loc_lower = location.lower()
        if "united states" in loc_lower or ", us" in loc_lower:
            country = "us"
        elif "australia" in loc_lower or ", au" in loc_lower:
            country = "au"
        elif "canada" in loc_lower or ", ca" in loc_lower:
            country = "ca"

        # Extract city
        where = location.split(",")[0].strip() if "," in location else location

        all_jobs = []
        pages_to_fetch = min(3, (max_results // 10) + 1)

        # SSL context - disable verification for container compatibility
        ssl_ctx = ssl.create_default_context()
        ssl_ctx.check_hostname = False
        ssl_ctx.verify_mode = ssl.CERT_NONE
        connector = aiohttp.TCPConnector(ssl=ssl_ctx)

        async with aiohttp.ClientSession(connector=connector) as session:
            for page in range(1, pages_to_fetch + 1):
                params = {
                    "app_id": self.adzuna_app_id,
                    "app_key": self.adzuna_app_key,
                    "results_per_page": 10,
                    "what": what,
                    "where": where,
                }

                if min_salary and min_salary > 0:
                    params["salary_min"] = min_salary
                if max_salary and max_salary > 0:
                    params["salary_max"] = max_salary

                url = f"{self.base_url}/{country}/search/{page}"
                print(f"🔍 Calling: {url} with params: {params}")

                try:
                    async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=10)) as response:
                        print(f"📡 Response status: {response.status}")
                        if response.status == 200:
                            data = await response.json()
                            results = data.get("results", [])
                            total = data.get("count", 0)
                            print(f"✅ Page {page}: {len(results)} jobs (total available: {total})")
                            jobs = self._parse_adzuna_jobs(results, keywords)
                            all_jobs.extend(jobs)
                        else:
                            text = await response.text()
                            print(f"❌ Adzuna error {response.status}: {text}")
                            break
                except Exception as e:
                    print(f"❌ Exception: {type(e).__name__}: {e}")
                    break

                await asyncio.sleep(0.3)

        all_jobs.sort(key=lambda j: (
            j.get("keyword_matches", 0) * 10 + max(0, 30 - j.get("posted_days_ago", 30))
        ), reverse=True)

        top_jobs = all_jobs[:max_results]
        print(f"\n✅ Returning {len(top_jobs)} real jobs")
        return top_jobs

    def _parse_adzuna_jobs(self, results: List[Dict], keywords: List[str]) -> List[Dict]:
        jobs = []
        for r in results:
            try:
                created = r.get("created", "")
                days_ago = 0
                if created:
                    try:
                        created_dt = datetime.fromisoformat(created.replace("Z", "+00:00"))
                        days_ago = (datetime.now().astimezone() - created_dt).days
                    except:
                        days_ago = 0

                sal_min = r.get("salary_min", 0) or 0
                sal_max = r.get("salary_max", 0) or 0
                if sal_min and sal_max and sal_min != sal_max:
                    salary = f"£{int(sal_min):,} - £{int(sal_max):,}"
                elif sal_max:
                    salary = f"Up to £{int(sal_max):,}"
                elif sal_min:
                    salary = f"£{int(sal_min):,}+"
                else:
                    salary = "Salary not specified"

                contract_time = r.get("contract_time", "")
                contract_type = r.get("contract_type", "")
                if contract_time == "full_time":
                    job_type = "Full-time"
                elif contract_time == "part_time":
                    job_type = "Part-time"
                elif contract_type == "contract":
                    job_type = "Contract"
                else:
                    job_type = "Full-time"

                description = r.get("description", "")
                keyword_matches = 0
                if keywords and description:
                    desc_lower = description.lower()
                    keyword_matches = sum(1 for kw in keywords if kw.lower() in desc_lower)

                job = {
                    "id": r.get("id", ""),
                    "title": r.get("title", ""),
                    "company": r.get("company", {}).get("display_name", "Unknown"),
                    "location": r.get("location", {}).get("display_name", ""),
                    "salary": salary,
                    "currency": "GBP",
                    "min_salary": sal_min,
                    "max_salary": sal_max,
                    "experience": "Mid-Level",
                    "job_type": job_type,
                    "remote": self._detect_remote(description),
                    "easy_apply": self._detect_easy_apply(description),
                    "posted_date": created,
                    "posted_days_ago": days_ago,
                    "description": description[:500] + "..." if len(description) > 500 else description,
                    "url": r.get("redirect_url", ""),
                    "keyword_matches": keyword_matches,
                    "relevance_score": keyword_matches * 10 + max(0, 30 - days_ago),
                    "source": "Adzuna"
                }
                jobs.append(job)
            except Exception as e:
                print(f"Error parsing job: {e}")
                continue
        return jobs

    def _detect_easy_apply(self, description: str) -> bool:
        desc_lower = description.lower()
        signals = ["easy apply", "quick apply", "one click", "apply now",
                   "apply directly", "apply online", "apply today",
                   "no cover letter", "apply in minutes", "simple application"]
        return any(s in desc_lower for s in signals)

    def _detect_remote(self, description: str) -> str:
        desc_lower = description.lower()
        if "fully remote" in desc_lower or "100% remote" in desc_lower:
            return "Remote"
        elif "hybrid" in desc_lower:
            return "Hybrid"
        elif "remote" in desc_lower:
            return "Remote"
        return "On-site"
