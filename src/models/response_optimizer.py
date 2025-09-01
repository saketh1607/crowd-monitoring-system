"""
Response Optimization System for Emergency Management
"""
import numpy as np
import heapq
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging
from scipy.optimize import linear_sum_assignment
from scipy.spatial.distance import euclidean

logger = logging.getLogger(__name__)


@dataclass
class EmergencyIncident:
    """Emergency incident data structure"""
    id: str
    type: str  # medical, fire, security
    location: Tuple[float, float]  # (x, y) coordinates
    severity: str  # low, medium, high, critical
    priority: int  # 1 (highest) to 5 (lowest)
    detected_at: datetime
    estimated_response_time: int  # seconds
    required_resources: List[str]
    status: str = "detected"


@dataclass
class Resource:
    """Emergency response resource data structure"""
    id: str
    type: str  # medical_personnel, fire_personnel, security_personnel, vehicle
    location: Tuple[float, float]  # current (x, y) coordinates
    capacity: int
    is_available: bool
    capabilities: List[str]
    response_time_factor: float = 1.0  # multiplier for response time
    current_assignment: Optional[str] = None


class ResourceAllocator:
    """Optimal resource allocation for emergency response"""
    
    def __init__(self):
        self.active_incidents = {}
        self.available_resources = {}
        self.assignments = {}
        
        # Priority weights for different emergency types
        self.type_priorities = {
            "fire": 1,
            "medical": 2,
            "security": 3
        }
        
        # Severity multipliers
        self.severity_multipliers = {
            "critical": 4.0,
            "high": 3.0,
            "medium": 2.0,
            "low": 1.0
        }
    
    def add_incident(self, incident: EmergencyIncident):
        """Add new emergency incident"""
        self.active_incidents[incident.id] = incident
        logger.info(f"Added incident {incident.id}: {incident.type} at {incident.location}")
    
    def add_resource(self, resource: Resource):
        """Add available resource"""
        self.available_resources[resource.id] = resource
        logger.info(f"Added resource {resource.id}: {resource.type} at {resource.location}")
    
    def calculate_response_time(self, resource: Resource, incident: EmergencyIncident) -> float:
        """Calculate estimated response time"""
        # Calculate distance
        distance = euclidean(resource.location, incident.location)
        
        # Base response time (assuming 1 unit distance = 1 minute)
        base_time = distance * 60  # seconds
        
        # Apply resource-specific factor
        response_time = base_time * resource.response_time_factor
        
        return response_time
    
    def calculate_assignment_score(self, resource: Resource, incident: EmergencyIncident) -> float:
        """Calculate assignment score (lower is better)"""
        # Response time component
        response_time = self.calculate_response_time(resource, incident)
        
        # Priority component
        type_priority = self.type_priorities.get(incident.type, 3)
        severity_multiplier = self.severity_multipliers.get(incident.severity, 1.0)
        
        # Resource capability match
        capability_match = 1.0
        for req_capability in incident.required_resources:
            if req_capability in resource.capabilities:
                capability_match *= 0.8  # Better match = lower score
        
        # Combined score
        score = (response_time / 60) * type_priority * capability_match / severity_multiplier
        
        return score
    
    def optimize_assignments(self) -> Dict[str, str]:
        """Optimize resource assignments using Hungarian algorithm"""
        try:
            # Get available resources and active incidents
            available_resources = [r for r in self.available_resources.values() if r.is_available]
            active_incidents = list(self.active_incidents.values())
            
            if not available_resources or not active_incidents:
                return {}
            
            # Create cost matrix
            cost_matrix = []
            for resource in available_resources:
                resource_costs = []
                for incident in active_incidents:
                    # Check if resource can handle this incident type
                    if self._can_handle_incident(resource, incident):
                        cost = self.calculate_assignment_score(resource, incident)
                    else:
                        cost = float('inf')  # Cannot handle
                    resource_costs.append(cost)
                cost_matrix.append(resource_costs)
            
            cost_matrix = np.array(cost_matrix)
            
            # Solve assignment problem
            resource_indices, incident_indices = linear_sum_assignment(cost_matrix)
            
            # Create assignments
            assignments = {}
            for r_idx, i_idx in zip(resource_indices, incident_indices):
                if cost_matrix[r_idx, i_idx] != float('inf'):
                    resource_id = available_resources[r_idx].id
                    incident_id = active_incidents[i_idx].id
                    assignments[resource_id] = incident_id
                    
                    # Update resource status
                    self.available_resources[resource_id].is_available = False
                    self.available_resources[resource_id].current_assignment = incident_id
            
            self.assignments.update(assignments)
            logger.info(f"Optimized assignments: {assignments}")
            
            return assignments
            
        except Exception as e:
            logger.error(f"Error optimizing assignments: {e}")
            return {}
    
    def _can_handle_incident(self, resource: Resource, incident: EmergencyIncident) -> bool:
        """Check if resource can handle the incident"""
        # Check if resource type matches incident requirements
        incident_type_mapping = {
            "medical": ["medical_personnel", "ambulance"],
            "fire": ["fire_personnel", "fire_truck"],
            "security": ["security_personnel", "police_car"]
        }
        
        required_types = incident_type_mapping.get(incident.type, [])
        return resource.type in required_types
    
    def get_assignment_recommendations(self) -> List[Dict[str, Any]]:
        """Get detailed assignment recommendations"""
        recommendations = []
        
        for resource_id, incident_id in self.assignments.items():
            resource = self.available_resources[resource_id]
            incident = self.active_incidents[incident_id]
            
            response_time = self.calculate_response_time(resource, incident)
            
            recommendation = {
                "resource_id": resource_id,
                "resource_type": resource.type,
                "incident_id": incident_id,
                "incident_type": incident.type,
                "incident_severity": incident.severity,
                "estimated_response_time": response_time,
                "priority": incident.priority,
                "assignment_score": self.calculate_assignment_score(resource, incident)
            }
            recommendations.append(recommendation)
        
        # Sort by priority and response time
        recommendations.sort(key=lambda x: (x["priority"], x["estimated_response_time"]))
        
        return recommendations


class EvacuationPlanner:
    """Plan optimal evacuation routes and procedures"""
    
    def __init__(self, venue_layout: Dict[str, Any]):
        self.venue_layout = venue_layout
        self.exits = venue_layout.get("exits", [])
        self.capacity_zones = venue_layout.get("zones", {})
        self.obstacles = venue_layout.get("obstacles", [])
    
    def calculate_evacuation_plan(self, incident_location: Tuple[float, float], 
                                crowd_distribution: Dict[str, int]) -> Dict[str, Any]:
        """Calculate optimal evacuation plan"""
        try:
            # Identify affected zones
            affected_zones = self._identify_affected_zones(incident_location)
            
            # Calculate exit assignments
            exit_assignments = self._assign_zones_to_exits(affected_zones, crowd_distribution)
            
            # Estimate evacuation time
            evacuation_time = self._estimate_evacuation_time(exit_assignments, crowd_distribution)
            
            # Generate evacuation routes
            routes = self._generate_evacuation_routes(exit_assignments)
            
            return {
                "affected_zones": affected_zones,
                "exit_assignments": exit_assignments,
                "estimated_evacuation_time": evacuation_time,
                "evacuation_routes": routes,
                "recommendations": self._generate_evacuation_recommendations(
                    incident_location, affected_zones
                ),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error calculating evacuation plan: {e}")
            return {
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def _identify_affected_zones(self, incident_location: Tuple[float, float]) -> List[str]:
        """Identify zones affected by the incident"""
        affected_zones = []
        danger_radius = 50  # meters
        
        for zone_id, zone_info in self.capacity_zones.items():
            zone_center = zone_info.get("center", (0, 0))
            distance = euclidean(incident_location, zone_center)
            
            if distance <= danger_radius:
                affected_zones.append(zone_id)
        
        return affected_zones
    
    def _assign_zones_to_exits(self, affected_zones: List[str], 
                             crowd_distribution: Dict[str, int]) -> Dict[str, List[str]]:
        """Assign zones to optimal exits"""
        exit_assignments = {exit["id"]: [] for exit in self.exits}
        
        for zone_id in affected_zones:
            if zone_id not in crowd_distribution:
                continue
                
            zone_center = self.capacity_zones[zone_id]["center"]
            
            # Find closest available exit
            best_exit = None
            min_distance = float('inf')
            
            for exit_info in self.exits:
                exit_location = exit_info["location"]
                distance = euclidean(zone_center, exit_location)
                
                # Check exit capacity
                current_load = sum(crowd_distribution.get(z, 0) for z in exit_assignments[exit_info["id"]])
                if current_load + crowd_distribution[zone_id] <= exit_info["capacity"]:
                    if distance < min_distance:
                        min_distance = distance
                        best_exit = exit_info["id"]
            
            if best_exit:
                exit_assignments[best_exit].append(zone_id)
        
        return exit_assignments
    
    def _estimate_evacuation_time(self, exit_assignments: Dict[str, List[str]], 
                                crowd_distribution: Dict[str, int]) -> int:
        """Estimate total evacuation time in seconds"""
        max_time = 0
        
        for exit_id, assigned_zones in exit_assignments.items():
            total_people = sum(crowd_distribution.get(zone, 0) for zone in assigned_zones)
            
            # Find exit capacity
            exit_capacity = next(
                (exit["capacity"] for exit in self.exits if exit["id"] == exit_id), 
                100
            )
            
            # Estimate time (assuming 2 people per second per exit)
            exit_flow_rate = min(exit_capacity / 50, 2)  # people per second
            evacuation_time = total_people / exit_flow_rate if exit_flow_rate > 0 else 0
            
            max_time = max(max_time, evacuation_time)
        
        return int(max_time)
    
    def _generate_evacuation_routes(self, exit_assignments: Dict[str, List[str]]) -> List[Dict[str, Any]]:
        """Generate evacuation route instructions"""
        routes = []
        
        for exit_id, assigned_zones in exit_assignments.items():
            exit_info = next((exit for exit in self.exits if exit["id"] == exit_id), None)
            if not exit_info:
                continue
            
            for zone_id in assigned_zones:
                zone_info = self.capacity_zones.get(zone_id, {})
                
                route = {
                    "zone_id": zone_id,
                    "exit_id": exit_id,
                    "exit_name": exit_info.get("name", f"Exit {exit_id}"),
                    "direction": self._calculate_direction(
                        zone_info.get("center", (0, 0)), 
                        exit_info["location"]
                    ),
                    "distance": euclidean(
                        zone_info.get("center", (0, 0)), 
                        exit_info["location"]
                    ),
                    "instructions": f"Proceed to {exit_info.get('name', f'Exit {exit_id}')} via the shortest safe route"
                }
                routes.append(route)
        
        return routes
    
    def _calculate_direction(self, from_point: Tuple[float, float], 
                           to_point: Tuple[float, float]) -> str:
        """Calculate cardinal direction from one point to another"""
        dx = to_point[0] - from_point[0]
        dy = to_point[1] - from_point[1]
        
        angle = np.arctan2(dy, dx) * 180 / np.pi
        
        if -22.5 <= angle < 22.5:
            return "East"
        elif 22.5 <= angle < 67.5:
            return "Northeast"
        elif 67.5 <= angle < 112.5:
            return "North"
        elif 112.5 <= angle < 157.5:
            return "Northwest"
        elif 157.5 <= angle or angle < -157.5:
            return "West"
        elif -157.5 <= angle < -112.5:
            return "Southwest"
        elif -112.5 <= angle < -67.5:
            return "South"
        else:
            return "Southeast"
    
    def _generate_evacuation_recommendations(self, incident_location: Tuple[float, float], 
                                           affected_zones: List[str]) -> List[str]:
        """Generate evacuation recommendations"""
        recommendations = []
        
        recommendations.append("Activate emergency announcement system")
        recommendations.append("Deploy personnel to guide evacuation")
        recommendations.append("Ensure emergency exits are clear and accessible")
        
        if len(affected_zones) > 3:
            recommendations.append("Consider phased evacuation to prevent overcrowding")
        
        recommendations.append("Monitor crowd flow and adjust routes as needed")
        recommendations.append("Coordinate with external emergency services")
        
        return recommendations


class CommunicationCoordinator:
    """Coordinate emergency communications and notifications"""
    
    def __init__(self):
        self.notification_channels = {
            "emergency_services": {"priority": 1, "method": "direct_call"},
            "event_staff": {"priority": 2, "method": "radio"},
            "security_team": {"priority": 2, "method": "radio"},
            "medical_team": {"priority": 2, "method": "radio"},
            "attendees": {"priority": 3, "method": "public_announcement"},
            "media": {"priority": 4, "method": "press_release"}
        }
    
    def create_communication_plan(self, incident: EmergencyIncident, 
                                assignments: Dict[str, str]) -> Dict[str, Any]:
        """Create comprehensive communication plan"""
        try:
            # Generate messages for different audiences
            messages = self._generate_messages(incident)
            
            # Create notification timeline
            timeline = self._create_notification_timeline(incident, messages)
            
            # Generate contact list
            contacts = self._generate_contact_list(incident, assignments)
            
            return {
                "incident_id": incident.id,
                "messages": messages,
                "notification_timeline": timeline,
                "contact_list": contacts,
                "communication_channels": self.notification_channels,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error creating communication plan: {e}")
            return {
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def _generate_messages(self, incident: EmergencyIncident) -> Dict[str, str]:
        """Generate appropriate messages for different audiences"""
        messages = {}
        
        # Emergency services message
        messages["emergency_services"] = (
            f"Emergency at event location {incident.location}. "
            f"Type: {incident.type}, Severity: {incident.severity}. "
            f"Immediate response required."
        )
        
        # Staff message
        messages["event_staff"] = (
            f"Emergency situation detected: {incident.type} incident "
            f"at location {incident.location}. Follow emergency protocols. "
            f"Await further instructions."
        )
        
        # Public announcement
        if incident.severity in ["high", "critical"]:
            messages["attendees"] = (
                f"Attention: For your safety, please follow staff instructions "
                f"and proceed to designated safe areas. Remain calm and orderly."
            )
        else:
            messages["attendees"] = (
                f"Please be aware of ongoing safety procedures in your area. "
                f"Follow staff guidance and remain alert."
            )
        
        return messages
    
    def _create_notification_timeline(self, incident: EmergencyIncident, 
                                    messages: Dict[str, str]) -> List[Dict[str, Any]]:
        """Create timeline for notifications"""
        timeline = []
        base_time = datetime.utcnow()
        
        # Immediate notifications (0-2 minutes)
        timeline.append({
            "time": base_time,
            "audience": "emergency_services",
            "message": messages.get("emergency_services", ""),
            "method": "direct_call",
            "priority": 1
        })
        
        timeline.append({
            "time": base_time + timedelta(seconds=30),
            "audience": "event_staff",
            "message": messages.get("event_staff", ""),
            "method": "radio",
            "priority": 2
        })
        
        # Secondary notifications (2-5 minutes)
        if incident.severity in ["high", "critical"]:
            timeline.append({
                "time": base_time + timedelta(minutes=2),
                "audience": "attendees",
                "message": messages.get("attendees", ""),
                "method": "public_announcement",
                "priority": 3
            })
        
        return timeline
    
    def _generate_contact_list(self, incident: EmergencyIncident, 
                             assignments: Dict[str, str]) -> List[Dict[str, Any]]:
        """Generate prioritized contact list"""
        contacts = []
        
        # Emergency services
        contacts.append({
            "name": "Emergency Services",
            "type": "emergency_services",
            "phone": "911",
            "priority": 1,
            "notify_immediately": True
        })
        
        # Event management
        contacts.append({
            "name": "Event Manager",
            "type": "management",
            "priority": 2,
            "notify_immediately": True
        })
        
        # Assigned resources
        for resource_id in assignments.keys():
            contacts.append({
                "name": f"Resource {resource_id}",
                "type": "assigned_resource",
                "resource_id": resource_id,
                "priority": 2,
                "notify_immediately": True
            })
        
        return contacts
