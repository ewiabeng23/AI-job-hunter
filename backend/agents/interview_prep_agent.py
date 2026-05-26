import anthropic
from typing import Dict, List
import json

class InterviewPrepAgent:
    """
    AI-powered interview preparation assistant
    Generates questions, answers, and research based on job description
    """
    
    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = "claude-sonnet-4-20250514"
    
    async def generate_interview_prep(self, job_data: Dict) -> Dict:
        """
        Generate comprehensive interview preparation materials
        """
        
        job_title = job_data.get("title", "")
        company = job_data.get("company", "")
        description = job_data.get("description", "")
        
        # Create comprehensive prompt
        prompt = f"""You are an expert career coach preparing a candidate for a job interview.

Job Title: {job_title}
Company: {company}
Job Description: {description}

Generate comprehensive interview preparation materials in JSON format:

1. Technical Questions (10 questions specific to this role)
2. Behavioral Questions (10 STAR method questions)
3. Company-Specific Questions (5 questions about {company})
4. Questions to Ask Interviewer (5 smart questions)
5. Sample Answers (detailed answers for top 5 technical questions)
6. Key Skills to Highlight (based on job description)
7. Interview Tips (5 specific tips for this role)

Return ONLY valid JSON with this structure:
{{
    "technical_questions": ["question1", "question2", ...],
    "behavioral_questions": ["question1", "question2", ...],
    "company_questions": ["question1", "question2", ...],
    "questions_to_ask": ["question1", "question2", ...],
    "sample_answers": [
        {{"question": "...", "answer": "..."}},
        ...
    ],
    "key_skills": ["skill1", "skill2", ...],
    "interview_tips": ["tip1", "tip2", ...]
}}"""

        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=4000,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            
            response_text = message.content[0].text
            
            # Clean response (remove markdown if present)
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            prep_data = json.loads(response_text)
            
            return {
                "status": "success",
                "job_title": job_title,
                "company": company,
                "prep_data": prep_data
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "message": "Failed to generate interview prep"
            }
    
    async def get_common_questions(self, job_category: str) -> List[Dict]:
        """
        Get common interview questions for a job category
        """
        
        common_questions = {
            "software": [
                {
                    "question": "Tell me about yourself",
                    "category": "General",
                    "tip": "Give a 2-minute professional summary focusing on relevant experience"
                },
                {
                    "question": "What are your greatest strengths?",
                    "category": "Behavioral",
                    "tip": "Choose 2-3 strengths relevant to the role with specific examples"
                },
                {
                    "question": "Describe a challenging project you worked on",
                    "category": "Behavioral",
                    "tip": "Use STAR method (Situation, Task, Action, Result)"
                },
                {
                    "question": "Where do you see yourself in 5 years?",
                    "category": "Career Goals",
                    "tip": "Show ambition but align with company's growth path"
                },
                {
                    "question": "Why do you want to work here?",
                    "category": "Company Fit",
                    "tip": "Research company values and connect to your goals"
                }
            ],
            "devops": [
                {
                    "question": "Explain CI/CD pipeline",
                    "category": "Technical",
                    "tip": "Walk through the stages with real examples from your experience"
                },
                {
                    "question": "How do you handle production incidents?",
                    "category": "Problem Solving",
                    "tip": "Describe your incident response process step by step"
                },
                {
                    "question": "What's your experience with containerization?",
                    "category": "Technical",
                    "tip": "Mention Docker, Kubernetes, and specific use cases"
                }
            ]
        }
        
        # Return generic software questions as fallback
        return common_questions.get(job_category.lower(), common_questions["software"])
