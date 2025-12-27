"""
ai_drafter.py
-------------
AI-powered proposal generator using Google Gemini API
Automatically drafts professional proposals for freelance jobs
"""

import google.generativeai as genai
import logging
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURATION
# ============================================================================

api_key = os.getenv("GEMINI_API_KEY")

# Configure Gemini
genai.configure(api_key = os.getenv("GEMINI_API_KEY"))

# ============================================================================
# AI PROPOSAL GENERATOR
# ============================================================================

class AIProposalDrafter:
    """
    AI-powered proposal drafter using Google Gemini
    """
    
    def __init__(self, api_key = os.getenv("GEMINI_API_KEY")):
        """Initialize the AI drafter with API key"""
        self.api_key = api_key
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-pro')
        logger.info("✅ AI Proposal Drafter initialized")
    
    def generate_proposal(self, job_title, job_description):
        """
        Generate a professional proposal for a job
        
        Args:
            job_title (str): The job title
            job_description (str): The job description
            
        Returns:
            str: Generated proposal or error message
        """
        try:
            # Clean and truncate description if too long
            clean_description = job_description[:500] if len(job_description) > 500 else job_description
            
            # Craft the prompt
            prompt = f"""
Act as a Senior Python Freelancer with 5+ years of experience.

Write a short, punchy, and professional proposal for this job:

JOB TITLE: {job_title}

JOB DESCRIPTION: {clean_description}

GUIDELINES:
- Start with understanding their problem
- Mention relevant skills: Python, Flask, Django, Web Scraping, Selenium, Automation, API Development, Backend
- Keep it under 150 words
- Be confident but not arrogant
- End with a clear call to action
- Don't use generic templates
- Focus on solving THEIR specific problem

Write the proposal now:
"""
            
            logger.info(f"🤖 Generating proposal for: {job_title[:50]}...")
            
            # Generate content
            response = self.model.generate_content(prompt)
            proposal = response.text.strip()
            
            logger.info("✅ Proposal generated successfully")
            return proposal
            
        except Exception as e:
            logger.error(f"❌ Error generating proposal: {e}")
            return f"[AI Generation Failed: {str(e)}]\n\nPlease draft proposal manually for this job."
    
    def generate_quick_intro(self):
        """Generate a quick introduction line"""
        intros = [
            "Hi! I'm a Python developer specializing in automation and web scraping.",
            "Hello! Python automation expert here, ready to solve your problem.",
            "Hi there! I build robust Python solutions for automation and data extraction.",
        ]
        import random
        return random.choice(intros)


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def test_ai_drafter():
    """Test the AI drafter with a sample job"""
    drafter = AIProposalDrafter()
    
    sample_title = "Python Web Scraping Bot Needed"
    sample_description = "I need someone to build a bot that scrapes product data from e-commerce sites daily."
    
    print("=" * 60)
    print("🧪 TESTING AI PROPOSAL DRAFTER")
    print("=" * 60)
    print(f"\nJob: {sample_title}")
    print(f"Description: {sample_description}\n")
    print("-" * 60)
    print("🤖 GENERATED PROPOSAL:")
    print("-" * 60)
    
    proposal = drafter.generate_proposal(sample_title, sample_description)
    print(proposal)
    print("\n" + "=" * 60)


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    test_ai_drafter()