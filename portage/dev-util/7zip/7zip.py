import info
from CraftVersion import CraftVersion

class subinfo( info.infoclass ):
    def setTargets( self ):
        patchLvl = ".1"
        for ver in [ "1604"]:
            self.targets[ ver + patchLvl ] = f"http://www.7-zip.org/a/7z{ver}-extra.7z"
            self.targetInstallPath[ ver + patchLvl ] = os.path.join("dev-utils", "bin")
        self.targetDigests['1604.1'] = (['59f41025acc40cf2e0b30b5cc6e4bcb1e07573201e256fbe8edb3c9c514dd251'], CraftHash.HashAlgorithm.SHA256)

        self.shortDescription = "7-Zip is a file archiver with a high compression ratio."
        self.homepage = "http://www.7-zip.org/"
        self.defaultTarget = "1604.1"

    def setDependencies( self ):
        self.buildDependencies["dev-util/7zip-920"] = "default"

from Package.BinaryPackageBase import *

class Package( BinaryPackageBase ):
    def __init__( self ):
        BinaryPackageBase.__init__( self )

    def install( self ):
        utils.utilsCache.clear()
        if compiler.isX64():
            return utils.copyFile(os.path.join(self.sourceDir(), "x64", "7za.exe"), os.path.join(self.installDir(), "7za.exe"), linkOnly=False)
        else:
            return utils.copyFile(os.path.join(self.sourceDir(), "7za.exe"), os.path.join(self.installDir(), "7za.exe"), linkOnly=False)
