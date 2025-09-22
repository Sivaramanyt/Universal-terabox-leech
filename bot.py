#!/usr/bin/env python3
"""
Ultimate Terabox Bot with Configurable Shortlink System
Mobile-Optimized for Koyeb Free Tier
Premium Plans: 2h=₹5, 6h=₹10, 12h=₹15, 24h=₹20
Configurable Shortlink API Support
"""

import asyncio
import logging
import os
import re
import requests
import json
import hashlib
import time
import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict, List

from telethon import TelegramClient, events, Button
from telethon.tl.types import DocumentAttributeVideo, DocumentAttributeFilename

# Setup logging for mobile deployment
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
class Config:
    """Configuration with configurable shortlink system"""
    
    # Essential Bot Settings
    BOT_TOKEN = os.getenv("BOT_TOKEN", "")
    API_ID = int(os.getenv("API_ID", "29542645"))
    API_HASH = os.getenv("API_HASH", "06e505b8418565356ae79365df5d69e0")
    
    # Channels
    SAVE_CHANNEL = int(os.getenv("SAVE_CHANNEL", "-1003068078005"))
    PAYMENT_CHANNEL = int(os.getenv("PAYMENT_CHANNEL", "-1003037490791"))
    
    # Admin Settings
    OWNER_ID = int(os.getenv("OWNER_ID", "1206988513"))
    ADMIN_IDS = [int(x) for x in os.getenv("ADMIN_IDS", "").split() if x.strip()]
    
    # Payment System
    GPAY_UPI_ID = os.getenv("GPAY_UPI_ID", "sivaramanc49@okaxis")
    
    # CONFIGURABLE SHORTLINK SYSTEM - Change these for any service!
    SHORTLINK_URL = os.getenv("SHORTLINK_URL", "https://arolinks.com")
    SHORTLINK_API = os.getenv("SHORTLINK_API", "139ebf8c6591acc6a69db83f200f2285874dbdbf")
    
    # Premium Plans (Indian Rupees)
    PREMIUM_PLANS = {
        "2h": {"hours": 2, "price": 5, "name": "⚡ Quick Access", "description": "Perfect for urgent downloads"},
        "6h": {"hours": 6, "price": 10, "name": "📱 Standard Access", "description": "Great for regular use"}, 
        "12h": {"hours": 12, "price": 15, "name": "🔥 Extended Access", "description": "Best value for heavy users"},
        "24h": {"hours": 24, "price": 20, "name": "👑 Full Day Access", "description": "Maximum convenience"}
    }
    
    # Other Settings
    FREE_DOWNLOADS = int(os.getenv("FREE_DOWNLOADS", "3"))
    TERABOX_COOKIE = os.getenv("TERABOX_COOKIE", "lang=en; BAIDUID=mobile123:FG=1; BDUSS=mobilesession456; STOKEN=token789; ndus=mobileworking123;")
    
    MAX_FILE_SIZE = 1.5 * 1024 * 1024 * 1024  # 1.5GB for free users
    PREMIUM_MAX_SIZE = 2.5 * 1024 * 1024 * 1024  # 2.5GB for premium
    TOKEN_VALIDITY_HOURS = int(os.getenv("TOKEN_VALIDITY_HOURS", "24"))
class ShortlinkAPI:
    """Universal Shortlink API integration - supports multiple services"""
    
    def __init__(self):
        self.api_key = Config.SHORTLINK_API
        self.base_url = Config.SHORTLINK_URL
        
    def shorten_url(self, long_url):
        """Shorten URL using configured shortlink service"""
        try:
            # Different API patterns for different services
            if "arolinks.com" in self.base_url:
                return self._arolinks_shorten(long_url)
            elif "adf.ly" in self.base_url:
                return self._adfly_shorten(long_url)
            elif "shorte.st" in self.base_url:
                return self._shortest_shorten(long_url)
            elif "ouo.io" in self.base_url:
                return self._ouo_shorten(long_url)
            elif "gplinks" in self.base_url:
                return self._gplinks_shorten(long_url)
            else:
                # Generic API pattern
                return self._generic_shorten(long_url)
                
        except Exception as e:
            logger.error(f"Shortlink API error: {e}")
            return long_url  # Return original URL if shortening fails
    
    def _arolinks_shorten(self, url):
        """AroLinks API"""
        payload = {'api': self.api_key, 'url': url}
        response = requests.get(f"https://arolinks.com/api", params=payload, timeout=10)
        data = response.json()
        return data.get('shortenedUrl') if data.get('status') == 'success' else url
    
    def _adfly_shorten(self, url):
        """AdFly API"""
        api_url = f"https://api.adf.ly/api.php?key={self.api_key}&uid=YOUR_UID&advert_type=int&domain=adf.ly&url={url}"
        response = requests.get(api_url, timeout=10)
        return response.text.strip() if response.status_code == 200 else url
    
    def _shortest_shorten(self, url):
        """Shorte.st API"""
        payload = {'urlToShorten': url}
        headers = {'public-api-token': self.api_key}
        response = requests.put("https://api.shorte.st/v1/data/url", json=payload, headers=headers, timeout=10)
        data = response.json()
        return data.get('shortenedUrl') if data.get('status') == 'ok' else url
    
    def _ouo_shorten(self, url):
        """Ouo.io API"""
        api_url = f"http://ouo.io/api/{self.api_key}?s={url}"
        response = requests.get(api_url, timeout=10)
        return response.text.strip() if response.status_code == 200 else url
    
    def _gplinks_shorten(self, url):
        """GPLinks API"""
        payload = {'api': self.api_key, 'url': url}
        response = requests.get(f"{self.base_url}/api", params=payload, timeout=10)
        data = response.json()
        return data.get('shortenedUrl') if data.get('status') == 'success' else url
    
    def _generic_shorten(self, url):
        """Generic API pattern"""
        payload = {'api': self.api_key, 'url': url}
        response = requests.get(f"{self.base_url}/api", params=payload, timeout=10)
        try:
            data = response.json()
            return data.get('shortenedUrl', data.get('short_url', url))
        except:
            return url
    
    def create_verification_link(self, user_id, token):
        """Create verification link with configured shortlink service"""
        verification_url = f"{self.base_url}/verify?token={token}&user={user_id}"
        shortened = self.shorten_url(verification_url)
        return shortened
class SimpleStorage:
    """In-memory storage optimized for Koyeb free tier"""
    
    def __init__(self):
        self.users = {}
        self.payments = {}
        self.tokens = {}
        
    def get_user(self, user_id):
        if str(user_id) not in self.users:
            self.users[str(user_id)] = {
                "user_id": user_id,
                "downloads_used": 0,
                "subscriptions": [],
                "tokens": [],
                "joined_date": datetime.utcnow().isoformat(),
                "total_spent": 0,
                "total_files": 0,
                "verified_tokens": []
            }
        return self.users[str(user_id)]
    
    def save_user(self, user_id, data):
        self.users[str(user_id)] = data
    
    def save_payment(self, payment_id, data):
        self.payments[payment_id] = data
    
    def get_payment(self, payment_id):
        return self.payments.get(payment_id)
    
    def update_payment(self, payment_id, status):
        if payment_id in self.payments:
            self.payments[payment_id]["status"] = status
            self.payments[payment_id]["verified_at"] = datetime.utcnow().isoformat()
            return True
        return False

class TokenManager:
    """Token management with configurable shortlink verification"""
    
    def __init__(self, storage, shortlink_api):
        self.storage = storage
        self.shortlink = shortlink_api
    
    def generate_token(self, user_id):
        """Generate verification token"""
        timestamp = str(int(time.time()))
        token_data = f"{user_id}:{timestamp}:{Config.TOKEN_VALIDITY_HOURS}"
        token = hashlib.sha256(token_data.encode()).hexdigest()[:16]
        return token
    
    def create_verification_link(self, user_id):
        """Create shortlink verification link"""
        token = self.generate_token(user_id)
        
        # Save token
        user_info = self.storage.get_user(user_id)
        token_info = {
            "token": token,
            "created": datetime.utcnow().isoformat(),
            "used": False,
            "validity_hours": Config.TOKEN_VALIDITY_HOURS
        }
        user_info["tokens"].append(token_info)
        self.storage.save_user(user_id, user_info)
        
        # Create shortlink verification URL
        verification_link = self.shortlink.create_verification_link(user_id, token)
        
        return verification_link, token
    
    def verify_token(self, user_id, token):
        """Verify token and mark as used"""
        user_info = self.storage.get_user(user_id)
        
        for token_info in user_info.get("tokens", []):
            if token_info["token"] == token and not token_info.get("used", False):
                created = datetime.fromisoformat(token_info["created"])
                validity_hours = token_info.get("validity_hours", Config.TOKEN_VALIDITY_HOURS)
                
                if datetime.utcnow() - created < timedelta(hours=validity_hours):
                    token_info["used"] = True
                    user_info["verified_tokens"].append({
                        "token": token,
                        "verified_at": datetime.utcnow().isoformat(),
                        "validity_hours": validity_hours
                    })
                    self.storage.save_user(user_id, user_info)
                    return True
        return False
    
    def has_valid_token(self, user_id):
        """Check if user has valid verification tokens"""
        user_info = self.storage.get_user(user_id)
        current_time = datetime.utcnow()
        
        for verified_token in user_info.get("verified_tokens", []):
            verified_at = datetime.fromisoformat(verified_token["verified_at"])
            validity_hours = verified_token.get("validity_hours", Config.TOKEN_VALIDITY_HOURS)
            
            if current_time - verified_at < timedelta(hours=validity_hours):
                return True
        return False
class PaymentManager:
    """GPay/UPI payment system"""
    
    def __init__(self, storage):
        self.storage = storage
        
    def generate_payment_id(self):
        return str(uuid.uuid4())[:8].upper()
    
    def create_payment_request(self, user_id, plan_key):
        plan = Config.PREMIUM_PLANS.get(plan_key)
        if not plan:
            return {"error": "Invalid plan"}
        
        payment_id = self.generate_payment_id()
        
        payment_data = {
            "payment_id": payment_id,
            "user_id": user_id,
            "plan_key": plan_key,
            "plan_name": plan["name"],
            "amount": plan["price"],
            "hours": plan["hours"],
            "status": "pending",
            "created_at": datetime.utcnow().isoformat(),
            "expires_at": (datetime.utcnow() + timedelta(minutes=30)).isoformat(),
            "upi_link": self.generate_upi_link(payment_id, plan["price"])
        }
        
        self.storage.save_payment(payment_id, payment_data)
        return payment_data
    
    def generate_upi_link(self, payment_id, amount):
        """Generate UPI payment link"""
        upi_params = {
            "pa": Config.GPAY_UPI_ID,
            "pn": "Terabox Premium",
            "am": str(amount),
            "cu": "INR",
            "tn": f"Premium-{payment_id}"
        }
        
        upi_string = "&".join([f"{k}={v}" for k, v in upi_params.items()])
        return f"upi://pay?{upi_string}"
    
    def verify_payment(self, payment_id):
        return self.storage.update_payment(payment_id, "completed")

class UserManager:
    """User management with premium subscriptions"""
    
    def __init__(self, storage):
        self.storage = storage
    
    def get_user_info(self, user_id):
        return self.storage.get_user(user_id)
    
    def save_user_info(self, user_id, user_data):
        self.storage.save_user(user_id, user_data)
    
    def add_premium_subscription(self, user_id, hours, amount, payment_id):
        user_info = self.get_user_info(user_id)
        
        subscription = {
            "payment_id": payment_id,
            "hours": hours,
            "amount": amount,
            "start_time": datetime.utcnow().isoformat(),
            "end_time": (datetime.utcnow() + timedelta(hours=hours)).isoformat(),
            "active": True
        }
        
        user_info["subscriptions"].append(subscription)
        user_info["total_spent"] = user_info.get("total_spent", 0) + amount
        
        self.save_user_info(user_id, user_info)
        logger.info(f"Added {hours}h premium for user {user_id} - ₹{amount}")
    
    def get_active_subscription(self, user_id):
        user_info = self.get_user_info(user_id)
        current_time = datetime.utcnow()
        
        for sub in user_info.get("subscriptions", []):
            if sub.get("active", False):
                end_time = datetime.fromisoformat(sub["end_time"])
                if current_time < end_time:
                    remaining_seconds = (end_time - current_time).total_seconds()
                    sub["remaining_hours"] = max(0, remaining_seconds / 3600)
                    sub["remaining_minutes"] = max(0, remaining_seconds / 60)
                    return sub
                else:
                    sub["active"] = False
                    self.save_user_info(user_id, user_info)
        return None
    
    def can_download(self, user_id, token_manager):
        """Check if user can download (premium, free, or verified token)"""
        active_sub = self.get_active_subscription(user_id)
        if active_sub:
            return True
        
        user_info = self.get_user_info(user_id)
        if user_info["downloads_used"] < Config.FREE_DOWNLOADS:
            return True
        
        return token_manager.has_valid_token(user_id)
    
    def increment_download(self, user_id, file_size=0, filename=""):
        user_info = self.get_user_info(user_id)
        user_info["downloads_used"] += 1
        user_info["total_files"] += 1
        self.save_user_info(user_id, user_info)
class TeraboxDownloader:
    """Terabox file downloader optimized for mobile streaming"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Android 11; Mobile; rv:68.0) Gecko/68.0 Firefox/88.0',
            'Cookie': Config.TERABOX_COOKIE,
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://terabox.com/'
        })
    
    def extract_file_info(self, url):
        try:
            patterns = [
                r'surl=([^&]+)',
                r'/s/([^?&]+)',
                r'terabox\.com/.*?([a-zA-Z0-9_-]+)$'
            ]
            
            shorturl = None
            for pattern in patterns:
                match = re.search(pattern, url)
                if match:
                    shorturl = match.group(1)
                    break
            
            if not shorturl:
                return {"error": "Invalid Terabox URL format"}
            
            api_endpoints = [
                f"https://terabox.com/api/shorturlinfo?shorturl={shorturl}&root=1",
                f"https://1024terabox.com/api/shorturlinfo?shorturl={shorturl}&root=1"
            ]
            
            for api_url in api_endpoints:
                try:
                    response = self.session.get(api_url, timeout=30)
                    data = response.json()
                    
                    if data.get('errno') == 0:
                        files = data.get('list', [])
                        if files:
                            file_info = files[0]
                            return {
                                "filename": file_info.get('server_filename', 'unknown'),
                                "size": file_info.get('size', 0),
                                "fs_id": file_info.get('fs_id'),
                                "thumbnail": file_info.get('thumbs', {}).get('url3', ''),
                                "file_type": self.get_file_type(file_info.get('server_filename', '')),
                                "is_video": self.is_video_file(file_info.get('server_filename', ''))
                            }
                except:
                    continue
            
            return {"error": "Failed to get file info from any endpoint"}
            
        except Exception as e:
            logger.error(f"Error extracting file info: {e}")
            return {"error": str(e)}
    
    def get_download_link(self, fs_id):
        try:
            api_url = f"https://terabox.com/api/download?type=dlink&fidlist=[{fs_id}]"
            response = self.session.get(api_url, timeout=30)
            data = response.json()
            
            if data.get('errno') == 0:
                dlinks = data.get('dlink', [])
                if dlinks:
                    return dlinks[0].get('dlink')
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting download link: {e}")
            return None
    
    def get_file_type(self, filename):
        ext = filename.lower().split('.')[-1] if '.' in filename else ''
        
        video_exts = ['mp4', 'mkv', 'avi', 'mov', 'wmv', 'flv', 'webm', 'm4v', '3gp']
        audio_exts = ['mp3', 'flac', 'wav', 'aac', 'm4a', 'ogg', 'wma']
        image_exts = ['jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp', 'svg']
        doc_exts = ['pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'txt']
        archive_exts = ['zip', 'rar', '7z', 'tar', 'gz', 'bz2']
        
        if ext in video_exts:
            return "video"
        elif ext in audio_exts:
            return "audio"
        elif ext in image_exts:
            return "image"
        elif ext in doc_exts:
            return "document"
        elif ext in archive_exts:
            return "archive"
        else:
            return "other"
    
    def is_video_file(self, filename):
        return self.get_file_type(filename) == "video"
class TeraboxBot:
    """Main bot class with configurable shortlink integration"""
    
    def __init__(self):
        self.client = TelegramClient('bot', Config.API_ID, Config.API_HASH)
        self.storage = SimpleStorage()
        self.shortlink = ShortlinkAPI()
        self.payment_manager = PaymentManager(self.storage)
        self.user_manager = UserManager(self.storage)
        self.token_manager = TokenManager(self.storage, self.shortlink)
        self.downloader = TeraboxDownloader()
    
    def is_admin(self, user_id):
        return user_id == Config.OWNER_ID or user_id in Config.ADMIN_IDS
    
    async def start(self):
        await self.client.start(bot_token=Config.BOT_TOKEN)
        
        # Register handlers
        self.client.add_event_handler(self.handle_start, events.NewMessage(pattern='/start'))
        self.client.add_event_handler(self.handle_buy, events.NewMessage(pattern='/buy'))
        self.client.add_event_handler(self.handle_premium, events.NewMessage(pattern='/premium'))
        self.client.add_event_handler(self.handle_verify, events.NewMessage(pattern='/verify'))
        self.client.add_event_handler(self.handle_stats, events.NewMessage(pattern='/stats'))
        self.client.add_event_handler(self.handle_confirm, events.NewMessage(pattern='/confirm'))
        self.client.add_event_handler(self.handle_payment, events.NewMessage(pattern='/payment'))
        self.client.add_event_handler(self.handle_leech, events.NewMessage())
        self.client.add_event_handler(self.handle_callbacks, events.CallbackQuery())
        
        logger.info(f"🚀 Ultimate Terabox Bot started with {Config.SHORTLINK_URL}!")
        await self.client.run_until_disconnected()
    
    async def handle_start(self, event):
        user_id = event.sender_id
        user_info = self.user_manager.get_user_info(user_id)
        active_sub = self.user_manager.get_active_subscription(user_id)
        
        if active_sub:
            remaining_hours = int(active_sub["remaining_hours"])
            remaining_minutes = int(active_sub["remaining_minutes"]) % 60
            status = f"💎 **PREMIUM** ({remaining_hours}h {remaining_minutes}m left)"
        else:
            used = user_info["downloads_used"]
            remaining = Config.FREE_DOWNLOADS - used
            has_token = self.token_manager.has_valid_token(user_id)
            
            if remaining > 0:
                status = f"🆓 **Free User** ({remaining}/{Config.FREE_DOWNLOADS} downloads)"
            elif has_token:
                status = f"✅ **Verified** (Unlimited downloads)"
            else:
                status = f"🔒 **Verification Required** (Free downloads used)"
        
        buttons = [
            [Button.inline("📊 My Stats", b"stats"), Button.inline("🔗 Verify Free", b"verify")],
            [Button.inline("💎 Buy Premium", b"buy"), Button.inline("📱 Help", b"help")]
        ]
        
        shortlink_name = Config.SHORTLINK_URL.split('//')[1].split('/')[0]
        
        start_text = f"""🤖 **Ultimate Terabox Bot**

{status}

**🚀 Features:**
• Fast Terabox downloads
• {shortlink_name} verification system
• Premium subscription plans
• Auto file backup

**💎 Premium Plans:**
• 2 Hours - ₹5 (Quick Access)
• 6 Hours - ₹10 (Standard Access)
• 12 Hours - ₹15 (Extended Access)
• 24 Hours - ₹20 (Full Day Access)

**🔓 Access Options:**
1. **Free:** {Config.FREE_DOWNLOADS} downloads + verification
2. **Premium:** Unlimited + no verification
3. **Instant GPay:** ₹5-₹20 payment

📁 Send me a Terabox link to start downloading!"""
        
        await event.respond(start_text, buttons=buttons)
    
    async def handle_verify(self, event):
        user_id = event.sender_id
        
        active_sub = self.user_manager.get_active_subscription(user_id)
        if active_sub:
            remaining_hours = int(active_sub["remaining_hours"])
            remaining_minutes = int(active_sub["remaining_minutes"]) % 60
            await event.respond(
                f"💎 **You already have premium access!**\\n\\n"
                f"⏰ **Remaining:** {remaining_hours}h {remaining_minutes}m\\n"
                f"No verification needed!"
            )
            return
        
        user_info = self.user_manager.get_user_info(user_id)
        remaining = Config.FREE_DOWNLOADS - user_info["downloads_used"]
        if remaining > 0:
            await event.respond(
                f"✅ **{remaining} free downloads remaining!**\\n\\n"
                f"You can still download {remaining} files without verification.\\n"
                f"Verification will be needed after using all free downloads."
            )
            return
        
        if self.token_manager.has_valid_token(user_id):
            await event.respond(
                f"✅ **You're already verified!**\\n\\n"
                f"⏰ **Valid for:** {Config.TOKEN_VALIDITY_HOURS} hours\\n"
                f"You can download unlimited files!"
            )
            return
        
        verification_link, token = self.token_manager.create_verification_link(user_id)
        shortlink_name = Config.SHORTLINK_URL.split('//')[1].split('/')[0]
        
        verify_text = f"""🔐 **Free Verification Required**

**💰 Earn Money + Get Access:**
Your verification link is monetized with {shortlink_name}!

**📱 Steps:**
1. Click the verification button below
2. Complete the {shortlink_name} process (earn money!)
3. Get {Config.TOKEN_VALIDITY_HOURS}h unlimited access

**💎 Or Buy Premium:**
• Skip verification completely
• Instant access with GPay/UPI
• Plans: ₹5 (2h) to ₹20 (24h)

🔗 **Your monetized verification link:**"""
        
        buttons = [
            [Button.url(f"🔗 Verify & Earn ({shortlink_name})", verification_link)],
            [Button.inline("💎 Buy Premium Instead", b"buy")],
            [Button.inline("📊 My Stats", b"stats")]
        ]
        
        await event.respond(verify_text, buttons=buttons)
    async def handle_buy(self, event):
        user_id = event.sender_id
        command_parts = event.message.text.split()
        
        if len(command_parts) == 1:
            plans_text = """💎 **Premium Plans**

**🇮🇳 Instant GPay/UPI Payment:**

"""
            buttons = []
            
            for plan_key, plan_info in Config.PREMIUM_PLANS.items():
                hours = plan_info["hours"]
                price = plan_info["price"]
                name = plan_info["name"]
                description = plan_info["description"]
                
                plans_text += f"**{name}** - ₹{price}\\n"
                plans_text += f"• {hours} hours unlimited access\\n"
                plans_text += f"• {description}\\n"
                plans_text += f"• Per hour: ₹{price/hours:.1f}\\n\\n"
                
                buttons.append([Button.inline(f"{name} - ₹{price}", f"buy_{plan_key}".encode())])
            
            plans_text += """**💎 Premium Benefits:**
🚀 Unlimited downloads (no verification)
📁 2.5GB file limit (vs 1.5GB free)
⚡ Priority processing & faster speeds
❌ No shortlink verification needed
💬 Premium support

**💳 Payment:** Instant via GPay/UPI
**🚀 Activation:** Immediate after confirmation"""
            
            await event.respond(plans_text, buttons=buttons)
            return
        
        if len(command_parts) == 2:
            plan_key = command_parts[1]
            if plan_key in Config.PREMIUM_PLANS:
                await self.process_payment_request(event, plan_key)
            else:
                await event.respond(
                    "❌ **Invalid plan!**\\n\\n"
                    "Available plans: `2h`, `6h`, `12h`, `24h`\\n"
                    "Example: `/buy 6h`"
                )
    
    async def process_payment_request(self, event, plan_key):
        user_id = event.sender_id
        
        active_sub = self.user_manager.get_active_subscription(user_id)
        if active_sub:
            remaining_hours = int(active_sub["remaining_hours"])
            remaining_minutes = int(active_sub["remaining_minutes"]) % 60
            await event.respond(
                f"💎 **You already have active premium!**\\n\\n"
                f"⏰ **Remaining:** {remaining_hours}h {remaining_minutes}m\\n\\n"
                f"Wait for it to expire or contact admin."
            )
            return
        
        payment_data = self.payment_manager.create_payment_request(user_id, plan_key)
        
        if "error" in payment_data:
            await event.respond(f"❌ **Error:** {payment_data['error']}")
            return
        
        plan = Config.PREMIUM_PLANS[plan_key]
        payment_id = payment_data["payment_id"]
        upi_link = payment_data["upi_link"]
        
        payment_text = f"""💳 **Payment Details**

**Plan:** {plan["name"]}
**Duration:** {plan["hours"]} hours
**Amount:** ₹{plan["price"]}
**Payment ID:** `{payment_id}`

**📱 Pay via GPay/UPI:**
1. Click the payment button below
2. Complete payment in GPay/PhonePe/any UPI app
3. Send payment screenshot to admin
4. Get instant premium access!

**UPI ID:** `{Config.GPAY_UPI_ID}`
⏰ **Payment expires in 30 minutes**
🔄 **Check status:** `/payment {payment_id}`"""
        
        buttons = [
            [Button.url(f"💳 Pay ₹{plan['price']} via UPI", upi_link)],
            [Button.inline(f"✅ I've Paid ₹{plan['price']}", f"paid_{payment_id}".encode())]
        ]
        
        await event.respond(payment_text, buttons=buttons)
        
        if Config.PAYMENT_CHANNEL:
            try:
                user_info = await self.client.get_entity(user_id)
                username = f"@{user_info.username}" if user_info.username else f"ID:{user_id}"
                first_name = getattr(user_info, 'first_name', 'Unknown')
                
                admin_text = f"""💳 **New Payment Request**

**User:** {first_name} ({username})
**Plan:** {plan["name"]} ({plan["hours"]}h)
**Amount:** ₹{plan["price"]}
**Payment ID:** `{payment_id}`
**UPI ID:** `{Config.GPAY_UPI_ID}`

**Admin Actions:**
Use `/confirm {payment_id}` after payment verification"""
                
                await self.client.send_message(Config.PAYMENT_CHANNEL, admin_text)
            except Exception as e:
                logger.error(f"Error sending payment notification: {e}")

    async def handle_confirm(self, event):
        user_id = event.sender_id
        
        if not self.is_admin(user_id):
            await event.respond("❌ **Access Denied!** Only admins can confirm payments.")
            return
        
        command_parts = event.message.text.split()
        if len(command_parts) != 2:
            await event.respond("❌ **Usage:** `/confirm <payment_id>`")
            return
        
        payment_id = command_parts[1].upper()
        payment_info = self.storage.get_payment(payment_id)
        
        if not payment_info:
            await event.respond("❌ **Payment ID not found!**")
            return
        
        if payment_info["status"] != "pending":
            await event.respond(f"❌ **Payment already {payment_info['status']}!**")
            return
        
        confirmed = self.payment_manager.verify_payment(payment_id)
        
        if confirmed:
            customer_id = payment_info["user_id"]
            hours = payment_info["hours"]
            amount = payment_info["amount"]
            
            self.user_manager.add_premium_subscription(customer_id, hours, amount, payment_id)
            
            await event.respond(
                f"✅ **Payment Confirmed!**\\n\\n"
                f"**Payment ID:** `{payment_id}`\\n"
                f"**Plan:** {payment_info['plan_name']}\\n"
                f"**Amount:** ₹{amount}\\n"
                f"**Duration:** {hours} hours\\n\\n"
                f"User has been granted premium access!"
            )
            
            try:
                customer_text = f"""🎉 **Premium Activated!**

Your payment has been confirmed:

**Plan:** {payment_info["plan_name"]}
**Duration:** {hours} hours
**Amount Paid:** ₹{amount}
**Payment ID:** `{payment_id}`

✅ **Premium features now active:**
• Unlimited downloads
• No verification needed
• 2.5GB file size limit
• Priority processing
• Faster download speeds

Start downloading immediately! 🚀"""
                
                await self.client.send_message(customer_id, customer_text)
            except Exception as e:
                logger.error(f"Error notifying customer: {e}")
        else:
            await event.respond("❌ **Failed to confirm payment!** Please try again.")

    def is_terabox_link(self, text):
        if not text:
            return False
        
        patterns = [
            r'terabox\.com',
            r'1024terabox\.com',
            r'teraboxapp\.com',
            r'teraboxlink\.com',
            r'4funbox\.com'
        ]
        
        return any(re.search(pattern, text, re.IGNORECASE) for pattern in patterns)
    
    async def handle_leech(self, event):
        if not event.message.text or event.message.text.startswith('/'):
            return
        
        if not self.is_terabox_link(event.message.text):
            return
        
        user_id = event.sender_id
        
        can_download = self.user_manager.can_download(user_id, self.token_manager)
        if not can_download:
            shortlink_name = Config.SHORTLINK_URL.split('//')[1].split('/')[0]
            buttons = [
                [Button.inline("💎 Buy Premium", b"buy"), Button.inline("🔗 Verify Free", b"verify")],
                [Button.inline("📊 My Stats", b"stats")]
            ]
            
            await event.respond(
                f"""🔒 **Download Access Required!**

You've used all {Config.FREE_DOWNLOADS} free downloads.

**🔓 Choose your access method:**

**💎 Premium (Instant):**
• ₹5-₹20 for unlimited access
• No verification needed
• Instant activation

**🔗 {shortlink_name} Verification (Free):**
• Complete {shortlink_name} process
• Get {Config.TOKEN_VALIDITY_HOURS}h unlimited access
• Earn money while verifying!

**⚡ Quick Options:**
• Premium: No ads, instant access
• Verification: Free but requires {shortlink_name} completion""",
                buttons=buttons
            )
            return
        
        url = event.message.text.strip()
        active_sub = self.user_manager.get_active_subscription(user_id)
        is_premium = bool(active_sub)
        
        if active_sub:
            remaining_hours = int(active_sub["remaining_hours"])
            remaining_minutes = int(active_sub["remaining_minutes"]) % 60
            user_badge = f"💎 Premium ({remaining_hours}h {remaining_minutes}m)"
        else:
            user_info = self.user_manager.get_user_info(user_id)
            remaining_free = Config.FREE_DOWNLOADS - user_info["downloads_used"]
            has_token = self.token_manager.has_valid_token(user_id)
            
            if remaining_free > 0:
                user_badge = f"🆓 Free ({remaining_free} left)"
            elif has_token:
                user_badge = f"✅ Verified ({Config.TOKEN_VALIDITY_HOURS}h access)"
            else:
                user_badge = f"🔒 Access required"
        
        status_msg = await event.respond(f"🔍 **Processing Terabox link...** {user_badge}")
        
        try:
            await status_msg.edit(f"📋 **Getting file information...** {user_badge}")
            file_info = self.downloader.extract_file_info(url)
            
            if "error" in file_info:
                await status_msg.edit(f"❌ **Error:** {file_info['error']}\\n\\n💡 Try a different Terabox link")
                return
            
            filename = file_info['filename']
            file_size = file_info['size']
            fs_id = file_info['fs_id']
            file_type = file_info['file_type']
            
            max_size = Config.PREMIUM_MAX_SIZE if is_premium else Config.MAX_FILE_SIZE
            if file_size > max_size:
                size_mb = file_size / (1024*1024)
                limit_mb = max_size / (1024*1024)
                upgrade_msg = "" if is_premium else "\\n💎 **Premium users get 2.5GB limit!**"
                
                await status_msg.edit(
                    f"❌ **File too large:** {size_mb:.1f}MB\\n"
                    f"**Your limit:** {limit_mb:.0f}MB{upgrade_msg}"
                )
                return
            
            await status_msg.edit(f"🔗 **Getting download link...** {user_badge}")
            download_url = self.downloader.get_download_link(fs_id)
            
            if not download_url:
                await status_msg.edit("❌ **Failed to get download link**\\n\\n💡 Try again or contact admin")
                return
            
            await status_msg.edit(f"⬇️ **Downloading:** `{filename}` {user_badge}")
            
            response = self.downloader.session.get(download_url, stream=True, timeout=300)
            response.raise_for_status()
            
            await status_msg.edit(f"⬆️ **Uploading:** `{filename}` {user_badge}")
            
            attributes = [DocumentAttributeFilename(filename)]
            if file_info['is_video']:
                attributes.append(DocumentAttributeVideo(
                    duration=0, w=0, h=0, supports_streaming=True
                ))
            
            type_emoji = {
                "video": "🎥", "audio": "🎵", "image": "🖼️",
                "document": "📄", "archive": "📦", "other": "📁"
            }.get(file_type, "📁")
            
            caption = (
                f"{type_emoji} **File:** `{filename}`\\n"
                f"📊 **Size:** {file_size/(1024*1024):.1f}MB\\n"
                f"🏷️ **Type:** {file_type.title()}\\n"
                f"👤 **User:** {'💎 Premium' if is_premium else '🆓 Free'}"
            )
            
            await self.client.send_file(
                event.chat_id,
                response.raw,
                attributes=attributes,
                caption=caption
            )
            
            if Config.SAVE_CHANNEL:
                try:
                    response2 = self.downloader.session.get(download_url, stream=True)
                    await self.client.send_file(
                        Config.SAVE_CHANNEL,
                        response2.raw,
                        attributes=attributes,
                        caption=f"{type_emoji} `{filename}`\\n📊 {file_size/(1024*1024):.1f}MB"
                    )
                except Exception as e:
                    logger.error(f"Error saving to channel: {e}")
            
            self.user_manager.increment_download(user_id, file_size, filename)
            
            user_info = self.user_manager.get_user_info(user_id)
            remaining_free = Config.FREE_DOWNLOADS - user_info["downloads_used"]
            
            if is_premium:
                remaining_hours = int(active_sub["remaining_hours"])
                remaining_minutes = int(active_sub["remaining_minutes"]) % 60
                completion_msg = f"✅ **Download completed!** 💎\\n\\n🚀 **Premium:** {remaining_hours}h {remaining_minutes}m remaining"
            elif remaining_free > 0:
                completion_msg = f"✅ **Download completed!**\\n\\n📊 **Free downloads remaining:** {remaining_free}"
            elif self.token_manager.has_valid_token(user_id):
                completion_msg = f"✅ **Download completed!**\\n\\n✅ **Verified access active** ({Config.TOKEN_VALIDITY_HOURS}h remaining)"
            else:
                shortlink_name = Config.SHORTLINK_URL.split('//')[1].split('/')[0]
                completion_msg = f"✅ **Download completed!**\\n\\n🔒 **This was your last free download.**\\n💎 **Get Premium:** /buy or 🔗 **Verify:** /verify ({shortlink_name})"
            
            await status_msg.edit(completion_msg)
            
            logger.info(f"Successfully processed: {filename} for user {user_id} (Premium: {is_premium})")
            
        except Exception as e:
            logger.error(f"Error processing file: {e}")
            try:
                await status_msg.edit(f"❌ **Error:** {str(e)}\\n\\n💡 Please try again later")
            except:
                await event.respond(f"❌ **Download failed:** {str(e)}")
    
    async def handle_callbacks(self, event):
        try:
            data = event.data.decode()
            
            if data == "stats":
                await self.handle_stats(event)
            elif data == "premium":
                await self.handle_premium(event)
            elif data == "buy":
                await self.handle_buy(event)
            elif data == "verify":
                await self.handle_verify(event)
            elif data == "help":
                await self.show_help(event)
            elif data.startswith("buy_"):
                plan_key = data.replace("buy_", "")
                await self.process_payment_request(event, plan_key)
            elif data.startswith("paid_"):
                payment_id = data.replace("paid_", "")
                await event.answer("✅ Payment received! Admin will confirm soon.", show_alert=True)
                
        except Exception as e:
            logger.error(f"Error in callbacks: {e}")
            await event.answer("❌ Error processing request.")
    
    # Add other handler methods here (handle_stats, handle_premium, etc.)
    async def handle_stats(self, event):
        user_id = event.sender_id
        user_info = self.user_manager.get_user_info(user_id)
        active_sub = self.user_manager.get_active_subscription(user_id)
        
        total_spent = user_info.get("total_spent", 0)
        total_files = user_info.get("total_files", 0)
        downloads_used = user_info.get("downloads_used", 0)
        
        if active_sub:
            remaining_hours = int(active_sub["remaining_hours"])
            remaining_minutes = int(active_sub["remaining_minutes"]) % 60
            access_status = f"💎 Premium ({remaining_hours}h {remaining_minutes}m)"
            downloads_info = "Unlimited"
        else:
            remaining_free = Config.FREE_DOWNLOADS - downloads_used
            has_token = self.token_manager.has_valid_token(user_id)
            
            if remaining_free > 0:
                access_status = f"🆓 Free ({remaining_free} left)"
                downloads_info = f"{remaining_free}/{Config.FREE_DOWNLOADS} free"
            elif has_token:
                access_status = f"✅ Verified ({Config.TOKEN_VALIDITY_HOURS}h access)"
                downloads_info = "Unlimited (verified)"
            else:
                access_status = f"🔒 Verification needed"
                downloads_info = "0 (need verification)"
        
        stats_text = f"""📊 **Your Statistics**

**Status:** {access_status}
**Downloads Available:** {downloads_info}

**Account Info:**
• Member since: {user_info['joined_date'][:10]}
• Total spent: ₹{total_spent}
• Files downloaded: {total_files}
• Session downloads: {downloads_used}

**Current Access:** {"✅ Premium Active" if active_sub else "⏳ Need verification" if remaining_free == 0 and not self.token_manager.has_valid_token(user_id) else "✅ Can download"}

💡 **Tip:** Use `/premium` to see available plans!"""
        
        await event.edit(stats_text)

    async def handle_premium(self, event):
        user_id = event.sender_id
        active_sub = self.user_manager.get_active_subscription(user_id)
        
        if active_sub:
            remaining_hours = int(active_sub["remaining_hours"])
            remaining_minutes = int(active_sub["remaining_minutes"]) % 60
            
            premium_text = f"""💎 **Premium Subscription Active**

**Current Plan:** {active_sub.get("hours", 0)}h Access
**Remaining Time:** {remaining_hours}h {remaining_minutes}m
**Amount Paid:** ₹{active_sub.get("amount", 0)}

**Your Premium Benefits:**
✅ Unlimited downloads
✅ No verification required
✅ 2.5GB file size limit (vs 1.5GB free)
✅ Priority processing queue
✅ Faster download speeds
✅ Premium support

**Status:** Active Premium User
Keep downloading without limits! 🚀"""
        else:
            shortlink_name = Config.SHORTLINK_URL.split('//')[1].split('/')[0]
            premium_text = f"""💎 **Premium Subscription Plans**

**🇮🇳 Instant GPay/UPI Payment:**

**⚡ Quick Access** - ₹5
• 2 Hours unlimited downloads
• Perfect for urgent files
• Skip {shortlink_name} verification

**📱 Standard Access** - ₹10
• 6 Hours unlimited downloads  
• Great for regular use
• No verification needed

**🔥 Extended Access** - ₹15
• 12 Hours unlimited downloads
• Best value for heavy users
• Priority processing

**👑 Full Day Access** - ₹20
• 24 Hours unlimited downloads
• Maximum convenience
• All premium features

**Premium Benefits:**
🚀 Unlimited downloads (no verification)
📁 2.5GB file size limit (vs 1.5GB free)
⚡ Priority processing queue
🔥 Faster download speeds  
❌ Skip {shortlink_name} verification
💬 Premium support

**Payment:** Instant via GPay/UPI
**Activation:** Automatic after admin confirmation

Use `/buy` to choose your plan!"""
        
        await event.respond(premium_text)

    async def show_help(self, event):
        shortlink_name = Config.SHORTLINK_URL.split('//')[1].split('/')[0]
        help_text = f"""📱 **How to Use Ultimate Terabox Bot**

**🆓 Free Users ({Config.FREE_DOWNLOADS} downloads):**
1. Send any Terabox link
2. Get file instantly downloaded
3. Files are auto-saved to channel

**🔒 After {Config.FREE_DOWNLOADS} downloads:**
• Use `/verify` for {shortlink_name} verification (free {Config.TOKEN_VALIDITY_HOURS}h access)
• Use `/buy` for premium plans (₹5-₹20)

**💎 Premium Benefits:**
• Unlimited downloads (no verification)
• 2.5GB file limit (vs 1.5GB free)
• Priority processing & faster speeds
• Skip {shortlink_name} verification completely
• Premium support

**📱 Commands:**
• `/start` - Start the bot
• `/premium` - View premium plans  
• `/buy` - Purchase premium access
• `/verify` - Get {shortlink_name} verification link
• `/stats` - View your statistics
• `/payment <id>` - Check payment status
• `/help` - Show this help

**📁 Supported Files:**
Videos, documents, images, audio, archives, and more!

**💰 Premium Plans:**
• 2h - ₹5 (Quick) | 6h - ₹10 (Standard)
• 12h - ₹15 (Extended) | 24h - ₹20 (Full Day)

**💡 Tips:**
• Free users: Complete {shortlink_name} verification for {Config.TOKEN_VALIDITY_HOURS}h access
• Premium users: Instant access, no ads, larger files
• All files are automatically backed up to the bot channel

**🔧 Shortlink Service:** {shortlink_name}
• Configurable in bot settings
• Change anytime for better rates

Need help? Contact admin or use the bot commands above! 🚀"""
        
        await event.edit(help_text)

if __name__ == "__main__":
    if os.path.exists("config.env"):
        with open("config.env") as f:
            for line in f:
                if line.strip() and not line.startswith('#') and '=' in line:
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value
    
    required_vars = [
        'BOT_TOKEN', 'API_ID', 'API_HASH', 'SAVE_CHANNEL', 
        'OWNER_ID', 'GPAY_UPI_ID', 'TERABOX_COOKIE'
    ]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        logger.error(f"❌ Missing required variables: {', '.join(missing_vars)}")
        logger.error("Please set these in Koyeb environment variables!")
        exit(1)
    
    bot = TeraboxBot()
    try:
        shortlink_name = Config.SHORTLINK_URL.split('//')[1].split('/')[0]
        logger.info(f"🚀 Starting Ultimate Terabox Bot with {shortlink_name}...")
        asyncio.run(bot.start())
    except KeyboardInterrupt:
        logger.info("\\n👋 Bot stopped by user!")
    except Exception as e:
        logger.error(f"❌ Critical error: {e}")
        exit(1)
