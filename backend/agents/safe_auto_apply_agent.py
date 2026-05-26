import asyncio
from playwright.async_api import async_playwright
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import logging
from datetime import datetime
from typing import Dict, List
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SafeAutoApplyAgent:
    """
    Safe job application agent:
    - LinkedIn: Semi-automated (opens + assists, YOU submit)
    - Indeed/Others: Fully automated via email (no account needed)
    """
    
    def __init__(self, your_email: str = "", email_password: str = ""):
        self.your_email = your_email
        self.email_password = email_password
        self.applications_submitted = []
        
    async def linkedin_assisted_apply(self, job_url: str, custom_cv: str, cover_letter: str) -> Dict:
        """
        LinkedIn ASSISTED application (semi-automated - SAFE)
        - Opens job in browser
        - Shows you the CV and cover letter
        - Copies them to clipboard
        - YOU click the final submit button
        """
        logger.info(f"🎯 LinkedIn Assisted Apply: {job_url}")
        
        try:
            async with async_playwright() as p:
                # Launch browser (headless=False so user sees it)
                browser = await p.chromium.launch(headless=False)
                context = await browser.new_context()
                page = await context.new_page()
                
                # Navigate to job
                await page.goto(job_url)
                await page.wait_for_load_state("networkidle")
                
                # Copy CV to clipboard
                await page.evaluate(f"""
                    navigator.clipboard.writeText(`{custom_cv.replace('`', '').replace('\n', '\\n')}`);
                    alert('✅ CV copied to clipboard!\\n\\nNow click Easy Apply and paste your CV when needed.\\n\\nCover letter will be copied next.');
                """)
                
                await asyncio.sleep(3)
                
                # Copy cover letter to clipboard
                await page.evaluate(f"""
                    navigator.clipboard.writeText(`{cover_letter.replace('`', '').replace('\n', '\\n')}`);
                    alert('✅ Cover letter copied to clipboard!\\n\\nPaste this when LinkedIn asks for additional info.\\n\\nNow YOU click Submit!');
                """)
                
                # Keep browser open for user to finish
                logger.info("✅ Browser open - YOU can now complete the application!")
                logger.info("🔔 The browser will stay open. Close it when done.")
                
                # Wait for user to close browser manually
                await asyncio.sleep(300)  # Wait 5 minutes max
                
                await browser.close()
                
                return {
                    "status": "assisted",
                    "job_url": job_url,
                    "message": "Browser opened, user completes application"
                }
                
        except Exception as e:
            logger.error(f"❌ Error: {str(e)}")
            return {"status": "failed", "error": str(e)}
    
    async def indeed_email_apply(self, job_data: Dict, custom_cv: str, cover_letter: str) -> Dict:
        """
        Indeed/Glassdoor - Apply via EMAIL (no account needed, fully automated)
        Many jobs have "Apply by Email" option
        """
        logger.info(f"📧 Email application to: {job_data.get('company')}")
        
        # Extract email from job description if available
        description = job_data.get("description", "")
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, description)
        
        if not emails:
            # Check if job URL has email parameter
            job_url = job_data.get("url", "")
            if "mailto:" in job_url:
                emails = [job_url.split("mailto:")[1].split("?")[0]]
        
        if not emails:
            return {
                "status": "no_email",
                "message": "No email found - job requires online application"
            }
        
        recruiter_email = emails[0]
        
        # Send application via email
        result = await self._send_application_email(
            to_email=recruiter_email,
            job_title=job_data.get("title", ""),
            company=job_data.get("company", ""),
            cv_text=custom_cv,
            cover_letter=cover_letter
        )
        
        return result
    
    async def _send_application_email(self, to_email: str, job_title: str, 
                                     company: str, cv_text: str, cover_letter: str) -> Dict:
        """
        Send job application via email
        """
        if not self.your_email or not self.email_password:
            return {
                "status": "no_credentials",
                "message": "Email credentials not configured"
            }
        
        try:
            # Create email
            msg = MIMEMultipart()
            msg['From'] = self.your_email
            msg['To'] = to_email
            msg['Subject'] = f"Application for {job_title} at {company}"
            
            # Email body (cover letter)
            body = f"""
Dear Hiring Manager,

{cover_letter}

Please find my CV attached.

Best regards,
[Your Name]
"""
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Attach CV as text file
            cv_attachment = MIMEApplication(cv_text.encode('utf-8'), _subtype="txt")
            cv_attachment.add_header('Content-Disposition', 'attachment', filename='CV.txt')
            msg.attach(cv_attachment)
            
            # Send email via Gmail SMTP
            async with aiosmtplib.SMTP(hostname="smtp.gmail.com", port=587) as smtp:
                await smtp.starttls()
                await smtp.login(self.your_email, self.email_password)
                await smtp.send_message(msg)
            
            logger.info(f"✅ Email application sent to {to_email}")
            
            return {
                "status": "sent",
                "to_email": to_email,
                "job_title": job_title,
                "company": company,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to send email: {str(e)}")
            return {
                "status": "failed",
                "error": str(e)
            }
    
    async def smart_apply(self, job_data: Dict, custom_cv: str, cover_letter: str) -> Dict:
        """
        Smart application router:
        - LinkedIn → Semi-automated (safe)
        - Indeed/Others with email → Fully automated
        - Others → Return info for manual application
        """
        job_url = job_data.get("url", "")
        source = job_data.get("source", "")
        
        if "linkedin.com" in job_url or source == "LinkedIn":
            # LinkedIn: Assisted mode (safe)
            return await self.linkedin_assisted_apply(job_url, custom_cv, cover_letter)
        
        elif source in ["Indeed", "Glassdoor"] or "indeed.com" in job_url or "glassdoor.com" in job_url:
            # Indeed/Glassdoor: Try email application
            result = await self.indeed_email_apply(job_data, custom_cv, cover_letter)
            
            if result["status"] == "no_email":
                # No email found, return manual application info
                return {
                    "status": "manual_required",
                    "job_url": job_url,
                    "message": "Please apply manually via the link",
                    "cv": custom_cv,
                    "cover_letter": cover_letter
                }
            
            return result
        
        else:
            # Unknown platform
            return {
                "status": "manual_required",
                "job_url": job_url,
                "message": "Platform not supported - apply manually",
                "cv": custom_cv,
                "cover_letter": cover_letter
            }
    
    async def bulk_smart_apply(self, jobs_with_applications: List[Dict]) -> Dict:
        """
        Apply to multiple jobs intelligently:
        - LinkedIn jobs: Opens browser tabs (you submit)
        - Email jobs: Sends automatically
        - Others: Prepares for manual application
        """
        results = {
            "linkedin_assisted": [],
            "email_sent": [],
            "manual_required": [],
            "failed": []
        }
        
        for job in jobs_with_applications:
            job_data = job.get("job_data", {})
            custom_cv = job.get("custom_cv", "")
            cover_letter = job.get("cover_letter", "")
            
            result = await self.smart_apply(job_data, custom_cv, cover_letter)
            
            if result["status"] == "assisted":
                results["linkedin_assisted"].append(result)
            elif result["status"] == "sent":
                results["email_sent"].append(result)
            elif result["status"] == "manual_required":
                results["manual_required"].append(result)
            else:
                results["failed"].append(result)
            
            # Delay between applications
            await asyncio.sleep(3)
        
        summary = {
            "total_jobs": len(jobs_with_applications),
            "linkedin_assisted": len(results["linkedin_assisted"]),
            "email_sent": len(results["email_sent"]),
            "manual_required": len(results["manual_required"]),
            "failed": len(results["failed"]),
            "results": results
        }
        
        logger.info(f"\n{'='*60}")
        logger.info(f"📊 BULK APPLICATION SUMMARY")
        logger.info(f"{'='*60}")
        logger.info(f"Total Jobs: {summary['total_jobs']}")
        logger.info(f"LinkedIn Assisted: {summary['linkedin_assisted']} (YOU submit)")
        logger.info(f"Email Sent: {summary['email_sent']} (Auto-sent!)")
        logger.info(f"Manual Required: {summary['manual_required']}")
        logger.info(f"Failed: {summary['failed']}")
        logger.info(f"{'='*60}\n")
        
        return summary


# Test
async def test_safe_apply():
    agent = SafeAutoApplyAgent(
        your_email="YOUR_EMAIL@gmail.com",  # For email applications
        email_password="YOUR_APP_PASSWORD"   # Gmail app password
    )
    
    # Test LinkedIn assisted mode
    linkedin_job = {
        "url": "https://www.linkedin.com/jobs/view/test",
        "source": "LinkedIn"
    }
    
    cv = "Your CV here"
    cover = "Your cover letter here"
    
    result = await agent.smart_apply(linkedin_job, cv, cover)
    print(result)


if __name__ == "__main__":
    asyncio.run(test_safe_apply())
