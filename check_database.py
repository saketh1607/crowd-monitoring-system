"""
Check the current status of the Emergency Management System database
"""
import sqlite3
from datetime import datetime

def check_database_status():
    """Check and display database status"""
    try:
        conn = sqlite3.connect('emergency_management.db')
        cursor = conn.cursor()
        
        print('📊 Emergency Management System - Database Status')
        print('=' * 50)
        
        # Events
        cursor.execute('SELECT COUNT(*) FROM events')
        events_count = cursor.fetchone()[0]
        print(f'📅 Total Events: {events_count}')
        
        # Emergencies
        cursor.execute('SELECT COUNT(*) FROM emergencies')
        emergencies_count = cursor.fetchone()[0]
        print(f'🚨 Total Emergencies: {emergencies_count}')
        
        cursor.execute('SELECT type, severity, COUNT(*) FROM emergencies GROUP BY type, severity')
        emergency_breakdown = cursor.fetchall()
        if emergency_breakdown:
            print('   Emergency Breakdown:')
            for emergency_type, severity, count in emergency_breakdown:
                print(f'     {emergency_type} ({severity}): {count}')
        
        # Resources
        cursor.execute('SELECT COUNT(*) FROM resources WHERE status = "available"')
        available_resources = cursor.fetchone()[0]
        print(f'🚑 Available Resources: {available_resources}')
        
        # Sensors
        cursor.execute('SELECT COUNT(*) FROM sensors WHERE status = "active"')
        active_sensors = cursor.fetchone()[0]
        print(f'📡 Active Sensors: {active_sensors}')
        
        # Recent emergencies
        print('\n🕐 Recent Emergencies:')
        cursor.execute('SELECT id, type, severity, description, created_at FROM emergencies ORDER BY created_at DESC LIMIT 5')
        recent = cursor.fetchall()
        
        if recent:
            for emergency_id, etype, severity, desc, created in recent:
                desc_short = desc[:50] + '...' if len(desc) > 50 else desc
                print(f'   #{emergency_id}: {etype.upper()} ({severity}) - {desc_short}')
        else:
            print('   No emergencies recorded yet')
        
        # Recent events
        print('\n📅 Recent Events:')
        cursor.execute('SELECT id, name, venue, expected_attendance, risk_level FROM events ORDER BY created_at DESC LIMIT 3')
        events = cursor.fetchall()
        
        if events:
            for event_id, name, venue, attendance, risk in events:
                print(f'   #{event_id}: {name} at {venue} ({attendance:,} people, {risk} risk)')
        else:
            print('   No events recorded yet')
        
        conn.close()
        print('\n✅ Database query complete!')
        
        return True
        
    except Exception as e:
        print(f'❌ Error checking database: {e}')
        return False

if __name__ == "__main__":
    check_database_status()
