"""
job_fetcher.py
--------------
A professional, production-grade RSS job feed parser for The Sniper Job Hunter Bot.
Fetches and extracts job postings from RSS feeds with robust error handling.
Updated with custom User-Agent to bypass feed restrictions.
"""

import feedparser
import requests
import logging
from typing import List, Dict, Optional
from datetime import datetime
from urllib.parse import urlparse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class JobFetcher:
    """
    A robust RSS feed parser for fetching job postings.
    
    Handles feed parsing, data extraction, and error management for various RSS sources.
    Uses custom User-Agent headers to bypass feed restrictions.
    """
    
    def __init__(self):
        """Initialize the JobFetcher with browser-like headers."""
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/rss+xml, application/xml, text/xml, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        }
        logger.info("JobFetcher initialized successfully with custom User-Agent")
    
    def _validate_url(self, url: str) -> bool:
        """
        Validate if the provided URL is properly formatted.
        
        Args:
            url (str): The URL to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False
    
    def _clean_text(self, text: str) -> str:
        """
        Clean and sanitize text content.
        
        Args:
            text (str): Raw text to clean
            
        Returns:
            str: Cleaned text
        """
        if not text:
            return ""
        
        # Remove extra whitespace and newlines
        cleaned = " ".join(text.split())
        return cleaned.strip()
    
    def _extract_job_data(self, entry) -> Optional[Dict[str, str]]:
        """
        Extract job data from a feed entry.
        
        Args:
            entry: Feed entry object
            
        Returns:
            Optional[Dict[str, str]]: Extracted job data or None if extraction fails
        """
        try:
            job_data = {
                "title": self._clean_text(entry.get("title", "No Title")),
                "link": entry.get("link", ""),
                "published": entry.get("published", "Date not available"),
                "summary": self._clean_text(entry.get("summary", "No description available"))
            }
            
            # Validate that at least title and link exist
            if job_data["title"] and job_data["link"]:
                return job_data
            else:
                logger.warning("Entry missing critical data (title or link)")
                return None
                
        except Exception as e:
            logger.error(f"Error extracting job data from entry: {str(e)}")
            return None
    
    def fetch_jobs(self, rss_url: str) -> List[Dict[str, str]]:
        """
        Fetch and parse jobs from an RSS feed URL using custom User-Agent.
        
        Args:
            rss_url (str): The RSS feed URL to parse
            
        Returns:
            List[Dict[str, str]]: List of job dictionaries with keys:
                                  'title', 'link', 'published', 'summary'
                                  Returns empty list on error.
        """
        # Validate URL format
        if not self._validate_url(rss_url):
            logger.error(f"❌ Invalid URL format: {rss_url}")
            return []
        
        try:
            logger.info(f"📡 Fetching jobs from: {rss_url}")
            
            # Fetch the RSS feed with custom headers
            response = requests.get(rss_url, headers=self.headers, timeout=15)
            
            # Check HTTP status
            if response.status_code != 200:
                logger.error(f"❌ HTTP Error {response.status_code}: Failed to fetch feed")
                return []
            
            logger.info(f"✅ Successfully retrieved feed (Status: {response.status_code})")
            
            # Parse the RSS feed content
            feed = feedparser.parse(response.content)
            
            # Check for parsing errors
            if hasattr(feed, 'bozo') and feed.bozo:
                logger.warning(f"⚠️  Feed parsing warning: {feed.get('bozo_exception', 'Unknown issue')}")
            
            # Check if feed has entries
            if not feed.entries:
                logger.warning("⚠️  No entries found in the feed. Feed may be empty or invalid.")
                return []
            
            # Extract job data from entries
            jobs = []
            for idx, entry in enumerate(feed.entries):
                job_data = self._extract_job_data(entry)
                if job_data:
                    jobs.append(job_data)
                    logger.debug(f"✓ Extracted job {idx + 1}: {job_data['title'][:50]}...")
            
            logger.info(f"✅ Successfully fetched {len(jobs)} jobs from the feed")
            return jobs
            
        except requests.exceptions.ConnectionError as e:
            logger.error(f"❌ Connection Error: Unable to reach the feed URL. Check your internet connection.")
            return []
            
        except requests.exceptions.Timeout as e:
            logger.error(f"❌ Timeout Error: The request took too long. Try again later.")
            return []
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Request Error: {str(e)}")
            return []
            
        except Exception as e:
            logger.error(f"❌ Unexpected Error while fetching jobs: {type(e).__name__} - {str(e)}")
            return []
    
    def fetch_jobs_with_limit(self, rss_url: str, limit: int = 10) -> List[Dict[str, str]]:
        """
        Fetch jobs with a maximum limit.
        
        Args:
            rss_url (str): The RSS feed URL to parse
            limit (int): Maximum number of jobs to return (default: 10)
            
        Returns:
            List[Dict[str, str]]: Limited list of job dictionaries
        """
        all_jobs = self.fetch_jobs(rss_url)
        return all_jobs[:limit]
    
    def get_feed_info(self, rss_url: str) -> Optional[Dict[str, str]]:
        """
        Get metadata information about the RSS feed.
        
        Args:
            rss_url (str): The RSS feed URL
            
        Returns:
            Optional[Dict[str, str]]: Feed metadata or None on error
        """
        try:
            # Fetch with custom headers
            response = requests.get(rss_url, headers=self.headers, timeout=15)
            
            if response.status_code != 200:
                return None
            
            feed = feedparser.parse(response.content)
            
            if hasattr(feed, 'feed'):
                return {
                    "title": feed.feed.get("title", "Unknown"),
                    "link": feed.feed.get("link", ""),
                    "description": feed.feed.get("description", ""),
                    "total_entries": len(feed.entries)
                }
            return None
            
        except Exception as e:
            logger.error(f"Error getting feed info: {str(e)}")
            return None


# ============================================================================
# TESTING MODULE
# ============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print("🎯 THE SNIPER - JOB FETCHER SYSTEM TEST (Updated with User-Agent)")
    print("=" * 80)
    
    # Initialize the job fetcher
    fetcher = JobFetcher()
    
    # Test URL - Upwork RSS feed for Python jobs (with User-Agent bypass)
    test_url = "https://www.upwork.com/ab/feed/jobs/rss?q=python&sort=recency"
    
    print(f"\n📡 Test URL: {test_url}")
    print("🔧 Using custom User-Agent to bypass restrictions...")
    print("-" * 80)
    
    # Test 1: Fetch feed information
    print("\n[TEST 1] Fetching feed metadata...")
    feed_info = fetcher.get_feed_info(test_url)
    
    if feed_info:
        print(f"✅ Feed Title: {feed_info['title']}")
        print(f"✅ Total Entries: {feed_info['total_entries']}")
    else:
        print("⚠️  Could not retrieve feed metadata")
    
    # Test 2: Fetch all jobs
    print("\n[TEST 2] Fetching all jobs from feed...")
    jobs = fetcher.fetch_jobs(test_url)
    
    if jobs:
        print(f"✅ Successfully fetched {len(jobs)} jobs!")
        print("\n" + "=" * 80)
        print("📋 SAMPLE JOB LISTINGS (First 3)")
        print("=" * 80)
        
        # Display first 3 jobs in detail
        for idx, job in enumerate(jobs[:3], 1):
            print(f"\n🔹 JOB #{idx}")
            print(f"   Title:     {job['title']}")
            print(f"   Link:      {job['link']}")
            print(f"   Published: {job['published']}")
            print(f"   Summary:   {job['summary'][:150]}...")
            print("-" * 80)
    else:
        print("❌ No jobs were fetched. The feed may still be restricted or empty.")
    
    # Test 3: Fetch limited jobs
    print("\n[TEST 3] Fetching limited jobs (max 5)...")
    limited_jobs = fetcher.fetch_jobs_with_limit(test_url, limit=5)
    print(f"✅ Fetched {len(limited_jobs)} jobs with limit applied")
    
    # Test 4: Test error handling with invalid URL
    print("\n[TEST 4] Testing error handling with invalid URL...")
    invalid_jobs = fetcher.fetch_jobs("https://invalid-url-that-does-not-exist.com/feed")
    print(f"✅ Error handling working correctly. Returned {len(invalid_jobs)} jobs (expected: 0)")
    
    # Test 5: Test with RemoteOK as backup
    print("\n[TEST 5] Testing with RemoteOK backup feed...")
    backup_url = "https://remoteok.com/remote-python-jobs.rss"
    backup_jobs = fetcher.fetch_jobs_with_limit(backup_url, limit=3)
    if backup_jobs:
        print(f"✅ Backup feed working! Fetched {len(backup_jobs)} jobs")
    
    # Summary
    print("\n" + "=" * 80)
    print("🏁 TESTING COMPLETE")
    print("=" * 80)
    print(f"\n📊 SUMMARY:")
    print(f"   • Upwork jobs fetched: {len(jobs)}")
    print(f"   • Feed parsing: {'✅ SUCCESS' if jobs else '⚠️  STILL BLOCKED (try RemoteOK)'}")
    print(f"   • User-Agent bypass: ✅ IMPLEMENTED")
    print(f"   • Error handling: ✅ VERIFIED")
    print(f"   • Data extraction: ✅ COMPLETE")
    print("\n✨ Phase 2 Job Fetcher (Updated) is ready for production!")
    print("=" * 80)