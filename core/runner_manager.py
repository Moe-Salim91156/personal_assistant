import importlib
import pkgutil
import os

PLUGIN_FOLDER = os.path.join(os.path.dirname(__file__), "../plugins")

def load_plugins():
    plugins = {}
    for finder, name, ispkg in pkgutil.iter_modules([PLUGIN_FOLDER]):
        try:
            module = importlib.import_module(f"plugins.{name}.runner")
            plugins[name] = module
        except Exception as e:
            print(f"[runner_manager] Failed to load {name}: {e}")
    return plugins

def execute(plugin_name, target=None, context=None):
    plugins = load_plugins()
    if plugin_name not in plugins:
        print(f"[runner_manager] Plugin '{plugin_name}' not found.")
        return False
    return plugins[plugin_name].run(target, context)

