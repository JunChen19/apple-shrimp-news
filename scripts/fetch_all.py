#!/usr/bin/env python3
"""
手动触发全量抓取脚本
"""
import sys
import os

# 添加 backend 到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.main import run_fetch_task


def main():
    """主函数"""
    categories = sys.argv[1:] if len(sys.argv) > 1 else None

    if categories:
        print(f"开始抓取指定板块：{categories}")
    else:
        print("开始抓取所有板块...")

    run_fetch_task(categories)

    print("\n✅ 抓取完成！")
    print("查看结果：curl http://localhost:8000/api/articles")


if __name__ == "__main__":
    main()
