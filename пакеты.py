import pkg_resources

# Получаем список всех установленных пакетов в виртуальном окружении
installed_packages = pkg_resources.working_set

# Создаем строку с командой pip install для всех пакетов
pip_install_command = 'pip install ' + ' '.join([f"{package.key}=={package.version}" for package in installed_packages])

# Выводим команду pip install
print(pip_install_command)
