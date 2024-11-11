{
  description = "hasura-home-finances";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = {self, nixpkgs, flake-utils}:
    flake-utils.lib.eachDefaultSystem(localSystem:
      let
        pkgs = import nixpkgs {
          system = localSystem;
        };
      in {
        devShells = {
          default = pkgs.mkShell {
            buildInputs = [
              pkgs.python3Packages.python
              pkgs.python3Packages.venvShellHook
            ];
            packages = [ ];
            venvDir = "./.venv";
            postVenvCreation = ''
              unset SOURCE_DATE_EPOCH
            '';
            postShellHook = ''
              unset SOURCE_DATE_EPOCH
              export LD_LIBRARY_PATH=${pkgs.lib.makeLibraryPath [pkgs.stdenv.cc.cc]}
            '';
          };
        };
      }
    );
}
