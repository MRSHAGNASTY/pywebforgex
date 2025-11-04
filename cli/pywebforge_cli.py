
#!/usr/bin/env python3
import sys, json, argparse, requests

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="http://localhost:7860")
    ap.add_argument("--api-key", required=True)
    ap.add_argument("--tenant", default="public")
    sub = ap.add_subparsers(dest="cmd")

    ex = sub.add_parser("exec")
    ex.add_argument("--module", required=True)
    ex.add_argument("--function", required=True)
    ex.add_argument("--args", default="[]")
    ex.add_argument("--kwargs", default="{}")
    ex.add_argument("--mode", default="live", choices=["live","dry-run","record","replay"])
    ex.add_argument("--target", default="repaired", choices=["repaired","mutated","original"])
    ex.add_argument("--with-ai", action="store_true")

    args = ap.parse_args()
    headers = {"X-API-Key": args.api_key, "X-Tenant": args.tenant}

    if args.cmd == "exec":
        payload = {
            "module": args.module, "function": args.function,
            "args": json.loads(args.args), "kwargs": json.loads(args.kwargs),
            "mode": args.mode, "target": args.target, "with_ai": args.with_ai
        }
        r = requests.post(args.base + "/api/execute", headers=headers, json=payload, timeout=30)
        print(json.dumps(r.json(), indent=2))
    else:
        ap.print_help()

if __name__ == "__main__":
    main()
