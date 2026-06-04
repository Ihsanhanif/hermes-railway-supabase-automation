#!/usr/bin/env python3
"""
LLM Usage Monitor Automation for Hermes + Supabase
Tracks usage every 5 minutes and stores metrics in Supabase
"""

import os
import json
import time
from datetime import datetime, timezone
from hermes_tools import terminal
import supabase

# Initialize Supabase client
supabase_url = os.environ.get('SUPABASE_URL')
supabase_key = os.environ.get('SUPABASE_ANON_KEY')
supabase_client = supabase.create_client(supabase_url, supabase_key)

# Telegram configuration for alerts
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')

# Thresholds for alerts (adjust as needed)
DAILY_TOKEN_LIMIT = 100000  # 100k tokens per day
HOURLY_COST_LIMIT = 5.0     # $5 per hour

def send_telegram_message(message):
    """Send message via Telegram bot"""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
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

def get_hermes_usage_stats():
    """Get Hermes/LLM usage statistics"""
    try:
        # This would ideally come from Hermes internal metrics
        # For now, we'll simulate or read from logs if available
        # You might need to customize this based on how Hermes exposes usage data
        
        # Try to read from Hermes history or logs
        hermes_history_path = os.path.expanduser("~/.hermes/.hermes_history")
        if os.path.exists(hermes_history_path):
            # Simple parsing - in reality, you'd want more sophisticated metrics
            with open(hermes_history_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                # Count recent interactions as a proxy for usage
                recent_lines = [line for line in lines[-50:] if line.strip()]
                interaction_count = len(recent_lines)
                
                # Rough estimates (you'll want to replace with actual metrics)
                estimated_prompt_tokens = interaction_count * 150  # avg per interaction
                estimated_completion_tokens = interaction_count * 350
                estimated_total_tokens = estimated_prompt_tokens + estimated_completion_tokens
                estimated_cost = estimated_total_tokens * 0.000002  # rough estimate
                
                return {
                    'timestamp': datetime.now(timezone.utc).isoformat(),
                    'model': os.environ.get('HERMES_MODEL', 'unknown'),
                    'provider': os.environ.get('HERMES_PROVIDER', 'unknown'),
                    'prompt_tokens': estimated_prompt_tokens,
                    'completion_tokens': estimated_completion_tokens,
                    'total_tokens': estimated_total_tokens,
                    'cost_usd': round(estimated_cost, 6),
                    'response_time_ms': 1000  # placeholder
                }
        
        # Fallback: return minimal data
        return {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'model': os.environ.get('HERMES_MODEL', 'unknown'),
            'provider': os.environ.get('HERMES_PROVIDER', 'unknown'),
            'prompt_tokens': 0,
            'completion_tokens': 0,
            'total_tokens': 0,
            'cost_usd': 0.0,
            'response_time_ms': 0
        }
    except Exception as e:
        print(f"Error getting Hermes usage stats: {e}")
        return {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'model': 'error',
            'provider': 'error',
            'prompt_tokens': 0,
            'completion_tokens': 0,
            'total_tokens': 0,
            'cost_usd': 0.0,
            'response_time_ms': 0
        }

def check_usage_thresholds(usage_data):
    """Check if usage exceeds thresholds and send alerts"""
    alerts = []
    
    # Daily token limit check (simplified - in production you'd query Supabase for daily total)
    if usage_data['total_tokens'] > DAILY_TOKEN_LIMIT:
        alerts.append(f"⚠️ High token usage: {usage_data['total_tokens']:,} tokens this interaction")
    
    # Hourly cost check (simplified)
    if usage_data['cost_usd'] > HOURLY_COST_LIMIT:
        alerts.append(f"⚠️ High cost: ${usage_data['cost_usd']:.4f} this interaction")
    
    return alerts

def log_llm_usage(usage_data):
    """Log LLM usage to Supabase"""
    try:
        supabase_client.table('llm_usage').insert({
            'model': usage_data['model'],
            'provider': usage_data['provider'],
            'prompt_tokens': usage_data['prompt_tokens'],
            'completion_tokens': usage_data['completion_tokens'],
            'total_tokens': usage_data['total_tokens'],
            'cost_usd': usage_data['cost_usd'],
            'response_time_ms': usage_data['response_time_ms']
        }).execute()
    except Exception as e:
        print(f"Error logging LLM usage to Supabase: {e}")

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
    automation_name = "llm_monitor"
    start_time = datetime.now(timezone.utc)
    
    try:
        # Get usage statistics
        usage_data = get_hermes_usage_stats()
        
        # Log to Supabase
        log_llm_usage(usage_data)
        
        # Check for threshold alerts
        alerts = check_usage_thresholds(usage_data)
        
        # Send alerts if any
        if alerts:
            alert_message = "🤖 <b>Hermes Usage Alert</b>\n\n" + "\n".join(alerts)
            send_telegram_message(alert_message)
        
        status = "success"
        log_message = f"LLM usage logged: {usage_data['total_tokens']} tokens, ${usage_data['cost_usd']:.6f}"
        details = {
            'tokens_logged': usage_data['total_tokens'],
            'cost_logged': usage_data['cost_usd'],
            'alerts_sent': len(alerts)
        }
        
    except Exception as e:
        status = "error"
        log_message = str(e)
        details = {'error': str(e)}
    
    # Log the run
    log_automation_run(
        automation_name=automation_name,
        status=status,
        message=log_message,
        details=details
    )
    
    print(f"LLM monitor automation completed: {status}")
    return status == "success"

if __name__ == "__main__":
    # Import requests here to avoid issues if not used
    import requests
    success = main()
    exit(0 if success else 1)