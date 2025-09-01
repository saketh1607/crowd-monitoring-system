"""
Real-time Camera Detection Status Monitor
Shows live detection results from camera feed
"""
import requests
import time
import json
from datetime import datetime
import threading

class DetectionStatusMonitor:
    """Monitor and display real-time detection status"""
    
    def __init__(self, api_url="http://127.0.0.1:8000/api/v1"):
        self.api_url = api_url
        self.running = False
        self.stats = {
            "fire_detections": 0,
            "crowd_alerts": 0,
            "behavior_alerts": 0,
            "total_checks": 0,
            "last_fire_confidence": 0.0,
            "last_crowd_count": 0,
            "start_time": None
        }
    
    def start_monitoring(self):
        """Start monitoring detection status"""
        self.running = True
        self.stats["start_time"] = datetime.now()
        
        print("🎥 Real-time Camera Detection Status Monitor")
        print("=" * 60)
        print("📊 Monitoring live detection results from camera feed...")
        print("🔄 Updates every 5 seconds")
        print("Press Ctrl+C to stop")
        print("-" * 60)
        
        try:
            while self.running:
                self.check_detection_status()
                time.sleep(5)
        except KeyboardInterrupt:
            print("\n🛑 Stopping detection monitor...")
        finally:
            self.stop_monitoring()
    
    def stop_monitoring(self):
        """Stop monitoring"""
        self.running = False
        self.print_final_summary()
    
    def check_detection_status(self):
        """Check current detection status"""
        try:
            # Get dashboard data
            response = requests.get(f"{self.api_url}/monitoring/dashboard", timeout=3)
            if response.status_code == 200:
                data = response.json()
                self.update_stats(data)
                self.print_status_update(data)
            else:
                print("❌ Failed to get detection status")
                
        except Exception as e:
            print(f"❌ Error checking status: {e}")
    
    def update_stats(self, data):
        """Update internal statistics"""
        self.stats["total_checks"] += 1
        
        # Count emergencies by type
        recent_emergencies = data.get("recent_emergencies", [])
        for emergency in recent_emergencies:
            if emergency.get("type") == "fire":
                self.stats["fire_detections"] += 1
            elif emergency.get("type") == "crowd_control":
                self.stats["crowd_alerts"] += 1
            elif emergency.get("type") == "security":
                self.stats["behavior_alerts"] += 1
    
    def print_status_update(self, data):
        """Print current status update"""
        current_time = datetime.now().strftime("%H:%M:%S")
        uptime = datetime.now() - self.stats["start_time"]
        uptime_str = str(uptime).split('.')[0]
        
        # Clear screen (works on most terminals)
        print("\033[2J\033[H", end="")
        
        print("🎥 REAL-TIME CAMERA DETECTION STATUS")
        print("=" * 60)
        print(f"⏰ Time: {current_time} | ⏱️ Uptime: {uptime_str}")
        print(f"🔄 Status Checks: {self.stats['total_checks']}")
        print("-" * 60)
        
        # System Status
        risk_level = data.get("risk_level", "unknown").upper()
        risk_emoji = {"LOW": "🟢", "MEDIUM": "🟡", "HIGH": "🔴"}.get(risk_level, "⚪")
        print(f"🚨 SYSTEM STATUS: {risk_emoji} {risk_level} RISK")
        print(f"📊 Active Emergencies: {data.get('active_emergencies', 0)}")
        print(f"📡 Active Sensors: {data.get('active_sensors', 0)}")
        print()
        
        # Detection Status
        print("🔍 LIVE DETECTION STATUS:")
        print("-" * 30)
        
        # Fire Detection
        fire_status = "🟢 SAFE" if self.stats["fire_detections"] == 0 else f"🔴 {self.stats['fire_detections']} DETECTED"
        print(f"🔥 Fire Detection: {fire_status}")
        print(f"   Last Confidence: {self.stats['last_fire_confidence']:.3f}")
        
        # Crowd Analysis
        crowd_status = "🟢 NORMAL" if self.stats["crowd_alerts"] == 0 else f"🟡 {self.stats['crowd_alerts']} ALERTS"
        print(f"👥 Crowd Analysis: {crowd_status}")
        print(f"   Current Count: {self.stats['last_crowd_count']} people")
        
        # Behavior Analysis
        behavior_status = "🟢 NORMAL" if self.stats["behavior_alerts"] == 0 else f"🟡 {self.stats['behavior_alerts']} ALERTS"
        print(f"🚨 Behavior Analysis: {behavior_status}")
        print()
        
        # Recent Events
        recent_emergencies = data.get("recent_emergencies", [])
        if recent_emergencies:
            print("📋 RECENT EMERGENCY EVENTS:")
            print("-" * 30)
            for i, emergency in enumerate(recent_emergencies[:3]):
                emergency_time = emergency.get("created_at", "")
                if emergency_time:
                    try:
                        # Parse and format time
                        dt = datetime.fromisoformat(emergency_time.replace('Z', '+00:00'))
                        time_str = dt.strftime("%H:%M:%S")
                    except:
                        time_str = emergency_time[:8] if len(emergency_time) > 8 else emergency_time
                else:
                    time_str = "Unknown"
                
                emergency_type = emergency.get("type", "unknown").upper()
                severity = emergency.get("severity", "unknown").upper()
                description = emergency.get("description", "No description")[:40]
                
                print(f"{i+1}. [{time_str}] {emergency_type} ({severity})")
                print(f"   {description}...")
        else:
            print("📋 RECENT EVENTS: No emergencies detected")
        
        print()
        print("-" * 60)
        print("🎥 Camera feed running | 📊 Dashboard updating | 🔄 Next check in 5s")
    
    def print_final_summary(self):
        """Print final monitoring summary"""
        if self.stats["start_time"]:
            total_time = datetime.now() - self.stats["start_time"]
            
            print("\n" + "=" * 60)
            print("📊 DETECTION MONITORING SUMMARY")
            print("=" * 60)
            print(f"⏱️ Total Monitoring Time: {str(total_time).split('.')[0]}")
            print(f"🔄 Total Status Checks: {self.stats['total_checks']}")
            print(f"🔥 Fire Detections: {self.stats['fire_detections']}")
            print(f"👥 Crowd Alerts: {self.stats['crowd_alerts']}")
            print(f"🚨 Behavior Alerts: {self.stats['behavior_alerts']}")
            print("✅ Monitoring session completed")


def main():
    """Main function"""
    print("🎥 Starting Real-time Camera Detection Monitor")
    print("🔗 Make sure your camera system is running:")
    print("   python simple_live_detection.py")
    print("   python run_server.py")
    print()
    
    # Check if API is available
    try:
        response = requests.get("http://127.0.0.1:8000/health", timeout=3)
        if response.status_code == 200:
            print("✅ API server is running")
        else:
            print("❌ API server not responding")
            return
    except:
        print("❌ Cannot connect to API server")
        print("   Please start: python run_server.py")
        return
    
    # Start monitoring
    monitor = DetectionStatusMonitor()
    monitor.start_monitoring()


if __name__ == "__main__":
    main()
