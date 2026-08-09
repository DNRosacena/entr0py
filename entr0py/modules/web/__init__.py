from entr0py.modules.web.sqlmap  import Sqlmap
from entr0py.modules.web.nuclei  import Nuclei
from entr0py.modules.web.ffuf    import Ffuf
from entr0py.modules.web.dalfox  import Dalfox
from entr0py.modules.web.nikto   import Nikto
from entr0py.modules.web.arjun   import Arjun
from entr0py.modules.web.wafw00f import Wafw00f
from entr0py.modules.web.whatweb import WhatWeb
from entr0py.modules.web.corsy   import Corsy

ALL = [Sqlmap(), Nuclei(), Ffuf(), Dalfox(), Nikto(), Arjun(), Wafw00f(), WhatWeb(), Corsy()]
