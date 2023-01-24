{
  description = "A tool to set up development environment for OMNeT++ projects";

  inputs = {
    nixpkgs.url = "nixpkgs/nixos-22.11";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, flake-utils, nixpkgs }:
    flake-utils.lib.eachDefaultSystem(system:
    let
      pkgs = import nixpkgs { inherit system; };
      pname = "opp_env";
      githash = self.shortRev or "dirty";
      timestamp = pkgs.lib.substring 0 8 self.lastModifiedDate;
      version = "${githash}.${timestamp}";

    in with pkgs; rec {
      packages = rec {
        default = python3Packages.buildPythonApplication {
          inherit pname version;
          src = ./.;
          doCheck = false;
          format = "setuptools";

          propagatedBuildInputs = [ nix coreutils findutils bash wget gnutar gzip unzip git openssh ];

          meta = with lib; {
            description = "A tool to set up development environment for OMNeT++ projects";
            license = licenses.lgpl3;
          };
        };
      };

      devShells = rec {
        default = mkShell {
          name = "${pname}-${version}";
          packages = [ self.packages.${system}.default ];
        };

      };

    });
}