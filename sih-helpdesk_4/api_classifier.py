"""
Smart Ticket Classifier for PowerGrid Helpdesk
Keyword-based NLP classification
"""

class TicketClassifier:
    """Classify tickets into categories and assign teams"""
    
    # Keyword mappings for PowerGrid IT scenarios
    KEYWORDS = {
        'Network': [
            'vpn', 'network', 'connectivity', 'internet', 'wifi', 'lan', 'wan',
            'router', 'switch', 'ip', 'dns', 'gateway', 'firewall', 'ping',
            'connection', 'bandwidth', 'ethernet', 'cable', 'port'
        ],
        'Application': [
            'outlook', 'teams', 'sap', 'glpi', 'solman', 'application', 'app',
            'software crash', 'program', 'excel', 'word', 'powerpoint', 'sharepoint',
            'erp', 'crm', 'database query', 'report', 'dashboard'
        ],
        'Hardware': [
            'laptop', 'desktop', 'computer', 'printer', 'scanner', 'mouse', 'keyboard',
            'monitor', 'screen', 'display', 'cpu', 'ram', 'hard drive', 'disk',
            'usb', 'charger', 'battery', 'hardware', 'device', 'equipment'
        ],
        'Access': [
            'password', 'login', 'account', 'access', 'permission', 'unlock',
            'locked', 'authentication', 'credential', 'reset password', 'forgot password',
            'user account', 'access denied', 'authorization', 'rights', 'privileges'
        ],
        'Software': [
            'windows', 'office', 'installation', 'install', 'update', 'patch',
            'license', 'antivirus', 'software', 'driver', 'upgrade', 'uninstall',
            'config', 'configuration', 'settings', 'system'
        ]
    }
    
    # Team assignments
    TEAM_MAPPING = {
        'Network': 'NetworkTeam',
        'Application': 'AppTeam',
        'Hardware': 'HardwareTeam',
        'Access': 'AccessTeam',
        'Software': 'SoftwareTeam'
    }
    
    @classmethod
    def classify(cls, title, description):
        """
        Classify ticket based on keywords
        Returns: (category, assigned_team)
        """
        text = f"{title} {description}".lower()
        
        scores = {category: 0 for category in cls.KEYWORDS}
        
        # Count keyword matches
        for category, keywords in cls.KEYWORDS.items():
            for keyword in keywords:
                if keyword in text:
                    scores[category] += 1
        
        # Get category with highest score
        category = max(scores, key=scores.get)
        
        # If no matches, default to Software
        if scores[category] == 0:
            category = 'Software'
        
        team = cls.TEAM_MAPPING[category]
        
        return category, team
    
    @classmethod
    def get_priority_boost(cls, urgency):
        """Convert urgency to priority score for routing"""
        priority_map = {
            'Critical': 4,
            'High': 3,
            'Medium': 2,
            'Low': 1
        }
        return priority_map.get(urgency, 2)
