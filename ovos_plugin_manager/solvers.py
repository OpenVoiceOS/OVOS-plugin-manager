from ovos_plugin_manager.utils import load_plugin, normalize_lang, find_plugins, PluginTypes


def find_question_solver_plugins():
    return find_plugins(PluginTypes.QUESTION_SOLVER)


def get_question_solver_config_examples(module_name):
    cfgs = load_plugin(module_name + ".config", PluginTypes.QUESTION_SOLVER_CONFIG) or {}
    return {normalize_lang(lang): v for lang, v in cfgs.items()}


def get_question_solver_lang_config_examples(lang, include_dialects=False):
    lang = normalize_lang(lang)
    configs = {}
    for plug in find_question_solver_plugins():
        configs[plug] = []
        confs = get_question_solver_config_examples(plug)
        if include_dialects:
            lang = lang.split("-")[0]
            for l in confs:
                if l.startswith(lang):
                    configs[plug] += confs[l]
        elif lang in confs:
            configs[plug] += confs[lang]
        elif f"{lang}-{lang}" in confs:
            configs[plug] += confs[f"{lang}-{lang}"]
    return {k: v for k, v in configs.items() if v}


def get_question_solver_supported_langs():
    configs = {}
    for plug in find_question_solver_plugins():
        confs = get_question_solver_config_examples(plug)
        for lang, cfgs in confs.items():
            if confs:
                if lang not in configs:
                    configs[lang] = []
                configs[lang].append(plug)
    return configs


def load_question_solver_plugin(module_name):
    """Wrapper function for loading text_transformer plugin.

    Arguments:
        (str) Mycroft text_transformer module name from config
    Returns:
        class: found text_transformer plugin class
    """
    return load_plugin(module_name, PluginTypes.QUESTION_SOLVER)

