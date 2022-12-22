{
  description = "INET Framework - GPL licensed models";

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
      gversion = "${githash}.${timestamp}";

    in rec {
      packages = rec {
        default = pkgs.python310Packages.buildPythonApplication {
          inherit pname;
          version = gversion;
          src = ./.;
          doCheck = false;
          dontConfigure = true;
          dontBuild = true;
          format = "other";

          propagatedBuildInputs = with pkgs; [ nix coreutils findutils bash wget gnutar gzip unzip git openssh ];

          postPatch = ''
            patchShebangs ./opp_env
          '';

          installPhase = ''
            runHook preInstall
            install -D ./opp_env "$out"/bin/opp_env
            runHook postInstall
          '';

          meta = with pkgs.lib; {
            description = "A tool to set up development environment for OMNeT++ projects";
            license = licenses.lgpl3;
          };
        };
      };

      devShells = rec {
        default = pkgs.mkShell {
          name = "${pname}-${gversion}";
          packages = [ self.packages.${system}.default ];
        };

      };

    });
}