import importlib
import pkgutil

def source_loader():
    sources = []
    package = 'sources'
    package_path = importlib.import_module(package).__path__
    
    for _, module_name, _ in pkgutil.iter_modules(package_path):
        module = importlib.import_module(f'{package}.{module_name}')
        for attr in dir(module):
            if attr.startswith('Source'):
                source_class = getattr(module, attr)
                if isinstance(source_class, type) and issubclass(source_class, object):  # Adjust according to base class if any
                    sources.append(source_class())
    
    return sources
