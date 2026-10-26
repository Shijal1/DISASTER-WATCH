"""DISASTERWATCH benchmark suite — measures real system performance for the paper."""
import asyncio
import time
import statistics
import json
from datetime import datetime

import httpx


BASE = "http://127.0.0.1:8000"


# ---------- 1. SOS TRIAGE CLASSIFICATION ----------
TEST_SET = [
    # (description, expected_severity)
    ("People trapped on roof, water rising fast, child bleeding", "CRITICAL"),
    ("Family stuck in basement, drowning", "CRITICAL"),
    ("Building collapsed, people buried under debris", "CRITICAL"),
    ("Person unconscious, not breathing, urgent", "CRITICAL"),
    ("House on fire, family trapped inside", "CRITICAL"),
    ("Elderly woman injured, severe bleeding", "CRITICAL"),

    ("We need food and water urgently", "MODERATE"),
    ("Family stranded, running low on supplies", "MODERATE"),
    ("No medicine available, sick child needs help", "MODERATE"),
    ("Shelter needed, house damaged but safe", "MODERATE"),
    ("Evacuation help required for elderly", "MODERATE"),
    ("Running out of drinking water", "MODERATE"),

    ("Minor flooding in street", "LOW"),
    ("Checking in, all fine here", "LOW"),
    ("Power outage in area", "LOW"),
    ("Road blocked by fallen tree", "LOW"),
]


async def test_sos_classification():
    print("\n=== 1. SOS CLASSIFICATION ===")
    correct = 0
    total = 0
    results = []

    async with httpx.AsyncClient(timeout=10.0) as client:
        for desc, expected in TEST_SET:
            r = await client.post(f"{BASE}/api/sos", json={
                "category": "flood",
                "affected_people": 1,
                "description": desc,
                "latitude": 28.61,
                "longitude": 77.20,
            })
            actual = r.json().get("severity", "UNKNOWN")
            hit = actual == expected
            correct += int(hit)
            total += 1
            results.append({
                "text": desc[:50],
                "expected": expected,
                "actual": actual,
                "match": hit,
            })
            status = "OK" if hit else "MISS"
            print(f"  [{status}] expected={expected:9} actual={actual:9} | {desc[:60]}")

    accuracy = correct / total if total else 0
    print(f"\n  Accuracy: {correct}/{total} = {accuracy:.1%}")

    # Confusion matrix
    labels = ["CRITICAL", "MODERATE", "LOW"]
    matrix = {e: {a: 0 for a in labels} for e in labels}
    for r in results:
        if r["expected"] in matrix and r["actual"] in matrix[r["expected"]]:
            matrix[r["expected"]][r["actual"]] += 1

    print("\n  Confusion matrix (expected -> actual):")
    print(f"  {'':12} {'CRIT':>6} {'MOD':>6} {'LOW':>6}")
    for e in labels:
        row = matrix[e]
        print(f"  {e:12} {row['CRITICAL']:>6} {row['MODERATE']:>6} {row['LOW']:>6}")

    return {
        "accuracy": accuracy,
        "correct": correct,
        "total": total,
        "results": results,
        "confusion": matrix,
    }


# ---------- 2. API LATENCY ----------
async def test_api_latency():
    print("\n=== 2. API LATENCY ===")

    endpoints = [
        ("GET", "/api/incidents"),
        ("GET", "/api/alerts"),
        ("GET", "/api/assets"),
        ("GET", "/api/health"),
        ("GET", "/api/satellite/status"),
    ]

    async with httpx.AsyncClient(timeout=15.0) as client:
        for method, path in endpoints:
            times = []
            for _ in range(20):
                t0 = time.perf_counter()
                r = await client.request(method, f"{BASE}{path}")
                dt = (time.perf_counter() - t0) * 1000  # ms
                if r.status_code == 200:
                    times.append(dt)

            if times:
                median = statistics.median(times)
                p95 = sorted(times)[int(len(times) * 0.95)]
                print(f"  {path:30} median={median:7.1f}ms  p95={p95:7.1f}ms  n={len(times)}")
            else:
                print(f"  {path:30} no successful responses")


# ---------- 3. WEBSOCKET LATENCY ----------
async def test_websocket_latency():
    print("\n=== 3. WEBSOCKET LATENCY ===")
    try:
        import websockets
        async with websockets.connect("ws://127.0.0.1:8000/ws/events") as ws:
            # Trigger an SOS submission, time the WS event delivery
            async with httpx.AsyncClient(timeout=10.0) as client:
                t0 = time.perf_counter()
                await client.post(f"{BASE}/api/sos", json={
                    "category": "flood",
                    "affected_people": 1,
                    "description": "WS latency test trapped bleeding",
                    "latitude": 28.61,
                    "longitude": 77.20,
                })

                msg = await asyncio.wait_for(ws.recv(), timeout=5.0)
                dt = (time.perf_counter() - t0) * 1000
                data = json.loads(msg)
                print(f"  Event type: {data.get('type')}")
                print(f"  Latency: {dt:.0f} ms")
    except Exception as e:
        print(f"  WS test skipped: {e}")


# ---------- 4. DATA INTEGRATION ----------
async def test_data_integration():
    print("\n=== 4. DATA INTEGRATION ===")
    async with httpx.AsyncClient(timeout=15.0) as client:
        r = await client.get(f"{BASE}/api/incidents?limit=2000")
        incidents = r.json()
        by_source = {}
        by_severity = {}
        by_type = {}
        for inc in incidents:
            by_source[inc["source"]] = by_source.get(inc["source"], 0) + 1
            by_severity[inc["severity"]] = by_severity.get(inc["severity"], 0) + 1
            by_type[inc["type"]] = by_type.get(inc["type"], 0) + 1

        print(f"  Total incidents: {len(incidents)}")
        print(f"\n  By source:")
        for k, v in sorted(by_source.items(), key=lambda x: -x[1]):
            print(f"    {k:15} {v}")
        print(f"\n  By severity:")
        for k, v in sorted(by_severity.items(), key=lambda x: -x[1]):
            print(f"    {k:15} {v}")
        print(f"\n  By type:")
        for k, v in sorted(by_type.items(), key=lambda x: -x[1]):
            print(f"    {k:15} {v}")

        return {
            "total": len(incidents),
            "by_source": by_source,
            "by_severity": by_severity,
            "by_type": by_type,
        }


# ---------- 5. FEED INGESTION (count only) ----------
async def test_feed_status():
    print("\n=== 5. FEED STATUS ===")
    async with httpx.AsyncClient(timeout=15.0) as client:
        r = await client.get(f"{BASE}/api/incidents?limit=2000")
        incidents = r.json()
        counts = {"usgs": 0, "eonet": 0, "gdacs": 0, "citizen": 0, "admin": 0}
        for inc in incidents:
            if inc["source"] in counts:
                counts[inc["source"]] += 1
        print(f"  Feed ingestion counts:")
        for k, v in counts.items():
            print(f"    {k:15} {v}")


# ---------- MAIN ----------
async def main():
    print("=" * 70)
    print(f"DISASTERWATCH BENCHMARK  |  {datetime.utcnow().isoformat()}")
    print("=" * 70)

    sos_results = await test_sos_classification()
    await test_api_latency()
    await test_websocket_latency()
    data_results = await test_data_integration()
    await test_feed_status()

    # Save report
    report = {
        "timestamp": datetime.utcnow().isoformat(),
        "sos_classification": sos_results,
        "data_integration": data_results,
    }
    with open("benchmark_report.json", "w") as f:
        json.dump(report, f, indent=2)
    print("\n" + "=" * 70)
    print("Report saved to benchmark_report.json")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())