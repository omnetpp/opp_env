{ pkgs ? import <nixpkgs> {} }:
let
  version = "0.1";
in
pkgs.python3Packages.buildPythonPackage {
  name = "opp_env";
  src = ./.;

  patches = [
    ./nix/0001-Fix-permissions-after-copying-templates.patch
    ./nix/0002-Remove-upgrade-subcommand.patch
    ./nix/0003-Remove-pip-from-dependencies.patch
  ];

  SETUPTOOLS_SCM_PRETEND_VERSION = version;

  propagatedBuildInputs = with pkgs.python3Packages; [
    packaging
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

  doCheck = false;
}
