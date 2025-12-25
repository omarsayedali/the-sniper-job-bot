"""
The Sniper - Job Hunter Bot
Professional automated job monitoring system
"""

import sqlite3
import time
import logging
import html
from datetime import datetime
from notifier import TelegramNotifier
from job_fetcher import JobFetcher

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
# CONFIGURATION - EDIT THESE
# ============================================================================

TELEGRAM_TOKEN = "8329505275:AAFsbYpt2EAYyx1y5sfD9fU9eW9DrlVIsQ8"
TELEGRAM_CHAT_ID = "1277763542"

RSS_FEEDS = [
    "https://mostaql.com/rss",
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
# MAIN BOT CLASS
# ============================================================================

class SniperBot:
    def __init__(self):
        logger.info("🎯 Initializing The Sniper...")
        self.notifier = TelegramNotifier(TELEGRAM_TOKEN, TELEGRAM_CHAT_ID)
        self.fetcher = JobFetcher()
        self.db = JobDatabase()
        self.cycle_count = 0
        logger.info("✅ The Sniper is ready!")
    
    def format_alert(self, job, source):
        """Create a clean job alert message"""
        title = html.escape(job['title'])
        summary = html.escape(job['summary'][:200])
        
        return f"""🎯 <b>NEW JOB ALERT</b>

<b>{title}</b>

🔗 {job['link']}

📅 {job['published']}
📡 {source}

{summary}...
"""
    
    def check_feeds(self):
        """Check all feeds for new jobs"""
        self.cycle_count += 1
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
            new_jobs = [j for j in jobs if self.db.is_new_job(j['link'])]
            
            logger.info(f"   Found {len(jobs)} total, {len(new_jobs)} new")
            
            if is_first_run:
                all_new_jobs.extend([(j, source) for j in new_jobs])
            else:
                # Send alerts for new jobs
                for job in new_jobs:
                    self.notifier.send_message(self.format_alert(job, source))
                    self.db.save_job(job)
                    logger.info(f"   ✅ Alerted: {job['title'][:40]}...")
                    time.sleep(2)
        
        # Handle first run
        if is_first_run and all_new_jobs:
            logger.info(f"🆕 First run: alerting {FIRST_RUN_ALERT_LIMIT} newest jobs")
            for job, source in all_new_jobs[:FIRST_RUN_ALERT_LIMIT]:
                self.notifier.send_message(self.format_alert(job, source))
                self.db.save_job(job)
                time.sleep(2)
            
            for job, source in all_new_jobs[FIRST_RUN_ALERT_LIMIT:]:
                self.db.save_job(job)
        
        logger.info(f"💾 Total jobs tracked: {self.db.count()}")
        logger.info(f"{'='*60}\n")
    
    def run(self):
        """Main loop"""
        try:
            self.notifier.send_message("🔴 <b>SYSTEM ONLINE</b>\n\nThe Sniper is now hunting jobs! 🎯")
            logger.info(f"⏰ Checking every {CHECK_INTERVAL_MINUTES} minutes\n")
            
            while True:
                self.check_feeds()
                logger.info(f"😴 Sleeping {CHECK_INTERVAL_MINUTES} minutes...\n")
                time.sleep(CHECK_INTERVAL_MINUTES * 60)
                
        except KeyboardInterrupt:
            logger.info("\n🛑 Shutting down...")
            self.notifier.send_message("🔵 <b>SYSTEM OFFLINE</b>\n\nThe Sniper has shut down.")
            logger.info("👋 Goodbye!")

# ============================================================================
# START THE BOT
# ============================================================================

if __name__ == "__main__":
    print("""
╔═══════════════════════════════════════╗
║   🎯 THE SNIPER - JOB HUNTER BOT 🎯  ║
╚═══════════════════════════════════════╝
    """)
    
    bot = SniperBot()
    bot.run()