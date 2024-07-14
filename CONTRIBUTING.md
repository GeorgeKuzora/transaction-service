# Разработка и запуск проекта

Для разработки проекта используется рабочее окружение настроенное внутри devcontainer.

## Требования для разработки проекта в Devcontainer

В зависимости от используемой операционной системы некоторые шаги и команды могут оличатся. В этом случае обращайтесь к версии документации для вашей операционной системы.

Для работы над проектом в devcontainer необходимо:

- Для Windows: рекомендуется использовать [WSL](https://virgo.ftc.ru/pages/viewpage.action?pageId=1084887269).
- Установить Docker Desktop для MacOS/Windows или просто docker для Linux. [Docker Desktop](https://www.docker.com/products/docker-desktop/).
- Установить [Visual Studio Code](https://code.visualstudio.com/download).
-  [Настроить Visual Studio Code и Docker для использования Devcontainers](https://code.visualstudio.com/docs/devcontainers/containers#_getting-started).
  - Необходимые плагины VS Code:
    - `ms-vscode-remote.remote-containers`
    - `ms-azuretools.vscode-docker`
- Установить Git
- Установить OpenSSH с SSH Agent.
- [Настроить Git и SSH для работы в Devcontainer](https://code.visualstudio.com/remote/advancedcontainers/sharing-git-credentials)
- Установить OpenSSL
- Установить [Шрифты для powerlevel10k](https://github.com/romkatv/powerlevel10k?tab=readme-ov-file#fonts)
- [Установить шрифт Meslo Nerd Font для CLI в терминале](https://github.com/romkatv/powerlevel10k?tab=readme-ov-file#fonts)
- По необходимости установить и настроить kubectl, внутри контейнера будут использованы настройки с хоста
- Склонировать этот репозиторий на рабочую станцию
- Открыть директорию с репозиторием через Visual Studio Code
- Ввести `Ctrl+Shift+P` или `Cmd+Shift+P` и выбрать `Dev Containers: Rebuild and Reopen in Container`

## Работа над проектом внутри Devcontainer

### Конфигурация рабочего окружения

Если какие-то из дальнейших пунктов у вас уже выполнены, смело пропускайте шаг.

После установки необходимого ПО:
- Сгенерируйте SSH ключ и добавьте его в свой MosHub аккаунт
- Настройте `user.name` и `user.email` для Git
- [Настройте SSH Agent c вашим ключом](https://code.visualstudio.com/remote/advancedcontainers/sharing-git-credentials)
- Склонируйте текущий репозиторий в локальную директорию, если еще не сделали этого

Для настройки kubernetes:
- Сгенерируйте ключи для kubectl и положите их в папку `~/.kube`
- Настройте kubectl на использование ключей из папки `~/.kube`

После настройки локального окружения:
- Откройте директорию в Visual Studio Code
- Нажмите `Ctrl+Shift+P` или `Cmd+Shift+P`
- Введите `Dev Containers:`
- Выберите из предложенных вариантов пункт `Dev Containers: Rebuild and Reopen in Container`
- Дождитесь открытия проекта внутри окружения в Devcontainer

### Окружение доступное после старта Devcontainer

После старта контейнера будут доступны следующие преднастроенные возможности:

#### Преднастроенная конфигурация для запуска линтера

  Доступ из командной панели:

  - Нажмите `Ctrl+Shift+P` или `Cmd+Shift+P`
  - Выберете `Tasks: Run Task`
  - Выберете `Flake8` или `ISort`

#### Преднастроенная конфигурация для запуска тестов

Смотрите по кнопке `Testing` в боковой панели Visual Studio Code.

#### Преднастроенная конфигурация для запуска сервиса

  Смотрите по кнопке `Run and Debug` в боковой панели Visual Studio Code.

- `Zsh` с Oh-My-Zsh в качестве shell по-умолчанию
- базовые консольные инструменты вроде `git`, `curl` и прочие
- `kubectl` и `helm` для работы с kubernetes
- `python` версии 3.12 с `poetry` для управления зависимостями и виртуальным окружением
- настроен доступ до `docker` на хосте

## Структура проекта

`CHANGELOG.md` — файл изменений, содержащий информацию об изменениях в проекте.
`CONTRIBUTING.md` — файл с инструкциями по внесению вклада в проект.
`poetry.lock` — файл блокировки зависимостей, который гарантирует, что все зависимости проекта будут одинаковыми на всех машинах разработчиков.
`pyproject.toml` — файл конфигурации Poetry, менеджера зависимостей для Python.
`pytest.ini` — файл конфигурации Pytest, фреймворка для тестирования кода на Python.
`README.md` — файл с описанием проекта.
`src/` — каталог с исходным кодом проекта.
`app/` — каталог с кодом сервиса.
`api/` — каталог с кодом API проекта.
`core/` — каталог с кодом бизнес логики проекта.
`transactions.py` — файл с реализацией сервиса транзакций.
`external/` — каталог с внешними зависимостями проекта.
`in_memory_repository.py` - файл с реализацией хранилища данных в виде списков Python.
`metrics/` — каталог с метриками проекта.
`service.py` — файл с реализацией точки входа в приложение.
`config/` — каталог с конфигурационными файлами проекта.
`tests/` — каталог с тестами проекта.
`integration/` — каталог с интеграционными-тестами проекта.
`unit/` — каталог с юнит-тестами проекта.
`test_transactions.py` — файл с тестами сервиса транзакций.
`test_service.py` — файл с тестом проекта.
