{
  description = "TikTok Redirect";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-parts.url = "github:hercules-ci/flake-parts";
    treefmt-nix.url = "github:numtide/treefmt-nix";
    treefmt-nix.inputs.nixpkgs.follows = "nixpkgs";
  };

  outputs =
    inputs@{ flake-parts, ... }:
    flake-parts.lib.mkFlake { inherit inputs; } {
      imports = [
        inputs.treefmt-nix.flakeModule
      ];

      systems = [
        "x86_64-linux"
        "aarch64-linux"
        "x86_64-darwin"
        "aarch64-darwin"
      ];

      perSystem =
        { pkgs, system, ... }:
        let
          # Android SDK setup
          androidComposition = pkgs.androidenv.composeAndroidPackages {
            platformVersions = [ "35" ];
            buildToolsVersions = [ "35.0.1" ];
            includeEmulator = false;
            includeNDK = false;
            includeSources = false;
            includeSystemImages = false;
          };

        in
        {
          # Override nixpkgs to allow unfree packages for Android SDK
          _module.args.pkgs = import inputs.nixpkgs {
            inherit system;
            config = {
              android_sdk.accept_license = true;
              allowUnfree = true;
            };
          };

          devShells.default = pkgs.mkShell {
            buildInputs = with pkgs; [
              # Java Development Kit (for keytool in setup_signing.sh)
              jdk17

              # Python for generate_fdroid_repo.py
              python3

              # Kotlin tools
              kotlin
              ktlint

              # Android development tools
              gradle
              androidComposition.androidsdk
            ];

            # Set up Android SDK environment
            ANDROID_HOME = "${androidComposition.androidsdk}/libexec/android-sdk";
            ANDROID_SDK_ROOT = "${androidComposition.androidsdk}/libexec/android-sdk";

            # Add Android SDK build-tools to PATH
            shellHook = ''
              export PATH="$ANDROID_HOME/build-tools/35.0.1:$PATH"

              echo "TikTok Redirect Development Environment"
              echo "======================================"
              echo ""
              echo "Available tools:"
              echo "  - Java: $(java -version 2>&1 | head -n 1)"
              echo "  - Kotlin: $(kotlin -version 2>&1 | head -n 1)"
              echo "  - Python: $(python3 --version)"
              echo "  - Gradle: $(gradle --version | head -n 1)"
              echo "  - ktlint: $(ktlint --version)"
              echo "  - keytool: $(command -v keytool)"
              echo "  - Android SDK: $ANDROID_HOME"
              echo ""
              echo "Quick start:"
              echo "  - Run setup_signing.sh:  ./scripts/setup_signing.sh"
              echo "  - Build debug APK:       ./gradlew assembleDebug"
              echo "  - Build release APK:     ./gradlew assembleRelease"
              echo ""
            '';
          };

          # treefmt configuration for `nix fmt`
          treefmt.config = {
            projectRootFile = "flake.nix";
            programs = {
              nixfmt.enable = true;
              shellcheck.enable = true;
              shfmt.enable = true;
              prettier.enable = true;
              actionlint.enable = true;
              ktlint.enable = true;
              ruff.format = true;
              ruff.check = true;
              mypy.enable = true;
            };
            settings.formatter = {
              prettier.excludes = [
                "*.gradle"
                "gradlew"
                "gradlew.bat"
                ".github/workflows/*"
              ];
            };
          };
        };
    };
}
