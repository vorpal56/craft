import info
from CraftConfig import *

class subinfo(info.infoclass):
    def setTargets( self ):
        self.versionInfo.setDefaultValues( )
        self.shortDescription = "All kind of addons to improve your Plasma experience"

    def setDependencies( self ):
        self.runtimeDependencies['kde/kde-runtime'] = 'default'
        self.runtimeDependencies['kde/kde-workspace'] = 'default'
        self.runtimeDependencies['kde/kdepimlibs'] = 'default'
        self.runtimeDependencies['kde/marble'] = 'default'
        self.runtimeDependencies['kde/libkexiv2'] = 'default'
        self.runtimeDependencies['kdesupport/attica'] = 'default'
        self.runtimeDependencies['kdesupport/qca'] = 'default'
        self.runtimeDependencies['kdesupport/qjson'] = 'default'
        self.runtimeDependencies['kdesupport/dbusmenu-qt'] = 'default'
        self.runtimeDependencies['win32libs/eigen2'] = 'default'

from Package.CMakePackageBase import *

class Package(CMakePackageBase):
    def __init__( self ):
        CMakePackageBase.__init__( self )

