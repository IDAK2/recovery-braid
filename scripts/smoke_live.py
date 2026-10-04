import json
import re
import sys
from pathlib import Path

from genlayer_py import create_account, create_client
from genlayer_py.chains import studionet


ROOT = Path(__file__).parents[1]
text = (ROOT.parents[3] / "accounts.env").read_text()
key = re.search(r'^ACCOUNT_7_GENLAYER_PRIVATE_KEY\s*=\s*"?([^"\r\n]+)', text, re.M).group(1).strip()
client = create_client(chain=studionet, account=create_account(account_private_key=key))
address = sys.argv[1]
recovery_id = "RB-LIVE-20261004"
args = [
    recovery_id,
    "A production read replica emitted inconsistent checksums after a regional network partition.",
    [
        "Fence the inconsistent replica from serving traffic",
        "Verify a healthy replica against the last signed snapshot",
        "Promote the verified replica to primary",
        "Restore read traffic through the promoted replica",
    ],
    [[0, 1], [1, 2], [2, 3]],
    [
        "Never promote a replica before its snapshot checksum is verified",
        "Never restore read traffic before primary promotion is complete",
    ],
    4,
]
tx = client.write_contract(address=address, function_name="open_recovery", args=args)
print("open_recovery_tx=" + str(tx), flush=True)
receipt = client.wait_for_transaction_receipt(
    transaction_hash=tx,
    wait_until="finalized",
    retries=180,
    interval=5000,
    full_transaction=True,
)
leader = (receipt.get("consensus_data", {}).get("leader_receipt") or [{}])[0]
print(json.dumps({
    "tx": str(tx),
    "consensus": receipt.get("result_name"),
    "execution": leader.get("execution_result"),
}, default=str), flush=True)
print(json.dumps({
    "record": client.read_contract(address=address, function_name="get_recovery", args=[recovery_id]),
}, default=str), flush=True)
