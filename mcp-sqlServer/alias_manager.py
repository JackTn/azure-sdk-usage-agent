#!/usr/bin/env python3
"""
别名管理工具 - 用于管理和扩展别名配置
"""
import json
import sys
from pathlib import Path
from typing import Dict, List, Any

# 添加src目录到路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from product_aliases import UniversalAliasMapper


class AliasManager:
    """别名管理器 - 提供别名配置的管理功能"""
    
    def __init__(self, config_path: str = None):
        if config_path is None:
            config_path = Path(__file__).parent / "fixture" / "aliases.json"
        
        self.mapper = UniversalAliasMapper(config_path)
        self.config_path = Path(config_path)
    
    def show_stats(self):
        """显示别名配置统计信息"""
        print("📊 别名配置统计")
        print("=" * 50)
        
        all_aliases = self.mapper.get_all_aliases()
        metadata = self.mapper.get_metadata()
        
        print(f"🏷️  配置版本: {metadata.get('version', '未知')}")
        print(f"📅 最后更新: {metadata.get('last_updated', '未知')}")
        print(f"🌐 支持语言: {', '.join(metadata.get('supported_languages', []))}")
        print()
        
        for category, aliases in all_aliases.items():
            print(f"📂 {category}: {len(aliases)} 个别名")
        
        print()
        total_aliases = sum(len(aliases) for aliases in all_aliases.values())
        print(f"📋 总计: {total_aliases} 个别名")
    
    def show_category(self, category: str):
        """显示特定类别的别名"""
        aliases = self.mapper.get_aliases_for_category(category)
        
        if not aliases:
            print(f"❌ 未找到类别: {category}")
            return
        
        print(f"📂 {category} 别名列表")
        print("=" * 50)
        
        for alias, targets in aliases.items():
            if isinstance(targets, list):
                targets_str = ", ".join(targets)
            else:
                targets_str = str(targets)
            
            print(f"🔗 {alias} → {targets_str}")
    
    def test_query(self, query: str, category: str = None):
        """测试查询匹配"""
        print(f"🔍 测试查询: '{query}'")
        print("=" * 50)
        
        if category:
            matches = self.mapper.find_matches_by_category(query, category)
            print(f"📂 {category} 匹配结果: {matches}")
        else:
            # 测试所有类别
            categories = ['product_aliases', 'os_aliases', 'http_method_aliases', 'provider_aliases']
            for cat in categories:
                matches = self.mapper.find_matches_by_category(query, cat)
                if matches:
                    print(f"📂 {cat}: {matches}")
    
    def add_alias(self, category: str, alias: str, targets: List[str], save: bool = True):
        """添加新的别名"""
        print(f"➕ 添加别名: {alias} → {targets} (类别: {category})")
        
        try:
            self.mapper.add_alias(category, alias, targets, save_to_file=save)
            print("✅ 别名添加成功")
            
            if save:
                print(f"💾 已保存到: {self.config_path}")
        except Exception as e:
            print(f"❌ 添加失败: {e}")
    
    def validate_config(self):
        """验证配置文件的完整性"""
        print("🔍 验证别名配置")
        print("=" * 50)
        
        issues = []
        all_aliases = self.mapper.get_all_aliases()
        
        # 检查空的别名映射
        for category, aliases in all_aliases.items():
            if not aliases:
                issues.append(f"类别 '{category}' 为空")
            
            for alias, targets in aliases.items():
                if not targets:
                    issues.append(f"别名 '{alias}' 在类别 '{category}' 中没有目标")
                elif isinstance(targets, list) and len(targets) == 0:
                    issues.append(f"别名 '{alias}' 在类别 '{category}' 中目标列表为空")
        
        # 检查元数据
        metadata = self.mapper.get_metadata()
        required_metadata = ['version', 'last_updated', 'description']
        for field in required_metadata:
            if field not in metadata:
                issues.append(f"元数据缺少字段: {field}")
        
        if issues:
            print("⚠️ 发现问题:")
            for issue in issues:
                print(f"  - {issue}")
        else:
            print("✅ 配置验证通过")
    
    def export_aliases(self, output_path: str, category: str = None):
        """导出别名配置"""
        try:
            if category:
                data = {category: self.mapper.get_aliases_for_category(category)}
            else:
                data = self.mapper.get_all_aliases()
                data['_metadata'] = self.mapper.get_metadata()
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            print(f"✅ 已导出到: {output_path}")
        except Exception as e:
            print(f"❌ 导出失败: {e}")


def main():
    """主函数 - 命令行接口"""
    import argparse
    
    parser = argparse.ArgumentParser(description="别名配置管理工具")
    parser.add_argument("--config", help="别名配置文件路径")
    
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # 统计信息
    subparsers.add_parser("stats", help="显示别名统计信息")
    
    # 显示类别
    show_parser = subparsers.add_parser("show", help="显示特定类别的别名")
    show_parser.add_argument("category", help="类别名称")
    
    # 测试查询
    test_parser = subparsers.add_parser("test", help="测试查询匹配")
    test_parser.add_argument("query", help="查询文本")
    test_parser.add_argument("--category", help="指定类别")
    
    # 添加别名
    add_parser = subparsers.add_parser("add", help="添加新的别名")
    add_parser.add_argument("category", help="类别名称")
    add_parser.add_argument("alias", help="别名")
    add_parser.add_argument("targets", nargs="+", help="目标值列表")
    add_parser.add_argument("--no-save", action="store_true", help="不保存到文件")
    
    # 验证配置
    subparsers.add_parser("validate", help="验证配置文件")
    
    # 导出配置
    export_parser = subparsers.add_parser("export", help="导出别名配置")
    export_parser.add_argument("output", help="输出文件路径")
    export_parser.add_argument("--category", help="只导出指定类别")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # 创建管理器
    manager = AliasManager(args.config)
    
    # 执行命令
    if args.command == "stats":
        manager.show_stats()
    elif args.command == "show":
        manager.show_category(args.category)
    elif args.command == "test":
        manager.test_query(args.query, args.category)
    elif args.command == "add":
        manager.add_alias(args.category, args.alias, args.targets, not args.no_save)
    elif args.command == "validate":
        manager.validate_config()
    elif args.command == "export":
        manager.export_aliases(args.output, args.category)


if __name__ == "__main__":
    main()
