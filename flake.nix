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
      sversion = "0.1.0"; # schemantic version number

    in rec {
      packages = rec {
        default = pkgs.python310Packages.buildPythonApplication {
          inherit pname;
          version = gversion;
          src = ./.;
          doCheck = false;
          dontBuild = true;
          format = "other";

          buildInputs = with pkgs; [ bash wget git python310 ];

          postPatch = ''
            patchShebangs ./opp_env
          '';

          installPhase = ''
            runHook preInstall
            install -D ./opp_env "$out"/bin/opp_env
            runHook postInstall
          '';

          meta = with pkgs.lib; {
            description = "A tool to set up OMNeT++ model development environments";
            license = licenses.lgpl3;
          };
        };
      };

      devShells = rec {
        default = pkgs.mkShell {
          name = "${pname}-${gversion}";
          buildInputs = self.packages.${system}.default.buildInputs;

        };

      };

    });
}