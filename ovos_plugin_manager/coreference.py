from ovos_plugin_manager.utils import normalize_lang, load_plugin, find_plugins, PluginTypes
from ovos_config import Configuration
from ovos_utils.log import LOG
from ovos_plugin_manager.templates.coreference import CoreferenceSolverEngine, replace_coreferences


def find_coref_plugins():
    return find_plugins(PluginTypes.COREFERENCE_SOLVER)


def get_coref_config_examples(module_name):
    cfgs = load_plugin(module_name + ".config", PluginTypes.COREFERENCE_SOLVER_CONFIG) or {}
    return {normalize_lang(lang): v for lang, v in cfgs.items()}


def get_coref_lang_config_examples(lang, include_dialects=False):
    lang = normalize_lang(lang)
    configs = {}
    for plug in find_coref_plugins():
        configs[plug] = []
        confs = get_coref_config_examples(plug)
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


def get_coref_supported_langs():
    configs = {}
    for plug in find_coref_plugins():
        confs = get_coref_config_examples(plug)
        for lang, cfgs in confs.items():
            if confs:
                if lang not in configs:
                    configs[lang] = []
                configs[lang].append(plug)
    return configs


def load_coref_plugin(module_name):
    """Wrapper function for loading coref plugin.

    Arguments:
        module_name (str): coref module name from config
    Returns:
        class: CoreferenceSolver plugin class
    """
    return load_plugin(module_name, PluginTypes.COREFERENCE_SOLVER)


class OVOSCoreferenceSolverFactory:
    """ replicates the base mycroft class, but uses only OPM enabled plugins"""
    MAPPINGS = {
        "pronomial": "ovos-coref-plugin-pronomial"
    }

    @staticmethod
    def get_class(config=None):
        """Factory method to get a CoreferenceSolver engine class based on configuration.

        The configuration file ``mycroft.conf`` contains a ``coref`` section with
        the name of a CoreferenceSolver module to be read by this method.

        "coref": {
            "module": <engine_name>
        }
        """
        config = config or get_coref_config()
        coref_module = config.get("module", "dummy")
        if coref_module == "dummy":
            return CoreferenceSolverEngine
        if coref_module in OVOSCoreferenceSolverFactory.MAPPINGS:
            coref_module = OVOSCoreferenceSolverFactory.MAPPINGS[coref_module]
        return load_coref_plugin(coref_module)

    @staticmethod
    def create(config=None):
        """Factory method to create a CoreferenceSolver engine based on configuration.

        The configuration file ``mycroft.conf`` contains a ``coref`` section with
        the name of a CoreferenceSolver module to be read by this method.

        "coref": {
            "module": <engine_name>
        }
        """
        config = config or get_coref_config()
        plugin = config.get("module") or "dummy"
        plugin_config = config.get(plugin) or {}
        try:
            clazz = OVOSCoreferenceSolverFactory.get_class(config)
            return clazz(plugin_config)
        except Exception:
            LOG.error(f'CoreferenceSolver plugin {plugin} could not be loaded!')
            raise


def get_coref_config(config=None):
    config = config or Configuration()
    lang = config.get("lang")
    if "intentBox" in config and "coref" not in config:
        config = config["intentBox"] or {}
        lang = config.get("lang") or lang
    if "coref" in config:
        config = config["coref"]
        lang = config.get("lang") or lang
    config["lang"] = lang or "en-us"
    coref_module = config.get('module') or 'dummy'
    coref_config = config.get(coref_module, {})
    coref_config["module"] = coref_module
    return coref_config


