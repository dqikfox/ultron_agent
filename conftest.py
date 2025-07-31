import sys
from pathlib import Path

import inspect
import asyncio

# Ensure OpenAI API key is set for AsyncOpenAI
import os
os.environ.setdefault("OPENAI_API_KEY", "test_key")
import sys
from pathlib import Path

import inspect
import asyncio

# Run async test functions in the event loop
def pytest_pyfunc_call(pyfuncitem):
    testfunc = pyfuncitem.obj
    if inspect.iscoroutinefunction(testfunc):
        loop = asyncio.get_event_loop()
        # collect fixture arguments
        funcargs = {arg: pyfuncitem.funcargs[arg] for arg in pyfuncitem._fixtureinfo.argnames}
        loop.run_until_complete(testfunc(**funcargs))
        return True

# Ensure project root is on sys.path for imports in tests
root = Path(__file__).parent.resolve()
if str(root) not in sys.path:
    sys.path.insert(0, str(root))
