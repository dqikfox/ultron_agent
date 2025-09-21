"""
NVIDIA GPU Operator Management Tool for ULTRON Agent
Provides comprehensive GPU management capabilities for Kubernetes clusters
"""

import json
import logging
import subprocess
from pathlib import Path
from typing import Dict, List, Any

from utils.ultron_logger import (
    log_info, log_error, log_ai_decision, log_file_operation
)
from utils.model_awareness import should_modify_file

logger = logging.getLogger(__name__)


class GPUOperatorTool:
    """NVIDIA GPU Operator management tool for ULTRON Agent"""

    name = "gpu_operator"
    description = "Manage NVIDIA GPU Operator in Kubernetes clusters"

    def __init__(self):
        """Initialize GPU Operator tool"""
        self.helm_repo = "nvidia"
        self.helm_repo_url = "https://helm.ngc.nvidia.com/nvidia"
        self.chart_name = "gpu-operator"
        self.namespace = "gpu-operator"
        self.version = "v25.3.3"

        # Load configuration
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load GPU Operator configuration"""
        try:
            config_path = Path("ultron_config.json")
            if config_path.exists():
                with open(config_path, 'r') as f:
                    config = json.load(f)
                    return config.get("gpu_operator", {})
        except Exception as e:
            logger.error(f"Failed to load GPU Operator config: {e}")

        # Default configuration
        return {
            "enabled": False,
            "namespace": "gpu-operator",
            "version": "v25.3.3",
            "driver_enabled": True,
            "toolkit_enabled": True,
            "dcgm_exporter_enabled": True,
            "mig_manager_enabled": True,
            "nfd_enabled": True
        }

    @staticmethod
    def schema():
        """Return tool schema for ULTRON Agent"""
        return {
            "name": "gpu_operator",
            "description": "Manage NVIDIA GPU Operator in Kubernetes clusters",
            "parameters": {
                "action": {
                    "type": "string",
                    "description": "Action to perform (install, uninstall, "
                                   "status, upgrade, configure)",
                    "enum": ["install", "uninstall", "status", "upgrade",
                             "configure", "deploy_workload", "monitor"]
                },
                "options": {
                    "type": "object",
                    "description": "Additional options for the action",
                    "properties": {
                        "namespace": {
                            "type": "string",
                            "description": "Kubernetes namespace"
                        },
                        "version": {
                            "type": "string",
                            "description": "GPU Operator version"
                        },
                        "driver_enabled": {
                            "type": "boolean",
                            "description": "Enable GPU driver deployment"
                        },
                        "toolkit_enabled": {
                            "type": "boolean",
                            "description": "Enable container toolkit"
                        },
                        "workload_type": {
                            "type": "string",
                            "description": "Type of GPU workload "
                                           "(cuda, tensorflow, pytorch)"
                        },
                        "gpu_count": {
                            "type": "integer",
                            "description": "Number of GPUs to allocate"
                        }
                    }
                }
            }
        }

    def match(self, command: str) -> bool:
        """Check if command matches GPU Operator operations"""
        gpu_keywords = [
            "gpu", "nvidia", "operator", "kubernetes", "k8s", "helm",
            "cuda", "driver", "toolkit", "dcgm", "mig", "workload"
        ]

        command_lower = command.lower()
        return any(keyword in command_lower for keyword in gpu_keywords) and (
            "install" in command_lower or
            "deploy" in command_lower or
            "manage" in command_lower or
            "monitor" in command_lower or
            "status" in command_lower
        )

    def execute(self, command: str, **kwargs) -> str:
        """Execute GPU Operator command"""
        try:
            log_info(
                "gpu_operator", f"Executing command: {command}"
            )

            # Parse command to determine action
            action = self._parse_action(command)

            if action == "install":
                return self._install_operator(kwargs.get("options", {}))
            elif action == "uninstall":
                return self._uninstall_operator()
            elif action == "status":
                return self._get_status()
            elif action == "upgrade":
                return self._upgrade_operator(kwargs.get("options", {}))
            elif action == "configure":
                return self._configure_operator(kwargs.get("options", {}))
            elif action == "deploy_workload":
                return self._deploy_gpu_workload(kwargs.get("options", {}))
            elif action == "monitor":
                return self._monitor_gpu_resources()
            else:
                return ("Unknown GPU Operator action. Available actions: "
                        "install, uninstall, status, upgrade, configure, "
                        "deploy_workload, monitor")

        except Exception as e:
            error_msg = f"GPU Operator command failed: {str(e)}"
            log_error("gpu_operator", error_msg)
            return error_msg

    def _parse_action(self, command: str) -> str:
        """Parse action from command string"""
        command_lower = command.lower()

        if "install" in command_lower:
            return "install"
        elif "uninstall" in command_lower or "remove" in command_lower:
            return "uninstall"
        elif "status" in command_lower or "check" in command_lower:
            return "status"
        elif "upgrade" in command_lower or "update" in command_lower:
            return "upgrade"
        elif "configure" in command_lower or "config" in command_lower:
            return "configure"
        elif "deploy" in command_lower or "workload" in command_lower:
            return "deploy_workload"
        elif "monitor" in command_lower:
            return "monitor"
        else:
            return "status"  # Default action

    def _install_operator(self, options: Dict[str, Any]) -> str:
        """Install NVIDIA GPU Operator using Helm"""
        try:
            log_info(
                "gpu_operator", "Installing NVIDIA GPU Operator"
            )

            # Check prerequisites
            if not self._check_prerequisites():
                return ("Prerequisites not met. Please ensure "
                        "kubectl and helm are installed.")

            # Add Helm repository
            cmd = ["helm", "repo", "add", self.helm_repo,
                   self.helm_repo_url]
            self._run_command(cmd)
            self._run_command(["helm", "repo", "update"])

            # Prepare Helm install command
            install_cmd = [
                "helm", "install", "--wait", "--generate-name",
                "-n", options.get("namespace", self.namespace),
                "--create-namespace",
                f"{self.helm_repo}/{self.chart_name}",
                f"--version={options.get('version', self.version)}"
            ]

            # Add configuration options
            if not options.get("driver_enabled", True):
                install_cmd.extend(["--set", "driver.enabled=false"])
            if not options.get("toolkit_enabled", True):
                install_cmd.extend(["--set", "toolkit.enabled=false"])
            if not options.get("dcgm_exporter_enabled", True):
                install_cmd.extend(["--set", "dcgmExporter.enabled=false"])
            if not options.get("mig_manager_enabled", True):
                install_cmd.extend(["--set", "migManager.enabled=false"])
            if not options.get("nfd_enabled", True):
                install_cmd.extend(["--set", "nfd.enabled=false"])

            # Execute installation
            result = self._run_command(install_cmd)

            if result.returncode == 0:
                log_info(
                    "gpu_operator", "GPU Operator installed successfully"
                )
                return ("NVIDIA GPU Operator installed successfully. "
                        "Use 'gpu status' to check deployment.")
            else:
                return f"Installation failed: {result.stderr}"

        except Exception as e:
            log_error(
                "gpu_operator", f"Installation failed: {str(e)}"
            )
            return f"Installation failed: {str(e)}"

    def _uninstall_operator(self) -> str:
        """Uninstall NVIDIA GPU Operator"""
        try:
            log_info(
                "gpu_operator", "Uninstalling NVIDIA GPU Operator"
            )

            # Get release name
            result = self._run_command(
                ["helm", "list", "-n", self.namespace, "-q"]
            )
            if result.returncode != 0:
                return "Failed to get Helm releases"

            releases = result.stdout.strip().split('\n')
            gpu_releases = [r for r in releases if "gpu-operator" in r]

            if not gpu_releases:
                return "No GPU Operator releases found"

            # Uninstall releases
            for release in gpu_releases:
                self._run_command(
                    ["helm", "uninstall", release, "-n", self.namespace]
                )

            # Remove namespace if empty
            cmd = ["kubectl", "delete", "namespace", self.namespace,
                   "--ignore-not-found=true"]
            self._run_command(cmd)

            log_info(
                "gpu_operator", "GPU Operator uninstalled successfully"
            )
            return "NVIDIA GPU Operator uninstalled successfully"

        except Exception as e:
            log_error(
                "gpu_operator", f"Uninstallation failed: {str(e)}"
            )
            return f"Uninstallation failed: {str(e)}"

    def _get_status(self) -> str:
        """Get GPU Operator status"""
        try:
            log_info(
                "gpu_operator", "Checking GPU Operator status"
            )

            status_info = []

            # Check Helm releases
            result = self._run_command(["helm", "list", "-n", self.namespace])
            if result.returncode == 0:
                status_info.append(f"Helm Releases:\n{result.stdout}")
            else:
                status_info.append("No Helm releases found")

            # Check pods
            result = self._run_command(
                ["kubectl", "get", "pods", "-n", self.namespace]
            )
            if result.returncode == 0:
                status_info.append(f"Pods:\n{result.stdout}")
            else:
                status_info.append("No pods found")

            # Check GPU nodes
            result = self._run_command([
                "kubectl", "get", "nodes",
                "-l", "feature.node.kubernetes.io/pci-10de.present=true",
                "-o", "wide"
            ])
            if result.returncode == 0:
                status_info.append(f"GPU Nodes:\n{result.stdout}")
            else:
                status_info.append("No GPU nodes found")

            return "\n\n".join(status_info)

        except Exception as e:
            log_error(
                "gpu_operator", f"Status check failed: {str(e)}"
            )
            return f"Status check failed: {str(e)}"

    def _upgrade_operator(self, options: Dict[str, Any]) -> str:
        """Upgrade NVIDIA GPU Operator"""
        try:
            log_info(
                "gpu_operator", "Upgrading NVIDIA GPU Operator"
            )

            # Get current release
            result = self._run_command(
                ["helm", "list", "-n", self.namespace, "-q"]
            )
            if result.returncode != 0:
                return "Failed to get current releases"

            releases = result.stdout.strip().split('\n')
            gpu_releases = [r for r in releases if "gpu-operator" in r]

            if not gpu_releases:
                return "No GPU Operator releases found to upgrade"

            release_name = gpu_releases[0]

            # Upgrade command
            upgrade_cmd = [
                "helm", "upgrade", release_name,
                f"{self.helm_repo}/{self.chart_name}",
                "--version", options.get("version", self.version),
                "-n", self.namespace
            ]

            result = self._run_command(upgrade_cmd)

            if result.returncode == 0:
                log_info(
                    "gpu_operator", "GPU Operator upgraded successfully"
                )
                return "NVIDIA GPU Operator upgraded successfully"
            else:
                return f"Upgrade failed: {result.stderr}"

        except Exception as e:
            log_error(
                "gpu_operator", f"Upgrade failed: {str(e)}"
            )
            return f"Upgrade failed: {str(e)}"

    def _configure_operator(self, options: Dict[str, Any]) -> str:
        """Configure GPU Operator settings"""
        try:
            log_info("gpu_operator", "Configuring GPU Operator")

            # Update configuration
            config_updates = {
                "namespace": options.get("namespace", self.namespace),
                "version": options.get("version", self.version),
                "driver_enabled": options.get("driver_enabled", True),
                "toolkit_enabled": options.get("toolkit_enabled", True),
                "dcgm_exporter_enabled": options.get(
                    "dcgm_exporter_enabled", True
                ),
                "mig_manager_enabled": options.get(
                    "mig_manager_enabled", True
                ),
                "nfd_enabled": options.get("nfd_enabled", True)
            }

            # Save to ultron_config.json
            self._update_ultron_config(config_updates)

            log_info(
                "gpu_operator", "GPU Operator configuration updated"
            )
            return "GPU Operator configuration updated successfully"

        except Exception as e:
            log_error(
                "gpu_operator", f"Configuration failed: {str(e)}"
            )
            return f"Configuration failed: {str(e)}"

    def _deploy_gpu_workload(self, options: Dict[str, Any]) -> str:
        """Deploy GPU workload"""
        try:
            log_info("gpu_operator", "Deploying GPU workload")

            workload_type = options.get("workload_type", "cuda")
            gpu_count = options.get("gpu_count", 1)

            if workload_type == "cuda":
                return self._deploy_cuda_workload(gpu_count)
            elif workload_type == "tensorflow":
                return self._deploy_tensorflow_workload(gpu_count)
            elif workload_type == "pytorch":
                return self._deploy_pytorch_workload(gpu_count)
            else:
                return f"Unsupported workload type: {workload_type}"

        except Exception as e:
            log_error(
                "gpu_operator", f"Workload deployment failed: {str(e)}"
            )
            return f"Workload deployment failed: {str(e)}"

    def _deploy_cuda_workload(self, gpu_count: int) -> str:
        """Deploy CUDA VectorAdd workload"""
        workload_yaml = f"""
apiVersion: v1
kind: Pod
metadata:
  name: cuda-vectoradd
  namespace: {self.namespace}
spec:
  restartPolicy: OnFailure
  containers:
  - name: cuda-vectoradd
    image: "nvcr.io/nvidia/k8s/cuda-sample:vectoradd-cuda11.7.1-ubuntu20.04"
    resources:
      limits:
        nvidia.com/gpu: {gpu_count}
"""

        # Save and apply
        with open("cuda-workload.yaml", "w") as f:
            f.write(workload_yaml)

        result = self._run_command(
            ["kubectl", "apply", "-f", "cuda-workload.yaml"]
        )

        if result.returncode == 0:
            log_info(
                "gpu_operator", "CUDA workload deployed successfully"
            )
            return "CUDA VectorAdd workload deployed successfully"
        else:
            return f"CUDA workload deployment failed: {result.stderr}"

    def _deploy_tensorflow_workload(self, gpu_count: int) -> str:
        """Deploy TensorFlow workload"""
        workload_yaml = f"""
apiVersion: v1
kind: Pod
metadata:
  name: tf-notebook
  namespace: {self.namespace}
spec:
  securityContext:
    fsGroup: 0
  containers:
  - name: tf-notebook
    image: tensorflow/tensorflow:latest-gpu-jupyter
    resources:
      limits:
        nvidia.com/gpu: {gpu_count}
    ports:
    - containerPort: 8888
      name: notebook
"""

        # Save and apply
        with open("tensorflow-workload.yaml", "w") as f:
            f.write(workload_yaml)

        result = self._run_command(
            ["kubectl", "apply", "-f", "tensorflow-workload.yaml"]
        )

        if result.returncode == 0:
            log_info(
                "gpu_operator", "TensorFlow workload deployed successfully"
            )
            return "TensorFlow workload deployed successfully"
        else:
            return f"TensorFlow workload deployment failed: {result.stderr}"

    def _deploy_pytorch_workload(self, gpu_count: int) -> str:
        """Deploy PyTorch workload"""
        workload_yaml = f"""
apiVersion: v1
kind: Pod
metadata:
  name: pytorch-workload
  namespace: {self.namespace}
spec:
  containers:
  - name: pytorch
    image: pytorch/pytorch:latest
    command: [
        "python", "-c",
        "import torch; print('PyTorch version:', torch.__version__); "
        "print('CUDA available:', torch.cuda.is_available())"
    ]
    resources:
      limits:
        nvidia.com/gpu: {gpu_count}
"""

        # Save and apply
        with open("pytorch-workload.yaml", "w") as f:
            f.write(workload_yaml)

        result = self._run_command(
            ["kubectl", "apply", "-f", "pytorch-workload.yaml"]
        )

        if result.returncode == 0:
            log_info(
                "gpu_operator", "PyTorch workload deployed successfully"
            )
            return "PyTorch workload deployed successfully"
        else:
            return f"PyTorch workload deployment failed: {result.stderr}"

    def _monitor_gpu_resources(self) -> str:
        """Monitor GPU resources"""
        try:
            log_info("gpu_operator", "Monitoring GPU resources")

            monitoring_info = []

            # Check GPU nodes
            result = self._run_command([
                "kubectl", "get", "nodes",
                "-l", "feature.node.kubernetes.io/pci-10de.present=true",
                "-o", "wide"
            ])
            monitoring_info.append(
                "GPU Nodes:\n" +
                (result.stdout if result.returncode == 0
                 else 'No GPU nodes found')
            )

            # Check GPU pods
            result = self._run_command([
                "kubectl", "get", "pods", "-A",
                "-o",
                "jsonpath='{range .items[*]}{.metadata.name}{\"\\t\"}"
                "{.spec.containers[*].resources.requests.nvidia\\.com/gpu}"
                "{\"\\n\"}{end}'"
            ])
            monitoring_info.append(
                "GPU Pod Resources:\n" +
                (result.stdout if result.returncode == 0
                 else 'No GPU pods found')
            )

            # Check DCGM metrics if available
            result = self._run_command([
                "kubectl", "get", "services", "-n", self.namespace,
                "-l", "app.kubernetes.io/name=dcgm-exporter"
            ])
            if result.returncode == 0 and result.stdout.strip():
                monitoring_info.append("DCGM Exporter is running")
            else:
                monitoring_info.append("DCGM Exporter not found")

            return "\n\n".join(monitoring_info)

        except Exception as e:
            log_error(
                "gpu_operator", f"GPU monitoring failed: {str(e)}"
            )
            return f"GPU monitoring failed: {str(e)}"

    def _check_prerequisites(self) -> bool:
        """Check if prerequisites are met"""
        try:
            # Check kubectl
            result = self._run_command(["kubectl", "version", "--client"])
            if result.returncode != 0:
                logger.error("kubectl not found")
                return False

            # Check helm
            result = self._run_command(["helm", "version"])
            if result.returncode != 0:
                logger.error("helm not found")
                return False

            # Check kubernetes connection
            result = self._run_command(["kubectl", "cluster-info"])
            if result.returncode != 0:
                logger.error("Kubernetes cluster not accessible")
                return False

            return True

        except Exception as e:
            logger.error(f"Prerequisite check failed: {e}")
            return False

    def _run_command(self, command: List[str]) -> subprocess.CompletedProcess:
        """Run shell command and return result"""
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            return result
        except subprocess.TimeoutExpired:
            logger.error(f"Command timed out: {' '.join(command)}")
            return subprocess.CompletedProcess(
                command, -1, "", "Command timed out"
            )
        except Exception as e:
            logger.error(f"Command execution failed: {e}")
            return subprocess.CompletedProcess(command, -1, "", str(e))

    def _update_ultron_config(self, updates: Dict[str, Any]) -> None:
        """Update ultron_config.json with GPU Operator settings"""
        try:
            config_path = Path("ultron_config.json")

            # Check if modification should proceed
            # context = check_file_context(str(config_path))
            should_proceed, reason, _ = should_modify_file(
                str(config_path), "update", "gpu_operator"
            )

            if not should_proceed:
                log_ai_decision(
                    "gpu_operator", f"Config update denied: {reason}",
                    ai_model="gpu_operator"
                )
                return

            # Load existing config
            config = {}
            if config_path.exists():
                with open(config_path, 'r') as f:
                    config = json.load(f)

            # Update GPU operator section
            if "gpu_operator" not in config:
                config["gpu_operator"] = {}

            config["gpu_operator"].update(updates)

            # Save updated config
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=2)

            log_file_operation(
                "gpu_operator", "Updated ultron_config.json with GPU settings",
                str(config_path), "update"
            )

        except Exception as e:
            log_error(
                "gpu_operator", f"Config update failed: {str(e)}"
            )
            raise Exception(f"Config update failed: {str(e)}")
