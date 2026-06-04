#!/usr/bin/env python3
"""
Daily Market Brief Automation for Hermes + Supabase
Fetches Indonesian market data and sends via Telegram at 08:00 WIB
"""

import os
import json
import requests
from datetime import datetime, timezone, timedelta
from hermes_tools import terminal, web_search
import supabase

# Initialize Supabase client
supabase_url = os.environ.get('SUPABASE_URL')
supabase_key = os.environ.get('SUPABASE_ANON_KEY')
supabase_client = supabase.create_client(supabase_url, supabase_key)

# Telegram configuration
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')

def send_telegram_message(message):
    """Send message via Telegram bot"""
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

def get_indonesian_market_data():
    """Fetch Indonesian market data"""
    try:
        # Search for latest IHSG data and market news
        search_results = web_search(
            query="IHSG Indonesia stock market today close price volume",
            max_results=5
        )
        
        # Also search for market news
        news_results = web_search(
            query="Indonesia stock market news today IHSG",
            max_results=3
        )
        
        return {
            'search_results': search_results,
            'news_results': news_results,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        print(f"Error fetching market data: {e}")
        return None

def format_market_brief(data):
    """Format market data into a Telegram message"""
    if not data:
        return "❌ Failed to fetch market data"
    
    # Get current time in WIB (UTC+7)
    wib_time = datetime.now(timezone.utc) + timedelta(hours=7)
    time_str = wib_time.strftime("%d/%m/%Y %H:%M WIB")
    
    message = f"📈 <b>Indonesia Market Brief</b>\n🕐 {time_str}\n\n"
    
    # Add search results summary
    if data.get('search_results'):
        message += "<b>Market Data:</b>\n"
        # Extract key info from search results
        for result in data['search_results'][:3]:
            if isinstance(result, dict) and 'content' in result:
                content = result['content'][:200] + "..." if len(result['content']) > 200 else result['content']
                message += f"• {content}\n"
        message += "\n"
    
    # Add news summary
    if data.get('news_results'):
        message += "<b>Latest News:</b>\n"
        for result in data['news_results'][:3]:
            if isinstance(result, dict) and 'content' in result:
                content = result['content'][:150] + "..." if len(result['content']) > 150 else result['content']
                message += f"• {content}\n"
    
    message += "\n<i>Automated by Hermes Agent</i>"
    return message

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
    automation_name = "market_brief"
    start_time = datetime.now(timezone.utc)
    
    try:
        # Fetch market data
        market_data = get_indonesian_market_data()
        
        if market_data is None:
            raise Exception("Failed to fetch market data")
        
        # Format message
        message = format_market_brief(market_data)
        
        # Send via Telegram
        result = send_telegram_message(message)
        
        if result and result.get('ok'):
            status = "success"
            log_message = "Market brief sent successfully"
            details = {
                'telegram_message_id': result.get('result', {}).get('message_id'),
                'data_points_fetched': len(market_data.get('search_results', [])) + len(market_data.get('news_results', []))
            }
        else:
            status = "error"
            log_message = f"Failed to send Telegram message: {result}"
            details = {'error': str(result)}
            
    except Exception as e:
        status = "error"
        log_message = str(e)
        details = {'error': str(e)}
        message = f"❌ Market Brief Error: {str(e)}"
        # Try to send error message
        try:
            send_telegram_message(message)
        except:
            pass  # Don't fail on error reporting
    
    # Log the run
    finish_time = datetime.now(timezone.utc)
    log_automation_run(
        automation_name=automation_name,
        status=status,
        message=log_message,
        details=details
    )
    
    print(f"Market brief automation completed: {status}")
    return status == "success"

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)