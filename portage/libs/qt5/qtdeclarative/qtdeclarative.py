# -*- coding: utf-8 -*-
import info

class subinfo(info.infoclass):
    def setTargets( self ):
        self.versionInfo.setDefaultValues( )

    def setDependencies( self ):
        self.runtimeDependencies['libs/qtbase'] = 'default'
        self.runtimeDependencies['libs/qtxmlpatterns'] = 'default'
        self.runtimeDependencies['libs/qtsvg'] = 'default'


from Package.Qt5CorePackageBase import *

class QtPackage( Qt5CorePackageBase ):
    def __init__( self, **args ):
        Qt5CorePackageBase.__init__( self )

class Package( Qt5CoreSdkPackageBase ):
    def __init__(self):
        Qt5CoreSdkPackageBase.__init__(self, classA=QtPackage)

