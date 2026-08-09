"""
entr0py.modules
~~~~~~~~~~~~~~~
Auto-registers all modules into the global registry on import.
"""
from entr0py.core.registry import get_registry

from entr0py.modules import recon, osint, network, web, passwords
from entr0py.modules import exploitation, post_exploit, wireless, forensics, social, mobile

_registry = get_registry()
for _pkg in (recon, osint, network, web, passwords,
             exploitation, post_exploit, wireless, forensics, social, mobile):
    _registry.register_all(_pkg.ALL)
