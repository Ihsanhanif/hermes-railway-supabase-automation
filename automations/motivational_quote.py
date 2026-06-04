#!/usr/bin/env python3
"""
Daily Motivational Quote Automation for Hermes + Supabase
Sends motivational/trading quotes via Telegram at 07:00 WIB
"""

import os
import json
import random
from datetime import datetime, timezone, timedelta
from hermes_tools import terminal
import supabase

# Initialize Supabase client
supabase_url = os.environ.get('SUPABASE_URL')
supabase_key = os.environ.get('SUPABASE_ANON_KEY')
supabase_client = supabase.create_client(supabase_url, supabase_key)

# Telegram configuration
TELEGRAM_BOT_TOKEN=os.environ.get('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')

# Quote collections
TRADING_QUOTES = [
    "The stock market is filled with individuals who know the price of everything, but the value of nothing. – Philip Fisher",
    "In investing, what is comfortable is rarely profitable. – Robert Arnott",
    "The four most dangerous words in investing are: 'This time it's different.' – Sir John Templeton",
    "It's not whether you're right or wrong that's important, but how much money you make when you're right and how much you lose when you're wrong. – George Soros",
    "The goal of a successful trader is to make the best trades. Money is secondary. – Alexander Elder",
    "Risk comes from not knowing what you're doing. – Warren Buffett",
    "The market can stay irrational longer than you can stay solvent. – John Maynard Keynes",
    "Buy when there's blood in the streets, even if the blood is your own. – Baron Rothschild",
    "I will tell you how to become rich. Close the doors. Be fearful when others are greedy. Be greedy when others are fearful. – Warren Buffett",
    "Successful investing is anticipating the anticipations of others. – John Maynard Keynes"
]

STUDY_MOTIVATION_QUOTES = [
    "The expert in anything was once a beginner. – Helen Hayes",
    "Education is the most powerful weapon which you can use to change the world. – Nelson Mandela",
    "The beautiful thing about learning is that no one can take it away from you. – B.B. King",
    "Learning never exhausts the mind, never frightens, and never soothes. – Leonardo da Vinci",
    "The only limit to our realization of tomorrow is our doubts today. – Franklin D. Roosevelt",
    "Your time is limited, don't waste it living someone else's life. – Steve Jobs",
    "Stay hungry, stay foolish. – Steve Jobs",
    "The future belongs to those who believe in the beauty of their dreams. – Eleanor Roosevelt",
    "Don't watch the clock; do what it does. Keep going. – Sam Levenson",
    "It always seems impossible until it's done. – Nelson Mandela"
]

PERSONAL_GROWTH_QUOTES = [
    "The only way to do great work is to love what you do. – Steve Jobs",
    "Success is not final, failure is not fatal: It is the courage to continue that counts. – Winston Churchill",
    "Believe you can and you're halfway there. – Theodore Roosevelt",
    "It does not matter how slowly you go as long as you do not stop. – Confucius",
    "Everything you've ever wanted is on the other side of fear. – George Addair",
    "Challenges are what make life interesting and overcoming them is what makes life meaningful. – Joshua J. Marine",
    "If you want to lift yourself up, lift up someone else. – Booker T. Washington",
    "The best preparation for tomorrow is doing your best today. – H. Jackson Brown Jr.",
    "You are never too old to set another goal or to dream a new dream. – C.S. Lewis",
    "What you get by achieving your goals is not as important as what you become by achieving your goals. – Zig Ziglar"
]

def get_quote_for_time():
    """Get appropriate quote based on time or cycle through categories"""
    # You could customize this based on day of week, etc.
    # For now, we'll cycle through categories
    
    # Get current hour in WIB to determine context
    wib_time = datetime.now(timezone.utc) + timedelta(hours=7)
    hour = wib_time.hour
    
    # Morning (6-9): Trading focus
    # Day (9-17): Study/Personal growth mix  
    # Evening (17-21): Personal growth/Reflection
    # Night (21-6): Study preparation
    
    if 6 <= hour < 9:
        quotes = TRADING_QUOTES
        category = "trading"
    elif 9 <= hour < 17:
        # Mix study and personal growth during day
        if random.choice([True, False]):
            quotes = STUDY_MOTIVATION_QUOTES
            category = "study"
        else:
            quotes = PERSONAL_GROWTH_QUOTES
            category = "personal_growth"
    elif 17 <= hour < 21:
        quotes = PERSONAL_GROWTH_QUOTES
        category = "personal_growth"
    else:
        quotes = STUDY_MOTIVATION_QUOTES
        category = "study"
    
    quote_obj = random.choice(quotes)
    return {
        'quote': quote_obj,
        'category': category,
        'author': quote_obj.split('– ')[-1] if '– ' in quote_obj else 'Unknown',
        'timestamp': wib_time.isoformat()
    }

def send_telegram_message(message):
    """Send message via Telegram bot"""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("Telegram credentials not configured")
        return None
        
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': message,
        'parse_mode': 'HTML'
    }
    try:
        response = requests.post(url, json=payload)
        return response.json()
    except Exception as e:
        print(f"Error sending Telegram message: {e}")
        return None

def format_quote_message(quote_data):
    """Format quote data into a Telegram message"""
    wib_time = datetime.fromisoformat(quote_data['timestamp'].replace('Z', '+00:00'))
    time_str = wib_time.strftime("%d/%m/%Y %H:%M WIB")
    
    message = f"💫 <b>Daily Motivation</b>\n🕐 {time_str}\n\n"
    message += f"<i>\"{quote_data['quote']}\"</i>\n\n"
    message += f"— <b>{quote_data['author']}</b>\n"
    message += f"<i>Category: {quote_data['category'].replace('_', '').title()}</i>\n\n"
    message += "<i>Automated by Hermes Agent</i>"
    return message

def log_quote_sent(quote_data):
    """Log sent quote to Supabase"""
    try:
        supabase_client.table('quote_log').insert({
            'quote': quote_data['quote'],
            'author': quote_data['author'],
            'category': quote_data['category']
        }).execute()
    except Exception as e:
        print(f"Error logging quote to Supabase: {e}")

def log_automation_run(automation_name, status, message="", details=None):
    """Log automation run to Supabase"""
    try:
        supabase_client.table('automation_logs').insert({
            'automation_name': automation_name,
            'status': status,
            'message': message,
            'details': details or {}
        }).execute()
    except Exception as e:
        print(f"Error logging to Supabase: {e}")

def main():
    """Main automation function"""
    automation_name = "motivational_quote"
    start_time = datetime.now(timezone.utc)
    
    try:
        # Get quote for current time
        quote_data = get_quote_for_time()
        
        # Format message
        message = format_quote_message(quote_data)
        
        # Send via Telegram
        result = send_telegram_message(message)
        
        if result and result.get('ok'):
            status = "success"
            log_message = "Motivational quote sent successfully"
            details = {
                'telegram_message_id': result.get('result', {}).get('message_id'),
                'quote_category': quote_data['category'],
                'quote_author': quote_data['author']
            }
            
            # Log the quote to Supabase
            log_quote_sent(quote_data)
        else:
            status = "error"
            log_message = f"Failed to send Telegram message: {result}"
            details = {'error': str(result)}
            
    except Exception as e:
        status = "error"
        log_message = str(e)
        details = {'error': str(e)}
        message = f"❌ Motivational Quote Error: {str(e)}"
        # Try to send error message
        try:
            send_telegram_message(message)
        except:
            pass  # Don't fail on error reporting
    
    # Log the run
    log_automation_run(
        automation_name=automation_name,
        status=status,
        message=log_message,
        details=details
    )
    
    print(f"Motivational quote automation completed: {status}")
    return status == "success"

if __name__ == "__main__":
    # Import requests here to avoid issues if not used
    import requests
    success = main()
    exit(0 if success else 1)