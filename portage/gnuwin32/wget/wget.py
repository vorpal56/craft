import info

# notes:
# 1. because the python http implementation do not support
#    proxies a local copy of wget is used for downloading
#    the all inclusive wget binary is taken from
#    http://users.ugent.be/~bpuype/wget/
#    and do not have the multiple dll installation
#    problem normal gnuwin32 package have
#
# 2. This package do not use the class base class BinaryPackageBase
#    because of not wanted cyclic dependencies
#
#3. current version is from http://opensourcepack.blogspot.com/2010/05/wget-112-for-windows.html


class subinfo(info.infoclass):
    def setTargets( self ):
        self.targets['dummy'] = 'empty'
        self.defaultTarget = 'dummy'

from Package.BinaryPackageBase import *

class Package(BinaryPackageBase):
    def __init__( self):
        BinaryPackageBase.__init__(self)
        self.subinfo.options.merge.ignoreBuildType = True
        self.subinfo.options.merge.destinationPath = "dev-utils"

    def fetch(self):
        return True

    def unpack(self):
        utils.cleanDirectory(self.sourceDir())
        return utils.copyFile(os.path.join(self.packageDir(),'wget.exe'), os.path.join(self.sourceDir(), "bin",'wget.exe'))

