from conftest import CONTRACT
ACTIONS=['Isolate the damaged storage replica','Verify the healthy replica checksum','Promote the verified replica','Reopen read traffic']
DEPS=[[0,1],[1,2],[2,3]]
RULES=['Never promote a replica before its checksum is verified','Do not reopen traffic before promotion completes']
def setup(vm,deploy,a):
 vm.sender=a;c=deploy(CONTRACT);c.open_recovery('store-9','Primary storage returned corrupted blocks after a failed regional restart.',ACTIONS,DEPS,RULES,4);return c
def plan_mocks(vm,batches='[[0],[1],[2],[3]]',valid=True):
 vm.mock_llm(r'.*RecoveryBraid planner.*','{"batches":'+batches+'}');vm.mock_llm(r'.*RecoveryBraid verifier.*','{"valid":'+str(valid).lower()+'}')
def receipt_mocks(vm,complete=True,valid=True):
 vm.mock_web(r'evidence\.example',{'status':200,'body':'Operator log: damaged replica isolated; command succeeded; timestamp and host included.'});vm.mock_llm(r'.*RecoveryBraid receipt examiner.*','{"complete":'+str(complete).lower()+'}');vm.mock_llm(r'.*RecoveryBraid receipt verifier.*','{"valid":'+str(valid).lower()+'}')
def test_dependency_safe_plan(direct_vm,direct_deploy,direct_alice):
 c=setup(direct_vm,direct_deploy,direct_alice);plan_mocks(direct_vm);c.weave_plan('store-9');r=c.get_recovery('store-9');assert r['state']=='EXECUTING' and r['batches']==[[0],[1],[2],[3]]
def test_missing_duplicate_and_forward_dependency_rejected(direct_vm,direct_deploy,direct_alice):
 c=setup(direct_vm,direct_deploy,direct_alice);r=c.recoveries['STORE-9']
 for value in ({'batches':[[0],[1],[2]]},{'batches':[[0],[1,1],[2],[3]]},{'batches':[[1],[0],[2],[3]]}):
  rejected=False
  try:c._shape(value,r)
  except Exception:rejected=True
  assert rejected
def test_validator_rejects_semantically_unsafe_batch(direct_vm,direct_deploy,direct_alice):
 c=setup(direct_vm,direct_deploy,direct_alice);plan_mocks(direct_vm);r=c._plan(c.recoveries['STORE-9']);assert direct_vm.run_validator(leader_result=r) is True
 direct_vm.clear_mocks();plan_mocks(direct_vm,valid=False);assert direct_vm.run_validator(leader_result=r) is False
def test_permissionless_receipt_advances_exact_batch(direct_vm,direct_deploy,direct_alice,direct_bob):
 c=setup(direct_vm,direct_deploy,direct_alice);plan_mocks(direct_vm);c.weave_plan('store-9');direct_vm.sender=direct_bob;receipt_mocks(direct_vm);c.prove_next_batch('store-9','https://evidence.example/batch-0');r=c.get_recovery('store-9');assert r['next_batch']==1 and len(r['receipt_digests'])==1 and r['state']=='EXECUTING'
def test_incomplete_or_forged_receipt_rejected(direct_vm,direct_deploy,direct_alice):
 c=setup(direct_vm,direct_deploy,direct_alice);plan_mocks(direct_vm);c.weave_plan('store-9');receipt_mocks(direct_vm,False,True)
 with direct_vm.expect_revert('complete safe batch'):c.prove_next_batch('store-9','https://evidence.example/batch-0')
 direct_vm.clear_mocks();receipt_mocks(direct_vm,True,False);r=c._verify_batch(c.recoveries['STORE-9'],0,'https://evidence.example/batch-0');assert direct_vm.run_validator(leader_result=r) is False
def test_full_lifecycle_and_replay_guard(direct_vm,direct_deploy,direct_alice):
 c=setup(direct_vm,direct_deploy,direct_alice);plan_mocks(direct_vm);c.weave_plan('store-9')
 for i in range(4):receipt_mocks(direct_vm);c.prove_next_batch('store-9','https://evidence.example/batch-'+str(i))
 assert c.get_recovery('store-9')['state']=='RECOVERED'
 with direct_vm.expect_revert('executable next batch'):c.prove_next_batch('store-9','https://evidence.example/replay')
def test_owner_only_open_cancel_and_duplicate_id(direct_vm,direct_deploy,direct_alice,direct_bob):
 c=setup(direct_vm,direct_deploy,direct_alice);direct_vm.sender=direct_bob
 with direct_vm.expect_revert('owner may cancel'):c.cancel_open('store-9')
 direct_vm.sender=direct_alice;c.cancel_open('store-9');assert c.get_recovery('store-9')['state']=='CANCELLED'
 with direct_vm.expect_revert('unique incident'):c.open_recovery('store-9','Another sufficiently detailed incident record.',ACTIONS,DEPS,RULES,4)

