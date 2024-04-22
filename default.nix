{ pkgs ? import <nixpkgs> {} }:
let
  version = "0.28.1.240417";
in
pkgs.python3Packages.buildPythonPackage {
  name = "opp_env";
  src = ./.;

  SETUPTOOLS_SCM_PRETEND_VERSION = version;

  propagatedBuildInputs = with pkgs.python3Packages; [
    pkgs.nix
    pkgs.curl
    pkgs.git
    pkgs.btar
  ];

  pyproject = true;

  build-system = with pkgs.python3Packages; [ setuptools-scm ];

  pythonImportsCheck = [
    "opp_env.database"
  ];

  doCheck = true;
}
