"""
The Sniper V2.0 - Job Hunter Bot
Professional automated job monitoring system with AI proposal generation
"""

import sqlite3
import time
import logging
import html
from datetime import datetime
from notifier import TelegramNotifier
from job_fetcher import JobFetcher
from ai_drafter import AIProposalDrafter
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('sniper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURATION
# ============================================================================

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

RSS_FEEDS = [
    "https://mostaql.com/rss",
]

# Smart Filter Keywords (Case Insensitive)
FILTER_KEYWORDS = [
    'python', 'flask', 'django', 'scraping', 'selenium', 
    'automation', 'bot', 'api', 'backend', 'fastapi',
    'web scraping', 'data extraction', 'crawler'
]

CHECK_INTERVAL_MINUTES = 10
FIRST_RUN_ALERT_LIMIT = 3

# ============================================================================
# DATABASE CLASS
# ============================================================================

class JobDatabase:
    def __init__(self):
        self.connection = sqlite3.connect('sniper_jobs.db')
        self.cursor = self.connection.cursor()
        self._setup()
    
    def _setup(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS seen_jobs (
                job_link TEXT PRIMARY KEY,
                title TEXT,
                published TEXT,
                seen_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.connection.commit()
    
    def is_new_job(self, link):
        self.cursor.execute("SELECT 1 FROM seen_jobs WHERE job_link = ?", (link,))
        return self.cursor.fetchone() is None
    
    def save_job(self, job):
        self.cursor.execute(
            "INSERT OR IGNORE INTO seen_jobs (job_link, title, published) VALUES (?, ?, ?)",
            (job['link'], job['title'], job['published'])
        )
        self.connection.commit()
    
    def is_empty(self):
        self.cursor.execute("SELECT COUNT(*) FROM seen_jobs")
        return self.cursor.fetchone()[0] == 0
    
    def count(self):
        self.cursor.execute("SELECT COUNT(*) FROM seen_jobs")
        return self.cursor.fetchone()[0]

# ============================================================================
# SMART JOB FILTER
# ============================================================================

class SmartJobFilter:
    """
    Filters jobs based on relevant keywords
    """
    
    def __init__(self, keywords):
        self.keywords = [k.lower() for k in keywords]
        logger.info(f"🔍 Smart Filter initialized with {len(self.keywords)} keywords")
    
    def is_relevant(self, job_title, job_description):
        """
        Check if job is relevant based on keywords
        
        Args:
            job_title (str): Job title
            job_description (str): Job description
            
        Returns:
            bool: True if relevant, False otherwise
        """
        # Combine title and description
        text = f"{job_title} {job_description}".lower()
        
        # Check if any keyword is present
        for keyword in self.keywords:
            if keyword in text:
                logger.info(f"✅ Job matched keyword: '{keyword}'")
                return True
        
        logger.info(f"❌ Job filtered out: No relevant keywords found")
        return False

# ============================================================================
# MAIN BOT CLASS - V2.0
# ============================================================================

class SniperBotV2:
    def __init__(self):
        logger.info("=" * 60)
        logger.info("🎯 THE SNIPER V2.0 - INITIALIZING")
        logger.info("=" * 60)
        
        # Initialize components
        self.notifier = TelegramNotifier(TELEGRAM_TOKEN, CHAT_ID)
        self.fetcher = JobFetcher()
        self.db = JobDatabase()
        self.filter = SmartJobFilter(FILTER_KEYWORDS)
        self.ai_drafter = AIProposalDrafter()
        
        # Track statistics
        self.cycle_count = 0
        self.total_jobs_found = 0
        self.filtered_jobs = 0
        self.relevant_jobs = 0
        
        logger.info("✅ All components initialized")
        logger.info("🤖 AI Proposal Drafter: READY")
        logger.info("🔍 Smart Filter: ACTIVE")
    
    def format_alert_with_proposal(self, job, source, proposal):
        """
        Create an enhanced job alert with AI-generated proposal
        
        Args:
            job (Dict): Job data
            source (str): Source name
            proposal (str): AI-generated proposal
            
        Returns:
            str: Formatted message
        """
        title = html.escape(job['title'])
        
        message = f"""🎯 <b>NEW RELEVANT JOB FOUND!</b>

📌 <b>{title}</b>

🔗 <b>Link:</b> {job['link']}

📅 <b>Published:</b> {job['published']}
📡 <b>Source:</b> {source}

🤖 <b>AI-GENERATED PROPOSAL:</b>
<code>{html.escape(proposal)}</code>

💡 <b>Tip:</b> Copy the proposal above and customize it before sending!
"""
        return message
    
    def check_feeds(self):
        """Check all feeds for new relevant jobs"""
        self.cycle_count += 1
        cycle_relevant_jobs = 0
        cycle_filtered = 0
        
        logger.info(f"\n{'='*60}")
        logger.info(f"🔄 CYCLE #{self.cycle_count} - {datetime.now().strftime('%H:%M:%S')}")
        logger.info(f"{'='*60}")
        
        is_first_run = self.db.is_empty()
        all_new_jobs = []
        
        # Check each feed
        for feed_url in RSS_FEEDS:
            source = feed_url.split('/')[2].replace('www.', '').split('.')[0].title()
            logger.info(f"🔍 Checking {source}...")
            
            jobs = self.fetcher.fetch_jobs(feed_url)
            self.total_jobs_found += len(jobs)
            
            new_jobs = [j for j in jobs if self.db.is_new_job(j['link'])]
            logger.info(f"   Found {len(jobs)} total, {len(new_jobs)} new")
            
            # Filter for relevance
            for job in new_jobs:
                is_relevant = self.filter.is_relevant(job['title'], job['summary'])
                
                if is_relevant:
                    logger.info(f"   ✅ RELEVANT: {job['title'][:50]}...")
                    self.relevant_jobs += 1
                    
                    if is_first_run:
                        all_new_jobs.append((job, source))
                    else:
                        # Generate proposal
                        logger.info("   🤖 Generating AI proposal...")
                        proposal = self.ai_drafter.generate_proposal(
                            job['title'],
                            job['summary']
                        )
                        
                        # Send alert with proposal
                        self.notifier.send_message(
                            self.format_alert_with_proposal(job, source, proposal)
                        )
                        self.db.save_job(job)
                        cycle_relevant_jobs += 1
                        time.sleep(2)
                else:
                    logger.info(f"   ⏭️  FILTERED: {job['title'][:50]}...")
                    self.db.save_job(job)  # Save but don't alert
                    self.filtered_jobs += 1
                    cycle_filtered += 1
        
        # Handle first run
        if is_first_run and all_new_jobs:
            logger.info(f"🆕 First run: alerting {min(len(all_new_jobs), FIRST_RUN_ALERT_LIMIT)} newest relevant jobs")
            for job, source in all_new_jobs[:FIRST_RUN_ALERT_LIMIT]:
                proposal = self.ai_drafter.generate_proposal(job['title'], job['summary'])
                self.notifier.send_message(
                    self.format_alert_with_proposal(job, source, proposal)
                )
                self.db.save_job(job)
                time.sleep(2)
            
            for job, source in all_new_jobs[FIRST_RUN_ALERT_LIMIT:]:
                self.db.save_job(job)
        
        # Summary
        logger.info(f"\n📊 Cycle Summary:")
        logger.info(f"   • Relevant jobs alerted: {cycle_relevant_jobs}")
        logger.info(f"   • Irrelevant jobs filtered: {cycle_filtered}")
        logger.info(f"💾 Total jobs tracked: {self.db.count()}")
        logger.info(f"{'='*60}\n")
    
    def run(self):
        """Main loop"""
        try:
            self.notifier.send_message(
                "🔴 <b>THE SNIPER V2.0 ONLINE</b>\n\n"
                "✨ New Features:\n"
                "• 🔍 Smart keyword filtering\n"
                "• 🤖 AI-generated proposals\n"
                "• 📊 Enhanced job matching\n\n"
                "Ready to hunt relevant jobs! 🎯"
            )
            
            logger.info(f"⏰ Checking every {CHECK_INTERVAL_MINUTES} minutes\n")
            
            while True:
                self.check_feeds()
                logger.info(f"😴 Sleeping {CHECK_INTERVAL_MINUTES} minutes...\n")
                time.sleep(CHECK_INTERVAL_MINUTES * 60)
                
        except KeyboardInterrupt:
            logger.info("\n🛑 Shutting down...")
            
            stats_message = f"""🔵 <b>THE SNIPER V2.0 OFFLINE</b>

📊 <b>Session Statistics:</b>
• Cycles: {self.cycle_count}
• Total jobs: {self.total_jobs_found}
• Relevant: {self.relevant_jobs}
• Filtered out: {self.filtered_jobs}
• Database: {self.db.count()} jobs

👋 Shutdown complete!"""
            
            self.notifier.send_message(stats_message)
            logger.info("👋 Goodbye!")


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    print("""
╔═══════════════════════════════════════════════════════╗
║   🎯 THE SNIPER V2.0 - AI-POWERED JOB HUNTER 🤖      ║
║                                                       ║
║   ✨ Smart Filtering  |  🤖 AI Proposals             ║
╚═══════════════════════════════════════════════════════╝
    """)
    
    bot = SniperBotV2()
    bot.run()