import json
import re
import sys
from pathlib import Path

from genlayer_py import create_account, create_client
from genlayer_py.chains import studionet
from genlayer_py.contracts import actions as contract_actions


def studio_calldata(method=None, args=None, kwargs=None):
    value = {}
    if method is not None:
        value["method"] = method
    if args:
        value["args"] = args
    if kwargs:
        value["kwargs"] = kwargs
    return value


contract_actions.make_calldata_object = studio_calldata
ROOT = Path(__file__).parents[1]
text = (ROOT.parents[3] / "accounts.env").read_text()
key = re.search(r'^ACCOUNT_7_GENLAYER_PRIVATE_KEY\s*=\s*"?([^"\r\n]+)', text, re.M).group(1).strip()
client = create_client(chain=studionet, account=create_account(account_private_key=key))
address = sys.argv[1]
recovery_id = "RB-LIVE-20261004B"
tx = client.write_contract(address=address, function_name="weave_plan", args=[recovery_id])
print("weave_plan_tx=" + str(tx), flush=True)
receipt = client.wait_for_transaction_receipt(
    transaction_hash=tx,
    wait_until="finalized",
    retries=180,
    interval=5000,
    full_transaction=True,
)
leader = (receipt.get("consensus_data", {}).get("leader_receipt") or [{}])[0]
result = {"tx": str(tx), "consensus": receipt.get("result_name"), "execution": leader.get("execution_result")}
print(json.dumps(result), flush=True)
if result["execution"] != "SUCCESS":
    raise RuntimeError("StudioNet transaction did not execute successfully")
print(json.dumps(client.read_contract(address=address, function_name="get_recovery", args=[recovery_id]), default=str), flush=True)
