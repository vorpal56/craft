import info

class subinfo(info.infoclass):
    def setTargets( self ):
        self.versionInfo.setDefaultValues("")

        self.homepage = 'http://www.boost.org/'

        self.shortDescription = 'portable C++ libraries'

    def setDependencies( self ):
        self.runtimeDependencies['win32libs/boost-headers'] = 'default'
        self.runtimeDependencies['win32libs/boost-bjam'] = 'default'
        self.runtimeDependencies['win32libs/boost-atomic'] = 'default'
        self.runtimeDependencies['win32libs/boost-graph'] = 'default'
        self.runtimeDependencies['win32libs/boost-program-options'] = 'default'
        if self.options.features.pythonSupport:
            self.runtimeDependencies['win32libs/boost-python'] = 'default'
        self.runtimeDependencies['win32libs/boost-regex'] = 'default'
        self.runtimeDependencies['win32libs/boost-system'] = 'default'
        self.runtimeDependencies['win32libs/boost-thread'] = 'default'
        self.runtimeDependencies['win32libs/boost-random'] = 'default'
        self.runtimeDependencies['win32libs/boost-iostreams'] = 'default'
        self.runtimeDependencies['win32libs/boost-filesystem'] = 'default'
        self.runtimeDependencies['win32libs/boost-date-time'] = 'default'

from Package.VirtualPackageBase import *

class Package( VirtualPackageBase ):
    def __init__( self ):
        VirtualPackageBase.__init__( self )


