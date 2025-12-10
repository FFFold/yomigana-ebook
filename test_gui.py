#!/usr/bin/env python
"""测试GUI组件"""

import sys
from PySide6.QtWidgets import QApplication
from yomigana_ebook.checking import check_unidic_dictionary, download_unidic_dictionary

def test_dictionary():
    """测试词典功能"""
    print("测试词典检测功能...")
    installed = check_unidic_dictionary()
    print(f"词典已安装: {installed}")
    
    if not installed:
        print("词典未安装，测试下载功能...")
        try:
            download_unidic_dictionary()
            print("词典下载成功！")
        except Exception as e:
            print(f"词典下载失败: {e}")
    else:
        print("词典检测正常")

def test_gui_import():
    """测试GUI导入"""
    print("\n测试GUI模块导入...")
    try:
        from gui import MainWindow, DictionaryManager, ConversionThread
        print("GUI模块导入成功！")
        return True
    except Exception as e:
        print(f"GUI模块导入失败: {e}")
        return False

def test_gui_creation():
    """测试GUI创建（不显示）"""
    print("\n测试GUI创建...")
    try:
        app = QApplication(sys.argv)
        from gui import MainWindow
        
        # 只创建不显示
        window = MainWindow()
        print("GUI窗口创建成功！")
        return True
    except Exception as e:
        print(f"GUI创建失败: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("Yomigana Ebook GUI 测试")
    print("=" * 50)
    
    test_dictionary()
    
    if test_gui_import():
        test_gui_creation()
    
    print("\n" + "=" * 50)
    print("测试完成")
    print("=" * 50)