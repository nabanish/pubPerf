#!/usr/bin/env python3
"""
Prometheus Client for AI Autoscaler V3
Queries Prometheus for comprehensive metrics
"""

import requests
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)


class PrometheusClient:
    """Client for querying Prometheus metrics"""
    
    def __init__(self, prometheus_url: str = "http://localhost:30090"):
        """
        Initialize Prometheus client
        
        Args:
            prometheus_url: URL of Prometheus server
        """
        self.prometheus_url = prometheus_url.rstrip('/')
        self.api_url = f"{self.prometheus_url}/api/v1"
        logger.info(f"Initialized Prometheus client: {self.prometheus_url}")
    
    def query(self, query: str) -> Optional[Dict[str, Any]]:
        """
        Execute instant query
        
        Args:
            query: PromQL query string
            
        Returns:
            Query result or None on error
        """
        try:
            response = requests.get(
                f"{self.api_url}/query",
                params={'query': query},
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            if data['status'] == 'success':
                return data['data']
            else:
                logger.error(f"Query failed: {data.get('error', 'Unknown error')}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to query Prometheus: {e}")
            return None
    
    def query_range(self, query: str, start: datetime, end: datetime, 
                    step: str = "15s") -> Optional[Dict[str, Any]]:
        """
        Execute range query
        
        Args:
            query: PromQL query string
            start: Start time
            end: End time
            step: Query resolution step
            
        Returns:
            Query result or None on error
        """
        try:
            response = requests.get(
                f"{self.api_url}/query_range",
                params={
                    'query': query,
                    'start': start.timestamp(),
                    'end': end.timestamp(),
                    'step': step
                },
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            
            if data['status'] == 'success':
                return data['data']
            else:
                logger.error(f"Range query failed: {data.get('error', 'Unknown error')}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to query Prometheus range: {e}")
            return None
    
    def get_pod_count(self, namespace: str = "default", 
                      app_label: str = "tomcat-sample-app") -> int:
        """
        Get current number of running pods
        
        Args:
            namespace: Kubernetes namespace
            app_label: Application label
            
        Returns:
            Number of running pods
        """
        query = f'count(kube_pod_info{{namespace="{namespace}", pod=~"{app_label}.*"}})'
        result = self.query(query)
        
        if result and result['result']:
            return int(float(result['result'][0]['value'][1]))
        return 0
    
    def get_cpu_usage(self, namespace: str = "default", 
                      app_label: str = "tomcat-sample-app") -> Dict[str, float]:
        """
        Get CPU usage metrics
        
        Args:
            namespace: Kubernetes namespace
            app_label: Application label
            
        Returns:
            Dict with total_cpu and cpu_per_pod in millicores
        """
        # Total CPU usage across all pods
        total_query = f'''
        sum(rate(container_cpu_usage_seconds_total{{
            namespace="{namespace}",
            pod=~"{app_label}.*"
        }}[1m])) * 1000
        '''
        
        # CPU per pod
        per_pod_query = f'''
        sum(rate(container_cpu_usage_seconds_total{{
            namespace="{namespace}",
            pod=~"{app_label}.*"
        }}[1m])) * 1000 /
        count(kube_pod_info{{namespace="{namespace}", pod=~"{app_label}.*"}})
        '''
        
        total_result = self.query(total_query)
        per_pod_result = self.query(per_pod_query)
        
        total_cpu = 0.0
        cpu_per_pod = 0.0
        
        if total_result and total_result['result']:
            total_cpu = float(total_result['result'][0]['value'][1])
        
        if per_pod_result and per_pod_result['result']:
            cpu_per_pod = float(per_pod_result['result'][0]['value'][1])
        
        return {
            'total_cpu': total_cpu,
            'cpu_per_pod': cpu_per_pod
        }
    
    def get_memory_usage(self, namespace: str = "default", 
                         app_label: str = "tomcat-sample-app") -> Dict[str, float]:
        """
        Get memory usage metrics
        
        Args:
            namespace: Kubernetes namespace
            app_label: Application label
            
        Returns:
            Dict with total_memory and memory_per_pod in bytes
        """
        # Total memory usage
        total_query = f'''
        sum(container_memory_working_set_bytes{{
            namespace="{namespace}",
            pod=~"{app_label}.*"
        }})
        '''
        
        # Memory per pod
        per_pod_query = f'''
        sum(container_memory_working_set_bytes{{
            namespace="{namespace}",
            pod=~"{app_label}.*"
        }}) /
        count(kube_pod_info{{namespace="{namespace}", pod=~"{app_label}.*"}})
        '''
        
        total_result = self.query(total_query)
        per_pod_result = self.query(per_pod_query)
        
        total_memory = 0.0
        memory_per_pod = 0.0
        
        if total_result and total_result['result']:
            total_memory = float(total_result['result'][0]['value'][1])
        
        if per_pod_result and per_pod_result['result']:
            memory_per_pod = float(per_pod_result['result'][0]['value'][1])
        
        return {
            'total_memory': total_memory,
            'memory_per_pod': memory_per_pod,
            'total_memory_mb': total_memory / (1024 * 1024),
            'memory_per_pod_mb': memory_per_pod / (1024 * 1024)
        }
    
    def get_network_io(self, namespace: str = "default",
                       app_label: str = "tomcat-sample-app") -> Dict[str, float]:
        """
        Get network I/O metrics (cluster-wide from cAdvisor)
        
        Args:
            namespace: Kubernetes namespace
            app_label: Application label
            
        Returns:
            Dict with network_in and network_out in bytes/sec
        """
        # Network receive rate (cluster-wide from cAdvisor)
        rx_query = '''
        sum(rate(container_network_receive_bytes_total{job="kubernetes-cadvisor"}[1m]))
        '''
        
        # Network transmit rate (cluster-wide from cAdvisor)
        tx_query = '''
        sum(rate(container_network_transmit_bytes_total{job="kubernetes-cadvisor"}[1m]))
        '''
        
        rx_result = self.query(rx_query)
        tx_result = self.query(tx_query)
        
        network_in = 0.0
        network_out = 0.0
        
        if rx_result and rx_result['result']:
            network_in = float(rx_result['result'][0]['value'][1])
        
        if tx_result and tx_result['result']:
            network_out = float(tx_result['result'][0]['value'][1])
        
        return {
            'network_in': network_in,
            'network_out': network_out,
            'network_in_mbps': (network_in * 8) / (1024 * 1024),
            'network_out_mbps': (network_out * 8) / (1024 * 1024)
        }
    
    def get_comprehensive_metrics(self, namespace: str = "default", 
                                   app_label: str = "tomcat-sample-app") -> Dict[str, Any]:
        """
        Get all metrics in one call
        
        Args:
            namespace: Kubernetes namespace
            app_label: Application label
            
        Returns:
            Dict with all metrics
        """
        pod_count = self.get_pod_count(namespace, app_label)
        cpu_metrics = self.get_cpu_usage(namespace, app_label)
        memory_metrics = self.get_memory_usage(namespace, app_label)
        network_metrics = self.get_network_io(namespace, app_label)
        
        return {
            'timestamp': datetime.now().isoformat(),
            'pod_count': pod_count,
            'cpu': cpu_metrics,
            'memory': memory_metrics,
            'network': network_metrics
        }
    
    def get_historical_cpu(self, namespace: str = "default", 
                           app_label: str = "tomcat-sample-app",
                           duration_minutes: int = 15) -> List[Dict[str, Any]]:
        """
        Get historical CPU usage data
        
        Args:
            namespace: Kubernetes namespace
            app_label: Application label
            duration_minutes: How far back to look
            
        Returns:
            List of timestamp and value pairs
        """
        end = datetime.now()
        start = end - timedelta(minutes=duration_minutes)
        
        query = f'''
        sum(rate(container_cpu_usage_seconds_total{{
            namespace="{namespace}",
            pod=~"{app_label}.*"
        }}[1m])) * 1000
        '''
        
        result = self.query_range(query, start, end)
        
        if result and result['result']:
            values = result['result'][0]['values']
            return [
                {
                    'timestamp': datetime.fromtimestamp(float(v[0])).isoformat(),
                    'value': float(v[1])
                }
                for v in values
            ]
        return []
    
    def health_check(self) -> bool:
        """
        Check if Prometheus is accessible
        
        Returns:
            True if healthy, False otherwise
        """
        try:
            response = requests.get(f"{self.prometheus_url}/-/healthy", timeout=5)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False


if __name__ == "__main__":
    # Test the Prometheus client
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    client = PrometheusClient()
    
    if client.health_check():
        print("✓ Prometheus is healthy")
        
        metrics = client.get_comprehensive_metrics()
        print(f"\nCurrent Metrics:")
        print(f"  Pods: {metrics['pod_count']}")
        print(f"  Total CPU: {metrics['cpu']['total_cpu']:.2f}m")
        print(f"  CPU per Pod: {metrics['cpu']['cpu_per_pod']:.2f}m")
        print(f"  Total Memory: {metrics['memory']['total_memory_mb']:.2f} MB")
        print(f"  Memory per Pod: {metrics['memory']['memory_per_pod_mb']:.2f} MB")
        print(f"  Network In: {metrics['network']['network_in_mbps']:.2f} Mbps")
        print(f"  Network Out: {metrics['network']['network_out_mbps']:.2f} Mbps")
    else:
        print("✗ Prometheus is not accessible")

# Made by Nabanish with Bob's assistance
