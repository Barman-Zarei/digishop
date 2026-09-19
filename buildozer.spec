[app]
title = DigiShop
package.name = digishop
package.domain = org.barmanzarei
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
source.exclude_dirs = backend,.github,.git,venv,bin,tests,__pycache__
version = 5.7.48
requirements = python3==3.11.9,kivy==2.3.1,requests
orientation = portrait
android.accept_sdk_license = True
android.permissions = INTERNET
android.api = 33
android.minapi = 21
android.ndk = 25b
android.ndk_api = 21
android.archs = arm64-v8a, armeabi-v7a

[buildozer]
log_level = 2
warn_on_root = 1
