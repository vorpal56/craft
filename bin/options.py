## @package property handling
#
# (c) copyright 2009-2011 Ralf Habacker <ralf.habacker@freenet.de>
#
#
# properties from classes in this package could be set
#
# - by package scripts,
# - by setting the 'Options' environment variable or
# - by command line
#
# for example:
#
# in blueprints/subdir/package/file.py
#   ...
#   self.subinfo.options.cmake.openIDE=1
#
# or
#
# craft "--options=cmake.openIDE=1" --make kdewin-installer
#
# or
#
# set Options=cmake.openIDE=1
# craft --make kdewin-installer
#
# The parser in this package is able to set all attributes
#
# for example:
#
#  craft "--options=unpack.unpackIntoBuildDir=1 useBuildType=1" --make <package>
#
import utils
from CraftConfig import *
from CraftCore import CraftCore
from Blueprints.CraftPackageObject import *

import configparser
import atexit
import copy

class UserOptions(object):
    class UserOptionsSingleton(object):
        _instance = None

        @property
        def __coreCategory(self):
            return "#Core"

        @property
        def __header(self):
            return """\
# The content of this file is partly autogenerated
# You can modify values and add settings for your blueprints
# Common settings available for all blueprints are:
#     ignored: [True|False]
#     version: some version
#     args: arguments passed to the configure step
#
# Example:
##     [libs]
##     ignored = True
##
##     [lib/qt5]
##     version = 5.9.3
##     ignored = False
##     withMySQL = True
##
##     [kde/pim/akonadi]
##     args = -DAKONADI_BUILD_QSQLITE=On
##
#
# Settings are inherited, so you can set them for a whole sub branch or a single blueprint.
# While blueprint from [libs] are all ignored blueprint from [libs/qt5] are not.
#
"""

        def __init__(self):
            self.cachedOptions = {}
            self.commandlineOptions = {}
            self.packageOptions = {}
            self.options = {}
            self.registeredOptions = {}

            self.path = CraftCore.settings.get("Blueprints", "Settings",
                                               os.path.join(CraftCore.standardDirs.etcDir(), "BlueprintSettings.ini"))
            self.settings = configparser.ConfigParser(allow_no_value=True)
            self.settings.optionxform = str

            if os.path.isfile(self.path):
                self.settings.read(self.path)
            if not self.settings.has_section(self.__coreCategory):
                self.settings.add_section(self.__coreCategory)

            self.options = Options(package=None)

            settings = self.settings[self.__coreCategory]
            self._init_vars(settings, self.options)


        def initPackage(self, option):
            path = option._package.path
            if not self.settings.has_section(path):
                self.settings.add_section(path)
            settings = self.settings[path]
            return settings

        def toBool(self, x : str) -> bool:
            if not x:
                return False
            return self.settings._convert_to_boolean(x)

        def _init_vars(self, settings, opt, prefix="") -> None:
            for var in vars(opt):
                if var.startswith("_"):
                    continue
                attr = getattr(opt, var)
                if isinstance(attr, (bool, str, int, type(None))):
                    key = f"{prefix}{var}"
                    if key not in settings:
                        if not attr is None:
                            settings[key] = str(attr)
                        else:
                            settings[key] = None
                    else:
                        val = settings[key]
                        if isinstance(attr, bool):
                            val = self.toBool(val)
                        setattr(opt, var, val)
                else:
                    self._init_vars(settings, attr, prefix=f"{prefix}{var}.")

        @staticmethod
        @atexit.register
        def __dump():
            instance = UserOptions.UserOptionsSingleton._instance
            if instance:
                try:
                    with open(instance.path, 'wt+') as configfile:
                        print(instance.__header, file=configfile)
                        instance.settings.write(configfile)
                except:
                    CraftCore.log.debug(f"Failed so save {instance.path}")


    @staticmethod
    def instance():
        if not UserOptions.UserOptionsSingleton._instance:
                UserOptions.UserOptionsSingleton._instance = UserOptions.UserOptionsSingleton()
        return UserOptions.UserOptionsSingleton._instance


    def __init__(self, package):
        self._cachedFromParent = {}
        self._package = package

        _register  = self.registerOption
        _convert = self._convert

        _register("version", str, permanent=False)
        _register("patchLevel", int, permanent=False)
        _register("ignored", bool, permanent=False)
        _register("args", "", permanent=False)

        settings = UserOptions.instance().settings
        if settings.has_section(package.path):
            _registered = UserOptions.instance().registeredOptions[package.path]
            for k, v in settings[package.path].items():
                if k in _registered:
                    v = _convert(_registered[k], v)
                setattr(self, k, v)
    @staticmethod
    def get(package):
        _instance = UserOptions.instance()
        packagePath = package.path
        if packagePath in _instance.cachedOptions:
            option = _instance.cachedOptions[packagePath]
        else:
            option = UserOptions(package)
            _instance.cachedOptions[packagePath] = option
        return option

    def _convert(self, valA, valB):
        """
        Converts valB to type(valA)
        """
        if valA is None:
            return valB
        _type = valA if callable(valA) else type(valA)
        if _type == type(valB):
            return valB
        if _type is bool:
            return UserOptions.instance().toBool(valB)
        return _type(valB)

    @staticmethod
    def setOptions(optionsIn):
        options = {}
        packageOptions = {}
        for o in optionsIn:
            key, value = o.split("=", 1)
            key, value = key.strip(), value.strip()
            if "." in key:
                package, key = key.split(".", 1)
                if package == "dynamic":
                    CraftCore.log.warning(f"Detected a deprecated setting \"{package}.{key} = {value}\", use the BlueprintsSettings.ini")
                    options[key] = value
                else:
                    if "/" in package:
                        # make sure it is a blueprint related setting
                        if CraftPackageObject.get(package):
                            if package not in packageOptions:
                                 packageOptions[package] = {}
                            packageOptions[package][key] = value
                        elif not CraftPackageObject.bootstrapping():
                            # in case we are bootstrapping Craft, we might not know that package yet
                            raise BlueprintNotFoundException(package, f"Package {package} not found, failed to set option {key} = {value}")
                    else:
                        options[f"{package}.{key}"] = value
        UserOptions.instance().commandlineOptions = options
        UserOptions.instance().packageOptions = packageOptions


    @staticmethod
    def addPackageOption(package : CraftPackageObject, key : str, value : str) -> None:
        if package.path not in UserOptions.instance().packageOptions:
            UserOptions.instance().packageOptions[package.path] = {}
        UserOptions.instance().packageOptions[package.path][key] = value

    def registerOption(self, key : str, default, permanent=True) -> None:
        _instance = UserOptions.instance()
        package = self._package
        if package.path not in _instance.registeredOptions:
            _instance.registeredOptions[package.path] = {}
        _instance.registeredOptions[package.path][key] = default
        if permanent:
            settings = _instance.initPackage(self)
            if key and key not in settings:
                settings[key] = str(default)

        # don't try to save types
        if not callable(default):
            if not hasattr(self, key):
                setattr(self, key, default)
            else:
                # convert type
                old = getattr(self, key)
                new = self._convert(default, old)
                #print(key, type(old), old, type(new), new)
                setattr(self, key, new)


    def __getattribute__(self, name):
        if name.startswith("_"):
            return super().__getattribute__(name)
        try:
            member = super().__getattribute__(name)
        except AttributeError:
            member = None
        if member and callable(member):
            return member

        #check cache
        _cache = super().__getattribute__("_cachedFromParent")
        if not member and name in _cache:
            return _cache[name]

        out = None
        _instance = UserOptions.instance()
        _package = super().__getattribute__("_package")
        _packagePath = _package.path
        if _packagePath in _instance.packageOptions and name in _instance.packageOptions[_packagePath]:
            if _packagePath not in _instance.registeredOptions or name not in _instance.registeredOptions[_packagePath]:
                 raise BlueprintException(f"Package {_package} has no registered option {name}", _package)
            out = self._convert(_instance.registeredOptions[_packagePath][name], _instance.packageOptions[_packagePath][name])
        elif name in _instance.commandlineOptions:
            # legacy option, removee soon
            out = _instance.commandlineOptions[name]
            CraftCore.log.warning(f"Deprecated use of options without package, please specify the package for the option {name}:\n"
                                  f"{_packagePath}.{name}={out}")
        elif member is not None:
            # value is not overwritten by comand line options
            return member
        else:
            parent = _package.parent
            if parent:
                out = getattr(UserOptions.get(parent), name)

        if not out:
            # name is a registered option and not a type but a default value
            if _packagePath in _instance.registeredOptions and name in _instance.registeredOptions[_packagePath]:
                default = _instance.registeredOptions[_packagePath][name]
                if not callable(default):
                    out = default


        # skip lookup in command line options and parent objects the enxt time
        _cache[name] = out
        #print(_packagePath, name, type(out), out)
        return out

class OptionsBase(object):
    def __init__(self):
        pass

## options for enabling or disabling features of KDE
## in the future, a certain set of features make up a 'profile' together
class OptionsFeatures(OptionsBase):
    def __init__(self):
        class PhononBackend(OptionsBase):
            def __init__(self):
                ## options for the phonon backend
                self.vlc = True
                self.ds9 = False

        self.phononBackend = PhononBackend()

        ## option whether to build nepomuk
        self.nepomuk = True

        ## enable python support in several packages.
        self.pythonSupport = False

        ## stick to the gcc 4.4.7 version
        self.legacyGCC = False

        ## enable or disable the dependency to plasma
        self.fullplasma = False

        ## enable plugins of kdevelop
        self.fullkdevelop = False


## options for the fetch action
class OptionsFetch(OptionsBase):
    def __init__(self):
        ## option comment
        self.option = None
        self.ignoreExternals = False
        ## enable submodule support in git single branch mode
        self.checkoutSubmodules = False


## options for the unpack action
class OptionsUnpack(OptionsBase):
    def __init__(self):
        ## By default archives are unpackaged into the workdir.
        #  Use this option to unpack archives into recent build directory
        self.unpackIntoBuildDir = False
        #  Use this option to run 3rd party installers
        self.runInstaller = False


## options for the configure action
class OptionsConfigure(OptionsBase):
    def __init__(self):
        ## with this option additional arguments could be added to the configure commmand line
        self.args = None
        ## with this option additional arguments could be added to the configure commmand line (for static builds)
        self.staticArgs = None
        ## set source subdirectory as source root for the configuration tool.
        # Sometimes it is required to take a subdirectory from the source tree as source root
        # directory for the configure tool, which could be enabled by this option. The value of
        # this option is added to sourceDir() and the result is used as source root directory.
        self.configurePath = None
        # add build target to be included into build. This feature is cmake only and requires the
        # usage of the 'macro_optional_add_subdirectory' macro. The value is a string.
        self.onlyBuildTargets = None

        # add the cmake defines that are needed to build tests here
        self.testDefine = None

        ## run autogen in autotools
        self.bootstrap = False

        # do not use default include path
        self.noDefaultInclude = False

        ## do not use default lib path
        self.noDefaultLib = False

        ## set this attribute in case a non standard configuration
        # tool is required (supported currently by QMakeBuildSystem only)
        self.tool = False

        # do not add --prefix on msys
        self.noDefaultOptions = False

        # cflags currently only used for autotools
        self.cflags = ""

        # cxxflags currently only used for autotools
        self.cxxflags = ""

        # ldflags currently only used for autotools
        self.ldflags = ""

        # the project file, this is either a .pro for qmake or a sln for msbuild
        self.projectFile = None


## options for the make action
class OptionsMake(OptionsBase):
    def __init__(self):
        ## ignore make error
        self.ignoreErrors = None
        ## options for the make tool
        self.makeOptions = None
        ## define the basename of the .sln file in case cmake.useIDE = True
        self.slnBaseName = None
        self.supportsMultijob = True


## options for the install action
class OptionsInstall(OptionsBase):
    def __init__(self):
        ## use either make tool for installing or
        # run cmake directly for installing
        self.useMakeToolForInstall = True
        ## add DESTDIR=xxx support for autotools build system
        self.useDestDir = True


## options for the merge action
class OptionsMerge(OptionsBase):
    def __init__(self):
        ## subdir based on installDir() used as merge source directory
        self.sourcePath = None


## options for the package action
class OptionsPackage(OptionsBase):
    def __init__(self):
        ## defines the package name
        self.packageName = None
        ## defines the package version
        self.version = None
        ## use compiler in package name
        self.withCompiler = True
        ## use special packaging mode  (only for qt)
        self.specialMode = False
        ## pack also sources
        self.packSources = True
        ## pack from subdir of imageDir()
        # currently supported by SevenZipPackager
        self.packageFromSubDir = None
        ## use architecture in package name
        # currently supported by SevenZipPackager
        self.withArchitecture = False
        ## add file digests to the package located in the manifest sub dir
        # currently supported by SevenZipPackager
        self.withDigests = True
        ##disable stripping of binary files
        # needed for mysql, striping make the library unusable
        self.disableStriping = False

        ##disable the binary cache for this package
        self.disableBinaryCache = False

        ## wheter to move the plugins to bin
        self.movePluginsToBin = utils.OsUtils.isWin()


class OptionsCMake(OptionsBase):
    def __init__(self):
        ## use IDE for msvc2008 projects
        self.useIDE = False
        ## use IDE for configuring msvc2008 projects, open IDE in make action instead of running command line orientated make
        self.openIDE = False
        ## use CTest instead of the make utility
        self.useCTest = CraftCore.settings.getboolean("General", "EMERGE_USECTEST", False)


class OptionsGit(OptionsBase):
    def __init__(self):
        ## enable support for applying patches in 'format-patch' style with 'git am' (experimental support)
        self.enableFormattedPatch = False


## main option class
class Options(object):
    def __init__(self, package=None):
        if package:
            self.__dict__ = copy.deepcopy(UserOptions.instance().options.__dict__)
            self.dynamic = UserOptions.get(package)
            self.configure.args = self.dynamic.args
            return

        ## options for the dependency generation
        self.features = OptionsFeatures()
        ## options of the fetch action
        self.fetch = OptionsFetch()
        ## options of the unpack action
        self.unpack = OptionsUnpack()
        ## options of the configure action
        self.configure = OptionsConfigure()
        ## options of the configure action
        self.make = OptionsMake()
        ## options of the install action
        self.install = OptionsInstall()
        ## options of the package action
        self.package = OptionsPackage()
        ## options of the merge action
        self.merge = OptionsMerge()
        ## options of the cmake buildSystem
        self.cmake = OptionsCMake()
        ## options of the git module
        self.git = OptionsGit()

        ## add the date to the target
        self.dailyUpdate = False

        ## has an issue with a too long path
        self.needsShortPath = False

        ## this option controls if the build type is used when creating build and install directories.
        # The following example shows the difference:
        # \code
        #                True                                False
        # work/msvc2008-RelWithDebInfo-svnHEAD     work/msvc2008-svnHEAD
        # image-msvc2008-RelWithDebInfo-svnHEAD    image-msvc2008-svnHEAD
        # \endcode
        #
        self.useBuildType = True

        ## skip the related package from debug builds
        self.disableDebugBuild = False
        ## skip the related package from release builds
        self.disableReleaseBuild = False
        ## exit if system command returns errors
        self.exitOnErrors = True

        ## there is a special option available already
        self.buildTools = False
        self.buildStatic = CraftCore.settings.getboolean("Compile", "Static")

        self.useShadowBuild = True

    def isActive(self, package):
        if isinstance(package, str):
            package = CraftPackageObject.get(package)
        return not package.isIgnored()
