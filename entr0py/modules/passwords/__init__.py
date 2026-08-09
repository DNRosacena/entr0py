from entr0py.modules.passwords.hydra   import Hydra
from entr0py.modules.passwords.hashcat import Hashcat
from entr0py.modules.passwords.john    import John
from entr0py.modules.passwords.cupp    import Cupp
from entr0py.modules.passwords.cewl    import Cewl
from entr0py.modules.passwords.crunch  import Crunch

ALL = [Hydra(), Hashcat(), John(), Cupp(), Cewl(), Crunch()]
