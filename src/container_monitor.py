"""
Container monitoring module for GraniteRCA.

This module provides functionality to monitor container health for both Podman and Docker,
including resource usage, status, and log collection.

SPDX-License-Identifier: Apache-2.0
"""

import subprocess
import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional, Union

class ContainerMonitor:
    def __init__(self):
        self.container_runtime = self._detect_container_runtime()
        
    def _detect_container_runtime(self) -> Optional[str]:
        """Detect which container runtime is available (podman or docker)."""
        try:
            subprocess.run(['podman', '--version'], capture_output=True, check=True)
            return 'podman'
        except (subprocess.SubprocessError, FileNotFoundError):
            try:
                subprocess.run(['docker', '--version'], capture_output=True, check=True)
                return 'docker'
            except (subprocess.SubprocessError, FileNotFoundError):
                return None
    
    def get_container_stats(self) -> Union[List[Dict[str, Any]], Dict[str, str]]:
        """Get resource usage statistics for all containers."""
        if not self.container_runtime:
            return {"error": "No container runtime detected"}
            
        try:
            cmd = [self.container_runtime, 'stats', '--no-stream', '--format', 'json']
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return json.loads(result.stdout)
        except (subprocess.SubprocessError, json.JSONDecodeError) as e:
            return {"error": f"Failed to get container stats: {str(e)}"}
    
    def get_container_logs(self, container_id: str, lines: int = 100) -> Dict[str, Any]:
        """Get recent logs for a specific container."""
        if not self.container_runtime:
            return {"error": "No container runtime detected"}
            
        try:
            cmd = [self.container_runtime, 'logs', '--tail', str(lines), container_id]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return {"logs": result.stdout}
        except subprocess.SubprocessError as e:
            return {"error": f"Failed to get container logs: {str(e)}"}
    
    def get_container_info(self) -> Union[List[Dict[str, Any]], Dict[str, str]]:
        """Get detailed information about all containers."""
        if not self.container_runtime:
            return {"error": "No container runtime detected"}
            
        try:
            cmd = [self.container_runtime, 'ps', '-a', '--format', 'json']
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return json.loads(result.stdout)
        except (subprocess.SubprocessError, json.JSONDecodeError) as e:
            return {"error": f"Failed to get container info: {str(e)}"}
    
    def get_container_health(self) -> Dict[str, Any]:
        """Get comprehensive health status for all containers."""
        stats = self.get_container_stats()
        info = self.get_container_info()
        
        health_status: Dict[str, Any] = {
            "timestamp": datetime.now().isoformat(),
            "runtime": self.container_runtime,
            "containers": []
        }
        
        if isinstance(stats, dict) and "error" in stats or isinstance(info, dict) and "error" in info:
            health_status["error"] = "Failed to gather container health information"
            return health_status
            
        # Create a mapping of container IDs to their stats
        stats_map = {}
        if isinstance(stats, list):
            for stat in stats:
                if isinstance(stat, dict) and "ID" in stat:
                    stats_map[stat["ID"]] = stat
        
        if isinstance(info, list):
            for container in info:
                if not isinstance(container, dict):
                    continue
                    
                container_id = container.get("Id", "")
                names = container.get("Names", [])
                name = names[0] if names else "unknown"
                
                container_health = {
                    "id": container_id,
                    "name": name,
                    "status": container.get("Status", "unknown"),
                    "state": container.get("State", "unknown"),
                    "stats": stats_map.get(container_id, {}),
                    "logs": self.get_container_logs(container_id, lines=50)
                }
                health_status["containers"].append(container_health)
            
        return health_status 
