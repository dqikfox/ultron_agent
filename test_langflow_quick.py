import sys
sys.stdout.reconfigure(encoding='utf-8')

from tools.langflow_mcp_tool import LangflowMCPTool

tool = LangflowMCPTool()
print(tool.execute('test connection'))
print('\n' + '='*60 + '\n')
print(tool.execute('list workflows'))
