#
# copyright (c) 2009 Ralf Habacker <ralf.habacker@freenet.de>
#
# definitions for the qmake build system

from BuildSystem.BuildSystemBase import *
from Blueprints.CraftPackageObject import *
from Blueprints.CraftVersion import CraftVersion


class QMakeBuildSystem(BuildSystemBase):
    def __init__(self):
        BuildSystemBase.__init__(self, "qmake")
        self._platform = None
        self._qtVer = None
        self.subinfo.options.needsShortPath |= CraftCore.compiler.isMinGW()

    @property
    def qtVer(self):
        if not self._qtVer:
            self._qtVer = CraftVersion(CraftPackageObject.get("libs/qt5/qtbase").version)
        return self._qtVer

    @property
    def platform(self):
        if not self._platform:
            if OsUtils.isWin():
                if CraftCore.compiler.isMSVC():
                    if self.qtVer < CraftVersion("5.8"):
                        if CraftCore.compiler.isMSVC2017():
                            _compiler = "msvc2015"
                        else:
                            _compiler = CraftCore.compiler.abi.split("_")[0]
                    else:
                        _compiler = "msvc"
                    if CraftCore.compiler.isClang():
                        self._platform = f"win32-clang-{_compiler}"
                    else:
                        self._platform = f"win32-{_compiler}"
                elif CraftCore.compiler.isMinGW():
                    self._platform = "win32-g++"
                elif CraftCore.compiler.isIntel():
                    self._platform = "win32-icc"
                else:
                    CraftCore.log.critical(f"QMakeBuildSystem: unsupported compiler platform {CraftCore.compiler}")
            elif OsUtils.isUnix():
                if OsUtils.isMac():
                    osPart = "macx"
                elif OsUtils.isFreeBSD():
                    osPart = "freebsd"
                else:
                    osPart = "linux"

                if CraftCore.compiler.isClang():
                    compilerPart = "clang"
                else:
                    compilerPart = "g++"
                self._platform = osPart + "-" + compilerPart
        return self._platform

    def configure(self, configureDefines=""):
        """inplements configure step for Qt projects"""
        if not self.subinfo.options.useShadowBuild:
            self.enterSourceDir()
        else:
            self.enterBuildDir()

        proFile = self.configureSourceDir()
        if self.subinfo.options.configure.projectFile:
            proFile = os.path.join(self.configureSourceDir(), self.subinfo.options.configure.projectFile)
        command = "%s -makefile %s %s" % (CraftCore.cache.findApplication("qmake"), proFile, self.configureOptions(configureDefines))

        return utils.system(command)

    def make(self, options=""):
        """implements the make step for Qt projects"""
        if not self.subinfo.options.useShadowBuild:
            self.enterSourceDir()
        else:
            self.enterBuildDir()
        command = ' '.join([self.makeProgram, self.makeOptions(options)])

        return utils.system(command)

    def install(self, options=None):
        """implements the make step for Qt projects"""
        if not BuildSystemBase.install(self):
            return False

        if not self.subinfo.options.useShadowBuild:
            self.enterSourceDir()
        else:
            self.enterBuildDir()
        if options != None:
            command = f"{self.makeProgram} {options}"
        else:
            command = f"{self.makeProgram} install"

        return utils.system(command)

    def runTest(self):
        """running qmake based unittests"""
        return True

    def configureOptions(self, defines=""):
        """returns default configure options"""
        defines += BuildSystemBase.configureOptions(self, defines)
        if self.buildType() == "Release" or self.buildType() == "RelWithDebInfo":
            defines += ' "CONFIG -= debug"'
            defines += ' "CONFIG += release"'
        elif self.buildType() == "Debug":
            defines += ' "CONFIG += debug"'
            defines += ' "CONFIG -= release"'

        return defines

    def ccacheOptions(self):
        return ' "QMAKE_CC=ccache gcc" "QMAKE_CXX=ccache g++" "CONFIG -= precompile_header" '

    def clangOptions(self):
        if OsUtils.isUnix():
            return ' "CONFIG -= precompile_header" '
        return ''
