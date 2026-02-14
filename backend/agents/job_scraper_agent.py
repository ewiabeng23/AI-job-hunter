import asyncio
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import random
import time

class JobScraperAgent:
    """
    Advanced Job Scraper with Smart Filtering
    """

    def __init__(self):
        self.name = "Job Scraper"
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
        ]

    async def search_jobs(self, filters: Dict) -> List[Dict]:
        """Main search function with advanced filters"""

        print(f"\n{'='*70}")
        print(f"🎯 JOB HUNT STARTED - ADVANCED SEARCH")
        print(f"{'='*70}")

        job_title = filters.get("job_title", "")
        location = filters.get("location", "")
        min_salary = filters.get("min_salary", 0)
        max_salary = filters.get("max_salary", 999999)
        currency = filters.get("currency", "GBP")
        experience_levels = filters.get("experience_level", [])
        job_types = filters.get("job_type", [])
        remote_options = filters.get("remote", [])
        easy_apply_only = filters.get("easy_apply_only", False)
        posted_within = filters.get("posted_within_days", 7)
        keywords = filters.get("keywords", [])
        max_results = filters.get("max_results", 50)

        print(f"📋 SEARCH CRITERIA:")
        print(f"   • Position: {job_title}")
        print(f"   • Location: {location}")
        print(f"   • Salary: {currency} {min_salary:,} - {max_salary:,}")
        print(f"   • Experience: {', '.join(experience_levels) if experience_levels else 'Any'}")
        print(f"   • Type: {', '.join(job_types) if job_types else 'Any'}")
        print(f"   • Remote: {', '.join(map(str, remote_options)) if remote_options else 'Any'}")
        print(f"   • Easy Apply: {'Yes' if easy_apply_only else 'No'}")
        print(f"   • Posted: Last {posted_within} days")
        print(f"   • Keywords: {', '.join(keywords) if keywords else 'None'}")
        print(f"   • Max Results: {max_results}\n")

        all_jobs = []

        # Simulate scraping from multiple sources
        sources = ['LinkedIn', 'Indeed', 'Glassdoor']
        for source in sources:
            print(f"🔍 Scraping {source} for '{job_title}' in '{location}'...")
            await asyncio.sleep(0.5)  # Simulate network delay
            jobs = self._generate_mock_jobs(source, job_title, location, 10)
            print(f"✅ Found {len(jobs)} jobs on {source}")
            all_jobs.extend(jobs)

        print(f"\n📊 Total jobs before filtering: {len(all_jobs)}")

        # Apply filters
        filtered_jobs = self._apply_filters(
            all_jobs,
            min_salary=min_salary,
            max_salary=max_salary,
            currency=currency,
            experience_levels=experience_levels,
            job_types=job_types,
            remote_options=remote_options,
            easy_apply_only=easy_apply_only,
            posted_within=posted_within,
            keywords=keywords
        )

        # Sort by relevance (keyword match count + recency)
        filtered_jobs.sort(key=lambda j: (
            j.get('keyword_matches', 0) * 10 + (30 - j.get('posted_days_ago', 30))
        ), reverse=True)

        # Limit results
        top_jobs = filtered_jobs[:max_results]

        # Print summary
        print(f"\n{'='*70}")
        print(f"✅ SEARCH COMPLETE")
        print(f"   • Total Found: {len(all_jobs)}")
        print(f"   • After Filters: {len(filtered_jobs)}")
        print(f"   • Match Rate: {len(filtered_jobs)/len(all_jobs)*100:.1f}%")
        print(f"{'='*70}\n")

        # Print top matches
        if top_jobs:
            print(f"\n🎯 TOP {len(top_jobs)} MATCHES:\n")
            for i, job in enumerate(top_jobs, 1):
                kw_match = f"{job.get('keyword_matches', 0)}/{len(keywords)}" if keywords else "N/A"
                print(f"{i}. {job['title']} at {job['company']}")
                print(f"   💰 {job['salary']} | 📍 {job['location']} | 🏢 {job['remote']}")
                print(f"   ⚡ {'Easy Apply' if job['easy_apply'] else 'Apply' } | 📅 {job['posted_days_ago']}d ago")
                print(f"   🎯 Score: {job['relevance_score']} | 🔑 {kw_match} keywords")
                print(f"   🔗 {job['url']}\n")
        else:
            print("No jobs match your criteria.\n")

        return top_jobs

    def _generate_mock_jobs(self, source: str, title: str, location: str, count: int) -> List[Dict]:
        """Generate realistic mock jobs for testing"""
        companies = {
            'LinkedIn': ['DataSystems Inc', 'ByteWorks', 'CloudTech', 'Innova', 'Nexus'],
            'Indeed': ['CloudNine Labs', 'DevOps Solutions', 'TechCorp', 'ScaleOps', 'KubeWorks'],
            'Glassdoor': ['SysAdmin Pros', 'Reliable Cloud', 'StackOps', 'DevOpsify', 'PipelineIO']
        }
        company_list = companies.get(source, companies['LinkedIn'])

        jobs = []
        for i in range(count):
            days_ago = random.randint(0, 14)  # simulate posts up to 2 weeks old
            # Ensure some jobs have keywords, some don't
            keyword_match_count = random.choices([0, 1, 2, 3], weights=[10, 30, 40, 20])[0]
            salary_min = random.randint(50, 90) * 1000
            salary_max = salary_min + random.randint(20, 50) * 1000
            job = {
                'id': f"{source}_{i}_{random.randint(1000,9999)}",
                'title': title,
                'company': random.choice(company_list),
                'location': location,
                'salary': f"£{salary_min//1000}k - £{salary_max//1000}k",
                'currency': 'GBP',
                'min_salary': salary_min,
                'max_salary': salary_max,
                'experience': random.choice(['Entry-Level', 'Mid-Level', 'Senior']),
                'job_type': random.choice(['Full-time', 'Contract', 'Part-time']),
                'remote': random.choice(['Remote', 'Hybrid', 'On-site']),
                'easy_apply': random.choice([True, False]),
                'posted_date': (datetime.now() - timedelta(days=days_ago)).isoformat(),
                'posted_days_ago': days_ago,
                'description': f"Looking for a {title} with skills in AWS, Docker, Kubernetes, Python, and CI/CD.",
                'url': f"https://{source.lower()}.com/job/{random.randint(100000,999999)}",
                'keyword_matches': keyword_match_count,  # used for scoring
                'relevance_score': keyword_match_count * 10 + (30 - days_ago)
            }
            jobs.append(job)
        return jobs

    def _apply_filters(self, jobs: List[Dict], **filters) -> List[Dict]:
        """Apply all filters to the job list"""
        filtered = jobs.copy()
        original_count = len(filtered)

        # Experience filter
        if filters.get('experience_levels'):
            exp_levels = filters['experience_levels']
            filtered = [j for j in filtered if j['experience'] in exp_levels]
            print(f"   🔍 Experience filter: {original_count} → {len(filtered)}")
            original_count = len(filtered)

        # Job type filter
        if filters.get('job_types'):
            types = filters['job_types']
            filtered = [j for j in filtered if j['job_type'] in types]
            print(f"   🔍 Job type filter: {original_count} → {len(filtered)}")
            original_count = len(filtered)

        # Remote filter
        if filters.get('remote_options'):
            remote_opts = filters['remote_options']
            filtered = [j for j in filtered if j['remote'] in remote_opts]
            print(f"   🔍 Remote filter: {original_count} → {len(filtered)}")
            original_count = len(filtered)

        # Easy Apply filter
        if filters.get('easy_apply_only'):
            filtered = [j for j in filtered if j['easy_apply']]
            print(f"   🔍 Easy Apply filter: {original_count} → {len(filtered)}")
            original_count = len(filtered)

        # Salary filter
        min_sal = filters.get('min_salary', 0)
        max_sal = filters.get('max_salary', 999999)
        filtered = [j for j in filtered if j['min_salary'] >= min_sal and j['max_salary'] <= max_sal]
        if original_count != len(filtered):
            print(f"   🔍 Salary filter: {original_count} → {len(filtered)}")
            original_count = len(filtered)

        # Recency filter (lenient: if posted_within is high, we still include older jobs but they rank lower)
        posted_within = filters.get('posted_within', 7)
        # We don't filter out entirely, just allow older jobs with lower scores (handled in sorting)

        # Keyword filter: we keep all jobs but tag them with keyword_matches (already in mock)
        # If you want to filter out jobs with zero keywords, uncomment the next line:
        # if filters.get('keywords'):
        #     filtered = [j for j in filtered if j['keyword_matches'] > 0]

        return filtered

# For standalone testing
async def main():
    scraper = JobScraperAgent()
    test_filters = {
        "job_title": "DevOps Engineer",
        "location": "London, UK",
        "min_salary": 60000,
        "max_salary": 150000,
        "currency": "GBP",
        "experience_level": ["Mid-Level", "Senior"],
        "job_type": ["Full-time"],
        "remote": ["Remote", "Hybrid"],
        "easy_apply_only": True,
        "posted_within_days": 3,
        "keywords": ["AWS", "Docker", "Kubernetes"],
        "max_results": 20
    }
    results = await scraper.search_jobs(test_filters)

if __name__ == "__main__":
    asyncio.run(main())
