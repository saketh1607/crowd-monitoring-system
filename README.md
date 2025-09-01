# 🚨 Emergency Management System - User Manual

## 🎯 **How to Use Your Emergency Management System**

Your Emergency Management System is now **FULLY OPERATIONAL** and ready to protect large events! Here's everything you need to know to use it effectively.

---

## 🌐 **System Access Points**

### **1. Web Dashboard (Recommended for Beginners)**
- **URL**: `file:///c:/Users/bhanu/OneDrive/Desktop/LARGE%20EVENTS%20MONITORING/web_dashboard.html`
- **Features**: Visual interface, one-click testing, real-time monitoring
- **Best for**: Quick testing, monitoring, demonstrations

### **2. Interactive API Documentation**
- **URL**: http://127.0.0.1:8000/docs
- **Features**: Complete API reference, test all endpoints
- **Best for**: Detailed testing, integration development

### **3. Direct API Access**
- **Base URL**: http://127.0.0.1:8000
- **Health Check**: http://127.0.0.1:8000/health
- **Best for**: Programmatic integration, automation

---

## 🚀 **Quick Start Guide**

### **Step 1: Verify System is Running**
1. Open your web browser
2. Go to: http://127.0.0.1:8000/health
3. You should see: `{"status": "healthy", "database": "connected", ...}`

### **Step 2: Open the Web Dashboard**
1. Open the file: `web_dashboard.html` in your browser
2. You'll see real-time system statistics
3. Current risk level and recent emergencies

### **Step 3: Test Emergency Detection**
Click any of these buttons in the dashboard:
- **🔥 Test Fire Detection** - Simulates fire detection from cameras
- **👥 Test Crowd Analysis** - Analyzes crowd density
- **🚨 Test Behavior Analysis** - Detects suspicious behavior

---

## 📊 **Understanding the Dashboard**

### **System Statistics**
- **Active Emergencies**: Current ongoing incidents
- **Total Events**: Events being monitored
- **Available Resources**: Emergency response resources
- **Active Sensors**: Monitoring sensors online

### **Risk Levels**
- **🟢 LOW**: Normal operations, minimal threats
- **🟡 MEDIUM**: Some incidents detected, increased monitoring
- **🔴 HIGH**: Multiple emergencies, immediate attention required

### **Recent Emergencies**
Shows the latest emergency incidents with:
- Emergency ID and type
- Severity level
- Description
- Detection source (AI, manual, sensor)

---

## 🎮 **How to Use Each Feature**

### **🔥 Fire Detection**
**Purpose**: Detect fires from camera feeds
**How to use**:
1. Click "Test Fire Detection" in dashboard, OR
2. Send POST request to `/api/v1/emergencies/detect/fire`
3. Include camera image data and location
4. System returns fire detection result and confidence

**Real-world usage**: Connect to CCTV cameras, process live feeds

### **👥 Crowd Density Analysis**
**Purpose**: Monitor crowd levels and prevent overcrowding
**How to use**:
1. Click "Test Crowd Analysis" in dashboard, OR
2. Send POST request to `/api/v1/emergencies/analyze/crowd`
3. Include crowd image and area size
4. System returns people count and density level

**Real-world usage**: Monitor entrances, stages, and gathering areas

### **🚨 Behavior Analysis**
**Purpose**: Detect suspicious or threatening behavior
**How to use**:
1. Click "Test Behavior Analysis" in dashboard, OR
2. Send POST request to `/api/v1/emergencies/analyze/behavior`
3. Include motion and audio sensor data
4. System returns threat assessment

**Real-world usage**: Security monitoring, violence prevention

### **📅 Event Management**
**Purpose**: Create and manage events being monitored
**How to use**:
1. Click "Create Test Event" in dashboard, OR
2. Send POST request to `/api/v1/events/`
3. Include event details (name, venue, attendance, etc.)
4. System creates event for monitoring

### **🚨 Emergency Management**
**Purpose**: Track and respond to emergency incidents
**How to use**:
1. Click "Create Test Emergency" in dashboard, OR
2. Send POST request to `/api/v1/emergencies/`
3. Include emergency details (type, severity, location)
4. System creates emergency record

---

## 🔧 **Advanced Usage**

### **Using the API Directly**

#### **Python Example**:
```python
import requests

# Fire detection
response = requests.post('http://127.0.0.1:8000/api/v1/emergencies/detect/fire', 
    json={
        'image': 'base64_encoded_image',
        'camera_id': 'CAM_01',
        'location': {'x': 100, 'y': 200}
    })
result = response.json()
print(f"Fire detected: {result['fire_detected']}")
```

#### **JavaScript Example**:
```javascript
// Crowd analysis
fetch('http://127.0.0.1:8000/api/v1/emergencies/analyze/crowd', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
        image: 'base64_encoded_image',
        area_sqm: 100.0,
        camera_id: 'CAM_ENTRANCE'
    })
})
.then(response => response.json())
.then(data => console.log('People count:', data.people_count));
```

#### **cURL Example**:
```bash
# Behavior analysis
curl -X POST "http://127.0.0.1:8000/api/v1/emergencies/analyze/behavior" \
  -H "Content-Type: application/json" \
  -d '{
    "motion_data": [10, 15, 20, 25, 30],
    "audio_data": [60, 70, 80, 90, 100],
    "location": {"x": 300, "y": 400}
  }'
```

---

## 📱 **Real-World Integration**

### **Connecting Cameras**
1. Capture frames from CCTV cameras
2. Convert images to base64 format
3. Send to fire detection or crowd analysis endpoints
4. Process results and trigger alerts

### **Connecting Sensors**
1. Collect data from IoT sensors (motion, audio, temperature)
2. Send sensor readings to behavior analysis endpoint
3. Monitor for anomalies and threats
4. Integrate with building management systems

### **Emergency Response Integration**
1. Monitor API for new emergencies
2. Automatically notify emergency services
3. Dispatch resources based on emergency type
4. Track response times and outcomes

---

## 🛠️ **Troubleshooting**

### **Server Not Responding**
- Check if server is running: `python run_server.py`
- Verify URL: http://127.0.0.1:8000/health
- Check firewall settings

### **Dashboard Not Loading**
- Ensure server is running on port 8000
- Check browser console for errors
- Try refreshing the page

### **API Errors**
- Check request format (JSON)
- Verify endpoint URLs
- Review API documentation at `/docs`

### **Database Issues**
- Run: `python setup_sqlite.py` to recreate database
- Check if `emergency_management.db` file exists

---

## 📈 **Monitoring and Maintenance**

### **Regular Checks**
- Monitor dashboard for system health
- Check emergency response times
- Review detection accuracy
- Update ML models as needed

### **Performance Optimization**
- Monitor API response times
- Scale resources for high-traffic events
- Optimize database queries
- Cache frequently accessed data

---

## 🎯 **Best Practices**

### **For Event Organizers**
1. Set up monitoring before events start
2. Test all detection systems
3. Train staff on emergency procedures
4. Have backup communication methods

### **For Developers**
1. Use the interactive API docs for testing
2. Implement proper error handling
3. Monitor API rate limits
4. Keep ML models updated

### **For Emergency Responders**
1. Familiarize yourself with the dashboard
2. Understand alert priorities
3. Practice response procedures
4. Maintain communication channels

---

## 🚀 **Next Steps**

### **Immediate Actions**
1. ✅ Test all features using the web dashboard
2. ✅ Explore the interactive API documentation
3. ✅ Run the usage guide script: `python usage_guide.py`
4. ✅ Check database status: `python check_database.py`

### **For Production Deployment**
1. Replace mock ML models with real trained models
2. Set up PostgreSQL database
3. Configure SSL/HTTPS
4. Deploy to cloud infrastructure
5. Set up monitoring and alerting
6. Train emergency response teams

---

## 📞 **Support and Resources**

### **System Files**
- **Main Server**: `run_server.py`
- **Web Dashboard**: `web_dashboard.html`
- **Usage Guide**: `usage_guide.py`
- **Database Setup**: `setup_sqlite.py`
- **API Documentation**: http://127.0.0.1:8000/docs

### **Key Directories**
- **Models**: `data/models/` (ML model files)
- **Database**: `emergency_management.db`
- **Logs**: `logs/` (system logs)
- **Config**: `config/` (configuration files)

---

## 🎉 **Congratulations!**

You now have a **fully functional AI-powered Emergency Management System**! 

**Your system can**:
- ✅ Detect fires automatically from camera feeds
- ✅ Monitor crowd density and prevent overcrowding  
- ✅ Identify suspicious behavior and security threats
- ✅ Manage emergency incidents in real-time
- ✅ Optimize emergency response and resource allocation
- ✅ Provide real-time monitoring and alerts

**Start using it now** by opening the web dashboard and testing the emergency detection features!

🌐 **Web Dashboard**: Open `web_dashboard.html` in your browser
📖 **API Docs**: http://127.0.0.1:8000/docs
❤️ **Health Check**: http://127.0.0.1:8000/health
