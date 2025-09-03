#!/usr/bin/env python3
"""
Resource Monitor for ULTRON Agent
Prevents system overload and VS Code crashes by monitoring resource usage
"""

import psutil
import time
import logging
import threading
from typing import Callable, Optional

class ResourceMonitor:
    """Monitor system resources and take action when limits are exceeded"""
    
    def __init__(self, 
                 cpu_limit: float = 80.0,
                 memory_limit: float = 85.0,
                 check_interval: float = 5.0):
        """
        Initialize resource monitor
        
        Args:
            cpu_limit: CPU usage percentage threshold (0-100)
            memory_limit: Memory usage percentage threshold (0-100) 
            check_interval: How often to check resources (seconds)
        """
        self.cpu_limit = cpu_limit
        self.memory_limit = memory_limit
        self.check_interval = check_interval
        
        self.logger = logging.getLogger(__name__)
        self._monitoring = False
        self._monitor_thread: Optional[threading.Thread] = None
        
        # Callbacks for resource limit exceeded
        self._cpu_callback: Optional[Callable] = None
        self._memory_callback: Optional[Callable] = None
        
        # Circuit breaker state
        self._overload_count = 0
        self._max_overload_count = 3
        self._circuit_open = False
        
    def set_cpu_callback(self, callback: Callable):
        """Set callback to call when CPU limit is exceeded"""
        self._cpu_callback = callback
        
    def set_memory_callback(self, callback: Callable):
        """Set callback to call when memory limit is exceeded"""
        self._memory_callback = callback
        
    def start_monitoring(self):
        """Start resource monitoring in background thread"""
        if self._monitoring:
            return
            
        self._monitoring = True
        self._monitor_thread = threading.Thread(
            target=self._monitor_loop, 
            daemon=True,
            name="ResourceMonitor"
        )
        self._monitor_thread.start()
        self.logger.info(f"Resource monitoring started - CPU limit: {self.cpu_limit}%, Memory limit: {self.memory_limit}%")
        
    def stop_monitoring(self):
        """Stop resource monitoring"""
        self._monitoring = False
        if self._monitor_thread and self._monitor_thread.is_alive():
            self._monitor_thread.join(timeout=1)
        self.logger.info("Resource monitoring stopped")
        
    def _monitor_loop(self):
        """Main monitoring loop"""
        while self._monitoring:
            try:
                # Get current resource usage
                cpu_percent = psutil.cpu_percent(interval=1)
                memory_percent = psutil.virtual_memory().percent
                
                # Check thresholds
                cpu_exceeded = cpu_percent > self.cpu_limit
                memory_exceeded = memory_percent > self.memory_limit
                
                if cpu_exceeded or memory_exceeded:
                    self._overload_count += 1
                    self.logger.warning(
                        f"Resource limits exceeded - CPU: {cpu_percent:.1f}% "
                        f"(limit: {self.cpu_limit}%), Memory: {memory_percent:.1f}% "
                        f"(limit: {self.memory_limit}%) - Count: {self._overload_count}"
                    )
                    
                    # Trigger callbacks
                    if cpu_exceeded and self._cpu_callback:
                        try:
                            self._cpu_callback(cpu_percent)
                        except Exception as e:
                            self.logger.error(f"CPU callback error: {e}")
                            
                    if memory_exceeded and self._memory_callback:
                        try:
                            self._memory_callback(memory_percent)
                        except Exception as e:
                            self.logger.error(f"Memory callback error: {e}")
                    
                    # Circuit breaker logic
                    if self._overload_count >= self._max_overload_count:
                        if not self._circuit_open:
                            self.logger.critical(
                                f"System overload detected! Opening circuit breaker. "
                                f"CPU: {cpu_percent:.1f}%, Memory: {memory_percent:.1f}%"
                            )
                            self._circuit_open = True
                            self._trigger_emergency_measures()
                else:
                    # Reset overload counter if resources are normal
                    if self._overload_count > 0:
                        self._overload_count = max(0, self._overload_count - 1)
                        
                    # Close circuit breaker if resources are healthy
                    if self._circuit_open and cpu_percent < (self.cpu_limit - 10) and memory_percent < (self.memory_limit - 10):
                        self.logger.info("Resources normalized - closing circuit breaker")
                        self._circuit_open = False
                        self._overload_count = 0
                        
            except Exception as e:
                self.logger.error(f"Resource monitoring error: {e}")
                
            time.sleep(self.check_interval)
    
    def _trigger_emergency_measures(self):
        """Trigger emergency measures to prevent system crash"""
        self.logger.critical("Triggering emergency resource conservation measures")
        
        try:
            # Kill high-resource processes if possible
            current_process = psutil.Process()
            
            # Reduce process priority
            if hasattr(psutil, 'BELOW_NORMAL_PRIORITY_CLASS'):
                current_process.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
            else:
                current_process.nice(10)  # Lower priority on Unix-like systems
                
            self.logger.info("Reduced process priority to conserve resources")
            
            # Force garbage collection
            import gc
            gc.collect()
            self.logger.info("Forced garbage collection")
            
        except Exception as e:
            self.logger.error(f"Emergency measures error: {e}")
            
    def is_circuit_open(self) -> bool:
        """Check if circuit breaker is open (system overloaded)"""
        return self._circuit_open
        
    def get_current_usage(self) -> dict:
        """Get current resource usage"""
        try:
            return {
                'cpu_percent': psutil.cpu_percent(),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_percent': psutil.disk_usage('/').percent if psutil.os.name != 'nt' else psutil.disk_usage('C:').percent,
                'process_count': len(psutil.pids())
            }
        except Exception as e:
            self.logger.error(f"Error getting resource usage: {e}")
            return {}

# Global instance
_resource_monitor = None

def get_resource_monitor() -> ResourceMonitor:
    """Get global resource monitor instance"""
    global _resource_monitor
    if _resource_monitor is None:
        _resource_monitor = ResourceMonitor()
    return _resource_monitor

def start_resource_monitoring():
    """Start global resource monitoring"""
    monitor = get_resource_monitor()
    
    # Set up callbacks to pause heavy operations
    def cpu_overload_callback(cpu_percent):
        logging.warning(f"CPU overload at {cpu_percent:.1f}% - pausing heavy operations")
        
    def memory_overload_callback(memory_percent):
        logging.warning(f"Memory overload at {memory_percent:.1f}% - freeing memory")
        import gc
        gc.collect()
        
    monitor.set_cpu_callback(cpu_overload_callback)
    monitor.set_memory_callback(memory_overload_callback)
    monitor.start_monitoring()

if __name__ == "__main__":
    # Test the resource monitor
    logging.basicConfig(level=logging.INFO)
    start_resource_monitoring()
    
    try:
        while True:
            monitor = get_resource_monitor()
            usage = monitor.get_current_usage()
            print(f"CPU: {usage.get('cpu_percent', 0):.1f}%, "
                  f"Memory: {usage.get('memory_percent', 0):.1f}%, "
                  f"Circuit Open: {monitor.is_circuit_open()}")
            time.sleep(5)
    except KeyboardInterrupt:
        print("Stopping resource monitor...")
        get_resource_monitor().stop_monitoring()