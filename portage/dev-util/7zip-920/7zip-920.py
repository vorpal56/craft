from multiprocessing import sharedctypes

import info
from CraftVersion import CraftVersion
from Package.MaybeVirtualPackageBase import MaybeVirtualPackageBase


class subinfo( info.infoclass ):
    def setTargets( self ):
        self.targets["920"] = "http://www.7-zip.org/a/7za920.zip"
        self.targetInstallPath["920"] = os.path.join("dev-utils", "bin")
        self.targetDigests["920"] = (['2a3afe19c180f8373fa02ff00254d5394fec0349f5804e0ad2f6067854ff28ac'], CraftHash.HashAlgorithm.SHA256)


        self.shortDescription = "7-Zip is a file archiver with a high compression ratio."
        self.homepage = "http://www.7-zip.org/"
        self.defaultTarget = "920"

from Package.BinaryPackageBase import *

class SevenZipPackage( BinaryPackageBase ):
    def __init__( self ):
        BinaryPackageBase.__init__( self )
        self.subinfo.options.package.disableBinaryCache = True

    def install( self ):
        utils.utilsCache.clear()
        return utils.copyFile(os.path.join(self.sourceDir(), "7za.exe"), os.path.join(self.installDir(), "7za.exe"), linkOnly=False)



class Package(MaybeVirtualPackageBase):
    def __init__(self):
        # why does the commone pattern not work here \d+\.\d+
        MaybeVirtualPackageBase.__init__(self,
                                         not utils.utilsCache.checkVersionGreaterOrEqual("7za", version="16.04",
                                                                                         pattern=re.compile(".*(\d\d\.\d+).*", re.DOTALL), versionCommand="-version"),
                                         classA=SevenZipPackage)
