{
  description = "opp_env";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs";
  };

  outputs = { self, nixpkgs }:
  let
    system = "x86_64-linux";
    pkgs = import nixpkgs { inherit system; };
  in {

    packages.${system} = rec {
      opp_env = pkgs.callPackage ./default.nix {};
      default = opp_env;
    };

  };
}
