from entr0py.modules.osint.sherlock     import Sherlock
from entr0py.modules.osint.maigret      import Maigret
from entr0py.modules.osint.holehe       import Holehe
from entr0py.modules.osint.phoneinfoga  import PhoneInfoga
from entr0py.modules.osint.s3scanner    import S3Scanner

ALL = [Sherlock(), Maigret(), Holehe(), PhoneInfoga(), S3Scanner()]
