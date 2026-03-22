#!/usr/bin/env python3
"""
A股自选股智能分析系统 CLI
连接 http://192.168.1.49:8000
"""

import json
import sys
import argparse
import subprocess
from pathlib import Path

BASE_URL = "http://192.168.1.49:8000"


def curl_api(endpoint, method="GET", data=None, params=None):
    """调用 API"""
    url = f"{BASE_URL}{endpoint}"
    cmd = ["curl", "-s"]

    if method.upper() in ["POST", "PUT", "PATCH"]:
        cmd.extend(["-X", method])

    if data:
        cmd.extend(["-H", "Content-Type: application/json"])
        cmd.extend(["-d", json.dumps(data)])

    if params:
        param_str = "&".join([f"{k}={v}" for k, v in params.items()])
        url = f"{url}?{param_str}"

    cmd.append(url)

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            return json.loads(result.stdout) if result.stdout else None
        else:
            return {"error": result.stderr}
    except subprocess.TimeoutExpired:
        return {"error": "Request timeout"}
    except Exception as e:
        return {"error": str(e)}


def cmd_quote(args):
    """查询股票行情"""
    if not args.code:
        print("Error: 股票代码不能为空")
        return

    result = curl_api(f"/api/v1/stocks/{args.code}/quote")
    print(json.dumps(result, ensure_ascii=False, indent=2))


def cmd_history(args):
    """查询历史行情"""
    if not args.code:
        print("Error: 股票代码不能为空")
        return

    params = {}
    if args.period:
        params["period"] = args.period
    if args.start:
        params["start"] = args.start
    if args.end:
        params["end"] = args.end

    result = curl_api(f"/api/v1/stocks/{args.code}/history", params=params)
    print(json.dumps(result, ensure_ascii=False, indent=2))


def cmd_analyze(args):
    """触发股票分析"""
    data = {}
    if args.code:
        data["stock_code"] = args.code
    if args.text:
        data["text"] = args.text

    result = curl_api("/api/v1/analysis/analyze", method="POST", data=data)
    print(json.dumps(result, ensure_ascii=False, indent=2))


def cmd_tasks(args):
    """查询分析任务"""
    result = curl_api("/api/v1/analysis/tasks")
    print(json.dumps(result, ensure_ascii=False, indent=2))


def cmd_task_status(args):
    """查询任务状态"""
    if not args.task_id:
        print("Error: 任务ID不能为空")
        return

    result = curl_api(f"/api/v1/analysis/status/{args.task_id}")
    print(json.dumps(result, ensure_ascii=False, indent=2))


def cmd_history_list(args):
    """查询分析历史"""
    params = {}
    if args.limit:
        params["limit"] = args.limit

    result = curl_api("/api/v1/history", params=params)
    print(json.dumps(result, ensure_ascii=False, indent=2))


def cmd_history_detail(args):
    """查询历史详情"""
    if not args.record_id:
        print("Error: 记录ID不能为空")
        return

    result = curl_api(f"/api/v1/history/{args.record_id}")
    print(json.dumps(result, ensure_ascii=False, indent=2))


def cmd_history_markdown(args):
    """导出历史为 Markdown"""
    if not args.record_id:
        print("Error: 记录ID不能为空")
        return

    result = curl_api(f"/api/v1/history/{args.record_id}/markdown")
    if result and "markdown" in result:
        print(result["markdown"])
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))


def cmd_portfolio_accounts(args):
    """查询组合账户"""
    result = curl_api("/api/v1/portfolio/accounts")
    print(json.dumps(result, ensure_ascii=False, indent=2))


def cmd_portfolio_trades(args):
    """查询交易记录"""
    params = {}
    if args.account_id:
        params["account_id"] = args.account_id
    if args.limit:
        params["limit"] = args.limit

    result = curl_api("/api/v1/portfolio/trades", params=params)
    print(json.dumps(result, ensure_ascii=False, indent=2))


def cmd_portfolio_risk(args):
    """查询风险分析"""
    result = curl_api("/api/v1/portfolio/risk")
    print(json.dumps(result, ensure_ascii=False, indent=2))


def cmd_health(args):
    """健康检查"""
    result = curl_api("/api/health")
    print(json.dumps(result, ensure_ascii=False, indent=2))


def main():
    parser = argparse.ArgumentParser(
        description="A股自选股智能分析系统 CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # quote - 查询行情
    quote_parser = subparsers.add_parser("quote", help="查询股票行情")
    quote_parser.add_argument("code", help="股票代码，如 000001.SZ")
    quote_parser.set_defaults(func=cmd_quote)

    # history - 查询历史
    history_parser = subparsers.add_parser("history", help="查询历史行情")
    history_parser.add_argument("code", help="股票代码")
    history_parser.add_argument("--period", help="周期: 1d/1w/1m")
    history_parser.add_argument("--start", help="开始日期")
    history_parser.add_argument("--end", help="结束日期")
    history_parser.set_defaults(func=cmd_history)

    # analyze - 触发分析
    analyze_parser = subparsers.add_parser("analyze", help="触发AI分析")
    analyze_parser.add_argument("--code", help="股票代码")
    analyze_parser.add_argument("--text", help="分析文本")
    analyze_parser.set_defaults(func=cmd_analyze)

    # tasks - 分析任务
    tasks_parser = subparsers.add_parser("tasks", help="查询分析任务")
    tasks_parser.set_defaults(func=cmd_tasks)

    # task-status - 任务状态
    status_parser = subparsers.add_parser("task-status", help="查询任务状态")
    status_parser.add_argument("task_id", help="任务ID")
    status_parser.set_defaults(func=cmd_task_status)

    # history-list - 分析历史
    hlist_parser = subparsers.add_parser("history-list", help="查询分析历史")
    hlist_parser.add_argument("--limit", type=int, help="限制数量")
    hlist_parser.set_defaults(func=cmd_history_list)

    # history-detail - 历史详情
    hdetail_parser = subparsers.add_parser("history-detail", help="查询历史详情")
    hdetail_parser.add_argument("record_id", help="记录ID")
    hdetail_parser.set_defaults(func=cmd_history_detail)

    # history-markdown - 导出Markdown
    md_parser = subparsers.add_parser("markdown", help="导出为Markdown")
    md_parser.add_argument("record_id", help="记录ID")
    md_parser.set_defaults(func=cmd_history_markdown)

    # portfolio - 组合管理
    portfolio_parser = subparsers.add_parser("portfolio", help="组合管理")
    portfolio_subs = portfolio_parser.add_subparsers(dest="subcommand")

    # portfolio accounts
    accounts_parser = portfolio_subs.add_parser("accounts", help="查询账户")
    accounts_parser.set_defaults(func=cmd_portfolio_accounts)

    # portfolio trades
    trades_parser = portfolio_subs.add_parser("trades", help="查询交易")
    trades_parser.add_argument("--account-id", help="账户ID")
    trades_parser.add_argument("--limit", type=int, help="限制数量")
    trades_parser.set_defaults(func=cmd_portfolio_trades)

    # portfolio risk
    risk_parser = portfolio_subs.add_parser("risk", help="风险分析")
    risk_parser.set_defaults(func=cmd_portfolio_risk)

    # health - 健康检查
    health_parser = subparsers.add_parser("health", help="健康检查")
    health_parser.set_defaults(func=cmd_health)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    args.func(args)


if __name__ == "__main__":
    main()
