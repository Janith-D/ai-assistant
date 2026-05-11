import os
import sys
# Ensure workspace root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from tools.filesystem import create_folder, list_directory
from tools.system_info import get_system_info

home = os.path.expanduser('~')
desktop = os.path.join(home, 'Desktop')
path = os.path.join(desktop, 'Test_AI_Assistant')
print('Creating folder:', path)
def call_tool(t, arg):
	# Support different tool wrapper interfaces
	if callable(t):
		return t(arg)
	if hasattr(t, 'run'):
		return t.run(arg)
	if hasattr(t, 'func'):
		return t.func(arg)
	return f'UNCALLABLE TOOL: {type(t)}'

res = call_tool(create_folder, path)
print('create_folder ->', res)
print('\nListing Desktop parent:')
res_list = call_tool(list_directory, desktop)
print(res_list[:1000])
print('\nRAM info:')
res_ram = call_tool(get_system_info, 'ram')
print(res_ram)
