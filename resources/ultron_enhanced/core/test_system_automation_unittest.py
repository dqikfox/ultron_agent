import unittest
import time
from system_automation import SystemAutomation

class TestSystemAutomation(unittest.TestCase):
    def setUp(self):
        self.system = SystemAutomation({})
        self.system.is_admin = True  # Simulate admin for power tests

    def test_power_control_unknown(self):
        res = self.system._handle_power_control({'action': 'unknown'})
        self.assertFalse(res['success'])
        self.assertIn('Unknown power action', res['message'])

    def test_power_control_no_admin(self):
        self.system.is_admin = False
        res = self.system._handle_power_control({'action': 'shutdown'})
        self.assertFalse(res['success'])
        self.assertIn('Administrator privileges', res['message'])
        self.system.is_admin = True

    def test_system_info_basic(self):
        res = self.system._handle_system_info({'info_type': 'basic'})
        self.assertTrue(res['success'])
        self.assertIn('system_info', res)

    def test_system_info_memory(self):
        res = self.system._handle_system_info({'info_type': 'memory'})
        self.assertTrue(res['success'])
        self.assertIn('memory_info', res)

    def test_automation_task_lifecycle(self):
        create = self.system._create_automation_task({'name': 'Test', 'description': 'desc', 'commands': []})
        self.assertTrue(create['success'])
        tid = create['task_id']
        listed = self.system._list_automation_tasks()
        self.assertTrue(listed['success'])
        self.assertTrue(any(t['id'] == tid for t in listed['tasks']))
        deleted = self.system._delete_automation_task({'task_id': tid})
        self.assertTrue(deleted['success'])

    def test_scheduled_task_lifecycle(self):
        sched = self.system._create_scheduled_task({'schedule_time': time.time() + 60, 'task_data': {'type': 'system_info', 'data': {'info_type': 'basic'}}})
        self.assertTrue(sched['success'])
        tid = sched['task_id']
        listed = self.system._list_scheduled_tasks()
        self.assertTrue(listed['success'])
        self.assertTrue(any(t['id'] == tid for t in listed['scheduled_tasks']))
        cancel = self.system._cancel_scheduled_task({'task_id': tid})
        self.assertTrue(cancel['success'])

if __name__ == '__main__':
    unittest.main()
