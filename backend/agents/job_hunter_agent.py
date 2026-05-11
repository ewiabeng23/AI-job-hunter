import asyncio
import json
from datetime import datetime
from anthropic import Anthropic
import os

class JobHunterAgent:
    """
    Job Hunter Agent - Finds jobs, customizes applications, and applies automatically
    """
    
    def __init__(self, api_key):
        self.claude = Anthropic(api_key=api_key)
        self.name = "Job Hunter"
        self.status = "idle"
        
    async def analyze_job_posting(self, job_description, job_title, company):
        """Analyze a job posting and extract key requirements"""
        
        self.status = "analyzing"
        
        prompt = f"""Analyze this job posting and extract key information:

Job Title: {job_title}
Company: {company}

Job Description:
{job_description}

Extract and return ONLY a JSON object with:
{{
    "required_skills": ["skill1", "skill2", ...],
    "preferred_skills": ["skill1", "skill2", ...],
    "experience_years": "X-Y years",
    "education": "degree required",
    "key_responsibilities": ["resp1", "resp2", ...],
    "salary_range": "estimated range if mentioned",
    "match_score_factors": ["what makes a good candidate"]
}}
"""
        
        response = self.claude.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        analysis = response.content[0].text
        
        # Extract JSON from response
        try:
            if "```json" in analysis:
                analysis = analysis.split("```json")[1].split("```")[0].strip()
            elif "```" in analysis:
                analysis = analysis.split("```")[1].split("```")[0].strip()
            
            return json.loads(analysis)
        except:
            return {"error": "Could not parse analysis", "raw": analysis}
    
    async def match_candidate(self, job_analysis, user_cv):
        """Match user's CV against job requirements"""
        
        self.status = "matching"
        
        prompt = f"""You are a job matching expert. 

Job Requirements:
{json.dumps(job_analysis, indent=2)}

Candidate CV:
{user_cv}

Calculate a match score (0-100) and explain why. Return ONLY JSON:
{{
    "match_score": 85,
    "matching_skills": ["skill1", "skill2"],
    "missing_skills": ["skill3"],
    "strengths": ["what makes them a good fit"],
    "gaps": ["what they're missing"],
    "recommendation": "apply/skip/maybe"
}}
"""
        
        response = self.claude.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1500,
            messages=[{"role": "user", "content": prompt}]
        )
        
        match_result = response.content[0].text
        
        try:
            if "```json" in match_result:
                match_result = match_result.split("```json")[1].split("```")[0].strip()
            elif "```" in match_result:
                match_result = match_result.split("```")[1].split("```")[0].strip()
            
            return json.loads(match_result)
        except:
            return {"error": "Could not parse match", "raw": match_result}
    
    async def customize_cv(self, user_cv, job_title, company, job_analysis):
        """Customize CV for specific job"""
        
        self.status = "customizing_cv"
        
        prompt = f"""You are an expert CV writer. Customize this CV for the specific job.

Original CV:
{user_cv}

Target Job: {job_title} at {company}

Job Requirements:
{json.dumps(job_analysis, indent=2)}

Create an optimized CV that:
1. Highlights relevant experience for THIS specific role
2. Uses keywords from the job description (ATS-friendly)
3. Quantifies achievements where possible
4. Keeps the same format but reorders/emphasizes relevant parts
5. Maximum 2 pages

Return the complete customized CV in clean text format.
"""
        
        response = self.claude.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=3000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return response.content[0].text
    
    async def write_cover_letter(self, user_cv, job_title, company, job_analysis):
        """Write personalized cover letter"""
        
        self.status = "writing_cover_letter"
        
        prompt = f"""Write a compelling, personalized cover letter for this job application.

Candidate CV Summary:
{user_cv[:1000]}  

Target Job: {job_title} at {company}

Job Requirements:
{json.dumps(job_analysis, indent=2)}

Write a cover letter that:
1. Shows genuine interest in the company and role
2. Highlights 2-3 most relevant achievements
3. Explains why they're a perfect fit
4. Professional but personable tone
5. Maximum 300 words
6. No generic phrases - make it specific

Return ONLY the cover letter text (no "Dear Hiring Manager" - start with the company research).
"""
        
        response = self.claude.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1500,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return response.content[0].text
    
    async def humanise_cv(self, cv_text):
        """Rewrite CV to sound human and bypass AI detection tools"""
        self.status = "humanising_cv"
        prompt = f"""You are rewriting a CV to sound completely human-written.

CV to rewrite:
{cv_text}

Rules:
1. NEVER use these AI giveaway words: leverage, spearhead, dynamic, passionate, innovative, utilise, facilitate, streamline, robust, cutting-edge, synergy, proactive, results-driven, detail-oriented, team player
2. Vary sentence length — mix short punchy sentences with longer ones
3. Use natural first-person where appropriate ("I built", "I led")
4. Add specific numbers and real-sounding details
5. Use contractions occasionally (I've, I'd, wasn't)
6. Avoid perfect parallel structure in bullet points — vary them
7. Write like a real person talking about their work, not a template
8. Keep all the facts and achievements — just make the language natural
9. Avoid starting every bullet with a verb — vary the openings
10. Remove any filler phrases like "responsible for" or "tasked with"

Return the complete rewritten CV. Keep the same structure and sections.
"""
        response = self.claude.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=3000,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text

    async def process_job_application(self, job_data, user_profile):
        """Complete end-to-end job application process"""
        
        results = {
            "job_title": job_data["title"],
            "company": job_data["company"],
            "timestamp": datetime.now().isoformat(),
            "status": "processing"
        }
        
        try:
            # Step 1: Analyze job
            print(f"🔍 Analyzing {job_data['title']} at {job_data['company']}...")
            analysis = await self.analyze_job_posting(
                job_data["description"],
                job_data["title"],
                job_data["company"]
            )
            results["analysis"] = analysis
            
            # Step 2: Match candidate
            print(f"🎯 Matching your profile...")
            match = await self.match_candidate(analysis, user_profile["cv"])
            results["match"] = match
            
            # If match score too low, skip
            if match.get("match_score", 0) < 60:
                print(f"⏭️  Skipping - Match score too low ({match.get('match_score')}%)")
                results["status"] = "skipped"
                results["reason"] = "Low match score"
                return results
            
            # Step 3: Customize CV
            print(f"📝 Customizing CV...")
            custom_cv = await self.customize_cv(
                user_profile["cv"],
                job_data["title"],
                job_data["company"],
                analysis
            )
            results["custom_cv"] = custom_cv
            
            # Step 4: Write cover letter
            print(f"✍️  Writing cover letter...")
            cover_letter = await self.write_cover_letter(
                user_profile["cv"],
                job_data["title"],
                job_data["company"],
                analysis
            )
            results["cover_letter"] = cover_letter
            
            # Step 5: Would submit application here (we'll add this next)
            print(f"✅ Application prepared for {job_data['title']} at {job_data['company']}")
            results["status"] = "ready_to_apply"
            
            self.status = "idle"
            return results
            
        except Exception as e:
            print(f"❌ Error processing job: {str(e)}")
            results["status"] = "failed"
            results["error"] = str(e)
            self.status = "idle"
            return results

# Test function
async def test_job_hunter():
    """Test the Job Hunter Agent"""
    
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("❌ ANTHROPIC_API_KEY not set!")
        return
    
    agent = JobHunterAgent(api_key)
    
    # Sample job posting
    sample_job = {
        "title": "Senior Python Developer",
        "company": "TechCorp Inc",
        "description": """
        We're looking for a Senior Python Developer to join our team.
        
        Requirements:
        - 5+ years Python development experience
        - Experience with Django/Flask
        - Strong knowledge of REST APIs
        - PostgreSQL database experience
        - AWS deployment experience
        - Team leadership skills
        
        Nice to have:
        - Docker/Kubernetes
        - React.js
        - CI/CD pipelines
        
        Responsibilities:
        - Build scalable backend systems
        - Mentor junior developers
        - Design system architecture
        - Collaborate with product team
        """
    }
    
    # Sample user profile
    sample_profile = {
        "cv": """
        John Doe
        Senior Software Engineer
        
        Experience:
        - 6 years Python development
        - Built REST APIs using Django
        - Managed PostgreSQL databases
        - Deployed applications on AWS
        - Led team of 3 developers
        
        Skills: Python, Django, Flask, PostgreSQL, AWS, Docker, Git, JavaScript
        
        Education: BS Computer Science
        """
    }
    
    print("🚀 Starting Job Hunter Agent Test...\n")
    
    result = await agent.process_job_application(sample_job, sample_profile)
    
    print("\n" + "="*60)
    print("📊 RESULTS:")
    print("="*60)
    print(f"\nJob: {result['job_title']} at {result['company']}")
    print(f"Status: {result['status']}")
    
    if "match" in result:
        print(f"\n🎯 Match Score: {result['match'].get('match_score', 'N/A')}%")
        print(f"Recommendation: {result['match'].get('recommendation', 'N/A')}")
    
    if "custom_cv" in result:
        print(f"\n📄 Customized CV (first 200 chars):")
        print(result['custom_cv'][:200] + "...")
    
    if "cover_letter" in result:
        print(f"\n✉️ Cover Letter (first 200 chars):")
        print(result['cover_letter'][:200] + "...")
    
    print("\n✅ Test complete!")

if __name__ == "__main__":
    asyncio.run(test_job_hunter())
