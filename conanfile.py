from conans import ConanFile, AutoToolsBuildEnvironment, tools, CMake
import os


class ApacheAPR(ConanFile):
    name = "apache-apr"
    version = "1.6.3"
    url = "https://github.com/jgsogo/conan-apache-apr"
    homepage = "https://apr.apache.org/"
    license = "http://www.apache.org/LICENSE.txt"
    exports_sources = ["LICENSE",]
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False]}
    default_options = "shared=False"

    lib_name = "apr-" + version

    def source(self):
        file_ext = ".tar.gz" if not self.settings.os == "Windows" else "-win32-src.zip"
        tools.get("http://archive.apache.org/dist/apr/apr-{v}{ext}".format(v=self.version, ext=file_ext))

    def patch(self):
        if self.settings.os == "Windows":
            if self.settings.build_type == "Debug":
                tools.replace_in_file(os.path.join(self.lib_name, 'CMakeLists.txt'),
                                      "SET(install_bin_pdb ${install_bin_pdb} ${PROJECT_BINARY_DIR}/libapr-1.pdb)",
                                      "SET(install_bin_pdb ${install_bin_pdb} ${PROJECT_BINARY_DIR}/Debug/libapr-1.pdb)")

    def build(self):
        self.patch()
        if self.settings.os == "Windows":
            cmake = CMake(self)
            cmake.configure(source_folder=self.lib_name)
            cmake.build()
            cmake.install()
        else:
            env_build = AutoToolsBuildEnvironment(self)
            env_build.configure(configure_dir=self.lib_name,
                                args=['--prefix', self.package_folder, ],
                                build=False)  # TODO: Workaround for https://github.com/conan-io/conan/issues/2552
            env_build.make()
            env_build.make(args=['install'])

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
