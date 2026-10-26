import time
from system_automation import SystemAutomation

# Minimal config for testing
config = {}
system = SystemAutomation(config)

print('--- Testing _handle_power_control (simulate, no admin) ---')
# Simulate not admin
system.is_admin = False
print(system._handle_power_control({'action': 'shutdown'}))

print('--- Testing _handle_power_control (simulate, admin, unknown action) ---')
system.is_admin = True
print(system._handle_power_control({'action': 'unknown'}))

print('--- Testing _handle_system_info (basic) ---')
print(system._handle_system_info({'info_type': 'basic'}))

print('--- Testing _handle_system_info (memory) ---')
print(system._handle_system_info({'info_type': 'memory'}))

print('--- Testing _handle_system_info (disk) ---')
print(system._handle_system_info({'info_type': 'disk'}))

print('--- Testing _handle_system_info (processes) ---')
print(system._handle_system_info({'info_type': 'processes'}))

print('--- Testing _handle_system_info (network) ---')
print(system._handle_system_info({'info_type': 'network'}))

print('--- Testing _handle_system_info (unknown) ---')
print(system._handle_system_info({'info_type': 'foobar'}))

print('--- Testing _create_automation_task and _list_automation_tasks ---')
res = system._create_automation_task({'name': 'TestTask', 'description': 'desc', 'commands': []})
print(res)
print(system._list_automation_tasks())

print('--- Testing _delete_automation_task (not found) ---')
print(system._delete_automation_task({'task_id': 999}))

print('--- Testing _delete_automation_task (found) ---')
print(system._delete_automation_task({'task_id': 1}))

print('--- Testing _create_scheduled_task and _list_scheduled_tasks ---')
sched = system._create_scheduled_task({'schedule_time': time.time() + 60, 'task_data': {'type': 'system_info', 'data': {'info_type': 'basic'}}})
print(sched)
print(system._list_scheduled_tasks())

print('--- Testing _cancel_scheduled_task (not found) ---')
print(system._cancel_scheduled_task({'task_id': 'not_a_real_id'}))

print('--- Testing _cancel_scheduled_task (found) ---')
print(system._cancel_scheduled_task({'task_id': sched['task_id']}))
