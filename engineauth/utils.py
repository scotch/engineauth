

def load_config(default_values, user_values):
    if user_values is None:
        return default_values
    config = {}
    for k, v in user_values.items():
        if k in default_values:
            if isinstance(v, dict):
                cloned = user_values[k].copy()
                for key, value in default_values[k].items():
                    if key is not None and key not in user_values[k] \
                    or user_values[k][key] == '':
                        cloned[key] = value
                config[k] = cloned
            else:
                config[k] = v
        else:
            config[k] = v
    for k, v in default_values.items():
        if k not in config:
            config[k] = v
    return config

def import_class(full_path):
    path_split = full_path.split('.')
    path = ".".join(path_split[:-1])
    klass = path_split[-1:]
    mod = __import__(path, fromlist=[klass])
    return getattr(mod, klass[0])

