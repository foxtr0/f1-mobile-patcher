plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
    id("com.chaquo.python") version "17.2.0"
}

android {
    namespace = "io.github.f1patcher"
    compileSdk = 35

    defaultConfig {
        applicationId = "io.github.f1patcher"
        minSdk = 24
        targetSdk = 35
        versionCode = 1
        versionName = "1.0"

        // Every phone that can run this game is arm64.
        ndk { abiFilters += "arm64-v8a" }
    }

    buildTypes {
        release {
            isMinifyEnabled = false
            // Debug key so `assembleRelease` works without a keystore.
            signingConfig = signingConfigs.getByName("debug")
        }
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }

    kotlinOptions {
        jvmTarget = "17"
    }
}

chaquopy {
    defaultConfig {
        version = "3.12"
        // Chaquopy finds a matching python3 on PATH; set buildPython("...") if it can't.
    }
}
