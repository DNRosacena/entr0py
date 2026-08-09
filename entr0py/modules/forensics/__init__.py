from entr0py.modules.forensics.binwalk    import Binwalk
from entr0py.modules.forensics.volatility3 import Volatility3
from entr0py.modules.forensics.stegseek   import Stegseek
from entr0py.modules.forensics.exiftool   import Exiftool
from entr0py.modules.forensics.foremost   import Foremost

ALL = [Binwalk(), Volatility3(), Stegseek(), Exiftool(), Foremost()]
