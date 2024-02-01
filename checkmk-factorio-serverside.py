from .agent_based_api.v1 import *

def discover_factorio_version(section):
    yield Service()

def check_factorio_version(section):
    for line in section:
        if line[0].startswith("OK"):
            yield Result(state=State.OK, summary=" ".join(line))
        elif line[0].startswith("CRITICAL"):
            yield Result(state=State.CRIT, summary=" ".join(line))
        elif line[0].startswith("UNKNOWN"):
            yield Result(state=State.WARN, summary=" ".join(line))
        else:
            yield Result(state=State.UNKNOWN, summary="Unexpected response: " + " ".join(line))

register.check_plugin(
    name = "factorio_version",
    service_name = "Factorio Version",
    discovery_function = discover_factorio_version,
    check_function = check_factorio_version,
)