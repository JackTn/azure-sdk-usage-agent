"""
扩展的别名配置 - 包含更多常见的用户表达方式
"""
from typing import Dict, List, Set


class EnhancedAliasMapper:
    """增强的别名映射器，包含更全面的别名支持"""
    
    def __init__(self):
        # 产品别名映射
        self.product_aliases = {
            # JavaScript 系列
            'js': ['JavaScript', 'JavaScript (Node.JS)', 'JavaScript RLC'],
            'javascript': ['JavaScript', 'JavaScript (Node.JS)', 'JavaScript RLC'],
            'node': ['JavaScript (Node.JS)'],
            'nodejs': ['JavaScript (Node.JS)'],
            'node.js': ['JavaScript (Node.JS)'],
            'rlc': ['JavaScript RLC'],
            'rest': ['JavaScript RLC'],  # RLC 通常是 REST Level Client
            
            # .NET 系列
            '.net': ['.Net Code-gen', '.Net Fluent'],
            'dotnet': ['.Net Code-gen', '.Net Fluent'],
            'csharp': ['.Net Code-gen', '.Net Fluent'],
            'c#': ['.Net Code-gen', '.Net Fluent'],
            'net': ['.Net Code-gen', '.Net Fluent'],
            'cs': ['.Net Code-gen', '.Net Fluent'],
            
            # Java 系列
            'java': ['Java Fluent Lite', 'Java Fluent Premium'],
            'jdk': ['Java Fluent Lite', 'Java Fluent Premium'],
            
            # Python 系列
            'python': ['Python-SDK'],
            'py': ['Python-SDK'],
            'python3': ['Python-SDK'],
            'pip': ['Python-SDK'],
            
            # Go 系列
            'go': ['Go-SDK'],
            'golang': ['Go-SDK'],
            'gopher': ['Go-SDK'],
            
            # 其他语言
            'php': ['PHP-SDK'],
            'ruby': ['Ruby-SDK'],
            'rb': ['Ruby-SDK'],
            'rust': ['Rust'],
            'rs': ['Rust'],
            'rustlang': ['Rust'],
            
            # CLI 工具
            'cli': ['AzureCLI'],
            'azure-cli': ['AzureCLI'],
            'az': ['AzureCLI'],
            'command-line': ['AzureCLI'],
            'powershell': ['AzurePowershell'],
            'ps': ['AzurePowershell'],
            'pwsh': ['AzurePowershell'],
            'ps1': ['AzurePowershell'],
            
            # 基础设施即代码
            'terraform': ['Terraform'],
            'tf': ['Terraform'],
            'hcl': ['Terraform'],
            'ansible': ['Ansible'],
            'playbook': ['Ansible'],
            
            # IDE 和编辑器
            'vscode': ['VS Code Azure Extension'],
            'vs-code': ['VS Code Azure Extension'],
            'visual-studio-code': ['VS Code Azure Extension'],
            'code': ['VS Code Azure Extension'],
        }
        
        # OS 别名映射
        self.os_aliases = {
            # Windows
            'windows': ['Windows'],
            'win': ['Windows'],
            'microsoft': ['Windows'],
            'ms': ['Windows'],
            'win10': ['Windows'],
            'win11': ['Windows'],
            
            # Linux
            'linux': ['Linux'],
            'ubuntu': ['Linux'],
            'debian': ['Linux'],
            'centos': ['Linux'],
            'rhel': ['Linux'],
            'redhat': ['Linux'],
            'fedora': ['Linux'],
            'suse': ['Linux'],
            'unix': ['Linux'],
            
            # macOS
            'macos': ['macOS'],
            'mac': ['macOS'],
            'osx': ['macOS'],
            'apple': ['macOS'],
            'darwin': ['macOS'],
        }
        
        # HTTP 方法别名
        self.http_method_aliases = {
            # GET
            'get': ['GET'],
            'read': ['GET'],
            'fetch': ['GET'],
            'retrieve': ['GET'],
            'query': ['GET'],
            
            # POST
            'post': ['POST'],
            'create': ['POST'],
            'add': ['POST'],
            'insert': ['POST'],
            'new': ['POST'],
            
            # PUT
            'put': ['PUT'],
            'update': ['PUT'],
            'modify': ['PUT'],
            'change': ['PUT'],
            'edit': ['PUT'],
            
            # DELETE
            'delete': ['DELETE'],
            'remove': ['DELETE'],
            'del': ['DELETE'],
            'destroy': ['DELETE'],
            
            # PATCH
            'patch': ['PATCH'],
            'partial': ['PATCH'],
        }
        
        # 提供者服务别名
        self.provider_aliases = {
            # Compute
            'compute': ['Microsoft.Compute'],
            'vm': ['Microsoft.Compute'],
            'virtual-machine': ['Microsoft.Compute'],
            'server': ['Microsoft.Compute'],
            
            # Storage
            'storage': ['Microsoft.Storage'],
            'blob': ['Microsoft.Storage'],
            'file': ['Microsoft.Storage'],
            'disk': ['Microsoft.Storage'],
            
            # Network
            'network': ['Microsoft.Network'],
            'networking': ['Microsoft.Network'],
            'vnet': ['Microsoft.Network'],
            'subnet': ['Microsoft.Network'],
            'nsg': ['Microsoft.Network'],
            
            # Web
            'web': ['Microsoft.Web'],
            'webapp': ['Microsoft.Web'],
            'app-service': ['Microsoft.Web'],
            'website': ['Microsoft.Web'],
            
            # Database
            'sql': ['Microsoft.Sql'],
            'database': ['Microsoft.Sql'],
            'db': ['Microsoft.Sql'],
            'mysql': ['Microsoft.DBforMySQL'],
            'postgresql': ['Microsoft.DBforPostgreSQL'],
            'cosmos': ['Microsoft.DocumentDB'],
            'cosmosdb': ['Microsoft.DocumentDB'],
            
            # Container
            'container': ['Microsoft.ContainerService'],
            'aks': ['Microsoft.ContainerService'],
            'kubernetes': ['Microsoft.ContainerService'],
            'k8s': ['Microsoft.ContainerService'],
            
            # KeyVault
            'keyvault': ['Microsoft.KeyVault'],
            'vault': ['Microsoft.KeyVault'],
            'secret': ['Microsoft.KeyVault'],
            'certificate': ['Microsoft.KeyVault'],
        }
        
        # 资源类型别名
        self.resource_aliases = {
            # Virtual Machines
            'vm': ['virtualMachines'],
            'virtual-machine': ['virtualMachines'],
            'server': ['virtualMachines'],
            'instance': ['virtualMachines'],
            
            # Storage
            'storage-account': ['storageAccounts'],
            'blob': ['storageAccounts'],
            'storage': ['storageAccounts'],
            
            # Network
            'vnet': ['virtualNetworks'],
            'virtual-network': ['virtualNetworks'],
            'network': ['virtualNetworks'],
            'subnet': ['subnets'],
            'nsg': ['networkSecurityGroups'],
            'security-group': ['networkSecurityGroups'],
            
            # Web Apps
            'webapp': ['webApps'],
            'web-app': ['webApps'],
            'app-service': ['webApps'],
            'website': ['webApps'],
            
            # Databases
            'sql-server': ['sqlServers'],
            'database': ['databases'],
            'db': ['databases'],
            
            # Containers
            'aks': ['kubernetesClusters'],
            'kubernetes': ['kubernetesClusters'],
            'k8s': ['kubernetesClusters'],
            'cluster': ['kubernetesClusters'],
            
            # Key Vault
            'keyvault': ['keyVaults'],
            'vault': ['keyVaults'],
        }
        
        # 时间表达式别名
        self.time_aliases = {
            'today': '2025-08-28',
            'this-month': '2025-08',
            'current-month': '2025-08',
            'last-month': '2025-07',
            'previous-month': '2025-07',
            'this-year': '2025',
            'current-year': '2025',
            'last-year': '2024',
            'previous-year': '2024',
            'recent': 'ORDER BY Month DESC',
            'latest': 'ORDER BY Month DESC',
            'newest': 'ORDER BY Month DESC',
            'oldest': 'ORDER BY Month ASC',
            'earliest': 'ORDER BY Month ASC',
        }
        
        # 数量表达式别名
        self.quantity_aliases = {
            'top': 'TOP',
            'first': 'TOP',
            'limit': 'TOP',
            'most': 'ORDER BY [count_column] DESC',
            'highest': 'ORDER BY [count_column] DESC',
            'maximum': 'ORDER BY [count_column] DESC',
            'least': 'ORDER BY [count_column] ASC',
            'lowest': 'ORDER BY [count_column] ASC',
            'minimum': 'ORDER BY [count_column] ASC',
            'total': 'SUM([count_column])',
            'sum': 'SUM([count_column])',
            'count': 'COUNT(*)',
            'number': 'COUNT(*)',
            'average': 'AVG([count_column])',
            'avg': 'AVG([count_column])',
        }
    
    def get_all_aliases(self) -> Dict[str, Dict]:
        """获取所有别名映射"""
        return {
            'products': self.product_aliases,
            'os': self.os_aliases,
            'http_methods': self.http_method_aliases,
            'providers': self.provider_aliases,
            'resources': self.resource_aliases,
            'time_expressions': self.time_aliases,
            'quantity_expressions': self.quantity_aliases
        }
    
    def find_matches(self, text: str, category: str) -> List[str]:
        """在指定类别中查找匹配的别名"""
        text_lower = text.lower()
        matches = []
        
        alias_map = getattr(self, f'{category}_aliases', {})
        
        for alias, targets in alias_map.items():
            if alias in text_lower:
                matches.extend(targets)
        
        return list(set(matches))  # 去重
